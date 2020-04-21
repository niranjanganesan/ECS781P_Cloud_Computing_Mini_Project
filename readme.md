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

### External API 

#### *GET* @app.route('/external')
Get the summary of all countries and global stats.

#### *GET* @app.route('/summary/countrylist')
Get the list of all countries along with slug and country code details.

#### *GET*, *PUT* @app.route('/LoadDatabase')
This loads the database with COVID 19 country stats using the external API 'https://api.covid19api.com/summary'

### REST-based Service Interface
 
#### *GET* @app.route('/')
The Home page displays the Global statistics of COVID 19 along with links to view the Country wise stats and interaction with external REST API. One can use the curl command:

#### *GET* @app.route('/summary/country')
Get the stats of all countries from the database. Can be executed using following curl command:
```
curl -i -k https://0.0.0.0/summary/country
```

#### *GET* @app.route('/summary/global')
Get the global stats from the database. Can be executed using the following curl command:
```
curl -i -k https://0.0.0.0/summary/global
```

#### *GET* @app.route('/summary/country/<name>')
Get the country specific stats from the database. Can be executed using the follwing curl command:
```
curl -i -k https://0.0.0.0/summary/country/TestCountry
```
#### *POST* @app.route('/summary/country')
Add a new country to the database. The user must provided the following:

* Country
* NewConfirmed
* TotalConfirmed
* NewDeaths
* TotalDeaths
* NewRecovered
* TotalRecovered

This is a POST request and can be executed by using the following curl command:
```
curl -i -k -H "Content-Type: application/json" -X POST -d '{"NewConfirmed":2,"TotalConfirmed":3,"NewDeaths":3,"TotalDeaths":3,"NewRecovered":3,"TotalRecovered":3,"Country":"TestCountry"}' https://0.0.0.0/summary/country
```

#### *PUT* @app.route('/summary/country')
Update an existing country to the database. The user must provide the following:

* Country
* NewConfirmed
* TotalConfirmed
* NewDeaths
* TotalDeaths
* NewRecovered
* TotalRecovered

This is a PUT request and can be executed using the following curl command:
```
curl -i -k -H "Content-Type: application/json" -X PUT -d '{"NewConfirmed":999,"TotalConfirmed":3,"NewDeaths":3,"TotalDeaths":3,"NewRecovered":3,"TotalRecovered":3,"Country":"TestCountry"}' https://0.0.0.0/summary/country
```

#### *DELETE* @app.route('/summary/country')
Deletes a country record from the database. The user must provide the following:

* Country

This is a DELETE request and can be executed using the following curl command:
```
curl -i -k -H "Content-Type: application/json" -X DELETE -d '{"Country":"TestCountry"}' https://0.0.0.0/summary/country
```

### *POST* @app.route('/summary/global')
Add the global stats to the database. The user must provide the following:

* Key
* NewConfirmed
* TotalConfirmed
* NewDeaths
* TotalDeaths
* NewRecovered
* TotalRecovered

Here 'key' refers to value 'Global'. This is a POST request and can be executed using the following command:
```
curl -i -k -H "Content-Type: application/json" -X POST -d '{"NewConfirmed":9,"TotalConfirmed":3,"NewDeaths":3,"TotalDeaths":3,"NewRecovered":3,"TotalRecovered":3,"Key":"TestGlobal"}' https://0.0.0.0/summary/global
```

### *PUT* @app.route('/summary/global')
Updates the global stats to the database. The user must provide the following:

* Key
* NewConfirmed
* TotalConfirmed
* NewDeaths
* TotalDeaths
* NewRecovered
* TotalRecovered

Here 'key' refers to value 'Global'. This is a PUT request and can be executed using the following command:
```
curl -i -k -H "Content-Type: application/json" -X PUT -d '{"NewConfirmed":1,"TotalConfirmed":10,"NewDeaths":3,"TotalDeaths":3,"NewRecovered":3,"TotalRecovered":3,"Key":"TestGlobal"}' https://0.0.0.0/summary/global
```

#### *DELETE* @app.route('/summary/global')
Deletes the global stats record from the database. The user must provide the following:

*Key

Here 'key' referes to value 'Global'. This is a DELETE request and can be executed using the following command:
```
curl -i -k -H "Content-Type: application/json" -X DELETE -d '{"Key":"TestGlobal"}' https://0.0.0.0/summary/global
```

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
```

## Cloud Security - HTTPS Implementation

The app is served over https by setting up the self-signed certificates as shown below:
1. Run in your project folder
```
$ openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
2. Configure the certificate as shown below:
```
Generating a RSA private key
.....................................++++
....................................................................................++++
writing new private key to 'key.pem'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:UK
State or Province Name (full name) [Some-State]:England
Locality Name (eg, city) []:London
Organization Name (eg, company) [Internet Widgits Pty Ltd]:QMUL 
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:localhost
Email Address []:ec17524@qmul.ac.uk
```

3. The result is the creation of two files cret.pem and key.pem. Include these two files in the app_flask.py program file as shown below:
```
if __name__ == "__main__":
    context = ('cert.pem','key.pem')
    app.run(host='0.0.0.0',port=443,ssl_context=context)
```

4. Adding the certificate will serve the application over https

## Kubernetes Deployment

Below are the steps to build the docker image and deploy application in kubernetes

1. Install Kubernetes using the command:
```
sudo snap install microk8s --classic
```

2. For private Docker images the docker image must be registered to the built in registry for it to function. Install registry with following command:
```
sudo microk8s enable registry
```

3. Configure the deployment.yaml file in your project directory as shown below:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covidapp-deployment
  labels:
    app: covidapp
spec:
  selector:
    matchLabels:
      app: covidapp
  replicas: 3
  template:
    metadata:
      labels:
        app: covidapp
    spec:
      containers:
      - name: covidapp
        image: localhost:32000/covidapp:registry
        ports:
        - containerPort: 443
```

4. Build the cassandra docker image and tag it to registry. 
```
sudo docker build . -t localhost:32000/covidapp:registry
```

5. Push it to registry
```
sudo docker push localhost:32000/covidapp:registry
```

6. Pushing to this insecure registry may fail in some versions of Docker unless the daemon is explicitly configured to trust this registry. 
   To address this we need to edit /etc/docker/daemon.json and add:
```
{
  "insecure-registries" : ["localhost:32000"]
}
```
Note: This step is optional and must be done only if docker push has failed.

7. The new configuration should be loaded with a Docker daemon restart:
```
sudo systemectl restart docker
```

8. Now that we have restarted our docker daemon all the container instances would have stopped running. This means that the cassandra database docker container 'cassandra-test' 
   has stopped running. Re-start the same container instance using below command:
```
sudo docker start cassandra-test
```

9. Deploy the docker conatiner image 'covidapp:registry' present in registry using the configured deployment.yaml file:
```
sudo microk8s.kubectl apply -f ./deployment.yaml
```
The we app is now deployed in kubernetes

10. Check the deployment status
```
sudo microk8s.kubectl get deployment
```

11. Check the pods status
```
sudo microk8s.kubectl get pods
```

12. Create a service and expose the deployment to internet
```
sudo microk8s.kubectl expose deployment covidapp-deployment --port=443 --type=LoadBalancer
```

13. Check the service status
```
sudo microk8s.kubectl get services
```
Below is the sample status of the service:
```
NAME                            TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
service/covidappv3-deployment   LoadBalancer   10.152.183.77   <pending>     443:30873/TCP   17h
service/kubernetes              ClusterIP      10.152.183.1    <none>        443/TCP         9d
```
Here we can see the deployed web app is exposed to Nodeport '30873'. By default the kubernetes service allocates a port within range '30000-32767'.

Finally view the web app in the browser using the public DNS of AWS EC2 account along with this Nodeport that starts with '30xxx'.

### Cleanup

1. Delete the Kubernetes deployment and LoadBalancer service using below commands:
```
sudo microk8s.kubectl delete deployment covidapp-deployment
sudo microk8s.kubectl delete service covidapp-deployment
```
2. Delete the Cassandra database instance by:
```
sudo docker rm cassandra-test
```

## COVID 19 Web App built with:

* [Cassandra](http://cassandra.apache.org/doc/latest/) - Database used
* [Flask](http://flask.pocoo.org/docs/1.0/) - Web framework used
* [Coronavirus COVID19 API](https://covid19api.com/) - External API used
* [Kubernetes](https://microk8s.io/docs/registry-built-in) - Load balancing & Scaling
* [Encryption & Security](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) - TLS protocol using 'adhoc' SSL

## Authors

* **Niranjan Ganesan** - [Niranjan](https://github.com/niranjanganesan/ECS781P_Cloud_Computing_Mini_Project) 
