# feb24_project_job-market
### Ressources
job sites with api
https://publicapis.io/search?q=jobs

glasddor has also data on job salaries:
https://scrapingrobot.com/blog/glassdoor-api/#Scale%20API%20Glassdoor

SALARY SURVEYS AND RESOURCES
https://economics.virginia.edu/salary-surveys-and-resourcesgit

### tranform raw data and extract jobs
```bash
jq '[.[] | select(has("results")) | .results[]]' < data/raw/adzuna_raw_joblist.<page<number> 
| multiple_pages_<first>_<last>>.<timestamp>.json  > data/processed/adzuna_joblist__all_entries.json 
```
```bash
jq '[.[] | select(has("results")) | .results[]]' < data/raw/muse_raw_joblist.<page<number> 
| multiple_pages_<first>_<last>>.<timestamp>.json > data/processed/muse_joblist_all_entires.json
```
```bash
jq ' .jobs ' < data/raw/joodle_raw_joblist.<timestamp>.json > data/processed/joodle_joblist_all_entries.json`
```

### get single job
```bash 
jq '.[<number>]' < data/raw/adzuna_joblist_all_entries.json  > data/processed/adzuna_job_entry_<number>.json
```
same for muse
```bash 
jq '.[<number>]' < data/raw/joodle_joblist_all_entries.json > data/processed/joodle_job_entry_<number>.json
```
