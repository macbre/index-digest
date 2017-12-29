-- Report queries using INSERT IGNORE
--
-- https://github.com/macbre/index-digest/issues/70
-- https://medium.com/legacy-systems-diary/things-to-avoid-episode-1-insert-ignore-535b4c24406b
DROP TABLE IF EXISTS `0070_insert_ignore`;
CREATE TABLE `0070_insert_ignore` (
	`id` int(9) NOT NULL,
	`text` char(5) NOT NULL,
	`time` DATETIME,
	UNIQUE KEY (`id`)
) CHARSET=utf8;
