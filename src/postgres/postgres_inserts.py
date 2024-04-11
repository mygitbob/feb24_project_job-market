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


class MyDataWarning(Exception):
    """Exception used to create a warning in log file, no real error"""
    pass

# TODO: enable custom databse configuration, better put this in a seperate modul and use it for all other modules
def init_databse():
    pass
    
    
def insert_all_data(cur, df):
    """
    Function controls the table inserts and logs errors
    Args:
        cur :           = cursor database obejct
        df : DataFrame  = DataFrame to be stored in db
    Returns:
        (count_suc, count_err, count_dup) : tupel(int, int, int) = numer of rows that were inserted  successful, not successful, 
        not inserted because it´s already in the database (last number only for the fact table)
    """
    # number of successful inserted rows
    count_suc = 0
    # number of errors trying to insert rows
    count_err = 0
    # number of duplicate rows (therefor not inserted), this is only for the fact table
    count_dup = 0
    
    for _, row in df.iterrows():
        try:
            # first insert into dimension tables and get pk (or list of pk´s) of current insert
            jt_id = _insert_job_title(cur, row)        
            e_id = _insert_experience(cur, row)        
            c_id = _insert_currency(cur, row)
            l_id = _insert_location(cur, row)
            ds_id = _insert_data_source(cur, row)
            sl_id_list = _insert_into_skill_list(cur, row)
            jc_id_list = _insert_into_job_category(cur, row)
                    
            # afterwards insert into fact table
            jo_id = _insert_job_offer(cur, row, jt_id,c_id,e_id,l_id,ds_id)
            
            # finally insert into link tables, but only if we inserted stuff (both are optional)
            if len(sl_id_list) > 0:
                _insert_job_to_skills(cur, jo_id, sl_id_list)    
            if len(jc_id_list) > 0:
                _insert_job_to_categories(cur, jo_id, jc_id_list)    
            
            count_suc += 1
        except MyDataWarning as mdw:    # no error, only for logging
            logging.warning(f"{__file__}: {mdw}")
            count_dup += 1
        except MyDataError as mde:
            logging.error(f"{__file__}: MyDataError: {mde}")                
            count_err += 1
        except psy.DataError as de:
            logging.error(f"{__file__}: psy.DataError: {de}")
            count_err += 1
        except psy.IntegrityError as ie:
            logging.error(f"{__file__}: psy.IntegrityError: {ie}")
            count_err += 1
        except Exception as e:
            logging.error(f"{__file__}: UnkownError: {e}")
            count_err += 1
            
    return count_suc, count_err, count_dup


def _insert_job_title(cur, row):
    """
    Insert into table job_title
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        jt_id : int = primary key of inserted row
    """
    
    try:
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
                    raise MyDataError("could not get jt_id")
            except Exception as e:
                raise MyDataError(f"Unkown database error: {e}")
        else:
            raise MyDataError(
                f"'job_title' wrong type: '{type(job_title)}' or empty: '{job_title}'")        
            
    except MyDataError as mde:
        raise MyDataError(f"_insert_job_title: {mde}")
    except Exception as e:
        raise MyDataError(f"_insert_job_title: row['job_title_name'] missing ?: {e}")
    
    return jt_id

        
def _insert_currency(cur, row):
    """
    Insert into table currency
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        c_id : int = primary key of inserted row
    """
    
    try:
        # Insert data into currency table
        # currency_smybol is mandatory
        currency_symbol = row['currency_symbol']
        
        # currency_name is optional
        currency_name = row.get('currency_name', "NULL")
        if not isinstance(currency_name, str):
            logging.warning(
                f"{__file__}: insert_dim_tables: optional key 'currency_name' present but value does not fit:{currency_name}")
            currency_name = None
        
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
                    raise MyDataError("could not get c_id")
        except Exception as e:
            raise MyDataError(f"Unkown database error: {e}")
            
    except MyDataError as mde:
        raise MyDataError(f"_insert_currency: {mde}")
    except Exception as e:
        raise MyDataError(f"_insert_currency: row['currency_symbol'] missing ?: {e}")

    return c_id


def _insert_experience(cur, row):
    """
    Insert into table experience, this is optional
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        e_id : int = primary key of inserted row
    """
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
                raise MyDataError("could not get e_id")
        except Exception as e:
            raise MyDataError(f"Unkown database error: {e}")
    else:
        e_id = None
        logging.warning(
            f"{__file__}: _insert_experience: optional key 'experience_level' present but value does not fit:{experience_level}")
    
    return e_id
    
    
def _insert_location(cur, row):
    """
    Insert into table location, only country is mandatory (see DataModel)
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        l_id : int = primary key of inserted row
    """

    # Insert data into location table
    # country is mandatory
    try:
        country = row['location_country']
    except Exception as e:
        raise MyDataError(f"_insert_currency: row['location_country'] missing ?: {e}")
    
    if not (country and (country and isinstance(country, str))):
        raise MyDataError(
            f"location_country: wrong type: {type(country)} or value: {country}")

    region = row.get('location_region', "_UNKOWN_")
    if not isinstance(region, str):
        logging.warning(
            f"{__file__}: _insert_location: optional key 'location_region' present but value does not fit:{region}")
        region = "_UNKOWN_"

    city = row.get('location_city', "_UNKOWN_")
    if not isinstance(city, str):
        logging.warning(
            f"{__file__}: _insert_location: optional key 'location_city' present but value does not fit:{city}")
        city = "_UNKOWN_"

    city_district = row.get('location_city_district', "_UNKOWN_")
    if not isinstance(city_district, str):
        logging.warning(
            f"{__file__}: _insert_location: optional key 'location_city_district' present but value does not fit:{city_district}")
        city_district = "_UNKOWN_"

    area_code = row.get('location_area_code', "_UNKOWN_")
    if not isinstance(area_code, str):
        logging.warning(
            f"{__file__}: _insert_location: optional key 'location_area_code' present but value does not fit:{area_code}")
        area_code = "_UNKOWN_"

    state = row.get('location_state', "_UNKOWN_")
    if state is not None and not isinstance(state, str):
        logging.warning(
            f"{__file__}: _insert_location: optional key 'location_state' present but value does not fit:{state}")
        state = "_UNKOWN_"

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
                raise MyDataError("could not get l_id")
            
    except MyDataError as mde:
        raise MyDataError(f"_insert_location: {mde}")        
    except Exception as e:
        raise MyDataError(f"_insert_location: Unkown databse error: {e}")
    
    return l_id


def _insert_data_source(cur, row):
    """
    Insert into table data_source, only data_source_name is mandatory (see DataModel)
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        ds_id : int = primary key of inserted row
    """

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
                raise MyDataError("could not get ds_id")
        except MyDataError as mde:
            raise MyDataError(f"_insert_data_source: {mde}")
        except Exception as e:
            raise MyDataError(f"_insert_data_source: Unkown database error: {e}")
    else:
        raise MyDataError(
            f"_insert_data_source: name: wrong type: {type(source_name)} or value: {source_name}")
        
    return ds_id


def _insert_into_skill_list(cur, row):    
    """
    Insert into table skill_list, this is optional
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        sl_id_list : list[int] = list of primary key of inserted skills
    """
    # Insert data into skill_list table
    # skill_list is optional
    sl_id_list = []
    skill_list = row.get('skills', [])
    if not isinstance(skill_list, list):
        logging.warning(
            f"{__file__}: insert_dim_tables: optional key 'skills' is not a list: {type(skill_list)}")
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
                        raise MyDataError("could not get sl_id")
                    sl_id_list.append(sl_id)
                except Exception as e:
                    logging.warning(
                        f"{__file__}: _insert_into_skill_list: failed to insert skill:'{skill}': {e}")
                
    return sl_id_list


def _insert_into_job_category(cur, row):    
    """
    Insert into table job_category, this is optional
    
    Args:
        cur = database cursor
        row = data row to store
    Returns:
        jc_id_list : list[int] = list of primary key of inserted skills
    """

    # Insert data into job_category table
    # categories is optional
    jc_id_list = []
    cat_list = row.get('categories', [])
    if not isinstance(cat_list, list):
        logging.warning(
            f"{__file__}: _insert_into_job_category: optional key 'categories' is not a list: {type(cat_list)}")
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
                        raise MyDataError("could not get jc_id")
                    jc_id_list.append(jc_id)                                
                except Exception as e:
                    logging.warning(
                        f"{__file__}: _insert_into_job_category: failed to insert skill:'{cat}': {e}")
    return jc_id_list
                    
                    
def _insert_job_offer(cur, row, jt_id,c_id,e_id,l_id,ds_id):
        """
        Insert into table job_category, this is optional
        
        Args:
            cur = database cursor
            row = data row to store, must contain keys: 'source_id', 'joboffer_url', 'published','salary_min', 'salary_max'
            jt_id : int = primary key of insert into job_title
            c_id : int = primary key of insert into currency
            e_id : int = primary key of insert into experience
            l_id : int = primary key of insert into location
            ds_id : int = primary key of insert into data_source
        Returns:
            jo_id : int =  primary key of insert
        """
        
        try:
            source_id = row['source_id']
            joboffer_url = row['joboffer_url']
            published = row['published']
            salary_min = row['salary_min']
            salary_max = row['salary_max']
        except Exception as e:
            raise MyDataError(f"_insert_job_offer: soem of following keys missing: 'source_id', 'joboffer_url', 'published','salary_min', 'salary_max' : {e}")
        
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
            raise MyDataError(f"_insert_job_offer: cant exceute query: {e}")
        
        if not jo_id:
            raise MyDataWarning(f"_insert_job_offer: cant get jo_id -> already in db !?")
        
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
    
    
def connect_to_database(dbname=Constants.POSTGRES_DBNAME, user=Constants.POSTGRES_USER,
                      password=Constants.POSTGRES_PASSWORD, host=Constants.POSTGRES_HOST,
                      port=Constants.POSTGRES_PORT):
    """
    Connetcts to postgres databse, connection has to be closed after using
    Function does not handele Exceptions, these has to be handeled by the calling instance

    Args:
        TODO    
    Returns:
        conn : connection   = connection object to postgres        
    """
    conn = psy.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    
    return conn    
        
        
def store_dataframe(df, check_df=True):
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
    
    errors = []
    # check if DataFrame fullfills the requirements
    if check_df:
        errors = check_dataframe(df)
        if errors:
            return errors
    
    # trim all values, just in case
    df = trim_strings(df)
    
    try: 
        
        # connect to databse TODO: chenage default values possible
        conn = connect_to_database()
        conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        insert_all_data(cur, df)
    
        conn.commit() # complete transaction
        
        logging.debug(f"{__file__}: insert_dataframe: insertions complete")
    except Exception as e:
        logging.error(f"{__file__}: insert_dataframe: some database error:\n{e}")
        
    finally:
        if conn:
            conn.close()
    
    return errors # shall be empty at this stage ;)


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
    setup_logging()

    df = pd.DataFrame(data)
    df_wh = pd.DataFrame(data_with_holes)
    df_woc = pd.DataFrame(data_without_optional_cols)
    df_we = pd.DataFrame(data_with_errors)
       
    for frame in [df, df_wh, df_woc, df_we]:
        errors = store_dataframe(frame, check_df=True)
        if not errors:
            print("data passed checks, check log for potential errors during inserts")
        else:
            print("data did´t pass checks:\n", errors)
