-- Report tables that were not updated recently
-- They may contain archive data or the script that updates it broke.
--
-- https://github.com/macbre/index-digest/issues/28
DROP TABLE IF EXISTS `0028_data_not_updated_recently`;
CREATE TABLE `0028_data_not_updated_recently` (
    `item_id` int(8) unsigned NOT NULL AUTO_INCREMENT,
    `cnt` int(8) unsigned NOT NULL,
     `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
     PRIMARY KEY (`item_id`)
) ENGINE=InnoDB;

-- table with old data (6 months old)
INSERT INTO 0028_data_not_updated_recently(cnt, `timestamp`) VALUES
    (20, NOW() - INTERVAL 50 DAY),
    (20, NOW() - INTERVAL 45 DAY),
    (20, NOW() - INTERVAL 40 DAY);
