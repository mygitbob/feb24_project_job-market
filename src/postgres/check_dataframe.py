import numpy as np
import pandas as pd


# DataFrame must include these keys
mandatory_keys = [
    "source_id",                   
    "job_title_name",              
    "published",                   
    "salary_min",                  
    "salary_max",                  
    "currency_symbol",             
    "location_country",            
    "data_source_name",         
    "joboffer_url"
]


def trim_strings(df):
    """
    Strips all string values of a DataFrame, works if value is a simple list, 
    strips all members of that list
    Args:
        DataFrame whose values have to be stripped
    Returns:
        DataFrame with stripped string values
    """
    if isinstance(df, pd.DataFrame):
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    elif isinstance(df, pd.Series):
        df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def check_keys(df):
    """
    Checks if the DatFrame contains all required keys.
    If the return value is an empty list -> no required keys missing
    Args:
        DataFrame to check
    Returns:
        missing_keys : list   = list of all missing required keys 
    """
    missing_keys = [key for key in mandatory_keys if key not in df.columns]
    return missing_keys


def check_values(df):
    """
    Checks if all values of a DatFrame fullfill the requirements.
    If the return value is an empty list -> no errors found
    Args:
        DataFrame to check
    Returns:
        errors : list   = list of errors with the index a the row(s) 
    """
    errors = []

    # Check column "source_id"
    if 'source_id' in df.columns and not all(df['source_id'].apply(lambda x: isinstance(x, str) or pd.isna(x) or len(x) <= 20)):
        for index, value in df.loc[~df['source_id'].apply(lambda x: isinstance(x, str) or pd.isna(x) or len(x) <= 20)].iterrows():
            errors.append(
                f"Invalid value '{value['source_id']}' in 'source_id' column at index {index}.")

    # Check column "job_title_name"
    if not all(df['job_title_name'].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0 and len(x) <= 50)):
        for index, value in df.loc[~df['job_title_name'].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0 and len(x) <= 50)].iterrows():
            errors.append(
                f"Invalid value '{value['job_title_name']}' in 'job_title_name' column at index {index}.")

    # Check column "experience_level"
    if 'experience_level' in df.columns and not all(df['experience_level'].apply(lambda x: isinstance(x, str) or pd.isna(x) or len(x) <= 20)):
        for index, value in df.loc[~df['experience_level'].apply(lambda x: isinstance(x, str) or pd.isna(x) or len(x) <= 20)].iterrows():
            errors.append(
                f"Invalid value '{value['experience_level']}' in 'experience_level' column at index {index}.")

    # Check column "published"
    if not pd.api.types.is_datetime64_any_dtype(df['published']):
        errors.append("Column 'published' must contain datetime values.")

    # Check columns "salary_min" and "salary_max"
    if not (pd.api.types.is_integer_dtype(df['salary_min']) & (df['salary_min'] > 0)).all() or not (pd.api.types.is_integer_dtype(df['salary_max']) & (df['salary_max'] > 0)).all():
        for index, value in df.loc[~(pd.api.types.is_integer_dtype(df['salary_min']) & (df['salary_min'] > 0)) | ~(pd.api.types.is_integer_dtype(df['salary_max']) & (df['salary_max'] > 0))].iterrows():
            errors.append(
                f"Invalid values '{value['salary_min']}' or '{value['salary_max']}' in 'salary_min' or 'salary_max' column at index {index}.")

    # Check column "currency_symbol"
    if not all(df['currency_symbol'].apply(lambda x: isinstance(x, str) and 1 <= len(x.strip()) <= 3)):
        for index, value in df.loc[~df['currency_symbol'].apply(lambda x: isinstance(x, str) and 1 <= len(x.strip()) <= 3)].iterrows():
            errors.append(
                f"Invalid value '{value['currency_symbol']}' in 'currency_symbol' column at index {index}.")

    # Check columns "location_country", "data_source_name", and "joboffer_url"
    for col in ['location_country', 'data_source_name', 'joboffer_url']:
        if col in df.columns and not all(df[col].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0 and len(x) <= 50)):
            for index, value in df.loc[~df[col].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0 and len(x) <= 50)].iterrows():
                errors.append(
                    f"Invalid value '{value[col]}' in '{col}' column at index {index}.")

    # Check optional columns "location_region", "location_city", "location_city_district", and "location_area_code"
    optional_location_cols = [
        'location_region', 'location_city', 'location_city_district', 'location_area_code']
    for col in optional_location_cols:
        if col in df.columns and not all(df[col].apply(lambda x: isinstance(x, str) or pd.isna(x) or len(x) <= 50)):
            for index, value in df.loc[~df[col].apply(lambda x: isinstance(x, str) or pd.isna(x) or len(x) <= 50)].iterrows():
                errors.append(
                    f"Invalid value '{value[col]}' in '{col}' column at index {index}.")

    # Check optional list columns "skills" and "categories"
    optional_list_cols = ['skills', 'categories']
    for col in optional_list_cols:
        if col in df.columns:
            for index, row in df.iterrows():
                if isinstance(row[col], list):
                    for item_index, item in enumerate(row[col]):
                        if not isinstance(item, str):
                            errors.append(
                                f"Invalid value '{item}' in '{col}' column at index {index}, item index {item_index}: must be a string.")
                        elif len(item) > 50:
                            errors.append(
                                f"String value '{item}' in '{col}' column at index {index}, item index {item_index} is longer than 50 characters.")

    return errors
