DROP TABLE IF EXISTS `gamescom_application`;
CREATE TABLE `gamescom_application` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) DEFAULT NULL,
    `city` VARCHAR(128) DEFAULT NULL,
    `zip_code` VARCHAR(128) DEFAULT NULL,
    `street` VARCHAR(128) DEFAULT NULL,
    `job_title` VARCHAR(128) DEFAULT NULL,
    `year` INT(11) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `gcapplication_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
)
    ENGINE = InnoDB
    DEFAULT CHARSET = utf8;

ALTER TABLE gamescom_application ADD COLUMN `country` VARCHAR(128) DEFAULT NULL AFTER `city`;
ALTER TABLE gamescom_application ADD COLUMN `experience` VARCHAR(128) DEFAULT NULL AFTER `job_title`;
ALTER TABLE gamescom_application ADD COLUMN `title` VARCHAR(128) DEFAULT NULL AFTER `user_id`;

ALTER TABLE gamescom_application ADD COLUMN `travel_funding_amount` INT(11) DEFAULT NULL AFTER `year`;
ALTER TABLE gamescom_application ADD COLUMN `travel_funding_reason` VARCHAR(255) DEFAULT NULL AFTER `travel_funding_amount`;
ALTER TABLE gamescom_application ADD COLUMN `reason` VARCHAR(255) DEFAULT NULL AFTER `experience`;
