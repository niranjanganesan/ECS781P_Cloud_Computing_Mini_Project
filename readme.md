# COVID-19 Web Application
The Global pandemic CoronaVirus COVID-19 also called as SARS-CoV-2 has already affected millions of people all over the world. The COVID-19 Web App is a prototype of a Cloud Application developed
in Python and Flask that gives the global statistics of COVID-19 affected cases. This App makes use of a REST API service to get the daily statistics of COVID-19 and the application is deployed 
in the AWS EC2 instance.

## The Application consists of following features:

  1. Dynamically generated REST API, API has set of services for the selected application domain, REST API responses conforming to REST standards (response codes).
  2. The application makes use of an external REST service to complement its functionality: REST API for COVID 19 https://api.covid19api.com/ has been used.
  3. The application uses Apache Cassandra Cloud database for accessing persistent information.
  4. Kubernetes Load Balancing service for application deployment.
  5. Support for Cloud Scalability, deploying in a container environment.
  6. Cloud Security measures by serving the application over HTTPS using self-signed certificate.
  7. Request followup orchestration using HATEOAS.

## Interacting with Web Application 

### Accessing the home page: @app.route('/', methods =['GET'])

The Home page displays the Global statistics of COVID 19 along with links to view the Country wise stats and interation with external REST API.

### @app.route('/LoadDatabase', methods=['GET','PUT'])

### @app.route('/external')

### @app.route('/summary/country', methods=['GET'])

### @app.route('/summary/global', methods=['GET'])

### @app.route('/summary/countrylist', methods=['GET'])

### @app.route('/summary/country/<name>',  methods=['GET'])

### @app.route('/summary/country',  methods=['POST'])

### @app.route('/summary/country',  methods=['PUT'])

### @app.route('/summary/country',  methods=['DELETE'])

### @app.route('/summary/global',  methods=['POST'])

### @app.route('/summary/global',  methods=['PUT'])

### @app.route('/summary/global',  methods=['DELETE'])

## Apache Cassandra Database setup

1. Initial steps
```
sudo apt update
sudo apt install docker.io
sudo docker pull cassandra:latest
```

2. Run Cassandra in a Docker and export port 9042:
```
sudo docker run --name cassandra-test -p 9042:9042 -d cassandra:latest
```

3. Download country.csv and global.csv file
```
wget https://raw.githubusercontent.com/niranjanganesan/ECS781P_Cloud_Computing_Mini_Project/master/country.csv
wget https://raw.githubusercontent.com/niranjanganesan/ECS781P_Cloud_Computing_Mini_Project/master/global.csv
```

4. Load the data into Cassandra database
```
sudo docker cp country.csv cassandra-test:/home/country.csv
sudo docker cp global.csv cassandra-test:/home/global.csv
```

5. Access Cassandra in interactive mode
```
sudo docker exec -it cassandra-test cqlsh
```

6. Create a keyspace inside cassandra for the COVID 19 Database
```
cqlsh> CREATE KEYSPACE COVID19 WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': '1'};
```

7. Create a database table for country stats:
``` 
cqlsh> CREATE TABLE COVID19.summary (Country text PRIMARY KEY,NewConfirmed int, 
       TotalConfirmed int, NewDeaths int, TotalDeaths int, NewRecovered int, 
       TotalRecovered int);
```

8. Create a database table for global stats:
```
cqlsh> CREATE TABLE COVID19.global (Key text PRIMARY KEY,NewConfirmed int, 
       TotalConfirmed int, NewDeaths int, TotalDeaths int, NewRecovered int, 
       TotalRecovered int, TimeStamp text);
```

9. Copy the contents of country.csv and global.csv to COVID19.summary and COVID19.global table respectively.
```
cqlsh> COPY COVID19.summary(Country, NewConfirmed, TotalConfirmed, NewDeaths, TotalDeaths, NewRecovered, TotalRecovered)
       FROM '/home/country.csv' WITH HEADER=TRUE;

cqlsh> COPY COVID19.global(Key, NewConfirmed, TotalConfirmed, NewDeaths, TotalDeaths, NewRecovered, TotalRecovered)
       FROM '/home/global.csv' WITH HEADER=TRUE;

