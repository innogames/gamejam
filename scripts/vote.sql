DROP TABLE IF EXISTS `vote`;
CREATE TABLE `vote` (
  `id`       INT(11) NOT NULL AUTO_INCREMENT,
  `game_id`  INT(11)          DEFAULT NULL,
  `jam_id`   INT(11)          DEFAULT NULL,
  `user_id`  INT(11)          DEFAULT NULL,
  `voted_at` DATETIME         DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `game_id` (`game_id`),
  KEY `jam_id` (`jam_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `vote_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `game` (`id`),
  CONSTRAINT `vote_ibfk_2` FOREIGN KEY (`jam_id`) REFERENCES `jam` (`id`),
  CONSTRAINT `vote_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = latin1;
