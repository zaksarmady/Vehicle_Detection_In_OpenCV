CREATE TABLE `EVENTS` (
	`eventID` INT NOT NULL AUTO_INCREMENT,
	`recorded` DATETIME,
	`timeCaptured` time(6),
	`entered` time(6),
	`exited` time(6),
	`full` BOOLEAN,
	`numFactors` INT,
	`streetID` INT,
	FOREIGN KEY (`streetID`) REFERENCES STREETS (`id`),
	PRIMARY KEY (`eventID`)
);