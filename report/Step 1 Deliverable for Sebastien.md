

# Salary Estimation App Development Report

## Introduction

This report introduces a newly developed application by Andreas Wagner, Boris Tsonkov, and Yue Wang. The application was developed for job posters and job seekers to rectify a common problem encountered during job posting: an improved way of making estimates on salaries with a better degree of accuracy. The application leverages a Machine Learning (ML) model to give end-users an estimate of their probable salaries, leading towards better, more informative career choices.

### Objective

Follow the steps provided in the project description [here](https://docs.google.com/document/d/1Z_Ojvq3D2yJxojpT6ghsC1YGwV2NL9PI3XjPT9esAzs/edit).


## Data Sources and Collection

### Primary Data Sources

This application relies on the data scraped from several popular job boards, treating each of them as an essential source of scraping salary information and job descriptions. Thus, the following sources for data scraping have been selected:

- **Indeed.com**: 

- **Glassdoor.com**: 

- **LinkedIn.com**: 

Example of data collection: Indeed.com collects data about the job title, name of the company, location, description of the job, and the salary. Similar datasets are collected from Glassdoor.com and LinkedIn.com in order to make the database rich so that it can be used for analysis.

### Secondary Data Sources
Once trained, the model's accuracy and reliability will be tested using data from Adzuna.com and Themuse.com. This validation step is critical for ensuring that the app performs well across diverse job postings and market conditions.

- Example Job Posting on The Muse - https://github.com/mygitbob/feb24_project_job-market/blob/main/data/processed/muse_job_entry_0.json
- Example Job Posting on Adzuna - https://github.com/mygitbob/feb24_project_job-market/blob/main/data/processed/adzuna_job_entry_0.json



## Data Processing and Machine Learning Model
### Data Cleaning and Preprocessing

First, before it goes through any of the cleaning and preprocessing stages, the following data should be collected and prepared for training the ML model:

- Removing duplicate entries

- Handling missing values

- Normalizing job titles and company names - Extracting and standardizing salary information

**Optional Preprocessing Steps:**  These may be utilized to provide more detail into the preprocess method, particularly techniques like text normalization and feature engineering, which allow improvement in the performance of the models.

### Machine Learning Model Development 
The core of the app is the development of an advanced Machine Learning model that can predict salaries based on job postings. We will cover this in Step 3.
#### Model Training

The training process will involve:

- Splitting the data into training and validation sets

- Selecting appropriate features for salary prediction

- Choosing and tuning a suitable ML algorithm (e.g., regression, random forest, neural networks) 

#### Prediction and Validation 
The model will then be validated by use of the datasets from Adzuna.com and Themuse.com to measure its accuracy and reliability. This is going to give a high degree of confidence that the app will produce useful results across a wide range of jobs and market conditions. 



