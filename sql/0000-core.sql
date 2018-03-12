-- Tables for core tests of Database class
DROP TABLE IF EXISTS `0000_the_table`;
CREATE TABLE `0000_the_table` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varchar(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`item_id`,`foo`),
	KEY `idx_foo` (`foo`)
) CHARACTER SET utf8;

INSERT INTO 0000_the_table VALUES(1, 'test'), (2, 'foo'), (3, 'foo ąęź');

-- handle dashes in table names
DROP TABLE IF EXISTS `0000_the_table-metadata`;
CREATE TABLE `0000_the_table-metadata` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varchar(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`item_id`,`foo`),
	KEY `idx_foo` (`foo`)
) CHARACTER SET utf8;

INSERT INTO `0000_the_table-metadata` VALUES(1, 'test'), (2, 'foo'), (3, 'foo ąęź'), (4, 'foo');

-- handle views, actually ignore them :)
DROP VIEW IF EXISTS `0000_the_view`;
CREATE VIEW 0000_the_view AS SELECT foo, COUNT(*) AS cnt FROM `0000_the_table-metadata` GROUP BY foo;
