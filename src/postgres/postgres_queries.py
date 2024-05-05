import pandas as pd
from sqlalchemy import create_engine

import postgres_initdb as idb


def connect_db(db_user, db_password, db_host, db_port, db_name='jobmarket'):
    """
    Args:
        db_user : str       = postgres username
        db_password : str   = password of user above
        db_host : str       = hostname/ip of postgres service
        db_port : int       = port of postgres service
        db_name : str       = name of database, probably 'jobmarket'
    Returns:
        engine  = database object
    """
    db_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    engine = create_engine(db_string)
    
    return engine


def get_job_title_df(engine, search_term=None):
    """
    Returns saved job titles that fit search_term as a DataFrame
    
    Args:
        engine              = database object
        search_term : str   = term to searched with a SQL LIKE statement
    Return 
        df : DataFrame   = DataFrame of all job titles that fits search_term
    """
    query = "SELECT * FROM job_title" 
    if search_term:
        query += " WHERE name LIKE %s"
        df = pd.read_sql_query(query, engine, params=('%' + search_term + '%',))
    else:
        df = pd.read_sql_query(query, engine)
    
    return df


def get_job_title_list(engine, search_term=None):
    """
    Returns saved job titles that fit search_term as a list
    
    Args:
        engine          = database object
        search_term : str   = term to searched with a SQL LIKE statement
    Return 
        titles_list : list = list of all saved job titles that fits search_term
    """
    df = get_job_title_df(engine, search_term)
    titles_list = df.loc[:, 'name'].to_list()
    
    return titles_list


def get_experience_df(engine):
    """
    Returns saved experience classes as DataFrame
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all saved experience classes
    """
    query = "SELECT * FROM experience"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_experience_list(engine):
    """
    Returns saved experience classes as list
    
    Args:
        engine          = database object
    Return 
        exp_list : list = list of all saved experience classes
    """
    df = get_experience_df(engine)
    exp_list = df.loc[:, 'level'].to_list()
    
    return exp_list


def get_currency_symbol_df(engine):
    """
    Returns saved currency smybols as DataFrame, does not include the id
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all saved currency smybols
    """
    query = "SELECT symbol FROM currency"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_currency_symbol_list(engine):
    """
    Returns saved currency smybols as list, does not include the id
    
    Args:
        engine           = database object
    Return 
        curr_list : list = list of all saved currency smybols
    """
    df = get_currency_symbol_df(engine)
    curr_list = df.loc[:, 'symbol'].to_list()
    
    return curr_list


def get_data_source_name_df(engine):
    """
    Returns saved data source names as DataFrame, does not include the id
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all data source names
    """
    query = "SELECT name FROM data_source"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_data_source_name_list(engine):
    """
    Returns saved currency smybols as list, does not include the id
    
    Args:
        engine           = database object
    Return 
        ds_list : list = list of all data source names
    """
    df = get_data_source_name_df(engine)
    ds_list = df.loc[:, 'name'].to_list()
    
    return ds_list


def get_skill_df(engine):
    """
    Returns all saved skills as DataFrame
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all saved skills
    """
    query = "SELECT * FROM skill_list"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_skill_list(engine):
    """
    Returns all saved skills as list
    
    Args:
        engine            = database object
    Return 
        skill_list : list = list of all saved skills
    """
    df = get_skill_df(engine)
    skill_list = df.loc[:, 'name'].to_list()
    skill_list = [entry.capitalize() for entry in skill_list]
    
    return list(set(skill_list))


def get_job_category_df(engine):
    """
    Returns all job categories as DataFrame
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all job categories
    """
    query = "SELECT * FROM job_category"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_job_category_list(engine):
    """
    Returns all job categories as list
    
    Args:
        engine          = database object
    Return 
        cat_list : list = list of all job categories
    """
    df = get_job_category_df(engine)
    cat_list = df.loc[:, 'name'].to_list()
    
    return cat_list


def get_location_df(engine):
    """
    Returns all locations as DataFrame
    This includes:
    country
    region
    city
    city_district
    area_code
    state
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all locations
    """
    query = "SELECT * FROM location"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_country_df(engine):
    """
    Returns all countries as DataFrame
    
    Args:
        engine           = database object
    Return 
        df : DataFrame   = DataFrame of all job categories
    """
    query = "SELECT DISTINCT country FROM location"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_country_list(engine):
    """
    Returns all countries as list
    
    Args:
        engine               = database object
    Return 
        country_list : list  = list of all job categories
    """
    df = get_country_df(engine)
    country_list = df.loc[:, 'country'].to_list()
    country_list = [entry.title() for entry in country_list]
    
    return list(set(country_list))


def get_city_df(engine, country=None):
    """
    Returns all cities as DataFrame
    You should specify the country, however it does work without
    
    Args:
        engine          = database object
        country : str   = name of country for which we want the cities
    Return 
        df : DataFrame   = DataFrame of all cities for a given country/all countires
    """
    query = "SELECT DISTINCT city FROM location"
    if country:
        query += f" WHERE country = '{country}'"
    df = pd.read_sql_query(query, engine)
    
    return df


def get_city_list(engine, country=None):
    """
    Returns all cities as a list
    You should specify the country, however it does work without
    
    Args:
        engine           = database object
        country : str    = name of country for which we want the cities
    Return 
        city_list : list   = list of all cities for a given country/all countires
    """
    df = get_city_df(engine, country)
    city_list = df.loc[:, 'city'].to_list()
    
    return city_list


def get_data(engine, limit=None, date=None, country=None):
    """
    Get all saved data, name of country can be specified
    Args:
        engine                = database object
        limit : int           = how many rows do we want
        date : date           = oldest date of rows to include
        country : str         = country to get data from
    Returns:
        df : DataFrame      =  complete data sets
    """

    results = dict()
        
    # get job offers
    job_offer_query = "SELECT * FROM job_offer"
    if date:
        job_offer_query += f" WHERE published >= '{date}'"
        if country:
            job_offer_query += f" AND location_id = (SELECT l_id FROM location WHERE country = '{country}')"
    elif country:
        job_offer_query += f" WHERE location_id = (SELECT l_id FROM location WHERE country = '{country}')"
    if limit:
        job_offer_query += f" LIMIT {limit}"
    results['job_offer_df'] = pd.read_sql_query(job_offer_query, engine)

    
    queries = [
    ("SELECT * FROM job_title", "titles_df"),
    ("SELECT * FROM currency", "curr_df"),
    ("SELECT * FROM experience", "exp_df"),
    ("SELECT * FROM data_source", "ds_df"),
    ("SELECT * FROM location", "loc_df"),
    ("SELECT * FROM skill_list", "skills_df"),
    ("SELECT * FROM job_category", "cats_df"),
    ("SELECT * FROM job_to_skills", "job2skill_df"),
    ("SELECT * FROM job_to_categories", "job2cats_df")
    ]

    # make queries for dim and link tables
    for query, df_name in queries:
        df = pd.read_sql_query(query, engine)
        results[df_name] = df  

    # basis of merge is job_offer
    final_df = results['job_offer_df']
    
    # merge dimension tables
    final_df = pd.merge(final_df, results['titles_df'], how="left", left_on="job_title_id", right_on="jt_id")
    final_df = pd.merge(final_df, results['curr_df'], how="left", left_on="currency_id", right_on="c_id")
    final_df = pd.merge(final_df, results['exp_df'], how="left", left_on="experience_id", right_on="e_id")
    final_df = pd.merge(final_df, results['ds_df'], how="left", left_on="data_source_id", right_on="ds_id")
    final_df = pd.merge(final_df, results['loc_df'], how="left", left_on="location_id", right_on="l_id")
    
    # merge link tables
    merged_skills_df = pd.merge(results['job2skill_df'], results['skills_df'], left_on='skill_id', right_on='sl_id', how='left')
    merged_cats_df = pd.merge(results['job2cats_df'], results['cats_df'], left_on='cat_id', right_on='jc_id', how='left')
    
    
    # make lists and merge
    grouped_skills = merged_skills_df.groupby('job_id')['name'].apply(list).reset_index()
    grouped_cats = merged_cats_df.groupby('job_id')['name'].apply(list).reset_index()
    
    final_df = pd.merge(final_df, grouped_skills, how='left', left_on='jo_id', right_on='job_id', suffixes=('_sleft', '_sright'))
    final_df = pd.merge(final_df, grouped_cats, how='left', left_on='jo_id', right_on='job_id', suffixes=('_cleft', '_cright'))
    
    # drop redundant columns & rename
    final_df = final_df.drop(columns=["job_title_id", "jo_id", "currency_id", "location_id", "job_id_cleft", "job_id_cright", 
                                      "jt_id", "c_id", "l_id", "data_source_id", "experience_id", "e_id", "ds_id"])
    final_df = final_df.rename(columns={'name_sright': 'skills', 'name': 'categories', 'name_sleft': 'data_source_name', 
                                        'name_y': 'currency_name', 'symbol': 'currency_symbol', 'name_x': 'job_title'})
    
    return final_df


if __name__ == "__main__":
    engine = connect_db(
    idb.POSTGRES_USER,
    idb.POSTGRES_PASSWORD,
    idb.POSTGRES_HOST,
    idb.POSTGRES_PORT,
    idb.POSTGRES_DBNAME)
    
    #print(get_job_title_df(engine))
    #print(get_job_title_list(engine))
    print(get_job_title_list(engine, search_term='Data'))
    #print(get_experience_df(engine))
    #print(get_experience_list(engine))
    #print(get_currency_symbol_df(engine))
    #print(get_currency_symbol_list(engine))
    #print(get_data_source_name_df(engine))
    #print(get_data_source_name_list(engine))    
    #print(get_skill_df(engine))
    #print(get_skill_list(engine))
    #print(get_job_category_df(engine))
    #print(get_job_category_list(engine))
    #print(get_location_df(engine))
    #print(get_country_df(engine))
    #print(get_country_list(engine))
    #print(get_city_df(engine))
    #print(get_city_list(engine))
    print(get_city_list(engine, country='USA'))
    print(get_data(engine))