-- Detect redundant indices
--
-- https://github.com/macbre/index-digest/issues/4
DROP TABLE IF EXISTS `0004-id-foo`;
CREATE TABLE `0004-id-foo` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varbinary(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`,`foo`),
	UNIQUE KEY `idx` (`id`,`foo`)
);

DROP TABLE IF EXISTS `0004-id-foo-bar`;
CREATE TABLE `0004-id-foo-bar` (
	`id` int(9) NOT NULL AUTO_INCREMENT,
	`foo` varbinary(16) NOT NULL DEFAULT '',
	`bar` varbinary(16) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`),
	KEY `idx_foo` (`foo`),
	KEY `idx_foo_bar` (`foo`, `bar`),
	KEY `idx_id_foo` (`id`, `foo`)
);

