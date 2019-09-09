-- MySQL dump 10.15  Distrib 10.0.30-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: 
-- ------------------------------------------------------
-- Server version	10.0.30-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `cluster`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `cluster` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `cluster`;

--
-- Table structure for table `access`
--

DROP TABLE IF EXISTS `access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `access` (
  `Command` varchar(128) NOT NULL,
  `GroupID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access`
--

LOCK TABLES `access` WRITE;
/*!40000 ALTER TABLE `access` DISABLE KEYS */;
INSERT INTO `access` VALUES ('*',0),('*',8),('list*',10),('list *',65533);
/*!40000 ALTER TABLE `access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliases`
--

DROP TABLE IF EXISTS `aliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliases` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL,
  `Network` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliases`
--

LOCK TABLES `aliases` WRITE;
/*!40000 ALTER TABLE `aliases` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appliances`
--

DROP TABLE IF EXISTS `appliances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `appliances` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT '',
  `Public` enum('yes','no') NOT NULL DEFAULT 'no',
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appliances`
--

LOCK TABLES `appliances` WRITE;
/*!40000 ALTER TABLE `appliances` DISABLE KEYS */;
INSERT INTO `appliances` VALUES (1,'frontend','no'),(2,'builder','no'),(3,'barnacle','no'),(4,'switch','no'),(5,'backend','yes'),(6,'replicant','yes'),(7,'external','no');
/*!40000 ALTER TABLE `appliances` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attributes`
--

DROP TABLE IF EXISTS `attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attributes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scope_map_id` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `scope_map_id` (`scope_map_id`),
  CONSTRAINT `attributes_ibfk_1` FOREIGN KEY (`scope_map_id`) REFERENCES `scope_map` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attributes`
--

LOCK TABLES `attributes` WRITE;
/*!40000 ALTER TABLE `attributes` DISABLE KEYS */;
INSERT INTO `attributes` VALUES (1,1,'Info_CertificateCountry','US'),(2,2,'Info_CertificateLocality','Solana Beach'),(3,3,'Info_CertificateOrganization','StackIQ'),(4,4,'Info_CertificateState','California'),(5,5,'Info_ClusterLatlong','N32.87 W117.22'),(6,6,'Info_FQDN','cluster-up-frontend'),(7,7,'Kickstart_Keyboard','us'),(8,8,'Kickstart_Lang','en_US'),(9,9,'Kickstart_Langsupport','en_US'),(10,10,'Kickstart_PrivateAddress','192.168.0.2'),(11,11,'Kickstart_PrivateBroadcast','192.168.0.255'),(12,12,'Kickstart_PrivateDNSServers','10.0.2.3'),(13,13,'Kickstart_PrivateEthernet','08:00:27:5e:15:9e'),(14,14,'Kickstart_PrivateGateway','10.0.2.2'),(15,15,'Kickstart_PrivateHostname','cluster-up-frontend'),(16,16,'Kickstart_PrivateInterface','eth1'),(17,17,'Kickstart_PrivateKickstartHost','192.168.0.2'),(18,18,'Kickstart_PrivateNTPHost','192.168.0.2'),(19,19,'Kickstart_PrivateNetmask','255.255.255.0'),(20,20,'Kickstart_PrivateNetmaskCIDR','24'),(21,21,'Kickstart_PrivateNetwork','192.168.0.0'),(22,23,'Kickstart_PublicNTPHost','pool.ntp.org'),(23,24,'Kickstart_Timezone','UTC'),(24,25,'Kickstart_Multicast','228.36.109.178'),(25,26,'Server_Partitioning','force-default-root-disk-only'),(26,27,'sync.ssh.authkey','True'),(27,28,'ssh.use_dns','True'),(28,29,'discovery.base.rack','0'),(29,30,'discovery.base.rank','0'),(30,31,'os','sles'),(31,32,'firewall','True'),(34,35,'node','server'),(35,36,'kickstartable','True'),(36,37,'managed','False'),(39,40,'node','builder'),(40,41,'kickstartable','True'),(41,42,'managed','True'),(44,45,'node','barnacle'),(45,46,'kickstartable','True'),(46,47,'managed','True'),(49,50,'kickstartable','False'),(50,51,'managed','False'),(53,54,'node','backend'),(54,55,'kickstartable','True'),(55,56,'managed','True'),(58,59,'node','replicant'),(59,60,'kickstartable','True'),(60,61,'managed','True'),(61,62,'const_overwrite','False'),(64,65,'kickstartable','False'),(65,66,'managed','False'),(66,69,'time.protocol','chrony'),(67,70,'time.protocol','chrony'),(68,77,'install.confirm','false'),(69,78,'install.final_reboot','false'),(70,79,'systemd.default.target','multi-user'),(71,80,'arch','x86_64'),(72,81,'cpus','1'),(73,82,'arch','x86_64'),(74,83,'cpus','1'),(81,90,'nukedisks','false'),(82,91,'nukecontroller','false'),(83,92,'secureerase','false'),(90,99,'nukedisks','false'),(91,100,'nukecontroller','false'),(92,101,'secureerase','false');
/*!40000 ALTER TABLE `attributes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attributes_doc`
--

DROP TABLE IF EXISTS `attributes_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attributes_doc` (
  `Attr` varchar(128) NOT NULL,
  `Doc` text,
  KEY `Attr` (`Attr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attributes_doc`
--

LOCK TABLES `attributes_doc` WRITE;
/*!40000 ALTER TABLE `attributes_doc` DISABLE KEYS */;
/*!40000 ALTER TABLE `attributes_doc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `boot`
--

DROP TABLE IF EXISTS `boot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `boot` (
  `Node` int(11) NOT NULL DEFAULT '0',
  `Action` enum('install','os') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `boot`
--

LOCK TABLES `boot` WRITE;
/*!40000 ALTER TABLE `boot` DISABLE KEYS */;
INSERT INTO `boot` VALUES (2,'os'),(3,'os');
/*!40000 ALTER TABLE `boot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bootactions`
--

DROP TABLE IF EXISTS `bootactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bootactions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `BootName` int(11) NOT NULL,
  `OS` int(11) DEFAULT NULL,
  `Kernel` varchar(256) DEFAULT NULL,
  `Ramdisk` varchar(256) DEFAULT NULL,
  `Args` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `BootnameOS` (`BootName`,`OS`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bootactions`
--

LOCK TABLES `bootactions` WRITE;
/*!40000 ALTER TABLE `bootactions` DISABLE KEYS */;
INSERT INTO `bootactions` VALUES (1,1,NULL,'com32 chain.c32',NULL,'hd0'),(2,2,NULL,'kernel memdisk bigraw','pxeflash.img','keeppxe'),(3,3,NULL,'localboot 0',NULL,NULL),(4,4,NULL,'localboot -1',NULL,NULL),(5,5,NULL,'kernel memtest',NULL,NULL),(6,6,3,'vmlinuz-sles-12-sp3-x86_64','initrd-sles-12-sp3-x86_64','install=http://192.168.0.2/install/pallets/SLES/12/sp3/sles/x86_64 autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 Server=192.168.0.2'),(7,7,3,'vmlinuz-sles-12-sp3-x86_64','initrd-sles-12-sp3-x86_64','install=http://192.168.0.2/install/pallets/SLES/12/sp3/sles/x86_64 autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 Server=192.168.0.2 console=ttyS0,115200n8 nomodeset=1 textmode=1'),(8,8,3,'vmlinuz-sles-12-sp3-x86_64','initrd-sles-12-sp3-x86_64','splash=silent rescue=1 showopts brokenmodules=mptfc,qla2xxx,mpt2sas,mpt3sas,mlx4_core,mlx4_ib,mlx4_en,mlx5_core,mlx5_ib'),(9,9,3,'vmlinuz-sles-12-sp2-x86_64','initrd-sles-12-sp2-x86_64','install=http://192.168.0.2/install/pallets/SLES/12/sp2/sles/x86_64 autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 Server=192.168.0.2'),(10,10,3,'vmlinuz-sles-12-sp2-x86_64','initrd-sles-12-sp2-x86_64','install=http://192.168.0.2/install/pallets/SLES/12/sp2/sles/x86_64 autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 Server=192.168.0.2 console=ttyS0,115200n8 nomodeset=1 textmode=1'),(11,11,3,'vmlinuz-sles-12-sp2-x86_64','initrd-sles-12-sp2-x86_64','splash=silent rescue=1 showopts brokenmodules=mptfc,qla2xxx,mpt2sas,mpt3sas,mlx4_core,mlx4_ib,mlx4_en,mlx5_core,mlx5_ib'),(12,12,3,'vmlinuz-sles-11.3-1.138-x86_64','initrd-sles-11.3-1.138-x86_64','install=http://192.168.0.2/install/pallets/SLES/11.3/1.138/sles/x86_64 autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 Server=192.168.0.2 insmod=ixgbe insmod=i40e forceinsmod=1'),(13,13,3,'vmlinuz-sles-11.3-1.138-x86_64','initrd-sles-11.3-1.138-x86_64','install=http://192.168.0.2/install/pallets/SLES/11.3/1.138/sles/x86_64 autoyast=file:///tmp/profile/autoinst.xml ramdisk_size=300000 biosdevname=0 console=ttyS0,115200n8 Server=192.168.0.2 nomodeset=1 textmode=1 insmod=ixgbe insmod=i40e forceinsmod=1'),(14,14,3,'vmlinuz-sles-11.3-1.138-x86_64','initrd-sles-11.3-1.138-x86_64','splash=silent rescue=1 showopts brokenmodules=mptfc,qla2xxx,mpt2sas,mpt3sas,mlx4_core,mlx4_ib,mlx4_en,mlx5_core,mlx5_ib');
/*!40000 ALTER TABLE `bootactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bootnames`
--

DROP TABLE IF EXISTS `bootnames`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bootnames` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(128) NOT NULL,
  `Type` enum('install','os') NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bootnames`
--

LOCK TABLES `bootnames` WRITE;
/*!40000 ALTER TABLE `bootnames` DISABLE KEYS */;
INSERT INTO `bootnames` VALUES (1,'default','os'),(2,'pxeflash','os'),(3,'localboot','os'),(4,'hplocalboot','os'),(5,'memtest','os'),(6,'default','install'),(7,'console','install'),(8,'rescue','install'),(9,'install sles 12.2','install'),(10,'install sles 12.2 console','install'),(11,'rescue sles 12.2','install'),(12,'install sles 11.3','install'),(13,'install sles 11.3 console','install'),(14,'rescue sles 11.3','install');
/*!40000 ALTER TABLE `bootnames` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `boxes`
--

DROP TABLE IF EXISTS `boxes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `boxes` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT 'default',
  `OS` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `boxes`
--

LOCK TABLES `boxes` WRITE;
/*!40000 ALTER TABLE `boxes` DISABLE KEYS */;
INSERT INTO `boxes` VALUES (1,'frontend',3),(2,'default',3);
/*!40000 ALTER TABLE `boxes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_stacks`
--

DROP TABLE IF EXISTS `cart_stacks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart_stacks` (
  `box` int(11) NOT NULL,
  `cart` int(11) NOT NULL,
  KEY `box` (`box`),
  KEY `cart` (`cart`),
  CONSTRAINT `cart_stacks_ibfk_1` FOREIGN KEY (`box`) REFERENCES `boxes` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `cart_stacks_ibfk_2` FOREIGN KEY (`cart`) REFERENCES `carts` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_stacks`
--

LOCK TABLES `cart_stacks` WRITE;
/*!40000 ALTER TABLE `cart_stacks` DISABLE KEYS */;
INSERT INTO `cart_stacks` VALUES (2,1);
/*!40000 ALTER TABLE `cart_stacks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `carts` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(128) NOT NULL DEFAULT '',
  `URL` text,
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (1,'vagrant',NULL);
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `environments`
--

DROP TABLE IF EXISTS `environments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `environments` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `environments`
--

LOCK TABLES `environments` WRITE;
/*!40000 ALTER TABLE `environments` DISABLE KEYS */;
/*!40000 ALTER TABLE `environments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firewall_rules`
--

DROP TABLE IF EXISTS `firewall_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firewall_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scope_map_id` int(11) NOT NULL,
  `name` varchar(256) NOT NULL,
  `table_type` enum('nat','filter','mangle','raw') NOT NULL,
  `chain` varchar(256) NOT NULL,
  `action` varchar(256) NOT NULL,
  `service` varchar(256) NOT NULL,
  `protocol` varchar(256) NOT NULL,
  `in_subnet_id` int(11) DEFAULT NULL,
  `out_subnet_id` int(11) DEFAULT NULL,
  `flags` varchar(256) DEFAULT NULL,
  `comment` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`(255)),
  KEY `table_type` (`table_type`),
  KEY `scope_map_id` (`scope_map_id`),
  KEY `in_subnet_id` (`in_subnet_id`),
  KEY `out_subnet_id` (`out_subnet_id`),
  CONSTRAINT `firewall_rules_ibfk_1` FOREIGN KEY (`scope_map_id`) REFERENCES `scope_map` (`id`) ON DELETE CASCADE,
  CONSTRAINT `firewall_rules_ibfk_2` FOREIGN KEY (`in_subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `firewall_rules_ibfk_3` FOREIGN KEY (`out_subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firewall_rules`
--

LOCK TABLES `firewall_rules` WRITE;
/*!40000 ALTER TABLE `firewall_rules` DISABLE KEYS */;
INSERT INTO `firewall_rules` VALUES (1,71,'LOOPBACK-NET','filter','INPUT','ACCEPT','all','all',NULL,NULL,'-i lo','Accept all traffic over loopback interface'),(2,72,'SSH','filter','INPUT','ACCEPT','ssh','tcp',NULL,NULL,'-m state --state NEW','Accept all ssh traffic on all networks'),(3,73,'PRIVATE-RELATED','filter','INPUT','ACCEPT','all','all',NULL,NULL,'-m state --state RELATED,ESTABLISHED','Accept related and established connections'),(4,74,'PRIVATE-NET','filter','INPUT','ACCEPT','all','all',1,NULL,NULL,'Accept all traffic on private network'),(5,75,'REJECT-ALL','filter','INPUT','REJECT','all','all',NULL,NULL,NULL,'Block all traffic');
/*!40000 ALTER TABLE `firewall_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firmware`
--

DROP TABLE IF EXISTS `firmware`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firmware` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_id` int(11) NOT NULL,
  `source` varchar(2048) NOT NULL,
  `version` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `hash_alg` varchar(255) NOT NULL DEFAULT 'md5',
  `hash` varchar(2048) NOT NULL,
  `file` varchar(2048) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_model_version` (`model_id`,`version`),
  KEY `version` (`version`),
  CONSTRAINT `firmware_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `firmware_model` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firmware`
--

LOCK TABLES `firmware` WRITE;
/*!40000 ALTER TABLE `firmware` DISABLE KEYS */;
/*!40000 ALTER TABLE `firmware` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firmware_imp`
--

DROP TABLE IF EXISTS `firmware_imp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firmware_imp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firmware_imp`
--

LOCK TABLES `firmware_imp` WRITE;
/*!40000 ALTER TABLE `firmware_imp` DISABLE KEYS */;
INSERT INTO `firmware_imp` VALUES (2,'dell_x1052'),(1,'mellanox');
/*!40000 ALTER TABLE `firmware_imp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firmware_make`
--

DROP TABLE IF EXISTS `firmware_make`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firmware_make` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `version_regex_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`name`),
  KEY `version_regex_id` (`version_regex_id`),
  KEY `name` (`name`),
  CONSTRAINT `firmware_make_ibfk_1` FOREIGN KEY (`version_regex_id`) REFERENCES `firmware_version_regex` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firmware_make`
--

LOCK TABLES `firmware_make` WRITE;
/*!40000 ALTER TABLE `firmware_make` DISABLE KEYS */;
INSERT INTO `firmware_make` VALUES (1,'mellanox',1),(2,'dell',2);
/*!40000 ALTER TABLE `firmware_make` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firmware_mapping`
--

DROP TABLE IF EXISTS `firmware_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firmware_mapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` int(11) NOT NULL,
  `firmware_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_node_firmware` (`node_id`,`firmware_id`),
  KEY `firmware_id` (`firmware_id`),
  CONSTRAINT `firmware_mapping_ibfk_1` FOREIGN KEY (`node_id`) REFERENCES `nodes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `firmware_mapping_ibfk_2` FOREIGN KEY (`firmware_id`) REFERENCES `firmware` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firmware_mapping`
--

LOCK TABLES `firmware_mapping` WRITE;
/*!40000 ALTER TABLE `firmware_mapping` DISABLE KEYS */;
/*!40000 ALTER TABLE `firmware_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firmware_model`
--

DROP TABLE IF EXISTS `firmware_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firmware_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `make_id` int(11) NOT NULL,
  `imp_id` int(11) NOT NULL,
  `version_regex_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_make_model` (`make_id`,`name`),
  KEY `imp_id` (`imp_id`),
  KEY `version_regex_id` (`version_regex_id`),
  KEY `name` (`name`),
  CONSTRAINT `firmware_model_ibfk_1` FOREIGN KEY (`make_id`) REFERENCES `firmware_make` (`id`),
  CONSTRAINT `firmware_model_ibfk_2` FOREIGN KEY (`imp_id`) REFERENCES `firmware_imp` (`id`),
  CONSTRAINT `firmware_model_ibfk_3` FOREIGN KEY (`version_regex_id`) REFERENCES `firmware_version_regex` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firmware_model`
--

LOCK TABLES `firmware_model` WRITE;
/*!40000 ALTER TABLE `firmware_model` DISABLE KEYS */;
INSERT INTO `firmware_model` VALUES (1,'m7800',1,1,NULL),(2,'m6036',1,1,NULL),(3,'x1052-software',2,2,NULL),(4,'x1052-boot',2,2,NULL);
/*!40000 ALTER TABLE `firmware_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firmware_version_regex`
--

DROP TABLE IF EXISTS `firmware_version_regex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firmware_version_regex` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `regex` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `description` varchar(2048) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firmware_version_regex`
--

LOCK TABLES `firmware_version_regex` WRITE;
/*!40000 ALTER TABLE `firmware_version_regex` DISABLE KEYS */;
INSERT INTO `firmware_version_regex` VALUES (1,'mellanox-version-regex','(?:\\d+\\.){2}\\d+','This turns X86_64 3.6.5009 2018-01-02 07:42:21 x86_64 into 3.6.5009'),(2,'x1052-version-regex','(?:\\d+\\.){3}\\d+','This turns 3.0.0.94 ( date  10-Sep-2017 time  22:31:38 ) into 3.0.0.94.');
/*!40000 ALTER TABLE `firmware_version_regex` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ib_memberships`
--

DROP TABLE IF EXISTS `ib_memberships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ib_memberships` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `switch` int(11) NOT NULL,
  `interface` int(11) NOT NULL,
  `part_name` int(11) NOT NULL,
  `member_type` varchar(32) NOT NULL DEFAULT 'limited',
  PRIMARY KEY (`id`),
  KEY `switch` (`switch`,`part_name`,`interface`),
  KEY `interface` (`interface`),
  KEY `part_name` (`part_name`),
  CONSTRAINT `ib_memberships_ibfk_1` FOREIGN KEY (`switch`) REFERENCES `nodes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ib_memberships_ibfk_2` FOREIGN KEY (`interface`) REFERENCES `networks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ib_memberships_ibfk_3` FOREIGN KEY (`part_name`) REFERENCES `ib_partitions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ib_memberships`
--

LOCK TABLES `ib_memberships` WRITE;
/*!40000 ALTER TABLE `ib_memberships` DISABLE KEYS */;
/*!40000 ALTER TABLE `ib_memberships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ib_partitions`
--

DROP TABLE IF EXISTS `ib_partitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ib_partitions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `switch` int(11) NOT NULL,
  `part_key` int(11) NOT NULL,
  `part_name` varchar(128) NOT NULL,
  `options` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `part_name` (`part_name`),
  KEY `switch` (`switch`),
  CONSTRAINT `ib_partitions_ibfk_1` FOREIGN KEY (`switch`) REFERENCES `nodes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ib_partitions`
--

LOCK TABLES `ib_partitions` WRITE;
/*!40000 ALTER TABLE `ib_partitions` DISABLE KEYS */;
/*!40000 ALTER TABLE `ib_partitions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `memberships`
--

DROP TABLE IF EXISTS `memberships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `memberships` (
  `nodeid` int(11) NOT NULL,
  `groupid` int(11) NOT NULL,
  KEY `nodeid` (`nodeid`),
  KEY `groupid` (`groupid`),
  CONSTRAINT `memberships_ibfk_1` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `memberships_ibfk_2` FOREIGN KEY (`groupid`) REFERENCES `groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `memberships`
--

LOCK TABLES `memberships` WRITE;
/*!40000 ALTER TABLE `memberships` DISABLE KEYS */;
/*!40000 ALTER TABLE `memberships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `networks`
--

DROP TABLE IF EXISTS `networks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `networks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node` int(11) NOT NULL,
  `mac` varchar(64) DEFAULT NULL,
  `ip` varchar(32) DEFAULT NULL,
  `netmask` varchar(32) DEFAULT NULL,
  `gateway` varchar(32) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `device` varchar(32) DEFAULT NULL,
  `subnet` int(11) DEFAULT NULL,
  `module` varchar(128) DEFAULT NULL,
  `vlanid` int(11) DEFAULT NULL,
  `options` varchar(128) DEFAULT NULL,
  `channel` varchar(128) DEFAULT NULL,
  `main` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `mac` (`mac`),
  KEY `device` (`device`),
  KEY `node` (`node`),
  KEY `subnet` (`subnet`),
  CONSTRAINT `networks_ibfk_1` FOREIGN KEY (`node`) REFERENCES `nodes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `networks_ibfk_2` FOREIGN KEY (`subnet`) REFERENCES `subnets` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `networks`
--

LOCK TABLES `networks` WRITE;
/*!40000 ALTER TABLE `networks` DISABLE KEYS */;
INSERT INTO `networks` VALUES (1,1,'08:00:27:5e:15:9e','192.168.0.2',NULL,NULL,'cluster-up-frontend','eth1',1,NULL,NULL,NULL,NULL,1),(2,2,'52:54:00:00:00:03','192.168.0.1',NULL,NULL,'backend-0-0','eth1',1,NULL,NULL,NULL,NULL,1),(3,3,'52:54:00:00:00:04','192.168.0.3',NULL,NULL,'backend-0-1','NULL',1,NULL,NULL,NULL,NULL,1),(4,2,'08:00:27:f4:4f:4c',NULL,NULL,NULL,NULL,'eth0',NULL,NULL,NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `networks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nodes`
--

DROP TABLE IF EXISTS `nodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nodes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `appliance` int(11) NOT NULL,
  `box` int(11) NOT NULL,
  `environment` int(11) DEFAULT NULL,
  `rack` varchar(64) NOT NULL,
  `rank` varchar(64) NOT NULL,
  `osaction` int(11) DEFAULT NULL,
  `installaction` int(11) DEFAULT NULL,
  `comment` varchar(140) DEFAULT NULL,
  `metadata` text,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `appliance` (`appliance`),
  KEY `box` (`box`),
  KEY `environment` (`environment`),
  KEY `osaction` (`osaction`),
  KEY `installaction` (`installaction`),
  CONSTRAINT `nodes_ibfk_1` FOREIGN KEY (`appliance`) REFERENCES `appliances` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `nodes_ibfk_2` FOREIGN KEY (`box`) REFERENCES `boxes` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `nodes_ibfk_3` FOREIGN KEY (`environment`) REFERENCES `environments` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `nodes_ibfk_4` FOREIGN KEY (`osaction`) REFERENCES `bootactions` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `nodes_ibfk_5` FOREIGN KEY (`installaction`) REFERENCES `bootactions` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nodes`
--

LOCK TABLES `nodes` WRITE;
/*!40000 ALTER TABLE `nodes` DISABLE KEYS */;
INSERT INTO `nodes` VALUES (1,'cluster-up-frontend',1,2,NULL,'0','0',1,6,NULL,NULL),(2,'backend-0-0',5,2,NULL,'0','0',1,6,NULL,NULL),(3,'backend-0-1',5,2,NULL,'0','1',1,6,NULL,NULL);
/*!40000 ALTER TABLE `nodes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oses`
--

DROP TABLE IF EXISTS `oses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oses` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oses`
--

LOCK TABLES `oses` WRITE;
/*!40000 ALTER TABLE `oses` DISABLE KEYS */;
INSERT INTO `oses` VALUES (1,'redhat'),(3,'sles'),(2,'ubuntu'),(4,'vmware'),(5,'xenserver');
/*!40000 ALTER TABLE `oses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `partitions`
--

DROP TABLE IF EXISTS `partitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `partitions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Node` int(11) NOT NULL,
  `Device` varchar(128) NOT NULL DEFAULT '',
  `Mountpoint` varchar(128) NOT NULL DEFAULT '',
  `UUID` varchar(128) NOT NULL DEFAULT '',
  `SectorStart` varchar(128) NOT NULL DEFAULT '',
  `PartitionSize` varchar(128) NOT NULL DEFAULT '',
  `PartitionID` varchar(128) NOT NULL DEFAULT '',
  `FsType` varchar(128) NOT NULL DEFAULT '',
  `PartitionFlags` varchar(128) NOT NULL DEFAULT '',
  `FormatFlags` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `partitions`
--

LOCK TABLES `partitions` WRITE;
/*!40000 ALTER TABLE `partitions` DISABLE KEYS */;
INSERT INTO `partitions` VALUES (1,2,'sda1','/','c04e9e7c-1ad2-4588-a624-459819adda26','0','16001','','xfs','',''),(2,2,'sda2','swap','06c3bf53-f9be-4a45-8d8e-fc72a5654ab4','0','1004','','swap','',''),(3,2,'sda3','/var','9cff8a29-93c7-4690-ac55-3c589c613156','0','16003','','xfs','',''),(4,2,'sda4','/state/partition1','8c4f19fd-7dec-475f-9f7d-71fad84d3d6f','0','478990','','xfs','',''),(5,3,'sda1','/','b00a8100-1302-4212-b2f1-cf710f3bf4f0','0','16001','','xfs','',''),(6,3,'sda2','swap','53a62ad2-68a1-455c-84e8-b3fa6d7c95df','0','1004','','swap','',''),(7,3,'sda3','/var','e75a0683-1f64-40fd-99c2-375478974d7c','0','16003','','xfs','',''),(8,3,'sda4','/state/partition1','cb37e4fa-23c4-4364-a53e-44118adec06d','0','478990','','xfs','','');
/*!40000 ALTER TABLE `partitions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_keys`
--

DROP TABLE IF EXISTS `public_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_keys` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Node` int(11) NOT NULL,
  `Public_Key` varchar(4096) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_keys`
--

LOCK TABLES `public_keys` WRITE;
/*!40000 ALTER TABLE `public_keys` DISABLE KEYS */;
/*!40000 ALTER TABLE `public_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rolls`
--

DROP TABLE IF EXISTS `rolls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rolls` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(128) NOT NULL DEFAULT '',
  `Version` varchar(32) NOT NULL DEFAULT '',
  `Rel` varchar(32) NOT NULL DEFAULT '',
  `Arch` varchar(32) NOT NULL DEFAULT '',
  `OS` varchar(32) NOT NULL DEFAULT 'sles',
  `URL` text,
  PRIMARY KEY (`ID`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rolls`
--

LOCK TABLES `rolls` WRITE;
/*!40000 ALTER TABLE `rolls` DISABLE KEYS */;
INSERT INTO `rolls` VALUES (1,'stacki','05.03.00.00_20190904_f9950e6','sles12','x86_64','sles','/export/stacki-iso/stacki-05.03.00.00_20190904_f9950e6-sles12.x86_64.disk1.iso'),(2,'SLES','12','sp3','x86_64','sles','/export/installer-iso/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso');
/*!40000 ALTER TABLE `rolls` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `routes`
--

DROP TABLE IF EXISTS `routes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `routes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scope_map_id` int(11) NOT NULL,
  `address` varchar(32) NOT NULL,
  `netmask` varchar(32) NOT NULL,
  `gateway` varchar(32) DEFAULT NULL,
  `subnet_id` int(11) DEFAULT NULL,
  `interface` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `address` (`address`),
  KEY `interface` (`interface`),
  KEY `scope_map_id` (`scope_map_id`),
  KEY `subnet_id` (`subnet_id`),
  CONSTRAINT `routes_ibfk_1` FOREIGN KEY (`scope_map_id`) REFERENCES `scope_map` (`id`) ON DELETE CASCADE,
  CONSTRAINT `routes_ibfk_2` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `routes`
--

LOCK TABLES `routes` WRITE;
/*!40000 ALTER TABLE `routes` DISABLE KEYS */;
INSERT INTO `routes` VALUES (1,67,'224.0.0.0','255.255.255.0',NULL,1,NULL),(2,68,'255.255.255.255','255.255.255.255',NULL,1,NULL);
/*!40000 ALTER TABLE `routes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scope_map`
--

DROP TABLE IF EXISTS `scope_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scope_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scope` enum('global','appliance','os','environment','host') NOT NULL,
  `appliance_id` int(11) DEFAULT NULL,
  `os_id` int(11) DEFAULT NULL,
  `environment_id` int(11) DEFAULT NULL,
  `node_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scope` (`scope`),
  KEY `appliance_id` (`appliance_id`),
  KEY `os_id` (`os_id`),
  KEY `environment_id` (`environment_id`),
  KEY `node_id` (`node_id`),
  CONSTRAINT `scope_map_ibfk_1` FOREIGN KEY (`appliance_id`) REFERENCES `appliances` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `scope_map_ibfk_2` FOREIGN KEY (`os_id`) REFERENCES `oses` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `scope_map_ibfk_3` FOREIGN KEY (`environment_id`) REFERENCES `environments` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `scope_map_ibfk_4` FOREIGN KEY (`node_id`) REFERENCES `nodes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scope_map`
--

LOCK TABLES `scope_map` WRITE;
/*!40000 ALTER TABLE `scope_map` DISABLE KEYS */;
INSERT INTO `scope_map` VALUES (1,'global',NULL,NULL,NULL,NULL),(2,'global',NULL,NULL,NULL,NULL),(3,'global',NULL,NULL,NULL,NULL),(4,'global',NULL,NULL,NULL,NULL),(5,'global',NULL,NULL,NULL,NULL),(6,'global',NULL,NULL,NULL,NULL),(7,'global',NULL,NULL,NULL,NULL),(8,'global',NULL,NULL,NULL,NULL),(9,'global',NULL,NULL,NULL,NULL),(10,'global',NULL,NULL,NULL,NULL),(11,'global',NULL,NULL,NULL,NULL),(12,'global',NULL,NULL,NULL,NULL),(13,'global',NULL,NULL,NULL,NULL),(14,'global',NULL,NULL,NULL,NULL),(15,'global',NULL,NULL,NULL,NULL),(16,'global',NULL,NULL,NULL,NULL),(17,'global',NULL,NULL,NULL,NULL),(18,'global',NULL,NULL,NULL,NULL),(19,'global',NULL,NULL,NULL,NULL),(20,'global',NULL,NULL,NULL,NULL),(21,'global',NULL,NULL,NULL,NULL),(22,'global',NULL,NULL,NULL,NULL),(23,'global',NULL,NULL,NULL,NULL),(24,'global',NULL,NULL,NULL,NULL),(25,'global',NULL,NULL,NULL,NULL),(26,'global',NULL,NULL,NULL,NULL),(27,'global',NULL,NULL,NULL,NULL),(28,'global',NULL,NULL,NULL,NULL),(29,'global',NULL,NULL,NULL,NULL),(30,'global',NULL,NULL,NULL,NULL),(31,'global',NULL,NULL,NULL,NULL),(32,'global',NULL,NULL,NULL,NULL),(35,'appliance',1,NULL,NULL,NULL),(36,'appliance',1,NULL,NULL,NULL),(37,'appliance',1,NULL,NULL,NULL),(40,'appliance',2,NULL,NULL,NULL),(41,'appliance',2,NULL,NULL,NULL),(42,'appliance',2,NULL,NULL,NULL),(45,'appliance',3,NULL,NULL,NULL),(46,'appliance',3,NULL,NULL,NULL),(47,'appliance',3,NULL,NULL,NULL),(50,'appliance',4,NULL,NULL,NULL),(51,'appliance',4,NULL,NULL,NULL),(54,'appliance',5,NULL,NULL,NULL),(55,'appliance',5,NULL,NULL,NULL),(56,'appliance',5,NULL,NULL,NULL),(59,'appliance',6,NULL,NULL,NULL),(60,'appliance',6,NULL,NULL,NULL),(61,'appliance',6,NULL,NULL,NULL),(62,'appliance',6,NULL,NULL,NULL),(65,'appliance',7,NULL,NULL,NULL),(66,'appliance',7,NULL,NULL,NULL),(67,'global',NULL,NULL,NULL,NULL),(68,'global',NULL,NULL,NULL,NULL),(69,'global',NULL,NULL,NULL,NULL),(70,'appliance',1,NULL,NULL,NULL),(71,'global',NULL,NULL,NULL,NULL),(72,'global',NULL,NULL,NULL,NULL),(73,'global',NULL,NULL,NULL,NULL),(74,'global',NULL,NULL,NULL,NULL),(75,'global',NULL,NULL,NULL,NULL),(76,'global',NULL,NULL,NULL,NULL),(77,'global',NULL,NULL,NULL,NULL),(78,'global',NULL,NULL,NULL,NULL),(79,'global',NULL,NULL,NULL,NULL),(80,'host',NULL,NULL,NULL,2),(81,'host',NULL,NULL,NULL,2),(82,'host',NULL,NULL,NULL,3),(83,'host',NULL,NULL,NULL,3),(90,'host',NULL,NULL,NULL,2),(91,'host',NULL,NULL,NULL,2),(92,'host',NULL,NULL,NULL,2),(99,'host',NULL,NULL,NULL,3),(100,'host',NULL,NULL,NULL,3),(101,'host',NULL,NULL,NULL,3);
/*!40000 ALTER TABLE `scope_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stacks`
--

DROP TABLE IF EXISTS `stacks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stacks` (
  `box` int(11) NOT NULL,
  `roll` int(11) NOT NULL,
  KEY `box` (`box`),
  KEY `roll` (`roll`),
  CONSTRAINT `stacks_ibfk_1` FOREIGN KEY (`box`) REFERENCES `boxes` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `stacks_ibfk_2` FOREIGN KEY (`roll`) REFERENCES `rolls` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stacks`
--

LOCK TABLES `stacks` WRITE;
/*!40000 ALTER TABLE `stacks` DISABLE KEYS */;
INSERT INTO `stacks` VALUES (2,1),(1,1),(2,2);
/*!40000 ALTER TABLE `stacks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storage_controller`
--

DROP TABLE IF EXISTS `storage_controller`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `storage_controller` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scope_map_id` int(11) NOT NULL,
  `enclosure` int(11) NOT NULL,
  `adapter` int(11) NOT NULL,
  `slot` int(11) NOT NULL,
  `raidlevel` varchar(16) NOT NULL,
  `arrayid` int(11) NOT NULL,
  `options` varchar(512) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `enclosure` (`enclosure`,`adapter`,`slot`),
  KEY `scope_map_id` (`scope_map_id`),
  CONSTRAINT `storage_controller_ibfk_1` FOREIGN KEY (`scope_map_id`) REFERENCES `scope_map` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storage_controller`
--

LOCK TABLES `storage_controller` WRITE;
/*!40000 ALTER TABLE `storage_controller` DISABLE KEYS */;
INSERT INTO `storage_controller` VALUES (1,76,-1,-1,-1,'0',-2,'');
/*!40000 ALTER TABLE `storage_controller` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storage_partition`
--

DROP TABLE IF EXISTS `storage_partition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `storage_partition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scope_map_id` int(11) NOT NULL,
  `device` varchar(128) NOT NULL,
  `mountpoint` varchar(128) DEFAULT NULL,
  `size` int(11) NOT NULL,
  `fstype` varchar(128) DEFAULT NULL,
  `partid` int(11) NOT NULL,
  `options` varchar(512) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `device` (`device`),
  KEY `mountpoint` (`mountpoint`),
  KEY `device_2` (`device`,`mountpoint`),
  KEY `scope_map_id` (`scope_map_id`),
  CONSTRAINT `storage_partition_ibfk_1` FOREIGN KEY (`scope_map_id`) REFERENCES `scope_map` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storage_partition`
--

LOCK TABLES `storage_partition` WRITE;
/*!40000 ALTER TABLE `storage_partition` DISABLE KEYS */;
/*!40000 ALTER TABLE `storage_partition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subnets`
--

DROP TABLE IF EXISTS `subnets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subnets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `zone` varchar(255) NOT NULL,
  `address` varchar(32) NOT NULL,
  `mask` varchar(32) NOT NULL,
  `gateway` varchar(32) DEFAULT NULL,
  `mtu` int(11) DEFAULT '1500',
  `dns` tinyint(1) DEFAULT '0',
  `pxe` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `name_2` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subnets`
--

LOCK TABLES `subnets` WRITE;
/*!40000 ALTER TABLE `subnets` DISABLE KEYS */;
INSERT INTO `subnets` VALUES (1,'private','','192.168.0.0','255.255.255.0','10.0.2.2',1500,0,1);
/*!40000 ALTER TABLE `subnets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `switchports`
--

DROP TABLE IF EXISTS `switchports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `switchports` (
  `interface` int(11) NOT NULL,
  `switch` int(11) NOT NULL,
  `port` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `switchports`
--

LOCK TABLES `switchports` WRITE;
/*!40000 ALTER TABLE `switchports` DISABLE KEYS */;
/*!40000 ALTER TABLE `switchports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `Scope` enum('box','cart','network','pallet') DEFAULT NULL,
  `Tag` varchar(128) NOT NULL,
  `Value` text,
  `ScopeID` int(11) DEFAULT NULL,
  KEY `Scope` (`Scope`),
  KEY `Tag` (`Tag`),
  KEY `ScopeID` (`ScopeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;
