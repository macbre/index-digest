-- Report tables that have really old data
-- Worth checking if such long data retention is actually needed
--
-- https://github.com/macbre/index-digest/issues/28
DROP TABLE IF EXISTS `0028_data_too_old`;
CREATE TABLE `0028_data_too_old` (
    `item_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
    `cnt` int(8) unsigned NOT NULL,
     `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
     PRIMARY KEY (`item_id`)
) ENGINE=InnoDB;


-- table with old data (6 months old)
INSERT INTO 0028_data_too_old VALUES
    (1, 12, NOW() - INTERVAL 6 MONTH),
    (2, 20, NOW() - INTERVAL 3 MONTH),
    (3, 42, NOW());

INSERT INTO 0028_data_too_old(cnt) VALUES
    (52);


-- table with no old data
DROP TABLE IF EXISTS `0028_data_ok`;
CREATE TABLE `0028_data_ok` LIKE `0028_data_too_old`;

INSERT INTO 0028_data_ok(cnt, `timestamp`) VALUES
    (1, NOW() - INTERVAL 7 DAY);


-- empty tables should be simply ignored
DROP TABLE IF EXISTS `0028_data_empty`;
CREATE TABLE `0028_data_empty` LIKE `0028_data_too_old`;

-- table with no time columns
DROP TABLE IF EXISTS `0028_no_time`;
CREATE TABLE `0028_no_time` (
    `item_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
    `cnt` int(8) unsigned NOT NULL,
     PRIMARY KEY (`item_id`)
) ENGINE=InnoDB;
