# feb24_project_job-market
### Ressources
job sites with api
https://publicapis.io/search?q=jobs

glasddor has also data on job salaries:
https://scrapingrobot.com/blog/glassdoor-api/#Scale%20API%20Glassdoor

SALARY SURVEYS AND RESOURCES
https://economics.virginia.edu/salary-surveys-and-resourcesgit

### tranform raw data and extract jobs
`jq '[.[] | select(has("results")) | .results[]]' < data/raw/adzuna_raw_joblist.<page<number> | multiple_pages_<first>_<last>>.<timestamp>.json  > data/raw/adzuna_joblist__all_entries.json `
`jq '[.[] | select(has("results")) | .results[]]' < data/raw/muse_raw_joblist.<page<number> | multiple_pages_<first>_<last>>.<timestamp>.json > data/raw/muse_joblist_all_entires.json`
`jq ' .jobs ' < data/raw/joodle_raw_joblist.<timestamp>.json > data/raw/joodle_joblist_all_entries.json`

### get single job
` jq '.[<number>]' < data/raw/adzuna_joblist_all_entries.json  > data/raw/adzuna_job_entry_<number>.json`  
same for muse
` jq '.[<number>]' < data/raw/joodle_joblist_all_entries.json`