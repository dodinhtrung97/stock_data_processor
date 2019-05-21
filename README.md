# Trade Advisor

### Description

Includes 4 modules: <br/>

- Pattern Matcher: <br/>
    - Assumes a set of data (ticker specified) exists
    - Find tickers with similar market patterns to provided pattern
- Web Scraper: <br/>
    - Scrapes headline data from `benzinga` and `cnbc`
    - Applies sentiment analysis on said data, outputing a score that is one of `[---, --, -, 0, +, ++, +++]`
- Price Predictor: <br/>
    - Predict stock price for `x` days ahead for input ticker symbol
    - Assumes the data required for prediction already exists
- Data Collector: <br/>
    - Collects data to serve the Price Predictor module
    - Wrapped in a runnable scheduled windows service

### Server Config

In `conf/config.ini`

### Windows Service Config

In `conf/windows_service_config.ini`

### Logger

Either in `/conf/logging.yaml` or set a `LOG_CFG` environment variable

## Pattern Matcher

### Application Configuration: `pattern_matcher/conf/conf.json`

```
    {
        "input": {
            "dir": "location_of_data_dir",
            "format": "format_of_files",
            "recursive": "Default is False"
        },
        "measure_type": "Either spearman or pearson measurement"
    }
```

### Usage:
- Default mode:
    - Default application configs at `pattern_matcher/conf/conf.json`
    - Default logging configs at `/conf/logging.yaml`
- Custom mode:
    - Change application's configurations in file `pattern_matcher/conf/conf.json`
    - Change logging's configurations in either file `/conf/logging.yaml` or create a new yaml logging conf file and set env variable `LOG_CFG` to the location of that file.
    - Run command: `LOG_CFG=my_custom_logging.yaml python app.py`

## Web Scraper

Change `web_scraper/conf/config_template.ini` appropriately and rename the file to `config.ini` before running

Scope may expand in future versions

### Mode

Supports a backend API mode and an auto scrapping mode <br/>

See `Usage`

### Automated Scraper

Starts an automated web scraper on the `sites` and `walking_patterns` defined in `web_scraper/conf/config.ini`

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
            "date": 1556964000,
            "direct": false,
            "headline": "IMDbPro and Box Office Mojo Reveal the Top-Grossing Films in April 2019 and the Most Anticipated Films Opening in May",
            "score": "+",
            "url": "https://www.benzinga.com/pressreleases/19/05/b13664704/imdbpro-and-box-office-mojo-reveal-the-top-grossing-films-in-april-2019-and-the-most-anticipated-f"
        },
    ],
    "BENZINGA_HEADLINES": [
        ...
    ],
    "BENZINGA_PARTNER": [
        ...
    ]
    ...
}
```
After a scrapping iteration's over, the service shall go to sleep for `SLEEP_TIME` (in seconds), defined in `web_scraper/conf/config.ini`

### Backend API

Found in src/controller/scraper_controller.py

#### News scraper API <br/>

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
            "date": 1556964000,
            "direct": false,
            "headline": "IMDbPro and Box Office Mojo Reveal the Top-Grossing Films in April 2019 and the Most Anticipated Films Opening in May",
            "score": "+",
            "url": "https://www.benzinga.com/pressreleases/19/05/b13664704/imdbpro-and-box-office-mojo-reveal-the-top-grossing-films-in-april-2019-and-the-most-anticipated-f"
        }
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

Uses optional `NEWS_DATE_FORMAT` parameters in `web_scrapper/conf/config.ini` <br/>

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

### Data Collector

Starts a scheduled windows service whose: <br/>

- Configuration is defined in `conf/config.ini` session `SERVICE`, including:
    - Service name `SVC_NAME`
    - Service display name `SVC_DISPLAY_NAME`
    - [Cron period](https://crontab.guru) `CRON_PERIOD`
- Collected data from `ticker_list`:
    - Is defined in `~/data_collector/conf/ticker_list.json` 
    - Saved into a directory defined in `~src/data_collector/conf/config.ini`

### Requirements

Python 3

### Setup

Create virtual env. Docs [here](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/#creating-a-virtualenv) 

#### To run the `Backend Server`:

```
pip install -r requirements.txt
python src\app.py [-h] [--websocket WEBSOCKET] [--scraper SCRAPPER]
               [--matcher MATCHER] [--logging LOGGING]
```

Where each optional parameter takes in an integer of `{0, 1}` signifying whether or not a module will be started.

For a more detailed description, run:
```
python src\app.py --help
```

#### To run the `Data Collector Windows Service`:

```
pip install -r requirements.txt
python src\data_collector_service.py install
python src\data_collector_service.py start
```

Refer to `/docs/TROUBLESHOOT.md` for any issue encountered

For a more detailed description, run:
```
python src\data_collector_service.py --help
```

### Deployment
#### Deploy each service individually
1. Pull latest code from [git repo](http://10.184.135.104:9001/root/TradeAdvisor)
2. Build docker image: `docker build -t <image-name> .`
3. Run: `docker run -p <host-port>:<container-port> -v <source-volume>:<target-volume> <docker-image> <server-type>` 
    - Example For api server: `docker run -p 5000:5000 -v D:\data:/app/data trade:v0 api`
    - Example For websocket server: `docker run -p 10005:10005 -v D:\data:/app\data trade:v0 ws`
4. References:
    - `image-name`: The tag name of the image. Ex: `trade:v0`
    - `host-port`: The port on the host machine for binding with the exposed port in a container
    - `container-port`: The exposed port in a container
    - `server-type`: The type of server. Currently support 2 types:
        - `api`: For REST HTTP server. With default port: `5000`
        - `ws`: For websocket. With default port: `10005`
    - `source-volume`: The mounting point between host machine's and container's volumes. Here the mounting point on a host machine. Ex: `D:\data`
    - `target-volume`: The mounting point between host machine's and container's volumes. Here the mounting point on a container. The default for `TradeAdvisor` is `\app\data`

#### Deploy all services at once
1. Build TradeAdvisor image: `docker build -t trade:v0 .`
2. Modify `docker-compose.yml` as following:
```
    version: '3'
    services:
    api:
        image: trade:v0 ---> The image tag being built above
        ports:
        - "5000:5000"   ---> Binding ports between api container and host machine
        volumes:
        - D:/data:/app/data ---> Mounting data dir between api container and host machine
        command: api  --> For starting api server
    ws:
        image: trade:v0  ---> The image tag being built above
        ports:
        - "10005:10005"  ---> Binding ports between api container and host machine
        command: ws ---> For starting websocket server
```
3. Run: `docker-compose up`