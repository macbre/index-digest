-- Report empty tables
--
-- https://github.com/macbre/index-digest/issues/89
DROP TABLE IF EXISTS `0089_empty_table`;
CREATE TABLE `0089_empty_table` (
    `id` int(9) NOT NULL AUTO_INCREMENT,
    `foo` int(9),
	PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `0089_not_empty_table`;
CREATE TABLE `0089_not_empty_table` (
    `id` int(9) NOT NULL AUTO_INCREMENT,
    `foo` int(9) DEFAULT 0,
	PRIMARY KEY (`id`)
);

INSERT INTO 0089_not_empty_table VALUES (1, NULL), (2, 5), (42, 56);
