-- Report not used indices
--
-- https://github.com/macbre/index-digest/issues/2
DROP TABLE IF EXISTS `0002_not_used_indices`;
CREATE TABLE `0002_not_used_indices` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varchar(16) NOT NULL DEFAULT '',
	`test` varchar(16) NOT NULL DEFAULT '',
	`bar` varchar(16),
	PRIMARY KEY (`id`),
	KEY `test_id_idx` (`test`, `id`),
	KEY `foo_id_idx` (`foo`, `id`)
);

INSERT INTO 0002_not_used_indices VALUES
    (NULL, 'test', '', NULL),
    (NULL, 'foo', 'test', NULL),
    (NULL, 'foo', '', NULL);
