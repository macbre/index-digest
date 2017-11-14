-- Detect redundant indices
--
-- https://github.com/macbre/index-digest/issues/4
DROP TABLE IF EXISTS `0004_id_foo`;
CREATE TABLE `0004_id_foo` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varbinary(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`,`foo`),
	UNIQUE KEY `idx` (`id`,`foo`)
);

DROP TABLE IF EXISTS `0004_id_foo_bar`;
CREATE TABLE `0004_id_foo_bar` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varbinary(16) NOT NULL DEFAULT '',
	`bar` varbinary(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`),
	KEY `idx_foo` (`foo`),
	KEY `idx_foo_bar` (`foo`, `bar`),
	KEY `idx_id_foo` (`id`, `foo`)
);

-- https://github.com/macbre/index-digest/issues/48
DROP TABLE IF EXISTS `0004_indices_duplicating_each_other`;
CREATE TABLE `0004_indices_duplicating_each_other` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varbinary(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`),
	UNIQUE KEY `idx_foo` (`foo`),
	UNIQUE KEY `idx_foo_2` (`foo`)
);

-- https://github.com/macbre/index-digest/issues/49
DROP TABLE IF EXISTS `0004_image_comment_temp`;
CREATE TABLE /*_*/0004_image_comment_temp (
  -- Key to img_name (ugh)
  imgcomment_name varchar(255) binary NOT NULL,
  -- Key to comment_id
  imgcomment_description_id bigint unsigned NOT NULL,
  PRIMARY KEY (imgcomment_name, imgcomment_description_id)
) /*$wgDBTableOptions*/;
-- Ensure uniqueness
CREATE UNIQUE INDEX /*i*/imgcomment_name ON /*_*/0004_image_comment_temp (imgcomment_name);
