-- docker cp populate_dummy_db.sql jobmarket-postgres:/populate_dummy_db.sql
-- docker exec -it jobmarket-postgres psql -U postgres -d dummy_db -f /populate_dummy_db.sql

-- dummy data from csv (can also be a json, this is just shorter)
-- elm1-5 should be list elements, this is a simplified example:
-- csv content:
-- measure1,measure2,attribute1,attribute2,elm1,elm2,elm3,elm4,elm5
-- 111,112,11a,11b,21elm,22elm,23elm,,
-- 211,212,12a,12b,24elm,25elm,,,
-- this example shows what steps must be done for each entry

-- 1st entry

-- insert dim1 data, 1-n relation to fact
INSERT INTO dimension_1 (attribute1, attribute2)
VALUES
    ('11a', '11b');
	
-- insert dim2 data, list of entries to be linked with fact (n-m relation)
INSERT INTO dimension_2 (list_element)
VALUES
    ('21elm'),
    ('22elm'),
    ('23elm');
	
-- insert fact data
INSERT INTO fact_table (measure1, measure2)
VALUES
    (111, 112);

-- add link to dim1	
UPDATE fact_table
SET dimension1_id = d.dimension1_id
FROM dimension_1 d
WHERE d.attribute1 = '11a' AND d.attribute2 = '11b';

-- 2nd entry

-- insert dim1 data, 1-n relation to fact
INSERT INTO dimension_1 (attribute1, attribute2)
VALUES
	('12a', '12b');
	
-- insert dim2 data, list of entries to be linked with fact (n-m relation)
INSERT INTO dimension_2 (list_element)
VALUES
	('24elm'),
    ('25elm');
	
-- insert fact data
INSERT INTO fact_table (measure1, measure2)
VALUES
	(211, 212);
	
-- add link to dim1
UPDATE fact_table
SET dimension1_id = d.dimension1_id
FROM dimension_1 d
WHERE d.attribute1 = '12a' AND d.attribute2 = '12b';

-- after all entries a re done, link fact and dim2 (n-m relation)
INSERT INTO link_table (fact_id, dimension2_id)
SELECT f.fact_id, d.dimension2_id
FROM fact_table f
CROSS JOIN dimension_2 d;


-- show inserted data, run from psql to view
SELECT f.*, d1.attribute1, d1.attribute2, d2.list_element
FROM fact_table f
JOIN dimension_1 d1 ON f.dimension1_id = d1.dimension1_id
JOIN link_table lt ON f.fact_id = lt.fact_id
JOIN dimension_2 d2 ON lt.dimension2_id = d2.dimension2_id;