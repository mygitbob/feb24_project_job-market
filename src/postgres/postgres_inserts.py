import sys
import os
import pandas as pd
from datetime import date
import psycopg2 as psy
import warnings
warnings.filterwarnings('ignore')

# project src diretory
project_src_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))
# add to python path
sys.path.append(project_src_path)

from config.constants import Constants
from check_dataframe import trim_strings, check_values, check_keys
from config.logger import setup_logging, logging


class DataError(Exception):
    """Exception raised when data fields are missing or values not in the right format or range"""
    pass


def insert_dim_tables(df, dbname=Constants.POSTGRES_DBNAME, user=Constants.POSTGRES_USER,
                      password=Constants.POSTGRES_PASSWORD, host=Constants.POSTGRES_HOST,
                      port=Constants.POSTGRES_PORT):

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

        for _, row in df.iterrows():
            try:

                # insert data into job_title table
                job_title = row['job_title_name']
                if job_title and isinstance(job_title, str):
                    try:
                        cur.execute("""
                            INSERT INTO job_title (name) VALUES (%s)
                            ON CONFLICT (name) DO NOTHING
                        """, (job_title,))
                    except Exception as e:
                        raise DataError(f"job_title_name: {e}")
                else:
                    raise DataError(
                        f"job_title_name: wrong type or empty: {type(job_title)}")

                # Insert data into currency table
                # currency_smybol is mandatory
                currency_symbol = row['currency_symbol']
                
                # currency_name is optional
                currency_name = row.get('currency_name', "NULL")
                if not isinstance(currency_name, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'currency_name' present but value does not fit:{currency_name}")
                    currency_name = "NULL"
                    
                if not (0 < len(currency_symbol) < 4 and isinstance(currency_symbol, str)):
                    raise DataError(
                        f"currency_symbol: wrong type: {type(currency_symbol)} or value: {currency_symbol}")

                try:
                    cur.execute("""
                        INSERT INTO currency (symbol, name)
                        VALUES (%s, %s)
                        ON CONFLICT (symbol) DO NOTHING
                    """, (currency_symbol, currency_name))
                except Exception as e:
                    raise DataError(f"currency: {e}")

                # Insert into experience table
                # experience_level is optional
                experience_level = row.get('experience_level', None)

                if experience_level and isinstance(experience_level, str):
                    try:
                        cur.execute("""
                            INSERT INTO experience (level)
                            VALUES (%s)
                            ON CONFLICT DO NOTHING
                        """, (experience_level,))
                    except psy.errors.UniqueViolation:
                        logging.warning(
                            f"{__file__}: insert_dim_tables: '{experience_level}' already exists in experience table.")
                    except Exception as e:
                        raise DataError(f"experience_level: {e}")
                else:
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'experience_level' present but value does not fit:{experience_level}")

                # Insert data into location table
                # country is mandatory
                country = row['location_country']
                if not (country and (country and isinstance(country, str))):
                    raise DataError(
                        f"location_country: wrong type: {type(country)} or value: {country}")

                region = row.get('location_region', "NULL")
                if not isinstance(region, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_region' present but value does not fit:{region}")
                    region = "NULL"

                city = row.get('location_city', "NULL")
                if not isinstance(city, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_city' present but value does not fit:{city}")
                    city = "NULL"

                city_district = row.get('location_city_district', "NULL")
                if not isinstance(city_district, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_city_district' present but value does not fit:{city_district}")
                    city_district = "NULL"

                area_code = row.get('location_area_code', "NULL")
                if not isinstance(area_code, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_area_code' present but value does not fit:{area_code}")
                    area_code = "NULL"

                state = row.get('location_state', "NULL")
                if state is not None and not isinstance(state, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_state' present but value does not fit:{state}")
                    state = "NULL"

                try:
                    cur.execute("""
                        INSERT INTO location (country, region, city, city_district, area_code, state)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (country, region, city, city_district, area_code, state) DO NOTHING
                    """, (country, region, city, city_district, area_code, state))
                except Exception as e:
                    raise DataError(f"location: {e}")

                # Insert data into data_source table
                # data_source_name is mandatory
                source_name = row['data_source_name']
                if source_name and isinstance(source_name, str):
                    try:
                        cur.execute("""
                            INSERT INTO data_source (name) VALUES (%s)
                            ON CONFLICT (name) DO NOTHING
                        """, (source_name, ))
                    except Exception as e:
                        raise DataError(f"data_source name,url: {e}")
                else:
                    raise DataError(
                        f"data_source name,url: wrong type: {type(source_name)} or value: {source_name}")

                # Insert data into skill_list table
                # skill_list is optional
                skill_list = row.get('skills', [])
                if not isinstance(skill_list, list):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'skills' but is not a list: {type(skill_list)}")
                else:
                    for skill in skill_list:
                        if isinstance(skill, str) and skill:
                            try:
                                cur.execute("""
                                    INSERT INTO skill_list (name) VALUES (%s)
                                    ON CONFLICT (name) DO NOTHING
                                """, (skill,))
                            except Exception as e:
                                logging.warning(
                                    f"Error inserting skill '{skill}': {e}")

                # Insert data into job_category table
                # categories is optional
                cat_list = row.get('categories', [])
                if not isinstance(cat_list, list):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'categories' but is not a list: {type(cat_list)}")
                else:
                    for cat in cat_list:
                        if isinstance(cat, str) and cat:
                            try:
                                cur.execute("""
                                    INSERT INTO job_category (name) VALUES (%s)
                                    ON CONFLICT (name) DO NOTHING
                                """, (cat,))
                            except Exception as e:
                                logging.warning(
                                    f"Error inserting category '{cat}': {e}")

            except psy.DataError as data_error:
                logging.error(f"Insert Dim: Data error occurred: {data_error}")
            except psy.IntegrityError as integrity_error:
                logging.error(f"Insert Dim: Integrity error occurred: {integrity_error}")
            except psy.DatabaseError as db_error:
                logging.error(f"Insert Dim: Database error occurred: {db_error}")
            except Exception as e:
                logging.error(f"Insert Dim: Unkown error: {e}")

        conn.commit()
        logging.debug("Dimension tables data inserts finished")

    except Exception as e:
        logging.error(f"Error inserting data into dimension tables:\n{e}")
    finally:
        if conn is not None:
            conn.close()


def check_type(to_check, type):
    return isinstance(to_check, type)


def insert_fact_table(df, dbname=Constants.POSTGRES_DBNAME, user=Constants.POSTGRES_USER,
                      password=Constants.POSTGRES_PASSWORD, host=Constants.POSTGRES_HOST,
                      port=Constants.POSTGRES_PORT):

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

        for index, row in df.iterrows():
            try:

                # insert data into job_offer table
                source_id = row['source_id']
                published = row['published']
                salary_min = row['salary_min']
                salary_max = row['salary_max']
                job_title = row['job_title_name']
                experience = row.get('experience_level', None)
                currency_symbol = row['currency_symbol']
                country = row['location_country']
                region = row.get('location_region', None)
                city = row.get('location_city', None)
                city_district = row.get('location_city_district', None)
                area_code = row.get('location_area_code', None)
                state = row.get('location_state', "NULL")
                data_source = row['data_source_name']
                data_url = row['data_source_url']
                
                # check for empty strings and right types
                if all([source_id, job_title, currency_symbol, country, data_source, data_url]) and \
                        all([check_type(source_id, str), check_type(job_title, str), check_type(currency_symbol, str),
                            check_type(country, str), check_type(data_source, str), check_type(data_url, str)]) and\
                        all([check_type(salary_min, int), check_type(salary_max, int), check_type(published, date)]):
                    try:
                        cur.execute("""
                            INSERT INTO job_offer (source_id, published, salary_min, salary_max, job_title_id, currency_id, experience_id, location_id, data_source_id) 
                            VALUES (%s, %s, %s, %s, (SELECT jt_id FROM job_title WHERE name = %s), 
                                            (SELECT c_id FROM currency WHERE symbol = %s),
                                            (SELECT e_id FROM experience WHERE level = %s), 
                                            (SELECT l_id FROM location WHERE country = %s AND region = %s AND city = %s AND city_district = %s AND area_code = %s AND  state = %s ), 
                                            (SELECT ds_id FROM data_source WHERE name = %s AND url = %s))
                            ON CONFLICT (source_id, published, job_title_id, currency_id, location_id, data_source_id) DO NOTHING
                        """, (source_id, published, salary_min, salary_max, job_title, currency_symbol, experience, country,
                              region, city, city_district, area_code, state, data_source, data_url))
                    except Exception as e:
                        raise DataError(f"fact table :cant exceute query: {e}")
                else:
                    raise DataError(
                        f"insert fact table: data error, don´t pass the test: {index, row.values}")

            except psy.DataError as data_error:
                logging.error(f"Insert Fact: Data error occurred: {data_error}")
            except psy.IntegrityError as integrity_error:
                logging.error(f"Insert Fact: Integrity error occurred: {integrity_error}")
            except psy.DatabaseError as db_error:
                logging.error(f"Insert Fact: Database error occurred: {db_error}")
            except Exception as e:
                logging.error(f"Insert Fact: Unknown error:{e}: for row:{index, row.values}")

        conn.commit()
        logging.debug("Fact table data inserts finished")

    except Exception as e:
        logging.error(f"Error inserting data into fact table:\n{e}")
    finally:
        if conn is not None:
            conn.close()


def insert_link_tables(df, dbname=Constants.POSTGRES_DBNAME, user=Constants.POSTGRES_USER,
                      password=Constants.POSTGRES_PASSWORD, host=Constants.POSTGRES_HOST,
                      port=Constants.POSTGRES_PORT):

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

        for _, row in df.iterrows():
            try:

                # insert

                # insert

                pass

            except psy.DataError as data_error:
                logging.error(f"Data error occurred: {data_error}")
            except psy.IntegrityError as integrity_error:
                logging.error(f"Integrity error occurred: {integrity_error}")
            except psy.DatabaseError as db_error:
                logging.error(f"Database error occurred: {db_error}")
            except Exception as e:
                logging.error(f"Unkown error: {e}")

        conn.commit()
        logging.debug("Link tables data inserts finished")

    except Exception as e:
        logging.error(f"Insert Link: Error inserting data into link tables:\n{e}")
    finally:
        if conn is not None:
            conn.close()


def insert_dataframe(df):
    """
    Inserts a dataframe in the postgres db.
    First checks if all required keys are present and if the value sfullfill the requirements.
    Then trims all string values and insert the data in the dimension tables, then in the fact 
    table and finally in the link tables, see DataModel in report

    Agrs:
        df : DataFrame      = data to insert

    Returns:
        errors : list       = empty when no errors occured, otherwise list of missing keys if any 
                              and index and error from rows that contain errors, 
                              check log for potenial conflicts during the sql inserts

    """
    missing_keys = check_keys(df)
    value_errors = check_values(df)
    errors = missing_keys + value_errors
    if errors:
        return errors
    df = trim_strings(df)
    insert_dim_tables(df)
    #insert_fact_table(df)
    #insert_link_tables(df)
    return []


if __name__ == "__main__":
    data = {
        "source_id": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "job_title_name": ["Software Engineer", "Data Scientist", "Project Manager", "Marketing Specialist", "Financial Analyst", "HR Manager", "Sales Representative", "Product Manager", "UX/UI Designer", "Customer Support Specialist"],
        "experience_level": ["Senior", "Junior", "Mid", "Senior", "Mid", "Junior", "Senior", "Mid", "Junior", "Mid"],
        "published": pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01"]),
        "salary_min": [60000, 50000, 70000, 55000, 65000, 60000, 55000, 70000, 55000, 60000],
        "salary_max": [120000, 100000, 140000, 110000, 130000, 120000, 110000, 140000, 110000, 120000],
        "currency_symbol": ["USD", "EUR", "GBP", "USD", "EUR", "GBP", "USD", "EUR", "GBP", "USD"],
        "currency_name": ["US Dollar", "Euro", "British Pound", "US Dollar", "Euro", "British Pound", "US Dollar", "Euro", "British Pound", "US Dollar"],
        "location_country": ["USA", "Germany", "UK", "USA", "Germany", "UK", "USA", "Germany", "UK", "USA"],
        "location_region": ["West", "North", "South", "West", "North", "South", "West", "North", "South", "West"],
        "location_city": ["New York", "Berlin", "London", "New York", "Berlin", "London", "New York", "Berlin", "London", "New York"],
        "location_city_district": ["Manhattan", "Mitte", "Westminster", "Manhattan", "Mitte", "Westminster", "Manhattan", "Mitte", "Westminster", "Manhattan"],
        "location_area_code": ["NY001", "BE001", "LON001", "NY002", "BE002", "LON002", "NY003", "BE003", "LON003", "NY004"],
        "data_source_name": ["Company A", "Company B", "Company C", "Company A", "Company A", "Company A", "Company x", "Company x", "Company x", "Company x"],
        "joboffer_url": ["http://companya.com", "http://companyb.com", "http://companyc.com", "http://companya.com", "http://companya.com", "http://companya.com", "http://companyx.com", "http://companyx.com", "http://companyx.com", "http://companyx.com"],
        "skills": [["some skill"], ["R", "Python", "Machine Learning"], ["Project Management", "Leadership", "Communication"], ["Marketing", "SEO", "Social Media"], ["Finance", "Excel", "Financial Analysis"], ["HR Management", "Recruitment", "Employee Relations"], ["Sales", "Negotiation", "Customer Relationship Management"], ["Product Management", "Agile", "Product Development"], ["UI/UX Design", "Adobe Creative Suite", "Wireframing"], ["Customer Support", "Troubleshooting", "Ticketing System"]],
        "categories": [["a category"], ["Data Science", "Analytics", "Machine Learning"], ["Project Management", "Business", "Management"], ["Marketing", "Digital Marketing", "Advertising"], ["Finance", "Accounting", "Financial Services"], ["HR", "Management", "Human Resources"], ["Sales", "Business Development", "Marketing"], ["Product Management", "Product Development", "Agile"], ["Design", "UI/UX", "Creative"], ["Customer Support", "Customer Service", "Technical Support"]]
    }
    
    data_with_holes = {
        "source_id": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "job_title_name": ["Software Engineer", "Data Scientist", "Project Manager", "Marketing Specialist", "Financial Analyst", "HR Manager", "Sales Representative", "Product Manager", "UX/UI Designer", "Customer Support Specialist"],
        "experience_level": [None, None, "Mid", "Senior", "Mid", "Junior", "Senior", "Mid", "Junior", "Mid"],
        "published": pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01"]),
        "salary_min": [60000, 50000, 70000, 55000, 65000, 60000, 55000, 70000, 55000, 60000],
        "salary_max": [120000, 100000, 140000, 110000, 130000, 120000, 110000, 140000, 110000, 120000],
        "currency_symbol": ["USD", "EUR", "GBP", "USD", "EUR", "GBP", "USD", "EUR", "GBP", "USD"],
        "currency_name": [None, None, None, None, None, None, None, None, None, None],
        "location_country": ["USA", "Germany", "UK", "USA", "Germany", "UK", "USA", "Germany", "UK", "USA"],
        "location_region": ["NorthWest", None, None, "NorthWest", None, None, None, None, None, None],
        "location_city": [None, "Berlin", None, None, "Berlin", None, None, None, None, None],
        "location_city_district": [None, None, "LondonCity", None, None, "LondonCity", None, None, None, None],
        "location_area_code": [None, None, None, None, None, None, "123", None, None, "123"],
        "data_source_name": ["Company A", "Company B", "Company C", "Company A", "Company A", "Company A", "Company x", "Company x", "Company x", "Company x"],
        "joboffer_url": ["http://companya.com1", "http://companyb.com2", "http://companyc.com3", "http://companya.com4", "http://companya.com5", "http://companya.com6", "http://companyx.com7", "http://companyx.com8", "http://companyx.com9", "http://companyx.com0"],
        "skills": [[], ["R", "Python", "Machine Learning"], ["Project Management", "Leadership", "Communication"], ["Marketing", "SEO", "Social Media"], ["Finance", "Excel", "Financial Analysis"], ["HR Management", "Recruitment", "Employee Relations"], ["Sales", "Negotiation", "Customer Relationship Management"], ["Product Management", "Agile", "Product Development"], ["UI/UX Design", "Adobe Creative Suite", "Wireframing"], ["Customer Support", "Troubleshooting", "Ticketing System"]],
        "categories": [None, ["Data Science", "Analytics", "Machine Learning"], ["Project Management", "Business", "Management"], ["Marketing", "Digital Marketing", "Advertising"], ["Finance", "Accounting", "Financial Services"], ["HR", "Management", "Human Resources"], ["Sales", "Business Development", "Marketing"], ["Product Management", "Product Development", "Agile"], ["Design", "UI/UX", "Creative"], ["Customer Support", "Customer Service", "Technical Support"]]
    }
    data_without_optional_cols = {
        "source_id": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "job_title_name": ["Software Engineer", "Data Scientist", "Project Manager", "Marketing Specialist", "Financial Analyst", "HR Manager", "Sales Representative", "Product Manager", "UX/UI Designer", "Customer Support Specialist"],
        "published": pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01"]),
        "salary_min": [60000, 50000, 70000, 55000, 65000, 60000, 55000, 70000, 55000, 60000],
        "salary_max": [120000, 100000, 140000, 110000, 130000, 120000, 110000, 140000, 110000, 120000],
        "currency_symbol": ["USD", "EUR", "GBP", "USD", "EUR", "GBP", "USD", "EUR", "GBP", "USD"],
        "location_country": ["USA", "Germany", "UK", "USA", "Germany", "UK", "USA", "Germany", "UK", "USA"],
        "data_source_name": ["Company A", "Company B", "Company C", "Company A", "Company A", "Company A", "Company x", "Company x", "Company x", "Company x"],
        "joboffer_url": ["http://companya.com1", "http://companyb.com2", "http://companyc.com3", "http://companya.com4", "http://companya.com5", "http://companya.com6", "http://companyx.com7", "http://companyx.com8", "http://companyx.com9", "http://companyx.com0"],
    }
    setup_logging()

    df = pd.DataFrame(data)
    df_wh = pd.DataFrame(data_with_holes)
    df_woc = pd.DataFrame(data_without_optional_cols)
    
    for frame in [df, df_wh, df_woc]:
        errors = insert_dataframe(frame)
        if not errors:
            print("data passed checks, check log for potential errors during inserts")
        else:
            print("data did´t pass checks:\n", errors)
