-- Report tables with a generic primary key (id)
--
-- https://github.com/macbre/index-digest/issues/94
DROP TABLE IF EXISTS `0094_generic_primary_key`;
CREATE TABLE `0094_generic_primary_key` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varchar(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `0094_generic_primary_key_id_as_column`;
CREATE TABLE `0094_generic_primary_key_id_as_column` (
	`foo` int(9) NOT NULL AUTO_INCREMENT,
	`id` varchar(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`foo`)
);

DROP TABLE IF EXISTS `0094_non_generic_primary_key`;
CREATE TABLE `0094_non_generic_primary_key` (
	`row_id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varchar(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`row_id`)
);
