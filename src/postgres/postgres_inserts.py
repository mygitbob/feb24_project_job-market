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
from check_dataframe import trim_strings, check_dataframe
from config.logger import setup_logging, logging


class MyDataError(Exception):
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
                            RETURNING jt_id
                        """, (job_title,))
                        # get pk jt_id
                        response = cur.fetchone()
                        if response:
                            jt_id = response[0]  # get jt_id if the job title was inserted
                        else:
                            cur.execute("""
                                SELECT jt_id FROM job_title WHERE name = %s
                            """, (job_title,))
                            response = cur.fetchone()
                            jt_id = response[0]  # get jt_id if the job title already exists
                        if not jt_id:
                            raise MyDataError(f"could not get jt_id")
                    except Exception as e:
                        raise MyDataError(f"job_title_name: {e}")
                else:
                    raise MyDataError(
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
                    raise MyDataError(
                        f"currency_symbol: wrong type: {type(currency_symbol)} or value: {currency_symbol}")
                try:
                    cur.execute("""
                        INSERT INTO currency (symbol, name)
                        VALUES (%s, %s)
                        ON CONFLICT (symbol) DO NOTHING
                        RETURNING c_id
                    """, (currency_symbol, currency_name))
                    # get pk c_id
                    response = cur.fetchone()
                    if response:
                        c_id = response[0]  # get c_id if currency_symbol was inserted
                    else:
                        cur.execute("""
                            SELECT c_id FROM currency WHERE symbol = %s
                        """, (currency_symbol,))
                        response = cur.fetchone()
                        c_id = response[0]  # get c_id if currency_symbol already exists
                    if not c_id:
                            raise MyDataError(f"could not get c_id")
                except Exception as e:
                    raise MyDataError(f"currency: {e}")
                
                # Insert into experience table
                # experience_level is optional
                experience_level = row.get('experience_level', None)

                if experience_level and isinstance(experience_level, str):
                    try:
                        cur.execute("""
                            INSERT INTO experience (level)
                            VALUES (%s)
                            ON CONFLICT DO NOTHING
                            RETURNING e_id
                        """, (experience_level,))
                        # get pk e_id
                        response = cur.fetchone()
                        if response:
                            e_id = response[0]  # get e_id if  was inserted
                        else:
                            cur.execute("""
                                SELECT e_id FROM experience WHERE level = %s
                            """, (experience_level,))
                            response = cur.fetchone()
                            e_id = response[0]  # get e_id if  already exists
                        if not e_id:
                            raise MyDataError(f"could not get e_id")
                    except Exception as e:
                        raise MyDataError(f"experience_level: {e}")
                else:
                    e_id = None
                    logging.warning(
                        f"{__file__}: insert_dim_tables: optional key 'experience_level' present but value does not fit:{experience_level}")

                # Insert data into location table
                # country is mandatory
                country = row['location_country']
                if not (country and (country and isinstance(country, str))):
                    raise MyDataError(
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
                        RETURNING l_id
                    """, (country, region, city, city_district, area_code, state))
                    # get pk l_id
                    response = cur.fetchone()
                    if response:
                        l_id = response[0]  # get l_id if  was inserted
                    else:
                        cur.execute("""
                            SELECT l_id FROM location WHERE country = %s AND region = %s AND city = %s AND city_district = %s AND area_code = %s AND  state = %s
                        """, (country, region, city, city_district, area_code, state))
                        response = cur.fetchone()
                        l_id = response[0]  # get e_id if  already exists
                    if not l_id:
                            raise MyDataError(f"could not get l_id")
                except Exception as e:
                    raise MyDataError(f"location: {e}")

                # Insert data into data_source table
                # data_source_name is mandatory
                source_name = row['data_source_name']
                if source_name and isinstance(source_name, str):
                    try:
                        cur.execute("""
                            INSERT INTO data_source (name) VALUES (%s)
                            ON CONFLICT (name) DO NOTHING
                            RETURNING ds_id
                        """, (source_name, ))
                        # get pk ds_id
                        response = cur.fetchone()
                        if response:
                            ds_id = response[0]  # get ds_id if  was inserted
                        else:
                            cur.execute("""
                                SELECT ds_id FROM data_source WHERE name = %s
                            """, (source_name,))
                            response = cur.fetchone()
                            ds_id = response[0]  # get ds_id if  already exists
                        if not ds_id:
                            raise MyDataError(f"could not get ds_id")
                    except Exception as e:
                        raise MyDataError(f"data_source name: {e}")
                else:
                    raise MyDataError(
                        f"data_source name,url: wrong type: {type(source_name)} or value: {source_name}")

                # Insert data into skill_list table
                # skill_list is optional
                sl_id_list = []
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
                                    RETURNING sl_id
                                """, (skill,))
                                 # get pk sl_id
                                response = cur.fetchone()
                                if response:
                                    sl_id = response[0]  # get sl_id if  was inserted
                                else:
                                    cur.execute("""
                                        SELECT sl_id FROM skill_list WHERE name = %s
                                    """, (skill,))
                                    response = cur.fetchone()
                                    sl_id = response[0]  # get sl_id if  already exists
                                if not sl_id:
                                    raise MyDataError(f"could not get sl_id")
                                sl_id_list.append(sl_id)
                            except Exception as e:
                                logging.warning(
                                    f"Error inserting skill_list'{skill}': {e}")
                                
                # Insert data into job_category table
                # categories is optional
                jc_id_list = []
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
                                    RETURNING jc_id
                                """, (cat,))
                                 # get pk jc_id
                                response = cur.fetchone()
                                if response:
                                    jc_id = response[0]  # get jc_id if  was inserted
                                else:
                                    cur.execute("""
                                        SELECT jc_id FROM job_category WHERE name = %s
                                    """, (cat,))
                                    response = cur.fetchone()
                                    jc_id = response[0]  # get jc_id if  already exists
                                if not jc_id:
                                    raise MyDataError(f"could not get jc_id")
                                jc_id_list.append(jc_id)                                
                            except Exception as e:
                                logging.warning(
                                    f"Error inserting job_category '{cat}': {e}")
                
                #print(jt_id,c_id,e_id,l_id,ds_id)
                #print("skill list:", sl_id_list)
                #print("jobcat list:", jc_id_list)
                #insert into fact table, need to return id
                jo_id = _insert_fact_table(cur, row, jt_id,c_id,e_id,l_id,ds_id)        
                
                #insert into link tables need ids as input
                _insert_job_to_skills(cur, jo_id, sl_id_list)
                _insert_job_to_categories(cur, jo_id, jc_id_list)
            
            except MyDataError as my_data_error:
                logging.error(f"Insert Dim: My Data error occurred: {my_data_error}")                
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
        logging.error(f"Database error:\n{e}")
    finally:
        if conn is not None:
            conn.close()
        
        
def _insert_fact_table(cur, row, jt_id,c_id,e_id,l_id,ds_id):
        
        source_id = row['source_id']
        joboffer_url = row['joboffer_url']
        published = row['published']
        salary_min = row['salary_min']
        salary_max = row['salary_max']
        
        try:
            cur.execute("""
                INSERT INTO job_offer (source_id, published, salary_min, salary_max, joboffer_url, job_title_id, currency_id, location_id, data_source_id, experience_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id) DO NOTHING
                RETURNING jo_id
            """, (source_id, published, salary_min, salary_max, joboffer_url, jt_id, c_id, l_id, ds_id, e_id))
            # get pk jo_id
            response = cur.fetchone()
            if response:
                jo_id = response[0]  # get jo_id if  was inserted
            else:
                jo_id = None # did not insert fact !?
        except Exception as e:
            raise MyDataError(f"fact table insert: cant exceute query: {e}")
        
        if not jo_id:
            raise MyDataError(f"fact table insert: cant get jo_id -> conflict -> already in db")
        return jo_id


def _insert_job_to_skills(cur, jo_id, sl_id_list):
    
    try:
        for sl_id in sl_id_list:
            cur.execute("""
                INSERT INTO job_to_skills (job_id, skill_id) 
                VALUES (%s, %s)
                ON CONFLICT (job_id, skill_id) DO NOTHING
            """, (jo_id, sl_id))
        
    except Exception as e:
        raise MyDataError(f"job_to_skill table insert :cant exceute query: {e}")


def _insert_job_to_categories(cur, jo_id, jc_id_list):
    try:
        for jc_id in jc_id_list:
            cur.execute("""
                INSERT INTO job_to_categories (job_id, cat_id) 
                VALUES (%s, %s)
                ON CONFLICT (job_id, cat_id) DO NOTHING
            """, (jo_id, jc_id))
        
    except Exception as e:
        raise MyDataError(f"job_to_categories table insert :cant exceute query: {e}")
    
    
def insert_dataframe(df, check_df=True):
    """
    Inserts a dataframe in the postgres db.
    First checks if all required keys are present and if the value sfullfill the requirements.
    Then trims all string values and insert the data in the dimension tables, then in the fact 
    table and finally in the link tables, see DataModel in report

    Agrs:
        df : DataFrame      = data to insert
        check_df : bool     = check df before inserting
    Returns:
        errors : list       = empty when no errors occured, otherwise list of missing keys if any 
                              and index and error from rows that contain errors, 
                              check log for potenial conflicts during the sql inserts
                              BEWARE, if check_df is False, return value is always []

    """
    
    if check_df:
        errors = check_dataframe(df)
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
        "joboffer_url": ["http://companya.com1", "http://companyb.com2", "http://companyc.com3", "http://companya.com4", "http://companya.com5", "http://companya.com6", "http://companyx.com7", "http://companyx.com8", "http://companyx.com9", "http://companyx.com0"],
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
    data_with_errors = {
        "source_id": [1, "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "job_title_name": ["Software Engineer", "", "Project Manager", "Marketing Specialist", "Financial Analyst", "HR Manager", "Sales Representative", "Product Manager", "UX/UI Designer", "Customer Support Specialist"],
        "experience_level": ["Senior", "Junior", "Mid", "Senior", "Mid", "Junior", "Senior", "Mid", "Junior", "Mid"],
        "published": pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01"]),
        "salary_min": [60000, 1500, 0, 55000, 65000, 60000, 55000, 70000, 55000, 60000],
        "salary_max": [120000, 100000, 140000, 0, 130000, 120000, 110000, 140000, 110000, 120000],
        "currency_symbol": ["USD", "EUR", "GBP", "USD", "", "GBP", "USD", "EUR", "GBP", "USD"],
        "currency_name": ["US Dollar", "Euro", "British Pound", "US Dollar", "Euro", "British Pound", "US Dollar", "Euro", "British Pound", "US Dollar"],
        "location_country": ["USA", "Germany", "UK", "USA", "Germany", "", "USA", "Germany", "UK", "USA"],
        "location_region": ["West", "North", "South", "West", "North", "South", 666, "North", "South", "West"],
        "location_city": ["New York", "Berlin", "London", "New York", "Berlin", "London", "New York", "Berlin", "London", "New York"],
        "location_city_district": ["Manhattan", "Mitte", "Westminster", "Manhattan", "Mitte", "Westminster", "Manhattan", "Mitte", "Westminster", "Manhattan"],
        "location_area_code": ["NY001", "BE001", "LON001", "NY002", "BE002", "LON002", "NY003", "BE003", "LON003", "NY004"],
        "data_source_name": ["Company A", "Company B", "Company C", "Company A", "Company A", "Company A", "Company x", "", "Company x", "Company x"],
        "joboffer_url": ["http://companya.com", "http://companyb.com", "http://companyc.com", "http://companya.com", "http://companya.com", "http://companya.com", "http://companyx.com", "http://companyx.com", "", "http://companyx.com"],
        "skills": [["some skill"], ["R", "Python", "Machine Learning"], ["Project Management", "Leadership", "Communication"], ["Marketing", "SEO", "Social Media"], ["Finance", "Excel", "Financial Analysis"], ["HR Management", "Recruitment", "Employee Relations"], ["Sales", "Negotiation", "Customer Relationship Management"], ["Product Management", "Agile", "Product Development"], ["UI/UX Design", "Adobe Creative Suite", "Wireframing"], ["Customer Support", "Troubleshooting", "Ticketing System"]],
        "categories": [["a category"], ["Data Science", "Analytics", "Machine Learning"], ["Project Management", "Business", "Management"], ["Marketing", "Digital Marketing", "Advertising"], ["Finance", "Accounting", "Financial Services"], ["HR", "Management", "Human Resources"], ["Sales", "Business Development", "Marketing"], ["Product Management", "Product Development", "Agile"], ["Design", "UI/UX", "Creative"], ["Customer Support", "Customer Service", "Technical Support"]]
    }
    #setup_logging()

    df = pd.DataFrame(data)
    df_wh = pd.DataFrame(data_with_holes)
    df_woc = pd.DataFrame(data_without_optional_cols)
    df_we = pd.DataFrame(data_with_errors)
       
    for frame in [df, df_wh, df_woc, df_we]:
        errors = insert_dataframe(frame, check_df=True)
        if not errors:
            print("data passed checks, check log for potential errors during inserts")
        else:
            print("data did´t pass checks:\n", errors)
