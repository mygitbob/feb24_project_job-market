DROP DATABASE IF EXISTS jobmarket;
CREATE DATABASE jobmarket;

\c jobmarket

CREATE TABLE IF NOT EXISTS job_title (
            jt_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_job_title UNIQUE (name)
        );

CREATE TABLE IF NOT EXISTS currency (
            c_id SERIAL PRIMARY KEY,
            symbol VARCHAR(3) NOT NULL, -- when we have no symbol we can use a 3 char abbreviation
            name VARCHAR(50),
            CONSTRAINT unique_currency UNIQUE (symbol)
        );

CREATE TABLE IF NOT EXISTS experience (
            e_id SERIAL PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            CONSTRAINT unique_experience UNIQUE (level)
        );

CREATE TABLE IF NOT EXISTS location (
            l_id SERIAL PRIMARY KEY,
            country VARCHAR(50) NOT NULL,
            region VARCHAR(50),
            city VARCHAR(50),
            city_district VARCHAR(50),
            area_code VARCHAR(50),
            state VARCHAR(50),
            CONSTRAINT unique_location_tuple UNIQUE (country, region, city, city_district, area_code, state)  -- change contraint to : ... UNIQUE NULLS NOT DISTINCT ...
        );

CREATE TABLE IF NOT EXISTS data_source (
            ds_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_data_source UNIQUE (name)
        );

CREATE TABLE IF NOT EXISTS skill_list (
            sl_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_skill_name UNIQUE (name)
        );

CREATE TABLE IF NOT EXISTS job_category (
            jc_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_job_category UNIQUE (name)
        );

CREATE TABLE IF NOT EXISTS job_offer (
            jo_id SERIAL PRIMARY KEY,
            source_id VARCHAR NOT NULL,
            published DATE NOT NULL,
            salary_min INT NOT NULL,
            salary_max INT NOT NULL,
            joboffer_url VARCHAR NOT NULL,
            job_title_id INT NOT NULL REFERENCES job_title(jt_id),
            currency_id INT NOT NULL REFERENCES currency(c_id),
            location_id INT NOT NULL REFERENCES location(l_id),
            data_source_id INT NOT NULL REFERENCES data_source(ds_id),
            experience_id INT REFERENCES experience(e_id),
            CONSTRAINT unique_data_source_id UNIQUE (source_id, data_source_id),
            CONSTRAINT unique_joboffer UNIQUE (joboffer_url)
        );

CREATE TABLE IF NOT EXISTS job_to_skills (
            job_id INT REFERENCES job_offer(jo_id),
            skill_id INT REFERENCES skill_list(sl_id),
            PRIMARY KEY (job_id, skill_id)
        );

CREATE TABLE IF NOT EXISTS job_to_categories (
            job_id INT REFERENCES job_offer(jo_id),
            cat_id INT REFERENCES job_category(jc_id),
            PRIMARY KEY (job_id, cat_id)
        );


