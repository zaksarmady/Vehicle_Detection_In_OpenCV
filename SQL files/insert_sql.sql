/*Examples*/

/*Street Entries*/
INSERT INTO STREETS (name, suburb, length, width)
VALUES ('Burwood Road', 'Hawthorn', 371, 14);

INSERT INTO STREETS (name, suburb, length, width)
VALUES ('Atkinson St', 'Chadstone', null, null);

/*Event Entries (Automated)*/
INSERT INTO EVENTS (recorded, entered, exited, full, numFactors, streetID)
VALUES ('2021-01-01 12:00:00', 3, 5, true, 5, 1);

INSERT INTO EVENTS (recorded, entered, exited, full, numFactors, streetID)
VALUES ('2021-09-04 17:39:28.298464', 0.033367, 2.302300, false, 5, 2);