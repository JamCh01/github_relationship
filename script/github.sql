-- 导出 github 的数据库结构
DROP DATABASE IF EXISTS `github`;
CREATE DATABASE IF NOT EXISTS `github` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `github`;

-- 导出  表 github.relationship 结构
DROP TABLE IF EXISTS `relationship`;
CREATE TABLE IF NOT EXISTS `relationship` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(256) CHARACTER SET latin1 NOT NULL DEFAULT '0',
  `level` varchar(256) CHARACTER SET latin1 NOT NULL DEFAULT '0',
  `referer` varchar(256) CHARACTER SET latin1 NOT NULL DEFAULT '0',
  `type` varchar(256) CHARACTER SET latin1 NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_name` (`user_name`),
  KEY `level` (`level`),
  KEY `referer` (`referer`),
  KEY `type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='github_relationship的MariaDB实现';