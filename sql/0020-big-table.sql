-- Report queries that use filesort or temporary file
--
-- https://github.com/macbre/index-digest/issues/20
DROP TABLE IF EXISTS `0020_big_table`;
CREATE TABLE `0020_big_table` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`val` int(9) NOT NULL,
	PRIMARY KEY (`id`)
);
