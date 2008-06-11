drop table locations_datasources;

CREATE TABLE locations_datasources (
    id INT NOT NULL AUTO_INCREMENT,
    datasource_id INT DEFAULT NULL,
    location_id INT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
