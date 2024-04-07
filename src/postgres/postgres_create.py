import sys
import os
import psycopg2 as psy

# project src diretory
project_scr_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# add to python path
sys.path.append(project_scr_path)

from config.constants import Constants
from config.logger import setup_logging, logging


# we must first create a database


def create_db(dbname, user, password, host, port):
    """
    Creates a databse in postgres

    Args:
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    try:
        conn = psy.connect(
            dbname='postgres',  # 1st time we connect to the psotgres db and then create our own
            user=user,
            password=password,
            host=host,
            port=port
        )
        # we need this because of we need it
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        create_db_sql = f'CREATE DATABASE {dbname}'
        cur.execute(create_db_sql)
        conn.commit()
        logging.debug(f"{__file__}: create_db: new database created")

    except psy.errors.DuplicateDatabase:
        logging.debug(f"{__file__}: create_db: database already exists")
    except Exception as e:
        logging.error(f"{__file__}: create_db: Error creating database: {e}")
    finally:
        if conn is not None:
            conn.close()


# create dimension tables first
def create_dim_tables(dbname, user, password, host, port):
    """
    Creates the dimesion tables of the database, see DataModel in report

    Args:
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    try:
        conn = psy.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        _create_job_title_table(cur)
        _create_currency_table(cur)
        _create_experience_table(cur)
        _create_location_table(cur)
        _create_data_source_table(cur)
        _create_skill_list_table(cur)
        _create_job_category_table(cur)

        conn.commit()
        logging.debug(
            f"{__file__}: create_dim_tables: dimension tables created successfully")

    except Exception as e:
        logging.error(
            f"{__file__}: create_dim_tables: Error creating dimension tables: {e}")
    finally:
        if conn is not None:
            conn.close()


def _create_job_title_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_title (
            jt_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT job_title_unique_idx UNIQUE (name)
        );
    """)


def _create_currency_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS currency (
            c_id SERIAL PRIMARY KEY,
            symbol VARCHAR(3) NOT NULL, -- when we have no symbol we can use a 3 char abbreviation
            name VARCHAR(50),
            CONSTRAINT currency_symbol_unique_idx UNIQUE (symbol)
        );
    """)


def _create_experience_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experience (
            e_id SERIAL PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            CONSTRAINT experience_unique_idx UNIQUE (level)
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
            CONSTRAINT location_unique_idx UNIQUE (country, region, city, city_district, area_code)
        );
    """)


def _create_data_source_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data_source (
            ds_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            url VARCHAR(50) NOT NULL,
            CONSTRAINT data_source_unique_idx UNIQUE (name, url)
        );
    """)


def _create_skill_list_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skill_list (
            sl_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT skill_list_unique_idx UNIQUE (name)
        );
    """)


def _create_job_category_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_category (
            jc_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            CONSTRAINT job_category_unique_idx UNIQUE (name)
        );
    """)


# create fact table after dimensions


def create_fact_table(dbname, user, password, host, port):
    """
    Creates the fact table of the database, see DataModel in report

    Args:
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    try:
        conn = psy.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_offer (
                jo_id SERIAL PRIMARY KEY,
                source_id BIGINT NOT NULL,
                published DATE NOT NULL,
                salary_min INT NOT NULL,
                salary_max INT NOT NULL,
                job_title_id INT NOT NULL REFERENCES job_title(jt_id),
                currency_id INT NOT NULL REFERENCES currency(c_id),
                location_id INT NOT NULL REFERENCES location(l_id),
                data_source_id INT NOT NULL REFERENCES data_source(ds_id),
                experience_id INT REFERENCES experience(e_id),
                CONSTRAINT unique_job_offer UNIQUE (source_id, published, job_title_id, currency_id, location_id, data_source_id)
            )
        """)

        conn.commit()
        logging.debug(
            f"{__file__}: create_fact_table: fact table created successfully")

    except Exception as e:
        logging.error(
            f"{__file__}: create_fact_table: Error creating fact table: {e}")
    finally:
        if conn is not None:
            conn.close()

# create link tables for n 2 m relations last


def create_link_table(dbname, user, password, host, port):
    """
    Creates the link tables of the database, see DataModel in report

    Args:
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    try:
        conn = psy.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # link job offers to skills
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_2_skills (
                job_id INT REFERENCES job_offer(jo_id),
                skill_id INT REFERENCES skill_list(sl_id),
                PRIMARY KEY (job_id, skill_id)
            )
        """)

        # link job offers to job categories
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_2_categories (
                job_id INT REFERENCES job_offer(jo_id),
                cat_id INT REFERENCES job_category(jc_id),
                PRIMARY KEY (job_id, cat_id)
            )
        """)
        conn.commit()
        logging.debug(
            f"{__file__}: create_link_table: all link tables created successfully")

    except Exception as e:
        logging.error(
            f"{__file__}: create_link_table: Error creating link tables: {e}")
    finally:
        if conn is not None:
            conn.close()


def drop_all_tables(dbname, user, password, host, port):
    """
    Deletes all tables of the database

    Args:
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    try:
        conn = psy.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

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

    except Exception as e:
        logging.error(f"{__file__}: Error dropping all tables: {e}")
    finally:
        if conn is not None:
            conn.close()


def create_tables(drop, dbname=Constants.POSTGRES_DBNAME, user=Constants.POSTGRES_USER,
                  password=Constants.POSTGRES_PASSWORD, host=Constants.POSTGRES_HOST,
                  port=Constants.POSTGRES_PORT):
    """
    Creates all tables of the database, see DataModel in report

    Args:
        drop : boolean      = drop tables ?
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    if drop:
        drop_all_tables(dbname, user, password, host, port)
    create_dim_tables(dbname, user, password, host, port)
    create_fact_table(dbname, user, password, host, port)
    create_link_table(dbname, user, password, host, port)


def create_all(drop, dbname=Constants.POSTGRES_DBNAME, user=Constants.POSTGRES_USER,
               password=Constants.POSTGRES_PASSWORD, host=Constants.POSTGRES_HOST,
               port=Constants.POSTGRES_PORT):
    """
    Creates database and all tables of the database, see DataModel in report

    Args:
        drop : boolean      = drop tables ?
        dbname : str        = name of db, default value see config/constants.py
        user : str          = username, default value see config/constants.py
        password : str      = password, default value see config/constants.py
        host : str          = hostname or ip adress, default value see config/constants.py
        port : int          = portnumber, default value see config/constants.py
    Returns:
        None
    """
    create_db(dbname, user, password, host, port)
    create_tables(drop, dbname, user, password, host, port)


if __name__ == "__main__":
    setup_logging()
    create_all(drop=True)
