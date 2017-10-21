-- Tables for core tests of Database class
DROP TABLE IF EXISTS `0000_the_table`;
CREATE TABLE `0000_the_table` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varchar(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`,`foo`),
	UNIQUE KEY `idx` (`id`,`foo`)
);

INSERT INTO 0000_the_table VALUES(1, 'test'), (2, 'foo'), (3, 'bar');
