API can be tested at https://developer.adzuna.com/activedocs#!/adzuna/history

### GET jobs/{country}/history
#### Request URL
```
https://api.adzuna.com/v1/api/jobs/gb/history?app_id=fb3d1b6c&app_key=d1999430f1b272b9af611b798e8b0789&
location0=Uk&location1=London&location2=Central%20London
```
#### Response Body
```json
{
  "location": {
    "display_name": "Central London, London",
    "area": [
      "UK",
      "London",
      "Central London"
    ],
    "__CLASS__": "Adzuna::API::Response::Location"
  },
  "__CLASS__": "Adzuna::API::Response::HistoricalSalary",
  "month": {
    "2023-07": 53382.77,
    "2023-12": 54091.47,
    "2023-08": 52886.62,
    "2024-02": 53989.94,
    "2023-05": 53817.47,
    "2023-03": 50254.92,
    "2023-04": 54095.26,
    "2023-09": 51129.69,
    "2024-01": 54190.51,
    "2023-06": 52998.18,
    "2023-10": 52184.27,
    "2023-11": 53014.35
  }
}
```