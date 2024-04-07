## Postgres for Docker 
This will change in the future but it works for now.
We have to look into the attached volume and it´s configuration, at the moment it uses the
default settings.

```shell
docker run --name jobmarket_sql_container -e POSTGRES_PASSWORD=feb24 -d -p 5432:5432 postgres
```
If you try this under Windows, strart `Docker Desktop` first.

For more details look in the src/postgres/example folder

## Requirements for data to be inserted into postgres
Data has to be in a DataFrame with the following columns:
```python
df.columns=[
    "source_id",                      # int or greater
    "job_title_name",                 # string, must not be empty
    "experience_level",               # optional string
    "published",                      # date > 2000-01-01
    "salary_min",                     # int > 0
    "salary_max",                     # int > 0
    "currency_symbol",                # string, 1 <= length <=3 
    "currency_name",                  # optional string
    "location_country",               # string, must not be empty
    "location_region",          # optional string
    "location_city",            # optional string
    "location_city_district",   # optional string
    "location_area_code",       # optional string
    "data_source_name",         # string, must not be empty
    "data_source_url",          # string, must not be empty
    "skills",                   # optional, when given is either an empty list or must contain non empty strings
    "categories"                # optional, when given is either an empty list or must contain non empty strings
]
```
The optional fields dont have to be included in DataFrame.
For the maximum allowed length of string values see DataModel in the report folder.
The postgres folder contains a script named `check_dataframe.py` that has the function `check_values` and `check_keys`.
This will check the DataFrame before trying to insert it into the db if its keys and values fullfill
the requirements.