

DROP TABLE IF EXISTS access;
CREATE TABLE access (
  Command       varchar(128) NOT NULL,
  GroupID       int(11) NOT NULL
);



insert into access (command, groupid) values ("*", 0);



DROP TABLE IF EXISTS aliases;
CREATE TABLE aliases (
  ID		int(11) NOT NULL auto_increment,
  Name		varchar(32) NOT NULL,
  Network	int(11) NOT NULL references networks,
  PRIMARY KEY (ID),
  INDEX (Name)
);



DROP TABLE IF EXISTS tags;
CREATE TABLE tags (
	Scope		enum ('box', 'cart', 'network', 'pallet'),
	Tag		varchar(128) NOT NULL,
	Value		text,
	ScopeID		int(11),
	INDEX (Scope),
	INDEX (Tag),
	INDEX (ScopeID)
);



DROP TABLE IF EXISTS attributes_doc;
CREATE TABLE attributes_doc (
  Attr          varchar(128) NOT NULL,
  Doc           text,
  INDEX (Attr)
);



DROP TABLE IF EXISTS oses;
CREATE TABLE oses (
  ID		int(11) NOT NULL auto_increment,
  Name		varchar(32) NOT NULL default '',
  PRIMARY KEY (ID),
  INDEX (Name)
);

insert into oses (name) values ("redhat");
insert into oses (name) values ("ubuntu");
insert into oses (name) values ("sles");
insert into oses (name) values ("vmware");
insert into oses (name) values ("xenserver");



DROP TABLE IF EXISTS environments;
CREATE TABLE environments (
  ID		int(11) NOT NULL auto_increment,
  Name		varchar(32) NOT NULL default '',
  PRIMARY KEY (ID),
  INDEX (Name)
);



DROP TABLE IF EXISTS appliances;
CREATE TABLE appliances (
  ID		int(11) NOT NULL auto_increment,
  Name		varchar(32) NOT NULL default '',
  Public	enum('yes','no') NOT NULL default 'no',
  PRIMARY KEY (ID),
  INDEX (Name)
);



DROP TABLE IF EXISTS boxes;
CREATE TABLE boxes (
  ID		int(11) NOT NULL auto_increment,
  Name		varchar(32) NOT NULL default 'default',
  OS		int(11) NOT NULL references oses,
  PRIMARY KEY (ID),
  INDEX (Name)
);



DROP TABLE IF EXISTS boot;
CREATE TABLE boot (
  Node  	int(11) NOT NULL default '0' references nodes on delete cascade,
  Action	enum ('install', 'os')
);

DROP TABLE IF EXISTS bootnames;
CREATE TABLE bootnames (
	ID		int(11) NOT NULL auto_increment,
	Name		varchar(128) NOT NULL,
	Type		enum ('install', 'os') NOT NULL,
	PRIMARY KEY (ID),
	INDEX (Name)
);

DROP TABLE IF EXISTS bootactions;
CREATE TABLE bootactions (
	ID		int(11) NOT NULL auto_increment,
	BootName	int(11) NOT NULL references bootnames,
	OS		int(11) default NULL references oses,
	Kernel		varchar(256) default NULL,
	Ramdisk		varchar(256) default NULL,
	Args		varchar(1024) default NULL,
	PRIMARY KEY (ID)
);

CREATE UNIQUE INDEX BootnameOS ON bootactions(BootName,OS);


DROP TABLE IF EXISTS subnets;
CREATE TABLE subnets (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	name		VARCHAR(128) UNIQUE NOT NULL,
	zone		VARCHAR(255) NOT NULL,
	address		VARCHAR(32) NOT NULL,
	mask		VARCHAR(32) NOT NULL,
	gateway		VARCHAR(32),
	mtu		INT DEFAULT '1500',
	dns		BOOLEAN	DEFAULT FALSE,
	pxe		BOOLEAN	DEFAULT FALSE,
	INDEX (name)
);


DROP TABLE IF EXISTS nodes;
CREATE TABLE nodes (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	name		VARCHAR(128) NOT NULL,
	appliance	INT NOT NULL,
	box		INT NOT NULL,
	environment	INT DEFAULT NULL,
	rack		VARCHAR(64) NOT NULL,
	rank		VARCHAR(64) NOT NULL,
	osaction	INT DEFAULT NULL,
	installaction	INT DEFAULT NULL,
	comment		VARCHAR(140) DEFAULT NULL,
	metadata	TEXT DEFAULT NULL,
	INDEX (name),
	FOREIGN KEY (appliance) REFERENCES appliances(id) ON DELETE CASCADE,
	FOREIGN KEY (box) REFERENCES boxes(id) ON DELETE CASCADE,
	FOREIGN KEY (environment) REFERENCES environments(id) ON DELETE SET NULL,
	FOREIGN KEY (osaction) REFERENCES bootactions(id) ON DELETE SET NULL,
	FOREIGN KEY (installaction) REFERENCES bootactions(id) ON DELETE SET NULL
);


DROP TABLE IF EXISTS networks;
CREATE TABLE networks (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	node		INT NOT NULL,
	mac		VARCHAR(64) DEFAULT NULL,
	ip		VARCHAR(32) DEFAULT NULL,
	netmask		VARCHAR(32) DEFAULT NULL,
	gateway		VARCHAR(32) DEFAULT NULL,
	name		VARCHAR(128) DEFAULT NULL,
	device		VARCHAR(32) DEFAULT NULL,
	subnet		INT DEFAULT NULL,
	module		VARCHAR(128) DEFAULT NULL,
	vlanid		INT DEFAULT NULL,
	options		VARCHAR(128) DEFAULT NULL,
	channel		VARCHAR(128) DEFAULT NULL,
	main		BOOLEAN	DEFAULT FALSE,
	INDEX (name),
	INDEX (mac),
	INDEX (device),
	FOREIGN KEY (node) REFERENCES nodes(id) ON DELETE CASCADE,
	FOREIGN KEY (subnet) REFERENCES subnets(id) ON DELETE SET NULL
);



DROP TABLE IF EXISTS switchports;
CREATE TABLE switchports (
	interface	int(11)		NOT NULL references networks,
	switch		int(11)		NOT NULL references nodes,
	port		int(11)		NOT NULL
);



DROP TABLE IF EXISTS carts;
CREATE TABLE carts (
  ID 		int(11) NOT NULL auto_increment,
  Name		varchar(128) NOT NULL default '',
  URL		text	    NULL default '',
  PRIMARY KEY (ID),
  INDEX (Name)
);



DROP TABLE IF EXISTS rolls;
CREATE TABLE rolls (
  ID 		int(11) NOT NULL auto_increment,
  Name		varchar(128) NOT NULL default '',
  Version	varchar(32) NOT NULL default '',
  Rel		varchar(32) NOT NULL default '',
  Arch		varchar(32) NOT NULL default '',
  OS		varchar(32) NOT NULL default 'sles',
  URL		text	    NULL default '',
  PRIMARY KEY (ID),
  INDEX (Name)
);


DROP TABLE IF EXISTS stacks;
CREATE TABLE stacks (
	box		INT NOT NULL,
	roll		INT NOT NULL,
	FOREIGN KEY (box) REFERENCES boxes(id) ON DELETE CASCADE,
	FOREIGN KEY (roll) REFERENCES rolls(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS cart_stacks;
CREATE TABLE cart_stacks (
	box		INT NOT NULL,
	cart		INT NOT NULL,
	FOREIGN KEY (box) REFERENCES boxes(id) ON DELETE CASCADE,
	FOREIGN KEY (cart) REFERENCES carts(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS groups;
CREATE TABLE groups (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	name		VARCHAR(128) NOT NULL,
	INDEX (name)
);

DROP TABLE IF EXISTS memberships;
CREATE TABLE memberships (
	nodeid		INT NOT NULL,
	groupid		INT NOT NULL,
	FOREIGN KEY (nodeid) REFERENCES nodes(id) ON DELETE CASCADE,
	FOREIGN KEY (groupid) REFERENCES groups(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS partitions;
CREATE TABLE partitions (
	ID				int(11) NOT NULL auto_increment,
	Node			int(11) NOT NULL references nodes,
	Device			varchar(128) NOT NULL default '',
	Mountpoint		varchar(128) NOT NULL default '',
	UUID			varchar(128) NOT NULL default '',
	SectorStart		varchar(128) NOT NULL default '',
	PartitionSize	varchar(128) NOT NULL default '',
	PartitionID		varchar(128) NOT NULL default '',
	FsType			varchar(128) NOT NULL default '',
	PartitionFlags	varchar(128) NOT NULL default '',
	FormatFlags		varchar(128) NOT NULL default '',
	PRIMARY KEY (ID)
);


DROP TABLE IF EXISTS attributes;
DROP TABLE IF EXISTS firewall_rules;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS storage_controller;
DROP TABLE IF EXISTS storage_partition;
DROP TABLE IF EXISTS scope_map;

CREATE TABLE scope_map (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope		ENUM('global','appliance','os','environment', 'host') NOT NULL,
	appliance_id	INT DEFAULT NULL,
	os_id		INT DEFAULT NULL,
	environment_id	INT DEFAULT NULL,
	node_id		INT DEFAULT NULL,
	INDEX (scope),
	FOREIGN KEY (appliance_id) REFERENCES appliances(id) ON DELETE CASCADE,
	FOREIGN KEY (os_id) REFERENCES oses(id) ON DELETE CASCADE,
	FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
	FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE TABLE attributes (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope_map_id	INT NOT NULL,
	name		VARCHAR(128) NOT NULL,
	value		TEXT NOT NULL,
	INDEX (name),
	FOREIGN KEY (scope_map_id) REFERENCES scope_map(id) ON DELETE CASCADE
);

CREATE TABLE firewall_rules (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope_map_id	INT NOT NULL,
	name		VARCHAR(256) NOT NULL,
	table_type	ENUM('nat','filter','mangle','raw') NOT NULL,
	chain		VARCHAR(256) NOT NULL,
	action		VARCHAR(256) NOT NULL,
	service		VARCHAR(256) NOT NULL,
	protocol	VARCHAR(256) NOT NULL,
	in_subnet_id	INT DEFAULT NULL,
	out_subnet_id	INT DEFAULT NULL,
	flags		VARCHAR(256) DEFAULT NULL,
	comment		VARCHAR(256) DEFAULT NULL,
	INDEX (name),
	INDEX (table_type),
	FOREIGN KEY (scope_map_id) REFERENCES scope_map(id) ON DELETE CASCADE,
	FOREIGN KEY (in_subnet_id) REFERENCES subnets(id) ON DELETE CASCADE,
	FOREIGN KEY (out_subnet_id) REFERENCES subnets(id) ON DELETE CASCADE
);

CREATE TABLE routes (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope_map_id	INT NOT NULL,
	address		VARCHAR(32) NOT NULL,
	netmask		VARCHAR(32) NOT NULL,
	gateway		VARCHAR(32) DEFAULT NULL,
	subnet_id	INT DEFAULT NULL,
	interface	VARCHAR(32) DEFAULT NULL,
	INDEX (address),
	INDEX (interface),
	FOREIGN KEY (scope_map_id) REFERENCES scope_map(id) ON DELETE CASCADE,
	FOREIGN KEY (subnet_id) REFERENCES subnets(id) ON DELETE CASCADE
);

CREATE TABLE storage_controller (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope_map_id	INT NOT NULL,
	enclosure	INT NOT NULL,
	adapter		INT NOT NULL,
	slot		INT NOT NULL,
	raidlevel	VARCHAR(16) NOT NULL,
	arrayid		INT NOT NULL,
	options		VARCHAR(512) NOT NULL,
	INDEX (enclosure, adapter, slot),
	FOREIGN KEY (scope_map_id) REFERENCES scope_map(id) ON DELETE CASCADE
);

CREATE TABLE storage_partition (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope_map_id	INT NOT NULL,
	device		VARCHAR(128) NOT NULL,
	mountpoint	VARCHAR(128) DEFAULT NULL,
	size		INT NOT NULL,
	fstype		VARCHAR(128) DEFAULT NULL,
	partid		INT NOT NULL,
	options		VARCHAR(512) NOT NULL,
	INDEX (device),
	INDEX (mountpoint),
	INDEX (device, mountpoint),
	FOREIGN KEY (scope_map_id) REFERENCES scope_map(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS public_keys;
CREATE TABLE public_keys (
 ID		int(11) NOT NULL auto_increment,
 Node		int(11) NOT NULL references nodes,
 Public_Key	varchar(4096) default NULL,
 PRIMARY KEY (ID)
);



DROP TABLE IF EXISTS ib_partitions;
CREATE TABLE ib_partitions (
  id		int(11) NOT NULL auto_increment,
  switch	int(11) NOT NULL references nodes on delete cascade,
  part_key	int(11) NOT NULL,
  part_name	varchar(128) NOT NULL,
  options	varchar(128) NOT NULL default '',
  PRIMARY KEY (id),
  INDEX (part_name),
  FOREIGN KEY (switch) REFERENCES nodes(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS ib_memberships;
CREATE TABLE ib_memberships (
  id		int(11) NOT NULL auto_increment,
  switch	int(11) NOT NULL references nodes on delete cascade,
  interface	int(11) NOT NULL references networks on delete cascade,
  part_name	int(11) NOT NULL references ib_partitions on delete cascade,
  member_type	varchar(32) NOT NULL default 'limited',
  PRIMARY KEY (id),
  INDEX (switch, part_name, interface),
  FOREIGN KEY (switch) REFERENCES nodes(id) ON DELETE CASCADE,
  FOREIGN KEY (interface) REFERENCES networks(id) ON DELETE CASCADE,
  FOREIGN KEY (part_name) REFERENCES ib_partitions(id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS firmware_mapping;
DROP TABLE IF EXISTS firmware;
DROP TABLE IF EXISTS firmware_model;
DROP TABLE IF EXISTS firmware_make;
DROP TABLE IF EXISTS firmware_imp;
DROP TABLE IF EXISTS firmware_version_regex;

CREATE TABLE firmware_version_regex (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
	regex VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
	description VARCHAR(2048) NOT NULL,
	INDEX (name),
	CONSTRAINT unique_name UNIQUE (name)
);

CREATE TABLE firmware_imp (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
	INDEX (name),
	CONSTRAINT unique_name UNIQUE (name)
);

CREATE TABLE firmware_make (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
	version_regex_id INT DEFAULT NULL,
	FOREIGN KEY (version_regex_id) REFERENCES firmware_version_regex(id) ON DELETE SET NULL,
	INDEX (name),
	CONSTRAINT unique_name UNIQUE (name)
);

CREATE TABLE firmware_model (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
	make_id INT NOT NULL,
	imp_id INT NOT NULL,
	version_regex_id INT DEFAULT NULL,
	FOREIGN KEY (make_id) REFERENCES firmware_make(id),
	FOREIGN KEY (imp_id) REFERENCES firmware_imp(id),
	FOREIGN KEY (version_regex_id) REFERENCES firmware_version_regex(id) ON DELETE SET NULL,
	INDEX (name),
	CONSTRAINT unique_make_model UNIQUE (make_id, name)
);

CREATE TABLE firmware (
	id INT AUTO_INCREMENT PRIMARY KEY,
	model_id INT NOT NULL,
	source VARCHAR(2048) NOT NULL,
	version VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
	hash_alg VARCHAR(255) NOT NULL default 'md5',
	hash VARCHAR(2048) NOT NULL,
	file VARCHAR(2048) NOT NULL,
	FOREIGN KEY (model_id) REFERENCES firmware_model(id),
	INDEX (version),
	CONSTRAINT unique_model_version UNIQUE (model_id, version)
);

CREATE TABLE firmware_mapping (
	id INT AUTO_INCREMENT PRIMARY KEY,
	node_id INT NOT NULL,
	firmware_id INT NOT NULL,
	FOREIGN KEY (node_id) REFERENCES nodes(ID) ON DELETE CASCADE,
	FOREIGN KEY (firmware_id) REFERENCES firmware(id) ON DELETE CASCADE,
	CONSTRAINT unique_node_firmware UNIQUE (node_id, firmware_id)
);

