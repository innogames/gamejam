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