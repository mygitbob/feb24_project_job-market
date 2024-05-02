# Salary Estimation App Development Report

## Introduction

This report introduces a newly developed application by Andreas Wagner, Boris Tsonkov, and Yue Wang. The application was developed for job posters and job seekers to rectify a common problem encountered during job posting: an improved way of making estimates on salaries with a better degree of accuracy. The development of the application was foccused mainly on the ETL process that is relevant for Data Engineering experience. The application also leverages a Machine Learning (ML) model to give end-users an estimate of their probable salaries, leading towards better, more informative career choices. We provided a simple yet effficient API interface to access the trained model and we zoomed specifically on Data-related job postings.

**Deployment documentation** - Follow the steps provided in the readme file [here](https://github.com/mygitbob/feb24_project_job-market/blob/main/README.md).


## Data Sources

This application relies on job boards with public API, treating each of them as an essential source of salary information and job descriptions. The list we evaluated at the start - arbeitnow.com, jobicy.com, jooble.org, okjob.io, reed.co.uk, themuse.com, and adzuna.com. As well as Indeed.com, Glassdoor.com, LinkedIn.com, but theese providers have protection agaist data scraping. 


 We pivoted toward sources with open APIs that won't put any obstacles to obtain the data. Thus, the following sources have been selected:
### Samples


- **[okjob.io](https://github.com/mygitbob/feb24_project_job-market/blob/main/src/unused/raw_sample_data/okjob_raw.json)**

{
  "range": "Sheet1!A1:N20",
  "majorDimension": "ROWS",
  "values": [
    [
      "Company-ID",
      "LinkedIn-Job-Link",
      "Company-Name",
      "Job-Title",
      "Location",
      "Job-Description",
      "Apply-Link",
      "Region",
      "Job-Type",
      "Job-Tags",
      "Job-Category",
      "Hours",
      "Salary-Min",
      "Salary-Max"
    ],
    [
      "1810",
      "https://www.linkedin.com/jobs/view/strategic-account-executive-at-signifyd-3762391942",
      "Signifyd",
      "Strategic Account Executive",
      "USA",
      "\u003ch2\u003eJob Description: Strategic Accounts Account Executive\u003c/h2\u003e\n\n\u003cp\u003eSignifyd is looking for a Strategic Accounts Account Executive to create the strategy, cadence, and execution necessary to scale revenue across our largest, high-value US-based strategic prospects and customers. In this role, ...",
      "https://www.linkedin.com/jobs/view/3762391942/",
      "North America",
      "Remote,100% Salary, Four Days",
      "eCommerce, SaaS, RiskManagement, SalesStrategy, BusinessAnalytics",
      "Sales & Account Management, Business Development",
      "32",
      "160000",
      "185000"
    ]
}

- **[reed.co.uk](https://github.com/mygitbob/feb24_project_job-market/blob/main/src/unused/raw_sample_data/reed_raw.json)** 

{
  "results": [
    {
      "jobId": 52262625,
      "employerId": 207454,
      "employerName": "The Recruitment Link Ltd",
      "employerProfileId": null,
      "employerProfileName": null,
      "jobTitle": "Design Engineer",
      "locationName": "ST145JP",
      "minimumSalary": 40000,
      "maximumSalary": 50000,
      "currency": "GBP",
      "expirationDate": "18/04/2024",
      "date": "06/03/2024",
      "jobDescription": "Our major client has plants locally and globally and are going through a period of unprecedented growth, with an order book at record levels. As they are continuing to develop and release exciting new products and pursue high growth plans, they are looking for a Design Engineer to join their UK engineering design team. Main duties To design components and systems for use on Material Handling products. To plan and manage the design of components ... ",
      "applications": 2,
      "jobUrl": "https://www.reed.co.uk/jobs/design-engineer/52262625"
    },
    {
      "jobId": 51962352,
      "employerId": 582327,
      "employerName": "ITonlinelearning Recruitment",
      "employerProfileId": null,
      "employerProfileName": null,
      "jobTitle": "Data Analyst Trainee",
      "locationName": "DA14FH",
      "minimumSalary": 30000,
      "maximumSalary": 50000,
      "currency": "GBP",
      "expirationDate": "10/04/2024",
      "date": "16/01/2024",
      "jobDescription": "Are you looking to benefit from a new career in Data Analysis? If you are detail orientated, perceptive, organised, competent, analytical and can communicate well with those around you; you could have a truly rewarding future as a Data Analyst We do this using our specialised Data Analyst career programme which looks to assist and place qualified candidates into a career pathway in Data Analysis. Please note this career program is designed for e... ",
      "applications": 45,
      "jobUrl": "https://www.reed.co.uk/jobs/data-analyst-trainee/51962352"
    }
    ]}

- **[themuse.com](https://github.com/mygitbob/feb24_project_job-market/blob/main/src/unused/raw_sample_data/muse_job_entry_0.json)**

{
  "contents": "<p>Bring your heart to CVS Health. Every one of us at CVS Health shares a single, clear purpose: Bringing our heart to every moment of your health...",
  "name": "Pharmacy Technician",
  "type": "external",
  "publication_date": "2024-03-08T12:01:41Z",
  "short_name": "pharmacy-technician-3aa6cd",
  "model_type": "jobs",
  "id": 14102864,
  "locations": [
    {
      "name": "Memphis, TN"
    }
  ],
  "categories": [
    {
      "name": "Healthcare"
    }
  ],
  "levels": [
    {
      "name": "Senior Level",
      "short_name": "senior"
    }
  ],
  "tags": [],
  "refs": {
    "landing_page": "https://www.themuse.com/jobs/cvshealth/pharmacy-technician-3aa6cd"
  },
  "company": {
    "id": 12096,
    "short_name": "cvshealth",
    "name": "CVS Health"
  }
}



## Architecture

The architecture of the project revolves around using Docker containers to manage the lifecycle of services for a job market database and associated applications. The process is split into distinct phases executed in specific order by a docker-compose file, to manage dependencies and ensure services execute in the correct order. Here’s a summary of how the architecture is set up:



### Containers

 #### 1. Data retrieval app

This phase serves as the foundation setup or "installation phase" and includes the following steps:

-   **Folder Structure Creation:** A script is run to create necessary directories for persistent storage needed by the Docker containers.
-   **Database Initialization:** A container for the database service is started, which includes creating the job market database. This service remains running indefinitely.
-   **Initial Data Retrieval:** Data is collected initially using a dedicated container. After the data collection is complete, this container stops.

With main.py here we can execute 2 commands:
command = 'init' 
command = 'update'. 
The only difference between the two is that the first one is using a step for the API calls where we can specify the start and the end index. Thanks to this and the sleep time we avoind breaching the API limitations because we have to accumulate a lot of data.  

We have a mechanism here that stores a 100 records per file untill the cap of 10,000 records is reached. Then we merge those files into a single one that gets stored in the persistent volume of the container.

#### 2. Transform app

Here we unify the data from the different sources and we extract useful features for the training of the ML models.

-   **Data Transformation:** Another container starts to transform the collected data and stores it in the Postgres database, then stops once complete.

#### 3. ML Model creation app

- **Connect to the DB**
- **Run the queries and return a dataframe**
- **Train the model** 

#### 4. API app

Here we initialize a container with a Fast API server.
- GET /job_titles
- GET /countries
- GET /skills
- GET /experience
- POST /make_prediction



### Dataflow

[URL to the image above](https://photos.app.goo.gl/2cpWqp9vjfd3rkQ7A)

#### Overview of Data Transformation Script

**Purpose**: The script transforms raw job listing data, adjusts salary figures to a standard yearly format, and categorizes jobs based on title and description to better fit into a structured database.

**Key Components**:

1.  **Data Loading**:
    Loads raw data from the merged CSV files and passes it as dataframes for further trnsformations. The merged source files will be deleted once the transformation is done and the data is loaded in the database.
2.  **Salary Transformation**:    
    -   The `determine_salary_period` function identifies salary periods like "per hour", "per day", "per week", "per month", "ph", "pd" by using a regex to match the given periods to the job descriptions.
    -   The `transform_salary_to_yearly` function converts salaries to their annual equivalents using specified conversion rates, ensuring standardized salary data.
  conversion_rates = {  
  "per year": 1,  
  "per month": 12,  
  "per week": 52,  
  ...
}
3.  **Job Categorization/Classification**:
    Here we create new columns that will be used later as features for our model training.
    -   The `categorize_seniority` function classifies jobs into seniority levels (e.g., Senior, Junior) based on keywords in job titles.
    -   The `categorize_by_keywords` function extracts and records specific skills and sites from job titles and descriptions.
    -   Job titles are further categorized based on predefined keyword lists through the `categorize_job_titles` function. To reduce the variety of the titles so our model is not very heavy, we manually created a small number of relevant job categories. 
4.  **Dataframe Transformation**:
    
    -   The script cleans and deduplicates data, particularly in the skills and job-site fields, to prevent redundancy and maintain clean data sets. For example, `hybrid, remote` and `remote, hybrid` carry the same meaning but have to be unified for the model training. 
    -   Column names are mapped to those used in the database to align the naming conventions, and additional fields are populated as needed.
5.  **Data Storage**:
    
    -   Transformed data is stored in a PostgreSQL database, with validation checks.
    -   An error logging mechanism captures and reports any issues encountered during the transformation process.

**Automation and Error Handling**:

-   The transformation process is automated to handle batches of files, with robust error handling to manage and log issues seamlessly.


### Services 

 1. Initial setup and data collection
 2. Update pipeline, run these apps as decribed above
 3. Restart trigger that should ensure services keep running

### Docker Compose Configuration for Update Pipeline

The Docker compose setup for the update pipeline is defined to manage dependencies between containers sequentially:

-   **First Container:** ( `data_retrieval_app` image) -  Executes data retrieval, with no automatic restart.
-   **Second Container:** (`transform_app` image) - Transforms data, set to start only after the first container completes its task.
-   **Third Container:** (`model_app`) - Handles model retraining, starts after the second container has finished.

Each service is modular, contained, and executed in sequence to ensure data integrity and system stability. This architecture allows for scalable updates and maintenance while keeping critical services like the database and API continuously operational.
