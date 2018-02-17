-- Report missing primary or unique keys
--
-- https://github.com/macbre/index-digest/issues/34
DROP TABLE IF EXISTS `0034_with_primary_key`;
CREATE TABLE `0034_with_primary_key` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	PRIMARY KEY (`item_id`)
) CHARSET=utf8;

DROP TABLE IF EXISTS `0034_with_unique_key`;
CREATE TABLE `0034_with_unique_key` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	UNIQUE KEY idx (`item_id`)
) CHARSET=utf8;

-- https://github.com/Wikia/app/pull/9863
DROP TABLE IF EXISTS `0034_querycache`;
CREATE TABLE `0034_querycache` (
  `qc_type` varbinary(32) NOT NULL,
  `qc_value` int(10) unsigned NOT NULL DEFAULT '0',
  `qc_namespace` int(11) NOT NULL DEFAULT '0',
  `qc_title` varchar(255) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL DEFAULT '',
  KEY `qc_type` (`qc_type`,`qc_value`)
) CHARSET=utf8;
