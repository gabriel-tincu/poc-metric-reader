POC project composed of 2 components:
- publisher : reads metrics from the host OS and sends them over kafka
- subscriber : reads said metrics (presumably) from kafka and stores them in Postgres

#### Run it

**Make sure you enable topic auto-create in your Aiven kafka service admin page OR use an already created topic**

##### Docker 

- make sure you have docker installed and running
- make sure the `env` file has all the defined values properly populated (kafka and PG credentials)
- run `run-docker.sh` with either of `tests publisher subscriber` as parameter   

For example, to run the tests you would run `./run-docker.sh tests` and so on


#### Normal 
- make sure you have python3 and virtualenv installed