-- Report queries that use filesort or temporary file
--
-- https://github.com/macbre/index-digest/issues/20
DROP TABLE IF EXISTS `0020_big_table`;
CREATE TABLE `0020_big_table` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`val` int(9) NOT NULL,
	`text` char(5) NOT NULL,
	`num` int(3) NOT NULL,
	PRIMARY KEY (`item_id`),
	KEY text_idx (`text`),
	KEY num_idx (`num`) -- low cardinality (#31)
) CHARSET=utf8;
