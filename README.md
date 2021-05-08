# Website Availabilites

## System  Architecture
![](https://i.imgur.com/Eu9Grwg.png)

![](https://i.imgur.com/bixtPhy.png)

This is a website checker that will perform checks periodically and collect the HTTP response time, error code returned, as well as optionally checking the returned page contents for a regexp pattern that is expected to be found on the page. To make it simple, I choose to collect the website title.
Those metrics will be sent to a kafka topics to be consume later and save to a PostgreSQL database.

## How does it work
For This project, I use a managed postgres(12.6) database and a managed Kafka(2.7)  both hosted on Aiven.io

### Producer
The producer is a Python kafka application  that periodically checks a target websites and sends the check results to a managed Kafka topic hosted on Aiven.io. The application will create the topics if it does not exist, that start collecting the date asynchronically and push them to the Kafka servers.

### Consumer
The python Kafka application consumer is a postgres/kafka application written in Python which jobs is to retrieve those data from the Kafka Topic and to store them on Aiven managed PostgreSQL database.

### Metrics Collected
For simplicity, we collect a very small of metrics data from those websites:
- url: The actual used for the web-request.
- name: Website site name.
- Title: Website page Title.
- Elapsed Time, The Time to first byte.
- Date the request was made.
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
The producer and consumer scripts use the same config file. We have to run separately either in the same machine or on two different machines or environment. The only requirements is to update the configuration and secrets directory with the correct data and secrets to access the Database and the Kafka server.

```sh=
# To run the the producer:
python3 producer_metrics.py

# To run the consumer db:
python3 consumer_metrics.py

```

There is also a docker-compose file, both scrips can be run with just one command after adding the necessary config files, just run:
```sh=
# The first time only use the command below to build the images.
docker-compose up --build -d

# Next time just run
docker-compose up -d

# When finishing running the app
docker-compose down -v
```

### System Configuration
The configuration is very minimal, just a few files certificates and password to access the database and Kafka  to download from the Aiven.io under the overview section on the specific database services.

![](https://i.imgur.com/VG2UEjD.png)

There is this an empty folder `confd/secrets/` at the root of the repo, create those files.

`confd/secrets/database_password.db` : The posgres Database with access right to write to the to the database service hosted on Aiven.io. That paswword db file can be any name as soon as it ends with the extension `.db` lower case.

`confd/secrets/kafka_password.ka`: This file hold the password to connect to the Kafka services. This file can be any nane, just one requirements, the name should end with the extension `.ka`.

This is the same for those SSL certificate files below to use when accessing Kafka.
confd/secrets/ca.pem
confd/secrets/service.cert
confd/secrets/service.key

![](https://i.imgur.com/3T3x8kj.png)

### Additional Config file

This file `confd/config.yaml` is a yaml file with few fied to be field prior running the script.

```yaml=
POSTGRES:
  DB_SERVER: your-pg-cloud-db-url-hosted-on.aivencloud.com
  DB_USER: db-user-name-with-access-right-to-create-table-and-db
  DB_PORT_NUMBER: 21882
  DB_NAME: add_the_name_of_the_database_to_save_the_metrics
  DB_TABLE: the_table_name_for_the_metrics
  DB_DEFAULT: the_name_to_use_when_login_can_be_same_as_DB_NAME_above

KAFKA:
  KAFKA_BOOTSTRAP_SERVERS: your-kafka-db-url-hosted-on.aivencloud.com
  KAFKA_PORT_NUMBER: 21884
  KAFKA_TOPIC: your-topic-name

```
After adding the missing ssl-certificates files and the kafka and postgres database files, the project tree should look like this, minus the log.data file. Those folders (secrets, logs) are now empty (with just a .gitkeep file).
![](https://i.imgur.com/xOkQA3Y.png)



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
There is a `requirements.txt` with the all the depedencies to `pip install -r requirements.txt` prior running the producer and consumer scripts.

The Kafka-producer is a Python application that will collect every 30 seconds a few metrics from a list of website. Those metrics are:

# Metrics collected view from Kafka Consumer:
![](https://i.imgur.com/WNpYr0v.png)


# Metrics Collected view from the Postgres DB
![](https://i.imgur.com/zYFX9cP.jpg)

