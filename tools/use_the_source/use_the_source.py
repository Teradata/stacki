#!/opt/stack/bin/python3
import sys
from pathlib import Path

dest_base = Path("/opt/stack/lib/python3.7/site-packages")

grafts_to_site_packages = (
	("command/stack/argument_processors", "stack/argument_processors"),
	("command/stack/commands", "stack/commands"),
	("discovery/command", "stack/commands"),
	("discovery/pylib", "stack"),
	("mq/pylib", "stack"),
	("mq/processors", "stack/mq/processors"),
	("mq/producers", "stack/mq/producers"),
	("pylib/stack", "stack"),
	("report-system/command", "stack/commands"),
	("switch/command", "stack/commands"),
	("graph_ql/command", "stack/commands"),
	("switch/pylib", "stack"),
	("ws/command", "stack/commands"),
	("ws/pylib", "stack"),
	("graph_ql", "stack/graph_ql"),
	("graph_ql/pylib", "stack"),
	("db", "stack/db"),
	("db/pylib", "stack"),
	("ws-client/pylib", "")
)

bin_file_grafts = (
	("discovery/bin/discover-nodes.py", "/opt/stack/sbin/discover-nodes"),
	("mq/clients/publish.py", "/opt/stack/bin/smq-publish"),
	("mq/clients/channel-ctrl.py", "/opt/stack/bin/channel-ctrl"),
	("mq/daemons/producer.py", "/opt/stack/sbin/smq-producer"),
	("mq/daemons/publisher.py", "/opt/stack/sbin/smq-publisher"),
	("mq/daemons/shipper.py", "/opt/stack/sbin/smq-shipper"),
	("mq/daemons/processor.py", "/opt/stack/sbin/smq-processor"),
	("mq/daemons/producer.init", "/etc/init.d/smq-producer"),
	("mq/daemons/publisher.init", "/etc/init.d/smq-publisher"),
	("mq/daemons/shipper.init", "/etc/init.d/smq-shipper"),
	("mq/daemons/processor.init", "/etc/init.d/smq-processor"),
	("ws-client/bin/wsclient.py", "/opt/stack/bin/wsclient")
)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'{Path(__file__).name} <path_to_stacki_source_tree>')
		sys.exit(1)

	# get the absolute path, expanding shell stuff
	src_base = Path(sys.argv[1]).expanduser().resolve() / 'common/src/stack/'

	for src, dest in grafts_to_site_packages:
		src_directory = src_base / src
		dest_directory = dest_base / dest

		# Find all our Python files
		for src_filename in src_directory.glob("**/*.py"):
			dest_filename = dest_directory / src_filename.relative_to(src_directory)

			# First blow away the old one, if it exists
			if dest_filename.exists() or dest_filename.is_symlink():
				dest_filename.unlink()

			# Create any missing directory structure in the destination.
			dest_filename.parent.mkdir(parents = True, exist_ok = True)

			# Now symlink over our src version
			dest_filename.symlink_to(src_filename)

		# Find all our GrrapQL files
		for src_filename in src_directory.glob("**/*.graphql"):
			dest_filename = dest_directory / src_filename.relative_to(src_directory)

			# First blow away the old one, if it exists
			if dest_filename.exists() or dest_filename.is_symlink():
				dest_filename.unlink()

			# Create any missing directory structure in the destination.
			dest_filename.parent.mkdir(parents = True, exist_ok = True)

			# Now symlink over our src version
			dest_filename.symlink_to(src_filename)


	for src, dest in bin_file_grafts:
		src_filename = src_base / src
		dest_filename = Path(dest)

		# Blow away the old one, if it exists
		if dest_filename.exists() or dest_filename.is_symlink():
			dest_filename.unlink()

		# Create any missing directory structure in the destination.
		dest_filename.parent.mkdir(parents = True, exist_ok = True)

		# Now symlink over our src version
		dest_filename.symlink_to(src_filename)
