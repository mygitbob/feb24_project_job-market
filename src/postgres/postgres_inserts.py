import sys
import os
import pandas as pd
import psycopg2 as psy
import warnings
warnings.filterwarnings('ignore')

# project src diretory
project_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# add to python path
sys.path.append(project_src_path)
from config.logger import setup_logging, logging
from check_dataframe import trim_strings, check_values, check_keys
from config.constants import Constants


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
                    # insert only if not already present
                    cur.execute(
                        "SELECT 1 FROM job_title WHERE name = %s", (job_title,))
                    existing_row = cur.fetchone()
                    if not existing_row:
                        cur.execute("""
                                    INSERT INTO job_title (name) VALUES (%s)
                                    """, (job_title,))
                else:
                    raise DataError(
                        f"job_title_name: wrong type or empty: {type(job_title)}")

                # Insert data into currency table
                currency_symbol = row['currency_symbol']
                currency_name = row.get('currency_name', None)

                if not (0 < len(currency_symbol) < 4 and isinstance(currency_symbol, str)):
                    raise DataError(
                        f"currency_symbol: wrong type: {type(currency_symbol)} or value: {currency_symbol}")

                # Insert only if not already present
                cur.execute(
                    "SELECT 1 FROM currency WHERE symbol = %s", (currency_symbol,))
                existing_row = cur.fetchone()
                if not existing_row:
                    if currency_name and isinstance(currency_name, str):
                        cur.execute("""
                            INSERT INTO currency (symbol, name) VALUES (%s, %s)
                            """, (currency_symbol, currency_name))
                    else:
                        cur.execute("""
                            INSERT INTO currency (symbol) VALUES (%s)
                            """, (currency_symbol,))
                        logging.warning(
                            f"{__file__}: insert_dim_tables: optional key 'currency_name' present but value does not fit:{currency_name}")

                # Insert optional data into experience table
                experience_level = row.get('experience_level', None)
                if experience_level and isinstance(experience_level, str):
                    # Insert only if not already present
                    cur.execute(
                        "SELECT 1 FROM experience WHERE level = %s", (experience_level,))
                    existing_row = cur.fetchone()
                    if not existing_row:
                        cur.execute("""
                            INSERT INTO experience (level) VALUES (%s)
                            """, (experience_level,))
                else:
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'experience_level' present but value does not fit:{experience_level}")

                # Insert data into location table
                country = row['location_country']
                if not (country and isinstance(country, str)):
                    raise DataError(
                        f"location_country: wrong type: {type(country)} or value: {country}")

                region = row.get('location_region', None)
                if region is not None and not isinstance(region, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_region' present but value does not fit:{region}")
                    region = None

                city = row.get('location_city', None)
                if city is not None and not isinstance(city, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_city' present but value does not fit:{city}")
                    city = None

                city_district = row.get('location_city_district', None)
                if city_district is not None and not isinstance(city_district, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_city_district' present but value does not fit:{city_district}")
                    city_district = None

                area_code = row.get('location_area_code', None)
                if area_code is not None and not isinstance(area_code, str):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'location_area_code' present but value does not fit:{area_code}")
                    area_code = None

                # Insert only if not already present
                cur.execute("SELECT 1 FROM location WHERE country = %s AND region = %s AND city = %s AND city_district = %s AND area_code = %s",
                            (country, region, city, city_district, area_code))
                existing_row = cur.fetchone()
                if not existing_row:
                    cur.execute("""
                        INSERT INTO location (country, region, city, city_district, area_code) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (country, region, city, city_district, area_code))

                # Insert data into data_source table
                source_name = row['data_source_name']
                source_url = row['data_source_url']
                if source_name and source_url and isinstance(source_name, str) and isinstance(source_url, str):
                    cur.execute("""
                        INSERT INTO data_source (name, url) VALUES (%s, %s)
                        """, (row['data_source_name'], row['data_source_url']))
                else:
                    raise DataError(
                        f"data_source name,url: wrong type: {type(source_name),type(source_url)} or value: {source_name,source_url}")

                # Insert data into skill_list table
                skill_list = row.get('skills', None)
                if not isinstance(skill_list, list):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'skills' but is no list:{type(skill_list)}")
                else:
                    for skill in skill_list:
                        if skill:
                            cur.execute("""
                                INSERT INTO skill_list (name) VALUES (%s)
                                """, (skill,))

                # Insert data into job_category table
                cat_list = row.get('categories', None)
                if not isinstance(cat_list, list):
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'categories' but is no list:{type(cat_list)}")
                else:
                    for cat in cat_list:
                        if cat:
                            cur.execute("""
                                INSERT INTO job_category (name) VALUES (%s)
                                """, (cat,))

            except psy.DataError as data_error:
                logging.error(f"Data error occurred: {data_error}")
            except psy.IntegrityError as integrity_error:
                logging.error(f"Integrity error occurred: {integrity_error}")
            except psy.DatabaseError as db_error:
                logging.error(f"Database error occurred: {db_error}")
            except Exception as e:
                logging.error(f"Unkown error: {e}")

        conn.commit()
        logging.debug("Dimension tables data inserted successfully")

    except Exception as e:
        logging.error(f"Error inserting data into dimension tables:\n{e}")
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
    return []


if __name__ == "__main__":
    data = {
        "source_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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
        "data_source_url": ["http://companya.com", "http://companyb.com", "http://companyc.com", "http://companya.com", "http://companya.com", "http://companya.com", "http://companyx.com", "http://companyx.com", "http://companyx.com", "http://companyx.com"],
        "skills": [["sdsdsadsadasdsadassssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss"], ["R", "Python", "Machine Learning"], ["Project Management", "Leadership", "Communication"], ["Marketing", "SEO", "Social Media"], ["Finance", "Excel", "Financial Analysis"], ["HR Management", "Recruitment", "Employee Relations"], ["Sales", "Negotiation", "Customer Relationship Management"], ["Product Management", "Agile", "Product Development"], ["UI/UX Design", "Adobe Creative Suite", "Wireframing"], ["Customer Support", "Troubleshooting", "Ticketing System"]],
        "categories": [[21323], ["Data Science", "Analytics", "Machine Learning"], ["Project Management", "Business", "Management"], ["Marketing", "Digital Marketing", "Advertising"], ["Finance", "Accounting", "Financial Services"], ["HR", "Management", "Human Resources"], ["Sales", "Business Development", "Marketing"], ["Product Management", "Product Development", "Agile"], ["Design", "UI/UX", "Creative"], ["Customer Support", "Customer Service", "Technical Support"]]
    }
    setup_logging()
    
    df = pd.DataFrame(data)

    errors = insert_dataframe(df.iloc[1:])
    if not errors:
        print("data passed checks, check log for potential errors during inserts")
    else:
        print("data did´t pass checks:\n", errors)
