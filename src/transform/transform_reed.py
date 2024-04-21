from helpers import *

from collections import defaultdict
#from pymongo import MongoClient
#from dotenv import load_dotenv
from job_categories_and_skills import *
import pandas as pd
import spacy
import json
import os
import re
import postgres_initdb
from postgres_inserts import store_dataframe


def load_df():

    load_dotenv()

    mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    mongo_host = 'localhost'
    mongo_port = '27017'
    mongo_db = 'raw_data'
    connection_string = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/'

    collection_name = 'reed_test'

    client = MongoClient(connection_string)
    db = client[mongo_db]
    collection = db[collection_name]

    # Query to select documents where none of the specified fields are empty
    query = {
        "$and": [
            {"sourceId": {"$ne": ""}},
            {"jobTitle": {"$regex": "data", "$options": "i"}},  # Case-insensitive search for "data" in jobTitle
            {"jobDescription": {"$ne": ""}},
            {"minimumSalary": {"$ne": ""}},
            {"maximumSalary": {"$ne": ""}},
            {"jobUrl": {"$ne": ""}}
        ]
    }

    # Projection to specify fields to include, adding 'jobDescription' to the projection
    projection = {
        "sourceId": 1,
        "jobTitle": 1,
        "date": 1,
        "minimumSalary": 1,
        "maximumSalary": 1,
        "jobUrl": 1,
        "currency": 1,
        "locationName": 1,
        "jobDescription": 1,
        "_id": 0
    }

    # Fetching the documents with projection
    documents = collection.find(query, projection).limit(10)
    #documents = collection.find(query, projection)

    return documents


def determine_salary_period(description, min_salary, max_salary):
    # Extract the integer part of the min_salary
    min_salary_int = re.match(r'^\d+', str(min_salary))
    if min_salary_int:
        min_salary_int = min_salary_int.group(0)
    else:
        # If no numeric part is found, the function returns "Not specified"
        return "Not specified"

    # Define possible salary periods with regex patterns to search for them
    # after the min_salary value
    salary_period_patterns = {
        "per hour": f"{min_salary_int}.*per hour",
        "per day": f"{min_salary_int}.*per day",
        "per week": f"{min_salary_int}.*per week",
        "per month": f"{min_salary_int}.*per month",
        "ph": f"{min_salary_int}.*ph",
        "pd": f"{min_salary_int}.*pd"
    }

    # Search for each period pattern in the description
    for period, pattern in salary_period_patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return period

    # If no period pattern is found, attempt to deduce the period
    # if len(str(min_salary)) >= 6 or len(str(max_salary)) >= 6:
    #     return "per year"

    return "Not specified"


def transform_salary_to_yearly(df, salary_col, period_col):
    """
    Adjusts salary values in the DataFrame to yearly equivalents based on the salary period.

    Parameters:
    - df: Pandas DataFrame containing the salary data.
    - salary_col: The name of the column containing the salary values.
    - period_col: The name of the column containing the salary period descriptions.
    """

    # Ensure the columns exist in the DataFrame
    if salary_col not in df.columns:
        raise ValueError(f"Column '{salary_col}' not found in DataFrame")
    if period_col not in df.columns:
        raise ValueError(f"Column '{period_col}' not found in DataFrame")

    # Conversion rates based on the salary period
    conversion_rates = {
        "per year": 1,
        "per month": 12,
        "per week": 52,
        "per day": 260,  # Assuming 5 working days per week
        "pd": 260,
        "per hour": 2080,  # Assuming 40 hours per week
        "ph": 2080,
        "Not specified": 1  # No change for unspecified
    }

    # Define a function to convert salary to yearly
    def salary_to_yearly(row):
        period = row[period_col]
        salary = row[salary_col]
        # Handle non-numeric salaries by returning them unmodified
        try:
            numeric_salary = float(salary)
        except ValueError:
            return salary  # Return the original salary if it's not a numeric value

        # Apply conversion based on the salary period
        if period in conversion_rates:
            return numeric_salary * conversion_rates[period]
        else:
            return numeric_salary  # Return the original salary if the period is unexpected

    # Apply the conversion function to rows
    df[salary_col + '_yearly'] = df.apply(salary_to_yearly, axis=1)

    return df


# Categorize job titles
def categorize_seniority(job_title, nlp):
    # Load the pre-trained model
    doc = nlp(job_title)
    # List of keywords (lemmas) to look for
    keywords_senior = ['strategic', 'principal', 'staff', 'lead', 'senior', 'head']
    keywords_junior = ['trainee', 'junior', 'apprentice', 'entry level']
    # Check if any token's lemma is in our keywords list
    if any(token.lemma_.lower() in keywords_senior for token in doc):
        return 'Senior'
    elif any(token.lemma_.lower() in keywords_junior for token in doc):
        return 'Junior'
    else:
        return 'Medium'


# Function to categorize job titles and descriptions by keywords, accepting a keyword list as a parameter
def categorize_by_keywords(text, keywords, nlp):
    doc = nlp(text)
    # Initialize an empty set to avoid duplicates
    keywords_found = set()
    # Check each token in the text
    for token in doc:
        # Normalize the token's text for case-insensitive matching
        token_text = token.text.lower()
        # If the normalized token is in our list of keywords, add the original token text to the set
        if token_text in [keyword.lower() for keyword in keywords]:
            keywords_found.add(token.text)
    # Return a comma-separated string of unique keywords found, or "None" if no keywords were identified
    return ', '.join(keywords_found) if keywords_found else "_NOTFOUND_"


def categorize_job_titles(job_title, keywords_title):
    # Prepare the job title: lowercase, remove special characters, and split into words
    words = re.sub('[^a-z0-9\s]', '', job_title.lower()).split()

    # Initialize a dictionary to hold the count of matches for each category
    matches = defaultdict(int)
    # Initialize a dictionary to hold the sum of indexes for matched words for tie-breaking
    index_sums = defaultdict(int)

    for category, keywords in keywords_title.items():
        for word in words:
            if word in keywords:
                matches[category] += 1
                # Sum the indexes of matched words for tie-breaking
                index_sums[category] += keywords.index(word)

    if not matches:
        return 'Other'

    # Find the category(ies) with the maximum count of matches
    max_matches = max(matches.values())
    candidates = [category for category, count in matches.items() if count == max_matches]

    # If there's a single best match, return it
    if len(candidates) == 1:
        return candidates[0]

    # If there are ties, use the sum of indexes for tie-breaking
    return min(candidates, key=lambda category: index_sums[category])


def clean_sort_and_deduplicate(text):
    if not isinstance(text, str):
        return text
    # Lowercase, strip whitespace, and split on commas
    parts = text.lower().strip().split(',')
    # Remove duplicates and sort
    cleaned_parts = sorted(set(part.strip() for part in parts))
    # Join the cleaned parts back into a single string
    return ', '.join(cleaned_parts)


def transform():
    nlp = spacy.load('en_core_web_sm')  # Or 'en_core_web_lg' for more accuracy but larger size

    documents = load_df()
    data_objects = []
    for doc in documents:
        # Determine the salary period
        salary_period = determine_salary_period(doc['jobDescription'], doc['minimumSalary'], doc['maximumSalary'])
        # Add the new field to the document
        doc['salaryPeriod'] = salary_period
        data_objects.append(doc)

    # Creating the DataFrame
    df_reed = pd.DataFrame(data_objects)

    df_reed['minimumSalary'] = pd.to_numeric(df_reed['minimumSalary'], errors='coerce')
    df_reed['maximumSalary'] = pd.to_numeric(df_reed['maximumSalary'], errors='coerce')

    df_reed.dropna(subset=['minimumSalary', 'maximumSalary'], inplace=True)

    df_reed = df_reed[df_reed['minimumSalary'] > 0]

    df_reed.loc[df_reed['minimumSalary'] < 70, 'salaryPeriod'] = 'per hour'
    df_reed.loc[
        (df_reed['minimumSalary'] >= 70) & (
                df_reed['minimumSalary'] < 999), 'salaryPeriod'] = 'per day'

    for column in ['minimumSalary', 'maximumSalary']:
        df_reed_salary_tr = transform_salary_to_yearly(df_reed, column, 'salaryPeriod')
    # Apply the function to create a new column
    df_reed_salary_tr['jobLevel'] = df_reed_salary_tr['jobTitle'].apply(lambda x: categorize_seniority(x, nlp))
    # Applying the function to each row for both jobSkills and jobSite columns
    df_reed_salary_tr['jobSkills'] = df_reed_salary_tr.apply(
        lambda row: categorize_by_keywords(row['jobTitle'] + " " + row['jobDescription'], keywords_skills, nlp), axis=1)
    df_reed_salary_tr['jobSite'] = df_reed_salary_tr.apply(
        lambda row: categorize_by_keywords(row['jobTitle'] + " " + row['jobDescription'], keywords_site, nlp), axis=1)
    # Apply the function to the 'jobTitle' column and create a new 'jobCategory' column
    df_reed_salary_tr['jobCategory'] = df_reed_salary_tr['jobTitle'].apply(
        lambda x: categorize_job_titles(x, keywords_title))

    # Apply the modified function to sort the terms within the 'jobSite' column using .loc
    df_reed_salary_tr.loc[:, 'jobSite'] = df_reed_salary_tr['jobSite'].apply(clean_sort_and_deduplicate)

    # Mapping of source column names to postgres db column names
    column_mappings = {
        'sourceId': 'source_id',
        'jobTitle': 'job_title_name',
        'jobLevel': 'experience_level',
        'date': 'published',
        'minimumSalary': 'salary_min',
        'maximumSalary': 'salary_max',
        'jobUrl': 'joboffer_url',
        'currency': 'currency_symbol',
        'locationName': 'location_country',
        'jobSite': 'job_site',
        'jobSkills': 'skills',
        'jobCategory': 'categories'
    }

    # Define additional columns and default values
    additional_columns = {
        'data_source_name': 'reed'
    }

    # Rename columns based on the mapping
    df_reed_salary_tr.rename(columns=column_mappings, inplace=True)

    # Define the new order of columns, add missing ones with default values
    df_reed_postgres = df_reed_salary_tr[
        [column_mappings.get(col, col) for col in column_mappings.keys()]
    ]

    # Add additional columns with default values
    for col, default_value in additional_columns.items():
        df_reed_postgres[col] = default_value

    # Replace specific column values
    df_reed_postgres['location_country'] = 'United Kingdom'

    df_reed_postgres['published'] = pd.to_datetime(df_reed_postgres['published'], format='%d/%m/%Y')

    # Ensure salaries are integers and greater than 0
    df_reed_postgres['salary_min'] = pd.to_numeric(df_reed_postgres['salary_min'], errors='coerce').fillna(0).astype(
        int)
    df_reed_postgres['salary_max'] = pd.to_numeric(df_reed_postgres['salary_max'], errors='coerce').fillna(0).astype(
        int)
    df_reed_postgres = df_reed_postgres[(df_reed_postgres['salary_min'] > 0) & (df_reed_postgres['salary_max'] > 0)]

    # Set the types for other fields as strings
    df_reed_postgres['source_id'] = df_reed_postgres['source_id'].astype(str)
    df_reed_postgres['experience_level'] = df_reed_postgres['experience_level'].astype(str)
    df_reed_postgres['joboffer_url'] = df_reed_postgres['joboffer_url'].astype(str)
    df_reed_postgres['currency_symbol'] = df_reed_postgres['currency_symbol'].astype(str)
    df_reed_postgres['location_country'] = df_reed_postgres['location_country'].astype(str)
    df_reed_postgres['data_source_name'] = df_reed_postgres['data_source_name'].astype(str)
    df_reed_postgres['skills'] = df_reed_postgres['skills'].str.split(', ')
    df_reed_postgres['categories'] = df_reed_postgres['categories'].str.split(', ')
    df_reed_postgres['job_site'] = df_reed_postgres['job_site'].astype(str)


    print(df_reed_postgres.head())

    errors = store_dataframe(df_reed_postgres, check_df=False)
    print(errors)
    
if __name__ == "__main__":
    df_list = get_raw_data(r"C:\Users\winbob\datasientest\feb24_project_job-market\data\processed\reed.co.uk\merged", delete=False)
    for df in df_list[:1]:
        data_objects = []
        for _, doc in df.iterrows():
            # Determine the salary period
            salary_period = determine_salary_period(doc['jobDescription'], doc['minimumSalary'], doc['maximumSalary'])
            # Add the new field to the document
            doc['salaryPeriod'] = salary_period
            data_objects.append(doc)
        nlp = spacy.load('en_core_web_sm')
        print(len(data_objects))
        
        df['minimumSalary'] = pd.to_numeric(df['minimumSalary'], errors='coerce')
        df['maximumSalary'] = pd.to_numeric(df['maximumSalary'], errors='coerce')
        
        df.dropna(subset=['minimumSalary', 'maximumSalary'], inplace=True)

        df = df[df['minimumSalary'] > 0]

        df.loc[df['minimumSalary'] < 70, 'salaryPeriod'] = 'per hour'
        df.loc[(df['minimumSalary'] >= 70) & (
                df['minimumSalary'] < 999), 'salaryPeriod'] = 'per day'

        for column in ['minimumSalary', 'maximumSalary']:
            df_reed_salary_tr = transform_salary_to_yearly(df, column, 'salaryPeriod')
        print(df_reed_salary_tr.columns)
        
        # Apply the function to create a new column
        df_reed_salary_tr['jobLevel'] = df_reed_salary_tr['jobTitle'].apply(lambda x: categorize_seniority(x, nlp))
        # Applying the function to each row for both jobSkills and jobSite columns
        df_reed_salary_tr['jobSkills'] = df_reed_salary_tr.apply(
            lambda row: categorize_by_keywords(row['jobTitle'] + " " + row['jobDescription'], keywords_skills, nlp), axis=1)
        df_reed_salary_tr['jobSite'] = df_reed_salary_tr.apply(
            lambda row: categorize_by_keywords(row['jobTitle'] + " " + row['jobDescription'], keywords_site, nlp), axis=1)
        # Apply the function to the 'jobTitle' column and create a new 'jobCategory' column
        df_reed_salary_tr['jobCategory'] = df_reed_salary_tr['jobTitle'].apply(
            lambda x: categorize_job_titles(x, keywords_title))

        # Apply the modified function to sort the terms within the 'jobSite' column using .loc
        df_reed_salary_tr.loc[:, 'jobSite'] = df_reed_salary_tr['jobSite'].apply(clean_sort_and_deduplicate)
        print(df_reed_salary_tr.columns)
        
        column_mappings = {
            'id': 'source_id',
            'jobTitle': 'job_title_name',
            'jobLevel': 'experience_level',
            'date': 'published',
            'minimumSalary': 'salary_min',
            'maximumSalary': 'salary_max',
            'jobUrl': 'joboffer_url',
            'currency': 'currency_symbol',
            'locationName': 'location_country',
            'jobSite': 'job_site',
            'jobSkills': 'skills',
            'jobCategory': 'categories'
        }
        
        # Define additional columns and default values
        additional_columns = {
            'data_source_name': 'reed'
        }

        # Rename columns based on the mapping
        df_reed_salary_tr.rename(columns=column_mappings, inplace=True)

        # Define the new order of columns, add missing ones with default values
        df_reed_postgres = df_reed_salary_tr[
            [column_mappings.get(col, col) for col in column_mappings.keys()]
        ]

        # Add additional columns with default values
        for col, default_value in additional_columns.items():
            df_reed_postgres[col] = default_value

        # Replace specific column values
        df_reed_postgres['location_country'] = 'United Kingdom'

        df_reed_postgres['published'] = pd.to_datetime(df_reed_postgres['published'], format='%d/%m/%Y')

        # Ensure salaries are integers and greater than 0
        df_reed_postgres['salary_min'] = pd.to_numeric(df_reed_postgres['salary_min'], errors='coerce').fillna(0).astype(
            int)
        df_reed_postgres['salary_max'] = pd.to_numeric(df_reed_postgres['salary_max'], errors='coerce').fillna(0).astype(
            int)
        df_reed_postgres = df_reed_postgres[(df_reed_postgres['salary_min'] > 0) & (df_reed_postgres['salary_max'] > 0)]

        # Set the types for other fields as strings
        df_reed_postgres['source_id'] = df_reed_postgres['source_id'].astype(str)
        df_reed_postgres['experience_level'] = df_reed_postgres['experience_level'].astype(str)
        df_reed_postgres['joboffer_url'] = df_reed_postgres['joboffer_url'].astype(str)
        df_reed_postgres['currency_symbol'] = df_reed_postgres['currency_symbol'].astype(str)
        df_reed_postgres['location_country'] = df_reed_postgres['location_country'].astype(str)
        df_reed_postgres['data_source_name'] = df_reed_postgres['data_source_name'].astype(str)
        df_reed_postgres['skills'] = df_reed_postgres['skills'].str.split(', ')
        df_reed_postgres['categories'] = df_reed_postgres['categories'].str.split(', ')
        df_reed_postgres['job_site'] = df_reed_postgres['job_site'].astype(str)

        store_dataframe(df_reed_postgres, check_df=False)
        
    