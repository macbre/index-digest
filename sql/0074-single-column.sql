-- Report tables with just a single column
--
-- https://github.com/macbre/index-digest/issues/74
DROP TABLE IF EXISTS `0074_bag_of_ints`;
CREATE TABLE `0074_bag_of_ints` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (`id`)
) CHARSET=utf8;
