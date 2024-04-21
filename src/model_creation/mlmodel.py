from collections import Counter
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

import os
from datetime import datetime
from init import PATH_MODEL
from init import logging

def replace_skills_with_frequency_sum(skills_string, skills_frequency):
    skills_list = skills_string.split(',')
    frequency_sum = sum(skills_frequency[skill.strip()] for skill in skills_list)
    return frequency_sum

def prepare_data(df):
    all_skills = [skill.strip() for sublist in df['jobSkills'].str.split(',').tolist() for skill in sublist]
    skills_frequency = Counter(all_skills)

    df['jobSkillsSumFrequency'] = df['jobSkills'].apply(lambda x: replace_skills_with_frequency_sum(x, skills_frequency))
    df.loc[df['jobSkills'] == 'none', 'jobSkillsSumFrequency'] = 0
    return df

def train_model(postgres_df):
    preprocessed_df = prepare_data(postgres_df)

    # Define categorical and numerical feature lists
    cat_other = ['jobCategory', 'jobSite']
    num = ['jobSkillsSumFrequency']
    job_level_order = [['junior', 'medium', 'senior']]

    # Preprocessor Pipelines
    numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(drop='first', sparse_output=False))])
    job_level_transformer = Pipeline(steps=[('ordinal', OrdinalEncoder(categories=job_level_order))])

    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, num),
        ('cat', categorical_transformer, cat_other),
        ('job_level', job_level_transformer, ['jobLevel'])
    ])

    # Model Pipelines
    pipeline_min_salary = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', DecisionTreeRegressor(random_state=343))
    ])
    pipeline_max_salary = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', DecisionTreeRegressor(random_state=343))
    ])

    # Splitting data
    target_min = preprocessed_df['minimumSalary_yearly']
    target_max = preprocessed_df['maximumSalary_yearly']
    feats = preprocessed_df.drop(['minimumSalary_yearly', 'maximumSalary_yearly'], axis=1)

    X_train, X_test, y_train_min, y_test_min = train_test_split(feats, target_min, test_size=0.2, random_state=343)
    _, _, y_train_max, y_test_max = train_test_split(feats, target_max, test_size=0.2, random_state=343)

    # Fit and evaluate models
    pipeline_min_salary.fit(X_train, y_train_min)
    pipeline_max_salary.fit(X_train, y_train_max)
    min_salary_pred = pipeline_min_salary.predict(X_test)
    max_salary_pred = pipeline_max_salary.predict(X_test)

    print(f"Mean Absolute Error (Min Salary): {mean_absolute_error(y_test_min, min_salary_pred)}")
    print(pipeline_min_salary.score(X_train, y_train_min))
    print(pipeline_min_salary.score(X_test, y_test_min))
    print(f"Mean Absolute Error (Max Salary): {mean_absolute_error(y_test_max, max_salary_pred)}")
    print(pipeline_max_salary.score(X_train, y_train_max))
    print(pipeline_max_salary.score(X_test, y_test_max))

    # Save the models
    path_min = os.path.join(PATH_MODEL, 'DecisionTreeRegressor_min_salary.latest.joblib')
    path_max = os.path.join(PATH_MODEL, 'DecisionTreeRegressor_max_salary.latest.joblib')

    # check if old modles are present, if yes rename them
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        if os.path.exists(path_min):
            backup_min = os.path.join(PATH_MODEL, f'DecisionTreeRegressor_min_salary_{timestamp}.joblib')
            os.rename(path_min, backup_min)

        if os.path.exists(path_max):
            backup_max = os.path.join(PATH_MODEL, f'DecisionTreeRegressor_max_salary_{timestamp}.joblib')
            os.rename(path_max, backup_max)
    except Exception as e:
        logging.error(f"{__file__}: error renaming old models: {e}")
    
    # save new models
    try:
        joblib.dump(pipeline_min_salary, path_min)
        joblib.dump(pipeline_max_salary, path_max)
    except Exception as e:
        logging.error(f"{__file__}: error saving new models: {e}")
    else:
        logging.debug(f"{__file__}: new models trained and saved")