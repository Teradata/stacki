# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
from peewee import *
import pymysql



def get_database_pw():
	try:
		file = open("/etc/apache.my.cnf", "r")
		for line in file.readlines():
			if line.startswith("password"):
				passwd = line.split("=")[1].strip()
				return passwd
		file.close()
	except:
		return ""

def connect_db(username="apache", passwd=""):
	passwd = get_database_pw()

	# Connect to a copy of the database if we are running pytest-xdist
	if "PYTEST_XDIST_WORKER" in os.environ:
		db_name = "cluster" + os.environ["PYTEST_XDIST_WORKER"]
	else:
		db_name = "cluster"

	if os.path.exists("/run/mysql/mysql.sock"):
		db = pymysql.connect(
			db=db_name,
			user=username,
			passwd=passwd,
			host="localhost",
			unix_socket="/run/mysql/mysql.sock",
			autocommit=True,
		)
	else:
		db = pymysql.connect(
			db=db_name,
			host="localhost",
			port=40000,
			user=username,
			passwd=passwd,
			autocommit=True,
		)
	return db.cursor(pymysql.cursors.DictCursor)

db = connect_db()
database = MySQLDatabase('cluster', user='apache', password=get_database_pw(), host='localhost')


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class Access(BaseModel):
    command = CharField(column_name="Command")
    group_id = IntegerField(column_name="GroupID")

    class Meta:
        table_name = "access"
        primary_key = False


class Aliases(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", index=True)
    network = IntegerField(column_name="Network")

    class Meta:
        table_name = "aliases"


class Appliances(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", constraints=[SQL("DEFAULT ''")], index=True)
    public = CharField(column_name="Public", constraints=[SQL("DEFAULT 'no'")])

    class Meta:
        table_name = "appliances"


class Attributes(BaseModel):
    attr = CharField(column_name="Attr", index=True)
    scope = CharField(column_name="Scope", index=True, null=True)
    scope_id = IntegerField(column_name="ScopeID", index=True, null=True)
    shadow = TextField(column_name="Shadow", null=True)
    value = TextField(column_name="Value", null=True)

    class Meta:
        table_name = "attributes"
        primary_key = False


class AttributesDoc(BaseModel):
    attr = CharField(column_name="Attr", index=True)
    doc = TextField(column_name="Doc", null=True)

    class Meta:
        table_name = "attributes_doc"
        primary_key = False


class Boot(BaseModel):
    action = CharField(column_name="Action", null=True)
    node = IntegerField(column_name="Node", constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = "boot"
        primary_key = False


class Bootactions(BaseModel):
    args = CharField(column_name="Args", null=True)
    boot_name = IntegerField(column_name="BootName")
    id = AutoField(column_name="ID")
    kernel = CharField(column_name="Kernel", null=True)
    os = IntegerField(column_name="OS", null=True)
    ramdisk = CharField(column_name="Ramdisk", null=True)

    class Meta:
        table_name = "bootactions"
        indexes = ((("boot_name", "os"), True),)


class Bootnames(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", index=True)
    type = CharField(column_name="Type")

    class Meta:
        table_name = "bootnames"


class Boxes(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(
        column_name="Name", constraints=[SQL("DEFAULT 'default'")], index=True
    )
    os = IntegerField(column_name="OS")

    class Meta:
        table_name = "boxes"


class CartStacks(BaseModel):
    box = IntegerField(column_name="Box", constraints=[SQL("DEFAULT 1")])
    cart = IntegerField(column_name="Cart")

    class Meta:
        table_name = "cart_stacks"
        primary_key = False


class Carts(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", constraints=[SQL("DEFAULT ''")], index=True)
    url = TextField(column_name="URL", null=True)

    class Meta:
        table_name = "carts"


class Environments(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name = "environments"


class Oses(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name = "oses"


class Nodes(BaseModel):
    appliance = ForeignKeyField(
        column_name="Appliance",
        field="id",
        model=Appliances,
        null=True,
        backref="appliances",
    )
    box = IntegerField(column_name="Box", null=True)
    comment = CharField(column_name="Comment", null=True)
    environment = IntegerField(column_name="Environment", null=True)
    id = AutoField(column_name="ID")
    install_action = IntegerField(column_name="InstallAction", null=True)
    meta_data = TextField(column_name="MetaData", null=True)
    name = CharField(column_name="Name", index=True, null=True)
    os_action = IntegerField(column_name="OSAction", null=True)
    rack = CharField(column_name="Rack", null=True)
    rank = CharField(column_name="Rank", null=True)

    class Meta:
        table_name = "nodes"


class ScopeMap(BaseModel):
    appliance = ForeignKeyField(
        column_name="appliance_id", field="id", model=Appliances, null=True
    )
    environment = ForeignKeyField(
        column_name="environment_id", field="id", model=Environments, null=True
    )
    node = ForeignKeyField(column_name="node_id", field="id", model=Nodes, null=True)
    os = ForeignKeyField(column_name="os_id", field="id", model=Oses, null=True)
    scope = CharField(index=True)

    class Meta:
        table_name = "scope_map"


class Subnets(BaseModel):
    id = AutoField(column_name="ID")
    address = CharField()
    dns = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    gateway = CharField(null=True)
    mask = CharField()
    mtu = IntegerField(constraints=[SQL("DEFAULT 1500")], null=True)
    name = CharField(index=True)
    pxe = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    zone = CharField()

    class Meta:
        table_name = "subnets"


class FirewallRules(BaseModel):
    action = CharField()
    chain = CharField()
    comment = CharField(null=True)
    flags = CharField(null=True)
    in_subnet = ForeignKeyField(
        column_name="in_subnet_id", field="id", model=Subnets, null=True
    )
    name = CharField(index=True)
    out_subnet = ForeignKeyField(
        backref="subnets_out_subnet_set",
        column_name="out_subnet_id",
        field="id",
        model=Subnets,
        null=True,
    )
    protocol = CharField()
    scope_map = ForeignKeyField(column_name="scope_map_id", field="id", model=ScopeMap)
    service = CharField()
    table_type = CharField(index=True)

    class Meta:
        table_name = "firewall_rules"


class FirmwareVersionRegex(BaseModel):
    description = CharField()
    name = CharField(index=True)
    regex = CharField()

    class Meta:
        table_name = "firmware_version_regex"


class FirmwareMake(BaseModel):
    name = CharField(index=True)
    version_regex = ForeignKeyField(
        column_name="version_regex_id",
        field="id",
        model=FirmwareVersionRegex,
        null=True,
    )

    class Meta:
        table_name = "firmware_make"


class FirmwareImp(BaseModel):
    name = CharField(index=True)

    class Meta:
        table_name = "firmware_imp"


class FirmwareModel(BaseModel):
    imp = ForeignKeyField(column_name="imp_id", field="id", model=FirmwareImp)
    make = ForeignKeyField(column_name="make_id", field="id", model=FirmwareMake)
    name = CharField(index=True)
    version_regex = ForeignKeyField(
        column_name="version_regex_id",
        field="id",
        model=FirmwareVersionRegex,
        null=True,
    )

    class Meta:
        table_name = "firmware_model"
        indexes = ((("make", "name"), True),)


class Firmware(BaseModel):
    file = CharField()
    hash = CharField()
    hash_alg = CharField(constraints=[SQL("DEFAULT 'md5'")])
    model = ForeignKeyField(column_name="model_id", field="id", model=FirmwareModel)
    source = CharField()
    version = CharField(index=True)

    class Meta:
        table_name = "firmware"
        indexes = ((("model", "version"), True),)


class FirmwareMapping(BaseModel):
    firmware = ForeignKeyField(column_name="firmware_id", field="id", model=Firmware)
    node = ForeignKeyField(column_name="node_id", field="id", model=Nodes)

    class Meta:
        table_name = "firmware_mapping"
        indexes = ((("node", "firmware"), True),)


class Groups(BaseModel):
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name = "groups"


class Networks(BaseModel):
    channel = CharField(column_name="Channel", null=True)
    device = CharField(column_name="Device", index=True, null=True)
    gateway = CharField(column_name="Gateway", null=True)
    id = AutoField(column_name="ID")
    ip = CharField(column_name="IP", null=True)
    mac = CharField(column_name="MAC", index=True, null=True)
    main = IntegerField(column_name="Main", constraints=[SQL("DEFAULT 0")], null=True)
    module = CharField(column_name="Module", null=True)
    name = CharField(column_name="Name", index=True, null=True)
    netmask = CharField(column_name="Netmask", null=True)
    node = IntegerField(column_name="Node", null=True)
    options = CharField(column_name="Options", null=True)
    subnet = ForeignKeyField(column_name="Subnet", field="id", model=Subnets, null=True)
    vlan_id = IntegerField(column_name="VlanID", null=True)

    class Meta:
        table_name = "networks"


class IbPartitions(BaseModel):
    options = CharField(constraints=[SQL("DEFAULT ''")])
    part_key = IntegerField()
    part_name = CharField(index=True)
    switch = ForeignKeyField(column_name="switch", field="id", model=Nodes)

    class Meta:
        table_name = "ib_partitions"


class IbMemberships(BaseModel):
    interface = ForeignKeyField(column_name="interface", field="id", model=Networks)
    member_type = CharField(constraints=[SQL("DEFAULT 'limited'")])
    part_name = ForeignKeyField(column_name="part_name", field="id", model=IbPartitions)
    switch = ForeignKeyField(column_name="switch", field="id", model=Nodes)

    class Meta:
        table_name = "ib_memberships"
        indexes = ((("switch", "part_name", "interface"), False),)


class Memberships(BaseModel):
    group_id = IntegerField(column_name="GroupID")
    node_id = IntegerField(column_name="NodeID")

    class Meta:
        table_name = "memberships"
        primary_key = False


class Partitions(BaseModel):
    device = CharField(column_name="Device", constraints=[SQL("DEFAULT ''")])
    format_flags = CharField(column_name="FormatFlags", constraints=[SQL("DEFAULT ''")])
    fs_type = CharField(column_name="FsType", constraints=[SQL("DEFAULT ''")])
    id = AutoField(column_name="ID")
    mountpoint = CharField(column_name="Mountpoint", constraints=[SQL("DEFAULT ''")])
    node = IntegerField(column_name="Node")
    partition_flags = CharField(
        column_name="PartitionFlags", constraints=[SQL("DEFAULT ''")]
    )
    partition_id = CharField(column_name="PartitionID", constraints=[SQL("DEFAULT ''")])
    partition_size = CharField(
        column_name="PartitionSize", constraints=[SQL("DEFAULT ''")]
    )
    sector_start = CharField(column_name="SectorStart", constraints=[SQL("DEFAULT ''")])
    uuid = CharField(column_name="UUID", constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name = "partitions"


class PublicKeys(BaseModel):
    id = AutoField(column_name="ID")
    node = IntegerField(column_name="Node")
    public_key = CharField(column_name="Public_Key", null=True)

    class Meta:
        table_name = "public_keys"


class Rolls(BaseModel):
    arch = CharField(column_name="Arch", constraints=[SQL("DEFAULT ''")])
    id = AutoField(column_name="ID")
    name = CharField(column_name="Name", constraints=[SQL("DEFAULT ''")], index=True)
    os = CharField(column_name="OS", constraints=[SQL("DEFAULT 'sles'")])
    rel = CharField(column_name="Rel", constraints=[SQL("DEFAULT ''")])
    url = TextField(column_name="URL", null=True)
    version = CharField(column_name="Version", constraints=[SQL("DEFAULT ''")])

    class Meta:
        table_name = "rolls"


class Routes(BaseModel):
    address = CharField(index=True)
    gateway = CharField(null=True)
    interface = CharField(index=True, null=True)
    netmask = CharField()
    scope_map = ForeignKeyField(column_name="scope_map_id", field="id", model=ScopeMap)
    subnet = ForeignKeyField(
        column_name="subnet_id", field="id", model=Subnets, null=True
    )

    class Meta:
        table_name = "routes"


class Stacks(BaseModel):
    box = IntegerField(column_name="Box", constraints=[SQL("DEFAULT 1")])
    roll = IntegerField(column_name="Roll")

    class Meta:
        table_name = "stacks"
        primary_key = False


class StorageController(BaseModel):
    adapter = IntegerField()
    arrayid = IntegerField()
    enclosure = IntegerField()
    options = CharField()
    raidlevel = CharField()
    scope_map = ForeignKeyField(column_name="scope_map_id", field="id", model=ScopeMap)
    slot = IntegerField()

    class Meta:
        table_name = "storage_controller"
        indexes = ((("enclosure", "adapter", "slot"), False),)


class StoragePartition(BaseModel):
    device = CharField(index=True)
    fstype = CharField(null=True)
    mountpoint = CharField(index=True, null=True)
    options = CharField()
    partid = IntegerField()
    scope_map = ForeignKeyField(column_name="scope_map_id", field="id", model=ScopeMap)
    size = IntegerField()

    class Meta:
        table_name = "storage_partition"
        indexes = ((("device", "mountpoint"), False),)


class Switchports(BaseModel):
    interface = IntegerField()
    port = IntegerField()
    switch = IntegerField()

    class Meta:
        table_name = "switchports"
        primary_key = False


class Tags(BaseModel):
    scope = CharField(column_name="Scope", index=True, null=True)
    scope_id = IntegerField(column_name="ScopeID", index=True, null=True)
    tag = CharField(column_name="Tag", index=True)
    value = TextField(column_name="Value", null=True)

    class Meta:
        table_name = "tags"
        primary_key = False

