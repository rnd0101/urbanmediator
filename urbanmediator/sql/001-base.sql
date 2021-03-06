CREATE TABLE locations (
    id INT NOT NULL AUTO_INCREMENT,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    title VARCHAR(64),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE notes (
    id INT NOT NULL AUTO_INCREMENT,
    location_id INT,
    text TEXT NOT NULL,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
