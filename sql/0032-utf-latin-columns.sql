-- Report text columns that use non-utf collation
--
-- https://github.com/macbre/index-digest/issues/32
DROP TABLE IF EXISTS `0032_utf8_table`;
CREATE TABLE `0032_utf8_table` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	`latin_column` varchar(255) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL,
	`big5_column` varchar(255) CHARACTER SET big5,
	`utf_blob` blob,
	PRIMARY KEY (`item_id`)
) CHARSET=utf8 COLLATE=utf8_polish_ci;

DROP TABLE IF EXISTS `0032_latin1_table`;
CREATE TABLE `0032_latin1_table` (
	`item_id` int(9) NOT NULL AUTO_INCREMENT,
	`name` varchar(255),
	`utf8_column` varchar(255) CHARACTER SET utf8 COLLATE utf8_polish_ci NOT NULL,
	`ucs2_column` varchar(255) CHARACTER SET ucs2,
	`utf8mb4_column` varchar(255) CHARACTER SET utf8mb4,
	`utf16_column` varchar(255) CHARACTER SET utf16,
	`utf16le_column` varchar(255) CHARACTER SET utf16le,
	`utf32_column` varchar(255) CHARACTER SET utf32,
	`binary_column` varchar(255) CHARACTER SET binary,
	`latin_blob` blob,
	PRIMARY KEY (`item_id`)
) CHARSET=latin1;
