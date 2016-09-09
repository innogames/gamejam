DROP TABLE IF EXISTS `jam_photo`;
CREATE TABLE `jam_photo` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `jam_id` INT(11) NOT NULL,
    `photo` LONGBLOB DEFAULT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `jp_jfk_1` FOREIGN KEY (`jam_id`) REFERENCES `jam` (`id`)
)
    ENGINE = InnoDB
    DEFAULT CHARSET = utf8;
