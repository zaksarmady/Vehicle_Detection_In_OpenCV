CREATE DATABASE `TrafficProj`;
USE `TrafficProj`;

/*Create Street Record Table*/
CREATE TABLE `STREETS` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(40),
	`suburb` VARCHAR(40),
	`length` INT,
	`width` INT,
	PRIMARY KEY (`id`)
);