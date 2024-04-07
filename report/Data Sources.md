## Data Sources used in the project
### okjob.io
Data is collected via API call. The maximum amount of data is 925 data sets. Data is updated every 4 days. HMTL Descriptions of the job offers are saved in a subfolder
to allow later text mining for skills and job categories.
### muse.com
Data is collected via API call. The maximum amount of data is 2000 data sets. Update frequency unkown at the moment.
### reed.co.uk
Data is collected via API call. Most of the job offers are from the United Kingdom. Maximum amount of single API is 10000 data sets. However we can call the API for a specific location
and the maximum amount is only for a single searched location. The source has about 4000 different locations (all UK psotcodes and a few foreign countires). This leeds to huge amounts of data.
It has to be carefully checked for duplicates. Language required by all job offers seems to be english. Update frequency currently unkown.
