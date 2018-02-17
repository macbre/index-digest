-- Report tables with "test" word in their name
--
-- https://github.com/macbre/index-digest/issues/75
DROP TABLE IF EXISTS `0075_some_guy_test_table`;
CREATE TABLE `0075_some_guy_test_table` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	PRIMARY KEY (`item_id`)
) CHARSET=utf8;
