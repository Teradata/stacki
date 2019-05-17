CREATE TABLE public.access (
    "Command" character varying(255) NOT NULL,
    "GroupID" integer NOT NULL
);
CREATE TABLE public.aliases (
    "ID" integer NOT NULL,
    "Name" character varying(255) NOT NULL,
    "Network" integer NOT NULL
);
CREATE SEQUENCE public."aliases_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."aliases_ID_seq" OWNED BY public.aliases."ID";
CREATE TABLE public.appliances (
    "ID" integer NOT NULL,
    "Name" character varying(255) DEFAULT ''::character varying NOT NULL,
    "Public" character varying(255) DEFAULT 'no'::character varying NOT NULL
);
CREATE SEQUENCE public."appliances_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."appliances_ID_seq" OWNED BY public.appliances."ID";
CREATE TABLE public.attributes (
    "Attr" character varying(255) NOT NULL,
    "Scope" character varying(255),
    "ScopeID" integer,
    "Shadow" text,
    "Value" text
);
CREATE TABLE public.attributes_doc (
    "Attr" character varying(255) NOT NULL,
    "Doc" text
);
CREATE TABLE public.boot (
    "Action" character varying(255),
    "Node" integer DEFAULT 0 NOT NULL
);
CREATE TABLE public.bootactions (
    "ID" integer NOT NULL,
    "Args" text,
    "BootName" integer NOT NULL,
    "Kernel" character varying,
    "OS" integer,
    "Ramdisk" character varying(255)
);
CREATE SEQUENCE public."bootactions_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."bootactions_ID_seq" OWNED BY public.bootactions."ID";
CREATE TABLE public.bootnames (
    "ID" integer NOT NULL,
    "Name" character varying(255) NOT NULL,
    "Type" character varying(255) NOT NULL
);
CREATE SEQUENCE public."bootnames_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."bootnames_ID_seq" OWNED BY public.bootnames."ID";
CREATE TABLE public.boxes (
    "ID" integer NOT NULL,
    "Name" character varying(255) DEFAULT 'default'::character varying NOT NULL,
    "OS" integer NOT NULL
);
CREATE SEQUENCE public."boxes_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."boxes_ID_seq" OWNED BY public.boxes."ID";
CREATE TABLE public.cart_stacks (
    "Box" integer DEFAULT 1 NOT NULL,
    "Cart" integer NOT NULL
);
CREATE TABLE public.carts (
    "ID" integer NOT NULL,
    "Name" character varying(255) DEFAULT ''::character varying NOT NULL,
    "URL" text
);
CREATE SEQUENCE public."carts_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."carts_ID_seq" OWNED BY public.carts."ID";
CREATE TABLE public.environments (
    "ID" integer NOT NULL,
    "Name" character varying(255) DEFAULT ''::character varying NOT NULL
);
CREATE SEQUENCE public."environments_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."environments_ID_seq" OWNED BY public.environments."ID";
CREATE TABLE public.firewall_rules (
    id integer NOT NULL,
    action character varying(255) NOT NULL,
    chain character varying(255) NOT NULL,
    comment character varying(255),
    flags character varying(255),
    in_subnet_id integer,
    name character varying(255) NOT NULL,
    out_subnet_id integer,
    protocol character varying(255) NOT NULL,
    scope_map_id integer NOT NULL,
    service character varying(255) NOT NULL,
    table_type character varying(255) NOT NULL
);
CREATE SEQUENCE public.firewall_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firewall_rules_id_seq OWNED BY public.firewall_rules.id;
CREATE TABLE public.firmware (
    id integer NOT NULL,
    file character varying(255) NOT NULL,
    hash character varying(255) NOT NULL,
    hash_alg character varying(255) DEFAULT 'md5'::character varying NOT NULL,
    model_id integer NOT NULL,
    source character varying(255) NOT NULL,
    version character varying(255) NOT NULL
);
CREATE SEQUENCE public.firmware_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firmware_id_seq OWNED BY public.firmware.id;
CREATE TABLE public.firmware_imp (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);
CREATE SEQUENCE public.firmware_imp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firmware_imp_id_seq OWNED BY public.firmware_imp.id;
CREATE TABLE public.firmware_make (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    version_regex_id integer
);
CREATE SEQUENCE public.firmware_make_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firmware_make_id_seq OWNED BY public.firmware_make.id;
CREATE TABLE public.firmware_mapping (
    id integer NOT NULL,
    firmware_id integer NOT NULL,
    node_id integer NOT NULL
);
CREATE SEQUENCE public.firmware_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firmware_mapping_id_seq OWNED BY public.firmware_mapping.id;
CREATE TABLE public.firmware_model (
    id integer NOT NULL,
    imp_id integer NOT NULL,
    make_id integer NOT NULL,
    name character varying(255) NOT NULL,
    version_regex_id integer
);
CREATE SEQUENCE public.firmware_model_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firmware_model_id_seq OWNED BY public.firmware_model.id;
CREATE TABLE public.firmware_version_regex (
    id integer NOT NULL,
    description character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    regex character varying(255) NOT NULL
);
CREATE SEQUENCE public.firmware_version_regex_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.firmware_version_regex_id_seq OWNED BY public.firmware_version_regex.id;
CREATE TABLE public.groups (
    "ID" integer NOT NULL,
    "Name" character varying(255) DEFAULT ''::character varying NOT NULL
);
CREATE SEQUENCE public."groups_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."groups_ID_seq" OWNED BY public.groups."ID";
CREATE TABLE public.ib_memberships (
    id integer NOT NULL,
    interface integer NOT NULL,
    member_type character varying(255) DEFAULT 'limited'::character varying NOT NULL,
    part_name integer NOT NULL,
    switch integer NOT NULL
);
CREATE SEQUENCE public.ib_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.ib_memberships_id_seq OWNED BY public.ib_memberships.id;
CREATE TABLE public.ib_partitions (
    id integer NOT NULL,
    options character varying(255) DEFAULT ''::character varying NOT NULL,
    part_key integer NOT NULL,
    part_name character varying(255) NOT NULL,
    switch integer NOT NULL
);
CREATE SEQUENCE public.ib_partitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.ib_partitions_id_seq OWNED BY public.ib_partitions.id;
CREATE TABLE public.memberships (
    "GroupID" integer NOT NULL,
    "NodeID" integer NOT NULL
);
CREATE TABLE public.networks (
    "ID" integer NOT NULL,
    "Channel" character varying(255),
    "Device" character varying(255),
    "Gateway" character varying(255),
    "IP" character varying(255),
    "MAC" character varying(255),
    "Main" integer DEFAULT 0,
    "Module" character varying(255),
    "Name" character varying(255),
    "Netmask" character varying(255),
    "Node" integer,
    "Options" character varying(255),
    "Subnet" integer,
    "VlanID" integer
);
CREATE SEQUENCE public."networks_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."networks_ID_seq" OWNED BY public.networks."ID";
CREATE TABLE public.nodes (
    "ID" integer NOT NULL,
    "Appliance" integer,
    "Box" integer,
    "Comment" character varying(255),
    "Environment" integer,
    "InstallAction" integer,
    "MetaData" text,
    "Name" character varying(255),
    "OSAction" integer,
    "Rack" character varying(255),
    "Rank" character varying(255)
);
CREATE SEQUENCE public."nodes_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."nodes_ID_seq" OWNED BY public.nodes."ID";
CREATE TABLE public.oses (
    "ID" integer NOT NULL,
    "Name" character varying(255) DEFAULT ''::character varying NOT NULL
);
CREATE SEQUENCE public."oses_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."oses_ID_seq" OWNED BY public.oses."ID";
CREATE TABLE public.partitions (
    "ID" integer NOT NULL,
    "Device" character varying(255) DEFAULT ''::character varying NOT NULL,
    "FormatFlags" character varying(255) DEFAULT ''::character varying NOT NULL,
    "FsType" character varying(255) DEFAULT ''::character varying NOT NULL,
    "Mountpoint" character varying(255) DEFAULT ''::character varying NOT NULL,
    "Node" integer NOT NULL,
    "PartitionFlags" character varying(255) DEFAULT ''::character varying NOT NULL,
    "PartitionID" character varying(255) DEFAULT ''::character varying NOT NULL,
    "PartitionSize" character varying(255) DEFAULT ''::character varying NOT NULL,
    "SectorStart" character varying(255) DEFAULT ''::character varying NOT NULL,
    "UUID" character varying(255) DEFAULT ''::character varying NOT NULL
);
CREATE SEQUENCE public."partitions_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."partitions_ID_seq" OWNED BY public.partitions."ID";
CREATE TABLE public.public_keys (
    "ID" integer NOT NULL,
    "Node" integer NOT NULL,
    "Public_Key" character varying(255)
);
CREATE SEQUENCE public."public_keys_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."public_keys_ID_seq" OWNED BY public.public_keys."ID";
CREATE TABLE public.rolls (
    "ID" integer NOT NULL,
    "Arch" character varying(255) DEFAULT ''::character varying NOT NULL,
    "Name" character varying(255) DEFAULT ''::character varying NOT NULL,
    "OS" character varying(255) DEFAULT 'sles'::character varying NOT NULL,
    "Rel" character varying(255) DEFAULT ''::character varying NOT NULL,
    "URL" text,
    "Version" character varying(255) DEFAULT ''::character varying NOT NULL
);
CREATE SEQUENCE public."rolls_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."rolls_ID_seq" OWNED BY public.rolls."ID";
CREATE TABLE public.routes (
    id integer NOT NULL,
    address character varying(255) NOT NULL,
    gateway character varying(255),
    interface character varying(255),
    netmask character varying(255) NOT NULL,
    scope_map_id integer NOT NULL,
    subnet_id integer
);
CREATE SEQUENCE public.routes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.routes_id_seq OWNED BY public.routes.id;
CREATE TABLE public.scope_map (
    id integer NOT NULL,
    appliance_id integer,
    environment_id integer,
    node_id integer,
    os_id integer,
    scope character varying(255) NOT NULL
);
CREATE SEQUENCE public.scope_map_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.scope_map_id_seq OWNED BY public.scope_map.id;
CREATE TABLE public.stacks (
    "Box" integer DEFAULT 1 NOT NULL,
    "Roll" integer NOT NULL
);
CREATE TABLE public.storage_controller (
    id integer NOT NULL,
    adapter integer NOT NULL,
    arrayid integer NOT NULL,
    enclosure integer NOT NULL,
    options character varying(255) NOT NULL,
    raidlevel character varying(255) NOT NULL,
    scope_map_id integer NOT NULL,
    slot integer NOT NULL
);
CREATE SEQUENCE public.storage_controller_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.storage_controller_id_seq OWNED BY public.storage_controller.id;
CREATE TABLE public.storage_partition (
    id integer NOT NULL,
    device character varying(255) NOT NULL,
    fstype character varying(255),
    mountpoint character varying(255),
    options character varying(255) NOT NULL,
    partid integer NOT NULL,
    scope_map_id integer NOT NULL,
    size integer NOT NULL
);
CREATE SEQUENCE public.storage_partition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.storage_partition_id_seq OWNED BY public.storage_partition.id;
CREATE TABLE public.subnets (
    "ID" integer NOT NULL,
    address character varying(255) NOT NULL,
    dns integer DEFAULT 0,
    gateway character varying(255),
    mask character varying(255) NOT NULL,
    mtu integer DEFAULT 1500,
    name character varying(255) NOT NULL,
    pxe integer DEFAULT 0,
    zone character varying(255) NOT NULL
);
CREATE SEQUENCE public."subnets_ID_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public."subnets_ID_seq" OWNED BY public.subnets."ID";
CREATE TABLE public.switchports (
    interface integer NOT NULL,
    port integer NOT NULL,
    switch integer NOT NULL
);
CREATE TABLE public.tags (
    "Scope" character varying(255),
    "ScopeID" integer,
    "Tag" character varying(255) NOT NULL,
    "Value" text
);
ALTER TABLE ONLY public.aliases ALTER COLUMN "ID" SET DEFAULT nextval('public."aliases_ID_seq"'::regclass);
ALTER TABLE ONLY public.appliances ALTER COLUMN "ID" SET DEFAULT nextval('public."appliances_ID_seq"'::regclass);
ALTER TABLE ONLY public.bootactions ALTER COLUMN "ID" SET DEFAULT nextval('public."bootactions_ID_seq"'::regclass);
ALTER TABLE ONLY public.bootnames ALTER COLUMN "ID" SET DEFAULT nextval('public."bootnames_ID_seq"'::regclass);
ALTER TABLE ONLY public.boxes ALTER COLUMN "ID" SET DEFAULT nextval('public."boxes_ID_seq"'::regclass);
ALTER TABLE ONLY public.carts ALTER COLUMN "ID" SET DEFAULT nextval('public."carts_ID_seq"'::regclass);
ALTER TABLE ONLY public.environments ALTER COLUMN "ID" SET DEFAULT nextval('public."environments_ID_seq"'::regclass);
ALTER TABLE ONLY public.firewall_rules ALTER COLUMN id SET DEFAULT nextval('public.firewall_rules_id_seq'::regclass);
ALTER TABLE ONLY public.firmware ALTER COLUMN id SET DEFAULT nextval('public.firmware_id_seq'::regclass);
ALTER TABLE ONLY public.firmware_imp ALTER COLUMN id SET DEFAULT nextval('public.firmware_imp_id_seq'::regclass);
ALTER TABLE ONLY public.firmware_make ALTER COLUMN id SET DEFAULT nextval('public.firmware_make_id_seq'::regclass);
ALTER TABLE ONLY public.firmware_mapping ALTER COLUMN id SET DEFAULT nextval('public.firmware_mapping_id_seq'::regclass);
ALTER TABLE ONLY public.firmware_model ALTER COLUMN id SET DEFAULT nextval('public.firmware_model_id_seq'::regclass);
ALTER TABLE ONLY public.firmware_version_regex ALTER COLUMN id SET DEFAULT nextval('public.firmware_version_regex_id_seq'::regclass);
ALTER TABLE ONLY public.groups ALTER COLUMN "ID" SET DEFAULT nextval('public."groups_ID_seq"'::regclass);
ALTER TABLE ONLY public.ib_memberships ALTER COLUMN id SET DEFAULT nextval('public.ib_memberships_id_seq'::regclass);
ALTER TABLE ONLY public.ib_partitions ALTER COLUMN id SET DEFAULT nextval('public.ib_partitions_id_seq'::regclass);
ALTER TABLE ONLY public.networks ALTER COLUMN "ID" SET DEFAULT nextval('public."networks_ID_seq"'::regclass);
ALTER TABLE ONLY public.nodes ALTER COLUMN "ID" SET DEFAULT nextval('public."nodes_ID_seq"'::regclass);
ALTER TABLE ONLY public.oses ALTER COLUMN "ID" SET DEFAULT nextval('public."oses_ID_seq"'::regclass);
ALTER TABLE ONLY public.partitions ALTER COLUMN "ID" SET DEFAULT nextval('public."partitions_ID_seq"'::regclass);
ALTER TABLE ONLY public.public_keys ALTER COLUMN "ID" SET DEFAULT nextval('public."public_keys_ID_seq"'::regclass);
ALTER TABLE ONLY public.rolls ALTER COLUMN "ID" SET DEFAULT nextval('public."rolls_ID_seq"'::regclass);
ALTER TABLE ONLY public.routes ALTER COLUMN id SET DEFAULT nextval('public.routes_id_seq'::regclass);
ALTER TABLE ONLY public.scope_map ALTER COLUMN id SET DEFAULT nextval('public.scope_map_id_seq'::regclass);
ALTER TABLE ONLY public.storage_controller ALTER COLUMN id SET DEFAULT nextval('public.storage_controller_id_seq'::regclass);
ALTER TABLE ONLY public.storage_partition ALTER COLUMN id SET DEFAULT nextval('public.storage_partition_id_seq'::regclass);
ALTER TABLE ONLY public.subnets ALTER COLUMN "ID" SET DEFAULT nextval('public."subnets_ID_seq"'::regclass);
ALTER TABLE ONLY public.aliases
    ADD CONSTRAINT aliases_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.appliances
    ADD CONSTRAINT appliances_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.bootactions
    ADD CONSTRAINT bootactions_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.bootnames
    ADD CONSTRAINT bootnames_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.boxes
    ADD CONSTRAINT boxes_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.carts
    ADD CONSTRAINT carts_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.environments
    ADD CONSTRAINT environments_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.firewall_rules
    ADD CONSTRAINT firewall_rules_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.firmware_imp
    ADD CONSTRAINT firmware_imp_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.firmware_make
    ADD CONSTRAINT firmware_make_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.firmware_mapping
    ADD CONSTRAINT firmware_mapping_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.firmware_model
    ADD CONSTRAINT firmware_model_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.firmware
    ADD CONSTRAINT firmware_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.firmware_version_regex
    ADD CONSTRAINT firmware_version_regex_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.ib_memberships
    ADD CONSTRAINT ib_memberships_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.ib_partitions
    ADD CONSTRAINT ib_partitions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.networks
    ADD CONSTRAINT networks_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.oses
    ADD CONSTRAINT oses_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.partitions
    ADD CONSTRAINT partitions_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.public_keys
    ADD CONSTRAINT public_keys_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.rolls
    ADD CONSTRAINT rolls_pkey PRIMARY KEY ("ID");
ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.scope_map
    ADD CONSTRAINT scope_map_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.storage_controller
    ADD CONSTRAINT storage_controller_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.storage_partition
    ADD CONSTRAINT storage_partition_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.subnets
    ADD CONSTRAINT subnets_pkey PRIMARY KEY ("ID");
CREATE INDEX "aliases_Name" ON public.aliases USING btree ("Name");
CREATE INDEX "appliances_Name" ON public.appliances USING btree ("Name");
CREATE INDEX "attributes_Attr" ON public.attributes USING btree ("Attr");
CREATE INDEX "attributes_Scope" ON public.attributes USING btree ("Scope");
CREATE INDEX "attributes_ScopeID" ON public.attributes USING btree ("ScopeID");
CREATE INDEX "attributesdoc_Attr" ON public.attributes_doc USING btree ("Attr");
CREATE UNIQUE INDEX "bootactions_BootName_OS" ON public.bootactions USING btree ("BootName", "OS");
CREATE INDEX "bootnames_Name" ON public.bootnames USING btree ("Name");
CREATE INDEX "boxes_Name" ON public.boxes USING btree ("Name");
CREATE INDEX "carts_Name" ON public.carts USING btree ("Name");
CREATE INDEX "environments_Name" ON public.environments USING btree ("Name");
CREATE INDEX firewallrules_in_subnet_id ON public.firewall_rules USING btree (in_subnet_id);
CREATE INDEX firewallrules_name ON public.firewall_rules USING btree (name);
CREATE INDEX firewallrules_out_subnet_id ON public.firewall_rules USING btree (out_subnet_id);
CREATE INDEX firewallrules_scope_map_id ON public.firewall_rules USING btree (scope_map_id);
CREATE INDEX firewallrules_table_type ON public.firewall_rules USING btree (table_type);
CREATE INDEX firmware_model_id ON public.firmware USING btree (model_id);
CREATE UNIQUE INDEX firmware_model_id_version ON public.firmware USING btree (model_id, version);
CREATE INDEX firmware_version ON public.firmware USING btree (version);
CREATE INDEX firmwareimp_name ON public.firmware_imp USING btree (name);
CREATE INDEX firmwaremake_name ON public.firmware_make USING btree (name);
CREATE INDEX firmwaremake_version_regex_id ON public.firmware_make USING btree (version_regex_id);
CREATE INDEX firmwaremapping_firmware_id ON public.firmware_mapping USING btree (firmware_id);
CREATE INDEX firmwaremapping_node_id ON public.firmware_mapping USING btree (node_id);
CREATE UNIQUE INDEX firmwaremapping_node_id_firmware_id ON public.firmware_mapping USING btree (node_id, firmware_id);
CREATE INDEX firmwaremodel_imp_id ON public.firmware_model USING btree (imp_id);
CREATE INDEX firmwaremodel_make_id ON public.firmware_model USING btree (make_id);
CREATE UNIQUE INDEX firmwaremodel_make_id_name ON public.firmware_model USING btree (make_id, name);
CREATE INDEX firmwaremodel_name ON public.firmware_model USING btree (name);
CREATE INDEX firmwaremodel_version_regex_id ON public.firmware_model USING btree (version_regex_id);
CREATE INDEX firmwareversionregex_name ON public.firmware_version_regex USING btree (name);
CREATE INDEX "groups_Name" ON public.groups USING btree ("Name");
CREATE INDEX ibmemberships_interface ON public.ib_memberships USING btree (interface);
CREATE INDEX ibmemberships_part_name ON public.ib_memberships USING btree (part_name);
CREATE INDEX ibmemberships_switch ON public.ib_memberships USING btree (switch);
CREATE INDEX ibmemberships_switch_part_name_interface ON public.ib_memberships USING btree (switch, part_name, interface);
CREATE INDEX ibpartitions_part_name ON public.ib_partitions USING btree (part_name);
CREATE INDEX ibpartitions_switch ON public.ib_partitions USING btree (switch);
CREATE INDEX "networks_Device" ON public.networks USING btree ("Device");
CREATE INDEX "networks_MAC" ON public.networks USING btree ("MAC");
CREATE INDEX "networks_Name" ON public.networks USING btree ("Name");
CREATE INDEX "networks_Subnet" ON public.networks USING btree ("Subnet");
CREATE INDEX "nodes_Appliance" ON public.nodes USING btree ("Appliance");
CREATE INDEX "nodes_Name" ON public.nodes USING btree ("Name");
CREATE INDEX "oses_Name" ON public.oses USING btree ("Name");
CREATE INDEX "rolls_Name" ON public.rolls USING btree ("Name");
CREATE INDEX routes_address ON public.routes USING btree (address);
CREATE INDEX routes_interface ON public.routes USING btree (interface);
CREATE INDEX routes_scope_map_id ON public.routes USING btree (scope_map_id);
CREATE INDEX routes_subnet_id ON public.routes USING btree (subnet_id);
CREATE INDEX scopemap_appliance_id ON public.scope_map USING btree (appliance_id);
CREATE INDEX scopemap_environment_id ON public.scope_map USING btree (environment_id);
CREATE INDEX scopemap_node_id ON public.scope_map USING btree (node_id);
CREATE INDEX scopemap_os_id ON public.scope_map USING btree (os_id);
CREATE INDEX scopemap_scope ON public.scope_map USING btree (scope);
CREATE INDEX storagecontroller_enclosure_adapter_slot ON public.storage_controller USING btree (enclosure, adapter, slot);
CREATE INDEX storagecontroller_scope_map_id ON public.storage_controller USING btree (scope_map_id);
CREATE INDEX storagepartition_device ON public.storage_partition USING btree (device);
CREATE INDEX storagepartition_device_mountpoint ON public.storage_partition USING btree (device, mountpoint);
CREATE INDEX storagepartition_mountpoint ON public.storage_partition USING btree (mountpoint);
CREATE INDEX storagepartition_scope_map_id ON public.storage_partition USING btree (scope_map_id);
CREATE INDEX subnets_name ON public.subnets USING btree (name);
CREATE INDEX "tags_Scope" ON public.tags USING btree ("Scope");
CREATE INDEX "tags_ScopeID" ON public.tags USING btree ("ScopeID");
CREATE INDEX "tags_Tag" ON public.tags USING btree ("Tag");
ALTER TABLE ONLY public.bootactions
    ADD CONSTRAINT "bootactions_BootName_fkey" FOREIGN KEY ("BootName") REFERENCES public.bootnames("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.boxes
    ADD CONSTRAINT "boxes_OS_fkey" FOREIGN KEY ("OS") REFERENCES public.oses("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.firewall_rules
    ADD CONSTRAINT firewall_rules_in_subnet_id_fkey FOREIGN KEY (in_subnet_id) REFERENCES public.subnets("ID");
ALTER TABLE ONLY public.firewall_rules
    ADD CONSTRAINT firewall_rules_out_subnet_id_fkey FOREIGN KEY (out_subnet_id) REFERENCES public.subnets("ID");
ALTER TABLE ONLY public.firewall_rules
    ADD CONSTRAINT firewall_rules_scope_map_id_fkey FOREIGN KEY (scope_map_id) REFERENCES public.scope_map(id);
ALTER TABLE ONLY public.firmware_make
    ADD CONSTRAINT firmware_make_version_regex_id_fkey FOREIGN KEY (version_regex_id) REFERENCES public.firmware_version_regex(id);
ALTER TABLE ONLY public.firmware_mapping
    ADD CONSTRAINT firmware_mapping_firmware_id_fkey FOREIGN KEY (firmware_id) REFERENCES public.firmware(id);
ALTER TABLE ONLY public.firmware_mapping
    ADD CONSTRAINT firmware_mapping_node_id_fkey FOREIGN KEY (node_id) REFERENCES public.nodes("ID");
ALTER TABLE ONLY public.firmware
    ADD CONSTRAINT firmware_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.firmware_model(id);
ALTER TABLE ONLY public.firmware_model
    ADD CONSTRAINT firmware_model_imp_id_fkey FOREIGN KEY (imp_id) REFERENCES public.firmware_imp(id);
ALTER TABLE ONLY public.firmware_model
    ADD CONSTRAINT firmware_model_make_id_fkey FOREIGN KEY (make_id) REFERENCES public.firmware_make(id);
ALTER TABLE ONLY public.firmware_model
    ADD CONSTRAINT firmware_model_version_regex_id_fkey FOREIGN KEY (version_regex_id) REFERENCES public.firmware_version_regex(id);
ALTER TABLE ONLY public.ib_memberships
    ADD CONSTRAINT ib_memberships_interface_fkey FOREIGN KEY (interface) REFERENCES public.networks("ID");
ALTER TABLE ONLY public.ib_memberships
    ADD CONSTRAINT ib_memberships_part_name_fkey FOREIGN KEY (part_name) REFERENCES public.ib_partitions(id);
ALTER TABLE ONLY public.ib_memberships
    ADD CONSTRAINT ib_memberships_switch_fkey FOREIGN KEY (switch) REFERENCES public.nodes("ID");
ALTER TABLE ONLY public.ib_partitions
    ADD CONSTRAINT ib_partitions_switch_fkey FOREIGN KEY (switch) REFERENCES public.nodes("ID");
ALTER TABLE ONLY public.networks
    ADD CONSTRAINT "networks_Node_fkey" FOREIGN KEY ("Node") REFERENCES public.nodes("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.networks
    ADD CONSTRAINT "networks_Subnet_fkey" FOREIGN KEY ("Subnet") REFERENCES public.subnets("ID");
ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT "nodes_Appliance_fkey" FOREIGN KEY ("Appliance") REFERENCES public.appliances("ID");
ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT "nodes_Box_fkey" FOREIGN KEY ("Box") REFERENCES public.boxes("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT "nodes_Environment_fkey" FOREIGN KEY ("Environment") REFERENCES public.environments("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT "nodes_InstallAction_fkey" FOREIGN KEY ("InstallAction") REFERENCES public.bootactions("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT "nodes_OSAction_fkey" FOREIGN KEY ("OSAction") REFERENCES public.bootactions("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_scope_map_id_fkey FOREIGN KEY (scope_map_id) REFERENCES public.scope_map(id);
ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_subnet_id_fkey FOREIGN KEY (subnet_id) REFERENCES public.subnets("ID");
ALTER TABLE ONLY public.scope_map
    ADD CONSTRAINT scope_map_appliance_id_fkey FOREIGN KEY (appliance_id) REFERENCES public.appliances("ID");
ALTER TABLE ONLY public.scope_map
    ADD CONSTRAINT scope_map_environment_id_fkey FOREIGN KEY (environment_id) REFERENCES public.environments("ID");
ALTER TABLE ONLY public.scope_map
    ADD CONSTRAINT scope_map_node_id_fkey FOREIGN KEY (node_id) REFERENCES public.nodes("ID");
ALTER TABLE ONLY public.scope_map
    ADD CONSTRAINT scope_map_os_id_fkey FOREIGN KEY (os_id) REFERENCES public.oses("ID");
ALTER TABLE ONLY public.stacks
    ADD CONSTRAINT "stacks_Roll_fkey" FOREIGN KEY ("Roll") REFERENCES public.rolls("ID") ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.storage_controller
    ADD CONSTRAINT storage_controller_scope_map_id_fkey FOREIGN KEY (scope_map_id) REFERENCES public.scope_map(id);
ALTER TABLE ONLY public.storage_partition
    ADD CONSTRAINT storage_partition_scope_map_id_fkey FOREIGN KEY (scope_map_id) REFERENCES public.scope_map(id);
