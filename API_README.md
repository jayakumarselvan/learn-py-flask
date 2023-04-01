# Initial setup for Flask

Below the steps for MAC OS / Linux
Create an environment
```bash
$ python3 -m venv venv
```
Activate the environment
```bash
$ . venv/bin/activate
```
Install Flask and dependency libraries
```bash
$ pip install -r requirement.txt
```
Start a Application
```bash
$ flask run
```
Reference link: 
https://flask.palletsprojects.com/en/2.2.x/installation/


# API
Base URL: `http://127.0.0.1:5000/api/v1`
#### Listing the average prices for each day


 <summary><code>GET</code>: <code><b>/rates</b></code></summary>

##### Parameters

> | name      |  type     | data type | description |
> |-----------|-----------|-----------|-------------|
> | date_from | required | string - date format (yyyy-mm-dd) | From Date |
> | date_to | required | string - date format (yyyy-mm-dd) | To Date |
> | origin | required | string | Origin value will be port codes or region slugs |
> | destination | required | string | Destination value will be port codes or region slugs  |
> | page | optional | int | current page number  |
> | limit | optional | int | per page limit  |

##### Responses

> | http code | content-type | response |
> |-----------|--------------|----------|
> | `200` | `application/json` | JSON String |
> | `400` | `application/json` | JSON String |

##### Example #1 - without pagination cURL

> ```javascript
> curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:5000/api/v1/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
> ```

##### Response

```bash
[
  {
    "day": "2016-01-01",
    "average_price": 1112
  },
  {
    "day": "2016-01-02",
    "average_price": 1112
  },
  {
    "day": "2016-01-03",
    "average_price": null
  },
  {
    "day": "2016-01-04",
    "average_price": null
  },
  {
    "day": "2016-01-05",
    "average_price": 1142
  },
  {
    "day": "2016-01-06",
    "average_price": 1142
  },
  {
    "day": "2016-01-07",
    "average_price": 1137
  },
  {
    "day": "2016-01-08",
    "average_price": 1124
  },
  {
    "day": "2016-01-09",
    "average_price": 1124
  },
  {
    "day": "2016-01-10",
    "average_price": 1124
  }
]
```

##### Example #2 - with pagination cURL

> ```javascript
> curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:5000/api/v1/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main&page=1&limit=5"
> ```

##### Response

```bash
[
  {
    "day": "2016-01-01",
    "average_price": 1112
  },
  {
    "day": "2016-01-02",
    "average_price": 1112
  },
  {
    "day": "2016-01-03",
    "average_price": null
  },
  {
    "day": "2016-01-04",
    "average_price": null
  },
  {
    "day": "2016-01-05",
    "average_price": 1142
  }
]
```

##### Example #3 - missing required field(s) cURL

> ```javascript
> curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:5000/api/v1/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH"
> ```

##### Response

```bash
{
  "message": "date_from, date_to, origin, and destination fields are required",
  "code": 400,
  "status": false
}
```
