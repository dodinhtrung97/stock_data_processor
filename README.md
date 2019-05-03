# News Headline Scrapper

Scrapes news headlines and information attached to said headlines

Applies sentiment analysis on said headlines and determine their sentiment polarity

Change `conf/config_template.ini` appropriately and rename the file to `config.ini` before running

Scope may expand in future versions

## Mode

Supports a backend API mode and an auto scrapping mode <br/>

See `Build Project`

### Automated Scrapper

Starts an automated web scrapper on the `sites` and `walking_patterns` defined in `conf/config.ini`

Communicate with clients via a websocket connection established upon connection request <br/>

#### Websocket API

An automated scrapping service that allows for multiple clients to subscribe to their requested `ticker_symbol` and scrape/update the clients on the news related to such symbols accordingly <br/>

Supports 2 user `actions`: `add_ticker` and `remove_ticker`

An input request such as:

```
{ 
    "action" : "remove_ticker", 
    "value" : "amzn"
}
```

Will receive a response such as:

```
{
    "action": "connect", 
    "actionStatus": "Success", 
    "value": "6d9309a1-76b7-4f9a-936e-2518a721681e"
}
```

Where `action` is the client requested action, `actionStatus` is the indicator of said action's successfulness, and `value` is and value that may be attached to such action. In this case it is the server assigned `uuid` for the connected client

Upon news retrieved, the server shall only send pieces of news that have not previously been updated to the clients.

```
"AMZN": {
    "CNBC": [
      {
        "source": "CNBC",
        "url": "https://www.cnbc.com/2019/04/22/us-futures-signal-lower-open-ahead-of-busy-earnings-week.html",
        "headline": "US futures signal a lower open ahead of busy earnings week",
        "date": 1555912800.0,
        "direct": false,
        "score": 0.05
      },
    ],
    "BENZINGA_HEADLINES": [
      {
        "source": "BENZINGA",
        "url": "https://www.benzinga.com/news/19/04/13560968/todays-pickup-amazon-ceasing-chinese-operations-due-to-insurmountable-domestic-rivalry",
        "headline": "Today's Pickup: Amazon Ceasing Chinese Operations Due To Insurmountable Domestic Rivalry",
        "date": 1555604119.0,
        "direct": false,
        "score": -0.041666666666666664
      },
    ],
    "BENZINGA_PARTNER": [
      {
        "source": "BENZINGA",
        "url": "https://talkmarkets.com/content/an-indecisive-market?post=218552",
        "headline": "An Indecisive Market",
        "date": 1555869600.0,
        "direct": false,
        "score": 0.0
      },
      ...
    ]
    ...
}
```
After a scrapping iteration's over, the service shall go to sleep for `SLEEP_TIME` (in seconds), defined in `conf/config.ini`

### Backend API

Found in src/controller/scrapper_controller.py

#### News Scrapper API <br/>

`/api/scrape/<news_source>/<ticker_symbol>?getDate=0&getSentiment=0`

Input: 

```
news_source: known news source (cnbc, seekingalpha, benzinga)
ticker_symbol: (eg: AAPL for Apple Inc.)
getDate, getSentiment: optional parameters on date and headline sentiment where 0 is False and 1 is True
withinHours: optional parameters to scrape only news with publish times no larger than the value of withinHours, defaults to 24
```

Using the URL:

`http://localhost:9005/api/scrape/benzinga/amzn?getDate=1&getSentiment=1&withinHours=40`

With JSON body:

```
{
    "walkingPattern": "//div[@id=\"stories-headlines\"][0]/ul[0]/li[@class=\"story\"]",
    "headlinePattern": "//a",
    "datePattern": "//span[@class=\"date\"]"
}
```

Will return the following result:

```
{
    "source": "BENZINGA",
    "resultSet": [
        {
            "date": 1554927023,
            "directHeadline": false,
            "headline": "Jumia Technologies IPO: What You Need To Know",
            "polarity": 0,
            "subjectivity": 0,
            "url": "https://www.benzinga.com/news/19/04/13493499/jumia-technologies-ipo-what-you-need-to-know"
        },
        {
            "date": 1554924214,
            "directHeadline": false,
            "headline": "Startups In Seattle: Where Are The Amazon Spin-Out Companies?",
            "polarity": 0,
            "subjectivity": 0,
            "url": "https://www.benzinga.com/news/19/04/13517836/start-ups-in-seattle-where-are-the-amazon-spin-out-companies"
        },
        ...
    ]
}
```

Where using the URL:

`http://localhost:9005/api/scrape/unknown_source/AAPL?getDate=1&getSentiment=1`

With any JSON body will return the following result:

```
{
    "error": "Bad request with exception: Unknown new source, list of known news source includes ['cnbc', 'seekingalpha']"
}
```

Date is formatted using the utils.date\_time class <br/>

Uses optional `NEWS_DATE_FORMAT` parameters in conf/config.ini <br/>

`Eg: 4 hrs ago - CNBC.com` 

Requires:

```
[NEWS_DATE_FORMAT]
CNBC_DAY_FORMAT = days
CNBC_HOUR_FORMAT = hrs
CNBC_MINUTE_FORMAT = mins
CNBC_OPTIONAL_SPLIT = -
CNBC_DATE_INDEX = 0
```

Where `_DAY_FORMAT`, `_HOUR_FORMAT` and `_MINUTE_FORMAT` let the program know the letters prior to such strings are their relative day/hour/minute

Where `_OPTIONAL_SPLIT` is to deal with cases where the date data comes with values that do not have any significance to the date itself and `_DATE_INDEX` is the location of the data after the split 
#### Find company name by ticker symbol

`/api/get_company_name/<ticker_symbol>`

Using the URL:

`http://localhost:9005/api/get_company_name/AAPL`

Will return the following result:

```
{
    "name": "Apple Inc."
}
```

#### Find list of company suggestions by ticker symbol

`/api/get_company_suggestion/<ticker_symbol>`

Return a list of suggestion based on input ticker_symbol (To later support type-ahead)

Using the URL:

`http://localhost:9005/api/get_company_suggestion/AAPL`

Will return the following result:

```
{
    "ResultSet": [
        {
            "name": "Apple Inc.",
            "symbol": "AAPL"
        },
        {
            "name": "NYSE Leveraged 2x AAPL Index",
            "symbol": "^NY2LAAPL"
        },
        {
            "name": "Apple Inc.",
            "symbol": "AAPL.MX"
        },
        ...
    ]
}
```

### Requirements

Python 3

### Build Project

```
pip install -r requirement.txt
py src\main.py
```