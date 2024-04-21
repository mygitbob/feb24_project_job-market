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

# Columns have to be of this type
column_types = {
        "source_id": str,
        "job_title_name": str,
        "experience_level": (str, type(None)),
        "published": pd.Timestamp,
        "salary_min": int,
        "salary_max": int,
        "joboffer_url": str,
        "currency_symbol": str,
        "currency_name": (str, type(None)),
        "location_country": str,
        "location_region": (str, type(None)),
        "location_city": (str, type(None)),
        "location_city_district": (str, type(None)),
        "location_area_code": (str, type(None)),
        "location_state": (str, type(None)),
        "data_source_name": str,
        "skills": (list[str], type(None)),
        "categories": (list[str], type(None))
    }

def strip_capitalize_strings(df):
    """
    Strips and capitalize all string values of a DataFrame, works if value is a simple list, 
    strips all members of that list and capitalize them
    Args:
        DataFrame whose values have to be stripped
    Returns:
        DataFrame with stripped string values
    """
    if isinstance(df, pd.DataFrame):
        df = df.applymap(lambda x: x.strip().capitalize() if isinstance(x, str) else x)
    elif isinstance(df, pd.Series):
        df = df.apply(lambda x: x.strip().capitalize() if isinstance(x, str) else x)
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


def check_column_types(df):
    """
    Checks if all columns in a DataFrame have the correct types.
    Args:
        DataFrame to check
    Returns:
        errors : list   = list of errors with the index a the row(s) 
    """
    errors = []


    for col, col_type in column_types.items():
        if col in df.columns:
            for index, value in df.iterrows():
                if isinstance(value[col], list):
                    
                    if not all(pd.isna(item) or isinstance(item, type(col_type)) for item in value[col]):
                        errors.append(
                            f"Column '{col}' contains invalid types at index {index}.")
                else:
                    if not isinstance(value[col], type(col_type)) and not pd.isna(value[col]):
                        errors.append(
                            f"Column '{col}' contains invalid types at index {index}.")

    for col in ["skills", "categories"]:
        if col in df.columns:
            for index, value in df.iterrows():
                if isinstance(value[col], list):
                    # Filtern der NaN-Werte aus der Liste
                    cleaned_list = [item for item in value[col] if not pd.isna(item)]
                    if not all(isinstance(item, str) or item is None for item in cleaned_list):
                        errors.append(
                            f"Invalid values in '{col}' column at index {index}. Must contain only strings or None.")
                elif not pd.isna(value[col]):  # Überprüfen, ob das Attribut vorhanden ist
                    errors.append(
                        f"Invalid type in '{col}' column at index {index}. Must be a list or None.")

    return errors
    
    
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

def check_dataframe(df):
    """
    Check if DataFrame has all keys, columns have right types and values are ok
    
    Args:
        DataFrame to check
    Return:
        list with errors | empty list -> DataFrame contains no errors
    """
    res = []
    res = check_keys(df)
    if res:     # error found
        return res
    #res = check_column_types(df)
    #if res:     # error found
    #    return res
    #res = check_values(df)
    if res:     # error found
        return res
    return res  # empty list -> no errors

data_with_errors = {
        #"source_id": [1, "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "job_title_name": ["Software Engineer", "", "Project Manager", "Marketing Specialist", "Financial Analyst", "HR Manager", "Sales Representative", "Product Manager", "UX/UI Designer", "Customer Support Specialist"],
        "experience_level": ["Senior", "Junior", "Mid", "Senior", "Mid", "Junior", "Senior", "Mid", "Junior", "Mid"],
        "published": pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01"]),
        "salary_min": [60000, 1500, 0, 55000, 65000, 60000, 55000, 70000, 55000, 60000],
        "salary_max": [120000, 100000, 140000, 0, 130000, 120000, 110000, 140000, 110000, 120000],
        "currency_symbol": ["USD", "EUR", "GBP", "USD", "", "GBP", "USD", "EUR", "GBP", "USD"],
        "currency_name": ["US Dollar", "Euro", "British Pound", "US Dollar", "Euro", "British Pound", "US Dollar", "Euro", "British Pound", "US Dollar"],
        "location_country": ["USA", "Germany", "UK", None, "Germany", "", "USA", "Germany", "UK", "USA"],
        "location_region": ["West", "North", "South", "West", "North", "South", 666, "North", "South", "West"],
        "location_city": ["New York", "Berlin", "London", "New York", "Berlin", "London", "New York", "Berlin", "London", "New York"],
        "location_city_district": ["Manhattan", None, "Westminster", "Manhattan", "Mitte", "Westminster", "Manhattan", "Mitte", "Westminster", "Manhattan"],
        "location_area_code": ["NY001", "BE001", "LON001", "NY002", "BE002", "LON002", "NY003", "BE003", "LON003", "NY004"],
        "data_source_name": ["Company A", "Company B", "Company C", "Company A", "Company A", "Company A", "Company x", "", "Company x", "Company x"],
        "joboffer_url": ["http://companya.com", "http://companyb.com", "http://companyc.com", "http://companya.com", "http://companya.com", "http://companya.com", "http://companyx.com", "http://companyx.com", "", "http://companyx.com"],
        "skills": [["some skill"], ["R", "Python", "Machine Learning"], ["Project Management", "Leadership", "Communication"], ["Marketing", "SEO", "Social Media"], ["Finance", "Excel", "Financial Analysis"], ["HR Management", "Recruitment", "Employee Relations"], ["Sales", "Negotiation", "Customer Relationship Management"], ["Product Management", "Agile", "Product Development"], ["UI/UX Design", "Adobe Creative Suite", "Wireframing"], ["Customer Support", "Troubleshooting", "Ticketing System"]],
        "categories": [["a category"], ["Data Science", "Analytics", "Machine Learning"], ["Project Management", "Business", "Management"], ["Marketing", "Digital Marketing", "Advertising"], ["Finance", "Accounting", "Financial Services"], ["HR", "Management", "Human Resources"], ["Sales", "Business Development", "Marketing"], ["Product Management", "Product Development", "Agile"], ["Design", "UI/UX", "Creative"], ["Customer Support", "Customer Service", "Technical Support"]]
    }

data_with_funny_strings = {
    "column_names": [" dddTTTe", "Im ok", "dfdsfMMer "],
    "should_be_ok": [" i AM a ", "second value", "123"]
}
if __name__ == "__main__":
        import pandas as pd
        df = pd.DataFrame(data_with_errors)
        print(check_keys(df))
        #print(check_column_types(df))
        #print(check_values(df[2:4]))
        df = pd.DataFrame(data_with_funny_strings)
        print(strip_capitalize_strings(df))