CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(128),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
ALTER TABLE locations ADD user_id INT NOT NULL;
ALTER TABLE notes ADD user_id INT NOT NULL;
