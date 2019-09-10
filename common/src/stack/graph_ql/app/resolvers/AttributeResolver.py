# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import defaultdict
import fnmatch
from functools import lru_cache
import os
import re
from collections import namedtuple, OrderedDict
import itertools
import socket
from functools import partial
from ipaddress import IPv4Network

from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
host = ObjectType("Host")
environment = ObjectType("Environment")
os_graphql = ObjectType("Os")
appliance = ObjectType("Appliance")
object_types = [host, environment, os_graphql, appliance]

@query.field("attributes")
def resolve_attributes(parent, info, scope=None, scope_name=None, **kwargs):
    where_conditionals = {
        f"attributes.{key}": value
        for key, value in kwargs.items()
        if key in ("id", "scope_map_id", "name", "value")
    }
    ignored_kwargs = set(key.split(".")[-1] for key in where_conditionals.keys()).difference(set(kwargs))
    if ignored_kwargs:
        raise ValueError(f"Received unsupported kwargs {ignored_kwargs}")

    cmd = """
        SELECT attributes.id, attributes.scope_map_id, attributes.name, attributes.value
        FROM attributes
        {join}
        {where}
    """
    join_string = ""
    if scope_name and not scope:
        raise ValueError("Cannot specify scope_name without scope")

    if scope_name and scope == "global":
        raise ValueError("Cannot specify scope_name at global scope")

    valid_scopes = ('global','appliance','os','environment', 'host')
    if scope:
        if scope not in valid_scopes:
            raise ValueError(f"{scope} is not one of the valid scopes {valid_scopes}")

        join_string = "INNER JOIN scope_map ON attributes.scope_map_id=scope_map.id "
        where_conditionals["scope_map.scope"] = scope

    if scope_name:
        if scope == 'appliance':
            table_name = "appliances"
        elif scope == 'os':
            table_name = "oses"
        elif scope == 'environment':
            table_name = "environments"
        elif scope == 'host':
            table_name = "nodes"
        else:
            raise RuntimeError(f"Bad scope {scope}")

        join_string += f"INNER JOIN {table_name} on scope_map.{scope if scope != 'host' else 'node'}_id={table_name}.id"
        where_conditionals[f"{table_name}.name"] = scope_name

    where_string = "WHERE"
    args = []
    first = True
    for key, value in where_conditionals.items():
        where_string += f" {'' if first else 'and '}{key}=%s"
        args.append(value)
        first = False

    if not args:
        where_string = ""

    cmd = cmd.format(join=join_string, where=where_string)
    result, _ = db.run_sql(cmd, args)

    return result

def str2bool(s):
    """Converts an on/off, yes/no, true/false string to
    True/False."""
    if type(s) == bool:
        return s
    if s and s.upper() in [ 'ON', 'YES', 'Y', 'TRUE', '1' ]:
        return True
    else:
        return False


def bool2str(b):
    """Converts an 1/0 to a yes/no"""
    if type(b) in [ bool, int ]:
        if b:
                return 'yes'
        else:
                return 'no'
    return None

def flatten(items):
    ''' flatten a nested list of items
    [(a,), (b,)]        -> [a, b]
    [(a,), (b,) (c, d)] -> [a, b, c, d]
    '''
    return list(itertools.chain.from_iterable(items))

def getApplianceNames(args=None):
    """
    Returns a list of appliance names from the database. For each arg
    in the ARGS list find all the appliance names that match the arg
    (assume SQL regexp). If an arg does not match anything in the
    database we raise an exception. If the ARGS list is empty return
    all appliance names.
    """

    appliances  = []
    if not args:
        args = ['%']		 # find all appliances

    for arg in args:
        result = db.run_sql_rows(
            'SELECT name from appliances where name like %s', (arg,)
        )
        names = flatten(result)

        if not names and arg != '%':
            raise ValueError(f"did not find appliance named {arg}")

        appliances.extend(names)

    return appliances

def getOSNames(args=None):
    oses = []
    if not args:
        args = ['%']		# find everything in table

    for arg in args:
        if arg == 'centos':
            if 'redhat' in oses:
                continue
            arg = 'redhat'

        names = flatten(db.run_sql_rows(
            'SELECT name from oses where name like %s order by name', (arg,)
        ))

        if not names and arg != '%':
            raise ValueError(f'OS named {arg} not found')

        oses.extend(names)

    return sorted(OrderedDict.fromkeys(oses))

def getEnvironmentNames(args=None):
    environments = []
    if not args:
        args = ['%']		# find everything in table

    for arg in args:
        names = flatten(db.run_sql_rows(
            'SELECT name from environments where name like %s', (arg,)
        ))

        if not names and arg != '%':
            raise ValueError(f'environment named {arg} not found')

        environments.extend(names)

    return sorted(OrderedDict.fromkeys(environments))

def _lookup_hostname(hostname):
    """
    Looks up a hostname in a case-insenstive manner to get how it is
    formarted in the DB, allowing MySQL LIKE patterns, and using the
    DatabaseConnection cache when possible.

    Returns None when the hostname doesn't exist.
    """

    # See if we need to do MySQL LIKE
    if '%' in hostname or '_' in hostname:
        rows = db.run_sql_rows('SELECT name FROM nodes WHERE name LIKE %s', (hostname,))
        if rows:
            return rows[0][0]

    rows = db.run_sql_rows('SELECT name FROM nodes WHERE name = %s', (hostname,))
    if rows:
        return rows[0][0]

    # No match
    return None

def getNodeName(hostname, subnet=None):
    if not subnet:
        lookup = _lookup_hostname(hostname)
        if lookup:
            hostname = lookup

        return hostname

    result = None

    for (netname, zone) in db.run_sql_rows("""
        net.name, s.zone from nodes n, networks net, subnets s
        where n.name like %s and s.name like %s
        and net.node = n.id and net.subnet = s.id
    """, (hostname, subnet)):
        # If interface exists, but name is not set
        # infer name from nodes table, and append
        # dns zone
        if not netname:
            netname = hostname
        if zone:
            result = '%s.%s' % (netname, zone)
        else:
            result = netname

    return result

def getHostname(hostname=None, subnet=None):
    """
    Returns the name of the given host as referred to in
    the database.  This is used to normalize a hostname before
    using it for any database queries.
    """

    # Look for the hostname in the database before trying to reverse
    # lookup the IP address and map that to the name in the nodes
    # table. This should speed up the installer w/ the restore pallet.

    if hostname and db.db_rows:
        if _lookup_hostname(hostname):
            return getNodeName(hostname, subnet)

    if not hostname:
        hostname = socket.gethostname()

        if db.db_rows:
            return ''
        else:
            return 'localhost'
    try:
        # Do a reverse lookup to get the IP address. Then do a
        # forward lookup to verify the IP address is in DNS. This is
        # done to catch evil DNS servers (timewarner) that have a
        # catchall address. We've had several users complain about
        # this one. Had to be at home to see it.
        #
        # If the resolved address is the same as the hostname then
        # this function was called with an ip address, so we don't
        # need the reverse lookup.
        #
        # For truly evil DNS (OpenDNS) that have catchall servers
        # that are in DNS we make sure the hostname matches the
        # primary or alias of the forward lookup Throw an Except, if
        # the forward failed an exception was already thrown.

        addr = socket.gethostbyname(hostname)
        if not addr == hostname:
            (name, aliases, addrs) = socket.gethostbyaddr(addr)
            if hostname != name and hostname not in aliases:
                raise NameError

    except:
        if hostname == 'localhost':
            addr = '127.0.0.1'
        else:
            addr = None

    if not addr:
        if db.db_rows:
            if _lookup_hostname(hostname):
                return getNodeName(hostname, subnet)

            # See if this is a MAC address
            try:
                hostname, = db.run_sql_rows("""
                    select nodes.name from networks,nodes
                    where nodes.id=networks.node and networks.mac=%s
                """, (hostname,), fetchone=True)
                return getNodeName(hostname, subnet)
            except:
                pass

            # See if this is a FQDN. If it is FQDN,
            # break it into name and domain.
            n = hostname.split('.')
            if len(n) > 1:
                name = n[0]
                domain = '.'.join(n[1:])

                try:
                    hostname, = db.run_sql_rows("""
                        select n.name from nodes n, networks nt, subnets s
                        where nt.subnet=s.id and nt.node=n.id
                        and s.zone=%s and (nt.name=%s or n.name=%s)
                    """, (domain, name, name), fetchone=True)
                    return getNodeName(hostname, subnet)
                except:
                    pass

            # Check if the hostname is a basename and the FQDN is
            # in /etc/hosts but not actually registered with DNS.
            # To do this we need lookup the DNS search domains and
            # then do a lookup in each domain. The DNS lookup will
            # fail (already has) but we might find an entry in the
            # /etc/hosts file.
            #
            # All this to handle the case when the user lies and gives
            # a FQDN that does not really exist. Still a common case.

            try:
                with open('/etc/resolv.conf', 'r') as f:
                    domains = []
                    for line in f.readlines():
                        tokens = line[:-1].split()
                        if len(tokens) == 0:
                            continue

                        if tokens[0] == 'search':
                            domains = tokens[1:]

                for domain in domains:
                    try:
                        name = '%s.%s' % (hostname, domain)
                        addr = socket.gethostbyname(name)
                        if addr:
                            return getHostname(name)
                    except:
                        pass
            except (OSError, IOError):
                pass

            # HostArgumentProcessor has changed handling of
            # appliances (and others) as hostnames. So do some work
            # here to point the user to the new syntax.
            message = None
            if db.run_sql_rows('SELECT count(id) from appliances where name=%s', (hostname,)):
                message = f'use "a:{hostname}" for {hostname} appliances'
            elif db.run_sql_rows('SELECT count(id) from environments where name=%s', (hostname,)):
                message = f'use "e:{hostname}" for hosts in the {hostname} environment'
            elif db.run_sql_rows('SELECT count(id) from oses where name=%s', (hostname,)):
                message = f'use "o:{hostname}" for {hostname} hosts'
            elif db.run_sql_rows('SELECT count(id) from boxes where name=%s', (hostname,)):
                message = f'use "b:{hostname}" for hosts using the {hostname} box'
            elif db.run_sql_rows('SELECT count(id) from groups where name=%s', (hostname,)):
                message = f'use "g:{hostname}" for host in the {hostname} group'
            elif hostname.find('rack') == 0:
                message = f'use "r:{hostname}" for hosts in {hostname}'

            if message:
                raise ValueError(message)
            raise ValueError(f'cannot resolve host "{hostname}"')

    if addr == '127.0.0.1': # allow localhost to be valid
        if db.db_rows:
            return getHostname(subnet=subnet)
        else:
            return 'localhost'

    if db.db_rows:
        # Look up the IP address in the networks table to find the
        # hostname (nodes table) of the node.
        #
        # If the IP address is not found also see if the hostname is
        # in the networks table. This last check handles the case
        # where DNS is correct but the IP address used is different.

        rows = db.run_sql_rows("""
            select nodes.name from networks,nodes
            where nodes.id=networks.node and ip=%s
        """, (addr,))

        if not rows:
            rows = db.run_sql_rows("""
                select nodes.name from networks,nodes
                where nodes.id=networks.node and networks.name=%s
            """, (hostname,))

            if not rows:
                raise ValueError(f'host "{hostname}" is not in cluster')

        hostname, = db.db_rows.fetchone()

    return getNodeName(hostname, subnet)

def sortHosts(hosts):
    def racksort(a):
        try:
            retval = int(a['rack'])
        except:
            retval = a['rack']
        return retval

    def ranksort(a):
        try:
            retval = int(a['rank'])
        except:
            retval = a['rank']
        return retval

    rank = sorted((h for h in hosts if h['rank'].isnumeric()), key=ranksort)
    rank += sorted((h for h in hosts if not h['rank'].isnumeric()), key=ranksort)

    rack = sorted((h for h in rank if h['rack'].isnumeric()), key=racksort)
    rack += sorted((h for h in rank if not h['rack'].isnumeric()), key=racksort)

    hosts = []
    for r in rack:
        hosts.append((r['host'],))

    return hosts

def getHostnames(names=[], managed_only=False, subnet=None, host_filter=None, order='asc'):
    """
    Expands the given list of names to valid cluster hostnames.	A name can be:

    - hostname
    - IP address
    - MAC address
    - where COND (e.g. 'where appliance=="backend"')

    Any combination of these is valid.  If the names list
    is empty a list of all hosts in the cluster is
    returned.

    The 'managed_only' flag means that the list of hosts will
    *not* contain hosts that traditionally don't have ssh login
    shells (for example, the following appliances usually don't
    have ssh login access: 'Ethernet Switches', 'Power Units',
    'Remote Management')

    The 'host_filter' flag is a callable (function, lambda, etc)
    that will be passed along with the final host list to filter().
    Equivalent code would look something like this:
    [host for host in final_host_list if host_filter(host)]

    Because filter() requires the callable to have only one arg,
    to allow access to 'self' as well as the host, host_filter()
    and 'self' are frozen with 'functools.partial', even if 'self'
    isn't required.	 The second arg will be each host name in the list.
    For example:
    host_filter = lambda self, host: self.db.getHostOS(host) == 'redhat'
    """

    adhoc	 = False
    hostList = []
    hostDict = {}

    # List the frontend first
    frontends = db.run_sql_rows("""
        SELECT n.name from nodes n, appliances a
        where a.name='frontend' and a.id=n.appliance order by rack, rank %s
    """ % order)

    # Performance improvement for `list host profile`
    if (
        names==["a:frontend"]
        and managed_only == False
        and subnet == None
        and host_filter == None
    ):
        return flatten(frontends)

    # Now get the backend appliances
    rows = db.run_sql_rows("""
        SELECT n.name, n.rack, n.rank from nodes n, appliances a
        where a.name != "frontend" and a.id=n.appliance
    """)

    hosts = []
    if frontends:
        hosts.extend(frontends)

    sortem = []
    for host, rack, rank in rows:
        sortem.append({ 'host' : host, 'rack' : rack, 'rank' : rank })

    backends = sortHosts(sortem)

    if backends:
        hosts.extend(backends)

    for host, in hosts:
        # If we have a list of hostnames (or groups) then
        # disable all the hosts first and selectively
        # turn them on later.
        # Otherwise just enable all the hosts.
        #
        # The hostList is used to preserve the SQL sort order
        # in the output, and the hostDict use use to map
        # the hosts on/off in the returned host list
        #
        # If the subnet names a network the hostname
        # stored in the hostDict will be the name of that
        # interface rather than the name in the nodes table

        hostList.append(host)

        if names:
            hostDict[host] = None
        else:
            hostDict[host] = getNodeName(host, subnet)

    l = []
    if names:
        for host in names:
            tokens = host.split(':', 1)
            if len(tokens) == 2:
                scope, target = tokens
                if scope == 'a':
                    l.append('where appliance == "%s"' % target)
                elif scope == 'e':
                    l.append('where environment == "%s"' % target)
                elif scope == 'o':
                    l.append('where os == "%s"' % target)
                elif scope == 'b':
                    l.append('where box == "%s"' % target)
                elif scope == 'g':
                    l.append('where group.%s == True' % target)
                elif scope == 'r':
                    l.append('where rack == "%s"' % target)
                adhoc = True
                continue

            if host.find('where') == 0:
                l.append(host)
                adhoc = True
                continue

            l.append(host.lower())
    names = l

    # If we have any Ad-Hoc groupings we need to load the attributes
    # for every host in the nodes tables.  Since this is a lot of
    # work handle the common case and avoid the work when just
    # a list of hosts.
    #
    # Also load the attributes if the managed_only argument is true
    # since we need to looked the managed attribute.

    hostAttrs  = {}
    for host in hostList:
        hostAttrs[host] = {}
    # if adhoc or managed_only:
    #     for row in self.call('list.host.attr', hostList):
    #         h = row['host']
    #         a = row['attr']
    #         v = row['value']
    #         hostAttrs[h][a] = v

    # Finally iterate over all the host/groups
    list	 = []
    explicit = {}
    for name in names:
        # Ad-hoc group
        if name.find('where') == 0:
            for host in hostList:
                exp = name[5:]
                res = EvalCondExpr(exp, hostAttrs[host])
                if res:
                    s = getHostname(host, subnet)
                    hostDict[host] = s
                    if host not in explicit:
                        explicit[host] = False
                # Debug('group %s is %s for %s' %
                # 	(exp, res, host))

        # Glob regex hostname
        #
        # Do extra work to make globbing case insensitve for
        # people that use uppercase hostname (don't be that
        # guy).
        elif '*' in name or '?' in name or '[' in name:
            for lower in fnmatch.filter([h.lower() for h in hostList], name):
                host = getHostname(lower) # fix case
                hostDict[host] = getHostname(host, subnet)
                if host not in explicit:
                    explicit[host] = False

        # Simple hostname
        else:
            host = getHostname(name)
            explicit[host] = True
            hostDict[host] = getHostname(name, subnet)

    # Preserving the SQL ordering build the list of hostname
    # selected.
    #
    # For each sorted host in the hostList include host if
    # the is an entry in the hostDict (interface name).
    #
    # If called with managed_only==True, filter out all
    # unmanaged hosts unless they explicitly appear in
    # the names list.  This effectively enforces the
    # filtering only on groups.
    list = []
    for host in hostList:
        if not hostDict[host]:
            continue

        if managed_only:
            managed = str2bool(hostAttrs[host]['managed'])
            if not managed and not explicit.get(host):
                continue

        list.append(hostDict[host])

    # # finally, apply the host_filter function, if it was passed
    # # explicitly check host_filter, because filter(None, iterable) has a semantic meaning
    # if host_filter:
    #     # filter(func, iterable) requires that func take a single argument
    #     # so we use functools.partial to get a function with one argument 'locked'
    #     part_func = partial(host_filter, self)
    #     list = filter(part_func, list)

    return list

def getScopeMappings(args=None, scope=None):
    # We will return a list of these
    ScopeMapping = namedtuple(
        'ScopeMapping',
        ['scope', 'appliance_id', 'os_id', 'environment_id', 'node_id']
    )
    scope_mappings = []

    # Validate the different scopes and get the keys to the targets
    if scope == 'global':
        # Global scope has no friends
        if args:
            raise ValueError("Arguments are not allowed at the global scope.")

        scope_mappings.append(
            ScopeMapping(scope, None, None, None, None)
        )

    elif scope == 'appliance':
        # Piggy-back to resolve the appliance names
        names = getApplianceNames(args)

        # Now we have to convert the names to the primary keys
        for appliance_id in flatten(db.run_sql_rows(
            'SELECT id from appliances where name in %s', (names,)
        )):
            scope_mappings.append(
                ScopeMapping(scope, appliance_id, None, None, None)
            )

    elif scope == 'os':
        # Piggy-back to resolve the os names
        names = getOSNames(args)

        # Now we have to convert the names to the primary keys
        for os_id in flatten(db.run_sql_rows(
            'id from oses where name in %s', (names,)
        )):
            scope_mappings.append(
                ScopeMapping(scope, None, os_id, None, None)
            )

    elif scope == 'environment':
        # Piggy-back to resolve the environment names
        names = getEnvironmentNames(args)

        if names:

            # Now we have to convert the names to the primary keys
            for environment_id in flatten(db.run_sql_rows(
                'id from environments where name in %s', (names,)
            )):
                scope_mappings.append(
                    ScopeMapping(scope, None, None, environment_id, None)
                )

    elif scope == 'host':
        # Piggy-back to resolve the host names
        names = getHostnames(args)
        if not names:
            raise ValueError('host argument required')

        # Now we have to convert the names to the primary keys
        for node_id in flatten(db.run_sql_rows(
            'SELECT id from nodes where name in %s', (names,)
        )):
            scope_mappings.append(
                ScopeMapping(scope, None, None, None, node_id)
            )

    else:
        raise ValueError('scope is not valid')

    return scope_mappings

@lru_cache(maxsize=None)
def _fnmatchcase(name, pattern):
    return fnmatch.fnmatchcase(name, pattern)

def _construct_host_query(node_ids, table, attr_type, attr, is_glob):
    joins = (
        "INNER JOIN scope_map ON scope_map.node_id = nodes.id",
        "INNER JOIN scope_map ON scope_map.environment_id = nodes.environment",
        """
        INNER JOIN boxes ON nodes.box = boxes.id
        INNER JOIN scope_map ON scope_map.os_id = boxes.os
        """,
        "INNER JOIN scope_map ON scope_map.appliance_id = nodes.appliance",
    )
    parts = []
    values = []
    for join in joins:
        part = f"""
        (
            SELECT nodes.name, scope_map.scope, '{attr_type}', attributes.name, attributes.value
            FROM nodes
            {join}
            INNER JOIN {table} ON attributes.scope_map_id = scope_map.id
            WHERE nodes.id IN %s
        """
        values.append(node_ids)
        # If we aren't a glob, we can let the DB filter by case-insensitive name
        if attr and not is_glob:
            part += "AND attributes.name = %s "
            values.append(attr)
        part += ")"
        parts.append(part)
    query = " UNION ".join(parts)
    return query, values

def fillParams(names, params):
    """
    Returns a list of variables with either default values of the
    values in the PARAMS dictionary.

    NAMES - list of (KEY, DEFAULT) tuples.
        KEY - key name of PARAMS dictionary
        DEFAULT - default value if key in not in dict
    PARAMS - optional dictionary
    REQUIRED - optional boolean (True means param is required)

    For example:

    (svc, comp) = self.fillParams(
        ('service', None),
        ('component', None))

    Can also be written as:

    (svc, comp) = self.fillParams(('service',), ('component', ))
    """

    # make sure names is a list or tuple
    if not type(names) in [type([]), type(())]:
        names = [names]

    # for each element in the names list make sure it is also
    # a tuple.  If the second element (default value) is missing
    # use None.  If the third element is missing assume the
    # parameter is not required.

    pdlist = []
    for e in names:
        if type(e) in [type([]), type(())]:
            if len(e) == 3:
                tuple = ( e[0], e[1], e[2] )
            elif len(e) == 2:
                tuple = ( e[0], e[1], False )
            elif len(e) == 1:
                tuple = ( e[0], None, False )
            else:
                assert len(e) in [1, 2, 3]
        else:
            tuple = ( e[0], None, False )
        pdlist.append(tuple)

    list = []
    for (key, default, required) in pdlist:
        if key in params:
            list.append(params[key])
        else:
            if required:
                raise ValueError(f"{key} is required")
            list.append(default)

    return list

def get_global_intrinsic(scope_mappings):
    # Figure out the output targets
    node_ids = []
    targets = []
    for scope_mapping in scope_mappings:
        # We only need to run for host or global scope
        if scope_mapping.scope == 'host':
            node_ids.append(scope_mapping.node_id)
        elif scope_mapping.scope == 'global':
            targets.append('')
        else:
            continue

    if node_ids:
        targets.extend(flatten(db.run_sql_rows(
            'SELECT nodes.name FROM nodes WHERE nodes.id IN %s',
            (node_ids,)
        )))

    # Get various kickstart networking data
    output_rows = []
    if targets:
        for ip, hostname, zone, address, netmask, network_name in db.run_sql_rows("""
            SELECT networks.ip, IF(networks.name IS NOT NULL, networks.name, nodes.name),
            subnets.zone, subnets.address, subnets.mask, subnets.name
            FROM networks
            INNER JOIN subnets ON subnets.id = networks.subnet
            INNER JOIN nodes ON nodes.id = networks.node
            INNER JOIN appliances ON appliances.id = nodes.appliance
            WHERE appliances.name = 'frontend'
            AND (subnets.name = 'public' OR subnets.name = 'private')
        """):
            network = IPv4Network(f"{address}/{netmask}")

            if network_name == 'private':
                for target in targets:
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateKickstartHost', ip])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateAddress', ip])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateHostname', hostname])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateBroadcast', str(network.broadcast_address)])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateDNSDomain', zone])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateNetwork', address])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateNetmask', netmask])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PrivateNetmaskCIDR', str(network.prefixlen)])
            elif network_name == 'public':
                for target in targets:
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicAddress', ip])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicHostname', f'{hostname}.{zone}'])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicBroadcast', str(network.broadcast_address)])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicDNSDomain', zone])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicNetwork', address])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicNetmask', netmask])
                    output_rows.append([target, 'global', 'const', 'Kickstart_PublicNetmaskCIDR', str(network.prefixlen)])

        # Add in the Stacki version info
        for target in targets:
            output_rows.append([target, 'global', 'const', 'release', "graphql"])
            output_rows.append([target, 'global', 'const', 'version', "graphql"])

    return output_rows

def get_host_intrinsic(scope_mappings):
    # Figure out the output targets
    node_ids = []
    for scope_mapping in scope_mappings:
        # We only need to run for host scope
        if scope_mapping.scope == 'host':
            node_ids.append(scope_mapping.node_id)
        else:
            continue

    output_rows = []
    box_map = defaultdict(list)
    hostname_map = {}

    # Get the data for the hosts
    if node_ids:
        for node_id, hostname, appliance, box_id, box, os, environment, rack, rank, metadata in db.run_sql_rows("""
            SELECT nodes.id, nodes.name, appliances.name, boxes.id, boxes.name, oses.name,
            environments.name, nodes.rack, nodes.rank, nodes.metadata
            FROM nodes
            INNER JOIN appliances ON appliances.id = nodes.appliance
            INNER JOIN boxes ON boxes.id = nodes.box
            INNER JOIN oses ON oses.id = boxes.os
            LEFT JOIN environments ON environments.id = nodes.environment
            WHERE nodes.id IN %s
        """, (node_ids,)):
            output_rows.append([hostname, 'host', 'const', 'hostname', hostname])
            output_rows.append([hostname, 'host', 'const', 'appliance', appliance])
            output_rows.append([hostname, 'host', 'const', 'box', box])
            output_rows.append([hostname, 'host', 'const', 'os', os])

            if environment:
                output_rows.append([hostname, 'host', 'const', 'environment', environment])

            output_rows.append([hostname, 'host', 'const', 'rack', rack])
            output_rows.append([hostname, 'host', 'const', 'rank', rank])

            if metadata:
                output_rows.append([hostname, 'host', 'const', 'metadata', metadata])

            # Add the host to the box map
            box_map[box_id].append(hostname)

            # And to the hostname map
            hostname_map[node_id] = hostname

        # Now figure out the pallets and carts for every box seen
        for box_id in box_map:
            # First the pallets
            pallets = []
            os_version = None
            for name, version, rel in db.run_sql_rows("""
                SELECT rolls.name, rolls.version, rolls.rel
                FROM rolls
                INNER JOIN stacks ON stacks.roll = rolls.id
                WHERE stacks.box = %s
            """, (box_id,)):
                pallets.append(f"{name}-{version}-{rel}")
                if name in ['SLES', 'CentOS']:
                    os_version = '%s.x' % version.split('.')[0]

            for hostname in box_map[box_id]:
                output_rows.append([hostname, 'host', 'const', 'pallets', pallets])
                output_rows.append([hostname, 'host', 'const', 'os.version', os_version])

            # Then the carts
            carts = flatten(db.run_sql_rows("""
                SELECT carts.name
                FROM carts
                INNER JOIN cart_stacks ON cart_stacks.cart = carts.id
                WHERE cart_stacks.box = %s
            """, (box_id,)))

            for hostname in box_map[box_id]:
                output_rows.append([hostname, 'host', 'const', 'carts', carts])

        # Get some network info for the hosts
        for node_id, zone, address in db.run_sql_rows("""
            SELECT networks.node, subnets.zone, networks.ip
            FROM networks
            INNER JOIN subnets ON networks.subnet=subnets.id
            WHERE networks.main = true
            AND networks.node IN %s
        """, (node_ids,)):
            output_rows.append([hostname_map[node_id], 'host', 'const', 'domainname', zone])

            if address:
                output_rows.append([hostname_map[node_id], 'host', 'const', 'hostaddr', address])

        # And finally any groups the hosts are in
        groups = defaultdict(list)
        for node_id, group in db.run_sql_rows("""
            SELECT memberships.nodeid, groups.name
            FROM groups
            INNER JOIN memberships ON memberships.groupid=groups.id
            WHERE memberships.nodeid IN %s
            ORDER BY groups.name
        """, (node_ids,)):
            groups[node_id].append(group)
            output_rows.append([hostname_map[node_id], 'host', 'const', f'group.{group}', 'true'])

        for node_id in node_ids:
            output_rows.append([hostname_map[node_id], 'host', 'const', 'groups', ' '.join(groups[node_id])])

    return output_rows

def run(params, args):
    # Get the scope and make sure the args are valid
    scope, = fillParams([('scope', 'global')], params=params)
    scope_mappings = getScopeMappings(args, scope)
    # Now validate the params
    attr, shadow, resolve, var, const, display = fillParams([
        ('attr',   None),
        ('shadow', True),
        ('resolve', True),
        ('var', True),
        ('const', True),
        ('display', 'all'),
    ], params=params)
    # If there isn't any environments, scope_mappings could be
    # an empty list, in which case we are done
    if not scope_mappings:
        return
    # Make sure bool params are bools
    resolve = str2bool(resolve)
    shadow = str2bool(shadow)
    var = str2bool(var)
    const = str2bool(const)
    is_glob = attr is not None and re.match('^[a-zA-Z_][a-zA-Z0-9_.]*$', attr) is None
    # Connect to a copy of the database if we are running pytest-xdist
    if 'PYTEST_XDIST_WORKER' in os.environ:
        db_name = 'shadow' + os.environ['PYTEST_XDIST_WORKER']
    else:
        db_name = 'shadow'  # pragma: no cover
    output = defaultdict(dict)
    if var:
        if resolve and scope == 'host':
            node_ids = [s.node_id for s in scope_mappings]
            hostnames = flatten(db.run_sql_rows(
                "SELECT nodes.name FROM nodes WHERE nodes.id IN %s",
                [node_ids]
            ))
            # Get all the normal attributes for the host's scopes
            query, values = _construct_host_query(
                node_ids, 'attributes', 'var', attr, is_glob
            )
            # The attributes come out of the DB with the higher weighted
            # scopes first. Surprisingly, there is no simple way in SQL
            # to squash these rules down by scope weight. So, we do it
            # here instead. Also, filter by attr name, if provided.
            seen = defaultdict(set)
            for host, *row in db.run_sql_rows(query, values):
                if row[2] not in seen[host]:
                    if attr is None or _fnmatchcase(row[2], attr):
                        output[host][row[2]] = row
                    seen[host].add(row[2])
            # Merge in any normal global attrs for each host
            query = """
                'global', 'var', attributes.name, attributes.value
                FROM attributes, scope_map
                WHERE attributes.scope_map_id = scope_map.id
                AND scope_map.scope = 'global'
            """
            values = []
            # If we aren't a glob, we can let the DB filter by case-insensitive name
            if attr and not is_glob:
                query += "AND attributes.name = %s"
                values.append(attr)
            for row in db.run_sql_rows(f"SELECT {query}", values):
                for host in hostnames:
                    if row[2] not in seen[host]:
                        if attr is None or _fnmatchcase(row[2], attr):
                            output[host][row[2]] = row
                        seen[host].add(row[2])
            # Now get the shadow attributes, if requested
            # if shadow:
            #     query, values = _construct_host_query(
            #         node_ids, f'{db_name}.attributes', 'shadow', attr, is_glob
            #     )
            #     # Merge in the shadow attributes for the host's scopes
            #     weights = {
            #         'global': 0,
            #         'appliance': 1,
            #         'os': 2,
            #         'environment': 3,
            #         'host': 4
            #     }
            #     for host, *row in db.run_sql_rows(query, values):
            #         if row[2] not in seen[host]:
            #             # If we haven't seen it
            #             if attr is None or _fnmatchcase(row[2], attr):
            #                 output[host][row[2]] = row
            #             seen[host].add(row[2])
            #         else:
            #             # Maybe the shadow attr is higher scope
            #             if weights[row[0]] >= weights[output[host][row[2]][0]]:
            #                 output[host][row[2]] = row
            #     # Merge in any shadow global attrs for each host
            #     query = f"""
            #         'global', 'shadow', attributes.name, attributes.value
            #         FROM {db_name}.attributes, scope_map
            #         WHERE attributes.scope_map_id = scope_map.id
            #         AND scope_map.scope = 'global'
            #     """
            #     values = []
            #     # If we aren't a glob, we can let the DB filter by case-insensitive name
            #     if attr and not is_glob:
            #         query += "AND attributes.name = %s"
            #         values.append(attr)
            #     for row in db.run_sql_rows(f"SELECT {query}", values):
            #         for host in hostnames:
            #             if row[2] not in seen[host]:
            #                 if attr is None or _fnmatchcase(row[2], attr):
            #                     output[host][row[2]] = row
            #                 seen[host].add(row[2])
            #             else:
            #                 if output[host][row[2]][0] == 'global':
            #                     output[host][row[2]] = row
        else:
            query_data = [('attributes', 'var')]
            # if shadow:
            #     query_data.append((f'{db_name}.attributes', 'shadow'))
            for table, attr_type in query_data:
                if scope == 'global':
                    query = f"""
                        '', 'global', '{attr_type}', attributes.name, attributes.value
                        FROM {table}
                        INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
                        WHERE scope_map.scope = 'global'
                    """
                else:
                    query = f"""
                        target.name, scope_map.scope, '{attr_type}', attributes.name, attributes.value
                        FROM {table}
                        INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
                    """
                values = []
                if scope == 'appliance':
                    query += """
                        INNER JOIN appliances AS target ON target.id = scope_map.appliance_id
                        WHERE scope_map.appliance_id IN %s
                    """
                    values.append([s.appliance_id for s in scope_mappings])
                elif scope == 'os':
                    query += """
                        INNER JOIN oses AS target ON target.id = scope_map.os_id
                        WHERE scope_map.os_id IN %s
                    """
                    values.append([s.os_id for s in scope_mappings])
                elif scope == 'environment':
                    query += """
                        INNER JOIN environments AS target ON target.id = scope_map.environment_id
                        WHERE scope_map.environment_id IN %s
                    """
                    values.append([s.environment_id for s in scope_mappings])
                elif scope == 'host':
                    query += """
                        INNER JOIN nodes AS target ON target.id = scope_map.node_id
                        WHERE scope_map.node_id IN %s
                    """
                    values.append([s.node_id for s in scope_mappings])
                # If we aren't a glob, we can let the DB filter by case-insensitive name
                if attr and not is_glob:
                    query += "AND attributes.name = %s"
                    values.append(attr)
                # Filter by attr name, if provided.
                for target, *row in db.run_sql_rows(f"SELECT {query}", values):
                    if attr is None or _fnmatchcase(row[2], attr):
                        output[target][row[2]] = row
    if const:
        # For any host targets, figure out if they have a "const_overwrite" attr
        node_ids = [s.node_id for s in scope_mappings if s.scope == 'host']
        const_overwrite = defaultdict(lambda: True)
        if node_ids:
            for target, value in db.run_sql_rows("""
                SELECT nodes.name, attributes.value
                FROM attributes
                INNER JOIN scope_map ON attributes.scope_map_id = scope_map.id
                INNER JOIN nodes ON scope_map.node_id = nodes.id
                WHERE attributes.name = BINARY 'const_overwrite'
                AND scope_map.scope = 'host'
                AND scope_map.node_id IN %s
            """, (node_ids,)):
                const_overwrite[target] = str2bool(value)
        # Now run the plugins and merge in the intrensic attrs
        results = [
            # *get_global_intrinsic(scope_mappings),
            # *get_host_intrinsic(scope_mappings),
        ]
        for result in results:
            for target, *row in result[1]:
                if attr is None or _fnmatchcase(row[2], attr):
                    if const_overwrite[target]:
                        output[target][row[2]] = row
                    else:
                        if row[2] not in output[target]:
                            output[target][row[2]] = row
    # # Handle the display parameter if we are host scoped
    # if scope == 'host' and display in {'common', 'distinct'}:
    #     # Construct a set of attr (name, value) for each target
    #     host_attrs = {}
    #     for target in output:
    #         host_attrs[target] = {
    #             (row[2], str(row[3])) for row in output[target].values()
    #         }
    #     common_attrs = set.intersection(*host_attrs.values())
    #     if display == 'common':
    #         for name, value in sorted(common_attrs):
    #             self.addOutput('_common_', [None, None, name, value])
    #     elif display == 'distinct':
    #         common_attr_names = set(v[0] for v in common_attrs)
    #         for target in sorted(output.keys()):
    #             for key in sorted(output[target].keys()):
    #                 if key not in common_attr_names:
    #                     self.addOutput(target, output[target][key])
    # else:
    # Output our combined attributes, sorting them by target then attr
    attribute_results = []
    for target in sorted(output.keys()):
        for key in sorted(output[target].keys()):
            headers = ('scope', 'type', 'attr', 'value')
            attribute_results.append(
                {
                    headers[index]: value
                    for index, value in enumerate(output[target][key])
                }
            )

    return attribute_results
    # if scope == 'global':
    #     header = ''
    # else:
    #     header = scope
    # self.endOutput(header=[
    #     header, 'scope', 'type', 'attr', 'value'
    # ])

@host.field("attributes")
def resolve_attributes_from_host(host, info):
    hostname = host.get("name")
    if not hostname:
        return None

    params = {"scope": "host"}
    args = [hostname]
    return run(params, args)

@environment.field("attributes")
def resolve_attributes_from_environment(environment, info):
    environment_name = environment.get("name")
    if not environment_name:
        return None

    params = {"scope": "environment"}
    args = [environment_name]
    return run(params, args)

@os_graphql.field("attributes")
def resolve_attributes_from_os(os_graphql, info):
    os_name = os_graphql.get("os")
    if not os_name:
        return None

    params = {"scope": "os"}
    args = [os_name]
    return run(params, args)

@appliance.field("attributes")
def resolve_attributes_from_appliance(appliance, info):
    appliance_name = appliance.get("name")
    if not appliance_name:
        return None

    params = {"scope": "appliance"}
    args = [appliance_name]
    return run(params, args)
