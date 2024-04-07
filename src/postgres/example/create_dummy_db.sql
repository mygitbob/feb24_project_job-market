-- first the database has to be created
-- log in dcoker container into psql
-- CREATE DATABASE dummy_db;
-- file has to be inside the container
-- docker cp create_dummy_db.sql jobmarket-postgres:/create_dummy_db.sql
-- docker exec -it jobmarket-postgres psql -U postgres -d dummy_db -f /create_dummy_db.sql
\c dummy_db;

DROP TABLE IF EXISTS dimension_1;
CREATE TABLE dimension_1 (
    dimension1_id SERIAL PRIMARY KEY,
    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255)
);

DROP TABLE IF EXISTS dimension_2;
CREATE TABLE dimension_2 (
    dimension2_id SERIAL PRIMARY KEY,
    list_element VARCHAR(255)
);

-- table has to be created after dimension_1 because of foreign key constraint
DROP TABLE IF EXISTS fact_table;
CREATE TABLE fact_table (
    fact_id SERIAL PRIMARY KEY,
    dimension1_id INT,
    measure1 INT,
    measure2 INT,
	FOREIGN KEY (dimension1_id) REFERENCES dimension_1(dimension1_id)
);

DROP TABLE IF EXISTS link_table;
CREATE TABLE link_table (
    fact_id INT,
    dimension2_id INT,
    PRIMARY KEY (fact_id, dimension2_id),
    FOREIGN KEY (fact_id) REFERENCES fact_table(fact_id),
    FOREIGN KEY (dimension2_id) REFERENCES dimension_2(dimension2_id)
);