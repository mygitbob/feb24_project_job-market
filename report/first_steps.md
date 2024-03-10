## First steps
-   After getting data samples as a groupe you should decide :
-   The different sources of data
-   The business problem to address with the data
	
	form project description:
	
			which sectors recruit the most, what skills
			are required, which cities are the most active, etc. ?


-   The required optional pre-processing to apply
-   The form of the product to build to answer the business problem (dashboard or API --> consume a ML model)
-   ![:warnung:](https://a.slack-edge.com/production-standard-emoji-assets/14.0/google-medium/26a0-fe0f.png)  Write the report to sum-up all these points --> The form could be a notebook \ google document or word \ PDF

## Data found on various locations
### Adzuna
#### API Documentation
https://developer.adzuna.com/overview
we can get historical salary data with the api

**web interface**:
- location
- company (no profiles)
- estimated salary (for jobs in US, missing for example for jobs in Germany)
- job category
- date posted
- salary
- remote/flexibel
- employment type
- hours

### Muse
#### API Documentation
https://www.themuse.com/developers/api/v2

**web interface**:
- job category
- company ( link to company profile )
- location
- date posted
- experience level 
- remote/flexibel 
- company type 
- company size
- perks and benefit 
- diversity 

### LinkedIn
- job category
- type of contract
- location
- date posted 
- company ( link to company profile )
- job experience
- remote/flexibel
- scope of activity
- commitment

### Welcomt to the jungle
- job category
- type of contract
- location
- salary
- company ( link to company profile )
- remote/flexibel
- date posted
- start date (optional)
- job experience (optional)
- education (optional)

## tested web scraping for following sites:
- adzuna : I tired to get a job description from the job list of the api response -> works fine but has no salary data (maybe other job offers contain salary info ?)
- welcometothe jungel: I tried the web search for minimum salary, filter is availible for USA but not for UK or Ireland, 
	tried to search US for data engineer & minimum salary -> no hits
	searched USA for software engineer & minimum salary -> 3 hits
	tried to search world wide -> Error (in my browser, no scripting involved)
- indeed : 403 -> do not like robots ?!
- glassdoor : 403 -> do not like robots ?!
- linkedin . 409 -> do not like robots ?! they have good data on salary and skills per job