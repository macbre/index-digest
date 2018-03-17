-- Report MyISAM tables and suggest to use InndDB
--
-- https://github.com/macbre/index-digest/issues/36
DROP TABLE IF EXISTS `0036_use_innodb_myisam`;
CREATE TABLE `0036_use_innodb_myisam` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` int(8),
	PRIMARY KEY (`item_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `0036_use_innodb`;
CREATE TABLE `0036_use_innodb` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` int(8),
	PRIMARY KEY (`item_id`)
);
