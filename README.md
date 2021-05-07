# Website Availabilites

## System  Architecture
![](https://i.imgur.com/Eu9Grwg.png)

![](https://i.imgur.com/bixtPhy.png)

This is a website checker that will perform checks periodically and collect the HTTP response time, error code returned, as well as optionally checking the returned page contents for a regexp pattern that is expected to be found on the page. To make it simple, I choose to collect the website title.
Those metrics will be sent to a kafka topics to be consume later and save to a PostgreSQL database.


## How does it work
For This project, I use a managed postgres(12.6) database and a managed Kafka(2.7)  both hosted on Aiven.io  

### Producer
The producer is a Python kafka application  that periodically checks a target websites and sends the check results to a managed Kafka topic hosted on Aiven.io. 

### Consumer
There is also python Kafka application consumer that stors those  data to an Aiven managed PostgreSQL database. 

### Metrics Collected
For simplicity, we collect a handful of metrics from those machines:
- Website site name
- Website page Title
- TTFB, Time to first bye, the elapsed time
- Date the page was generated
- Date the request was made
- The Error Code, HTTP-error 2xx, 4xx, 5xx, etc...
- The Error Reason, `OK, Forbidden

# How To Run the application.
### Requirements:

```bash=
(venv) ❯ python --version                                                                                                                                      website-availability/git/main !
Python 3.9.4
(venv) ❯ ~❯ pip --version
pip 21.1.1 from /usr/local/lib/python3.9/site-packages/pip (python 3.9)
(venv) ❯

and Optional
~❯ virtualenv --version
virtualenv 20.4.4 from /usr/local/lib/python3.9/site-packages/virtualenv/__init__.py
~❯

```
 To Run the scripts, Follow the steps below for some simple system configuration, then change to the `src` directory and run:
```sh=
# To run the the producer:
python3 producer_metrics.py

# To run the consumer db:
python3 consumer_metrics.py

```


### System Configuration
There is a few configuration we need to run the application:
There is this an empty folder `confd/secrets/` at the root of the repo, create those files.

`confd/secrets/database_password.db` : The posgres Database with access right to write to the to the database service hosted on Aiven.io. That paswword db file can be any name as soon as it ends with the extension `.db` lower case.

`confd/secrets/kafka_password.ka`: This file hold the password to connect to the Kafka services. This file can be any nane, just one requirements, the name should end with the extension `.ka` lower case.

This is the same for those SSL certificate files below. They are additional secrets files to use to connect to the kafka service.
confd/secrets/ca.pem
confd/secrets/service.cert
confd/secrets/service.key

Those files and passwords can be found under their respectives service on Aiven.io websites. They are not on the repo, check the `.gitignore` file

confd/secrets/
├── ca.pem
├── database_password.db
├── kafka_password.ka
├── service.cert
└── service.key

### Additional Config file

This file `confd/config.yaml` is a yaml file with few fied to be field prior running the script.
- Code block with color and line numbers：
```yaml=
POSTGRES:
  DB_SERVER: your-pg-cloud-db-url-hosted-on.aivencloud.com
  DB_USER: db-user-name
  DB_PORT_NUMBER: 21882
  DB_NAME: website_availability-but-you-can-change-me
  DB_TABLE: website_availability_metrics-you-can-change-me
  DB_DEFAULT: defaultdb

KAFKA:
  KAFKA_BOOTSTRAP_SERVERS: your-kafka-db-url-hosted-on.aivencloud.com
  KAFKA_PORT_NUMBER: 21884
  KAFKA_TOPIC: your-topic-name

```
- Web URLS
The file with the web-urls is located at `confd/website_urls.txt`
This file contains a list of websites to use during this experiments:
```
http://adobe.com
http://aiven.io
http://allrecipes.com
http://amazon.com
http://aol.com
http://apartments.com
http://apple.com
http://att.com
http://bankofamerica.com
http://bbc.com
http://bestbuy.com
http://bluehost.com
http://britannica.com
http://bulbagarden.net
http://businessinsider.com
http://ca.gov
http://capitalone.com
http://cbssports.com
http://cdc.gov
http://chase.com
http://cnbc.com
http://cnet.com
http://cnn.com
http://costco.com
http://craigslist.org
http://dictionary.com
http://digitalocean.com
```
### Packages to install
There is a `requirements.txt` with the all the depedencies to `pip install -r requirements.txt` prior running those producer and consumer scripts.

The Kafka-producer is a Python application that will collect every 30 seconds a few metrics from a list of website. Those metrics are:

# Metrics collected view from Kafka Consumer:
![](https://i.imgur.com/WNpYr0v.png)


# Metrics Collected view from the Postgres DB
![](https://i.imgur.com/zYFX9cP.jpg)

