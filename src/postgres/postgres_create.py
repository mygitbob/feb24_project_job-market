import psycopg2 as psy

from postgres_initdb import connect_to_database, POSTGRES_DBNAME, logging


def create_dim_tables(cur):
    """
    Creates the dimesion tables of the database, see DataModel in report

    Args:
        cur     = database cursor object
    Returns:
        None
    """

    _create_job_title_table(cur)
    _create_currency_table(cur)
    _create_experience_table(cur)
    _create_location_table(cur)
    _create_data_source_table(cur)
    _create_skill_list_table(cur)
    _create_job_category_table(cur)


def _create_job_title_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_title (
            jt_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_job_title UNIQUE (name)
        );
    """)


def _create_currency_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS currency (
            c_id SERIAL PRIMARY KEY,
            symbol VARCHAR(3) NOT NULL, -- when we have no symbol we can use a 3 char abbreviation
            name VARCHAR(50),
            CONSTRAINT unique_currency UNIQUE (symbol)
        );
    """)


def _create_experience_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experience (
            e_id SERIAL PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            CONSTRAINT unique_experience UNIQUE (level)
        );
    """)


def _create_location_table(cur):
    cur.execute("""
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
    """)


def _create_data_source_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data_source (
            ds_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_data_source UNIQUE (name)
        );
    """)


def _create_skill_list_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skill_list (
            sl_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_skill_name UNIQUE (name)
        );
    """)


def _create_job_category_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_category (
            jc_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT unique_job_category UNIQUE (name)
        );
    """)


def create_fact_table(cur):
    """
    Creates the fact table of the database, see DataModel in report

    Args:
        cur     = database cursor object
    Returns:
        None
    """

    cur.execute("""
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
            CONSTRAINT unique_source UNIQUE (source_id, joboffer_url),
            CONSTRAINT unique_job_details UNIQUE (published, job_title_id, location_id, data_source_id)
        )
    """)


def create_link_tables(cur):
    """
    Creates the link tables of the database, see DataModel in report

    Args:
        cur     = database cursor object
    Returns:
        None
    """

    # link job offers to skills
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_to_skills (
            job_id INT REFERENCES job_offer(jo_id),
            skill_id INT REFERENCES skill_list(sl_id),
            PRIMARY KEY (job_id, skill_id)
        )
    """)

    # link job offers to job categories
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_to_categories (
            job_id INT REFERENCES job_offer(jo_id),
            cat_id INT REFERENCES job_category(jc_id),
            PRIMARY KEY (job_id, cat_id)
        )
    """)


def create_tables(cur, drop):
    """
    Creates all tables of the database, see DataModel in report
    The order of creation matters, first dimension then fact and finally link tables
    
    Args:
        cur                 = database cursor object
        drop : boolean      = drop tables ?
    Returns:
        None
    """
    if drop:
        drop_all_tables(cur)
    create_dim_tables(cur)
    create_fact_table(cur)
    create_link_tables(cur)


def drop_all_tables(cur):
    """
    Deletes all tables of the database

    Args:
        cur     = database cursor object
    Returns:
        None
    """
    

    # get all table names
    cur.execute("""
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname='public'
    """)
    tables = cur.fetchall()

    # drop each table
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE")
        logging.debug(f"{__file__}: Dropped table: {table[0]}")


def create_db(dbname=POSTGRES_DBNAME):
    """
    Creates a databse in postgres
    We have to first connect to db 'postgres' and then we can create our own
    Args:
        dbname : str    = name of our databse, comes from import POSTGRES_DBNAME
    Returns:
        None
    """
    try:
        conn = connect_to_database("postgres") 
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute(f'CREATE DATABASE {dbname}')

        conn.commit() # complete transaction
        
    except psy.errors.DuplicateDatabase:
        logging.debug(f"{__file__}: create_db: database already exists")
    except Exception as e:
        logging.error(f"{__file__}: create_db: Error creating database: {e}")
        raise Exception from e
    finally:
        if conn:
            conn.close()
            
def create_all(drop):
    """
    Creates database and all tables of the database, see DataModel in report

    Args:
        drop : boolean      = drop tables ?
    Returns:
        None
    """
    
    # create databse first
    create_db()
    logging.debug(f"{__file__}: create_all: database creation complete")
    
    try: 
        
        # create tables
        conn = connect_to_database()
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        create_tables(cur, drop)
    
        conn.commit() # complete transaction
        
        logging.debug(f"{__file__}: create_all: table creation complete")
    except Exception as e:
        logging.error(f"{__file__}: create_all: some database error:\n{e}")
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_all(drop=True)
