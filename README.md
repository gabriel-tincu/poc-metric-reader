POC project composed of 2 components:
- publisher : reads metrics from the host OS and sends them over kafka
- subscriber : reads said metrics (presumably) from kafka and stores them in Postgres

#### Run it


##### Docker 

- make sure you have docker installed and running
- make sure the `env` file has all the defined values properly populated (kafka and PG credentials)
- run `run-docker.sh` with either of `tests publisher subscriber` as parameter   

For example, to run the tests you would run `./run-docker.sh tests` and so on


#### Normal 

- make sure you have python3 and virtualenv installed
- run `run.sh` with either of `tests publisher subscriber` as parameter. This will add a venv folder in the repo folder if it does not already exist, install the requirement file and run either the tests, publisher or subscriber

#### Notes
For ease of use (i have no way of knowing without further tests, weather the DB schema has been created or not) i will drop and recreate the PF tables on each launch
This should be fine for testing, but when it comes to pub / sub, it is preferred to launch the pub before the sub, as only the latter uses the DB.

E2E tests were a pain in the a** due to the way the background threads communicate with the broker and the general file like architecture of a kafka topic. Long story short it took a while to figure that a `seek` method existed and what it did.
 
One can make use of the docker compose file for local development. I have https://github.com/wurstmeister/kafka-docker to thank for the single broker kafka instance. 
The shell scripts will not work with that though, as they expect fully populated certificate and key files (as per a proper Aiven service config)
I tried using uuids as the topic names on each new test run, but either due to the async nature of kafka or due to my low level of knowledge regarding the system (more probable), that setup seemed to block indefinitely.

#### TODO

- Use custom pluggable serializer / deserializer OR integrate it with the kafka API (that means the message passing system would become tightly coupled)
- Figure out how to make it work with random name topic creation
- Add more metrics ?? (can't really think of any outstanding ones atm)
