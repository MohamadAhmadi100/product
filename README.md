# Prerequisite
## Database
This project uses mongodb as database. Install Mongodb in your local machine using [Install MongoDB Community Edition](https://docs.mongodb.com/manual/administration/install-community/)
## Settings virtual environment
```shell
sudo apt install python3-virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
# Usage
## Run mongodb
First you need to run mongo database:
- **Linux**
```shell
sudo systemctl start mongod
```
- **Mac OS**
```shell
brew services start mongodb-community@5.0
```
## .env file
Create a .env file in test directory with the following content:
```buildoutcfg
MONGO_HOST = "http://localhost"
MONGO_PORT = "27017"

UVICORN_HOST = "http://localhost"
UVICORN_PORT = "8000"
```
This is the place where you can also set database and uvicorn's host and port.
## Install the package
To install the package, run the following command in the product directory:
```shell
pip install -e .
```
## Run the project
Then you can start the projects using uvicorn:
```shell
uvicorn main:app --reload
```
## Run the project with debug mode
- You can visit [localhost:8000](http://localhost:8000) for root directory. 
- The API docs are available at [localhost:8000/docs/](http://localhost:8000/docs/)
- Alternative API docs are also available at [localhost:8000/redoc](http://localhost:8000/redoc)
## Database Visualization
Download mongodb compass:
[MongoDB Compass](https://www.mongodb.com/try/download/compass) 

Default database address is: [mongodb://localhost:27017](mongodb://localhost:27017)
## Stop mongodb
To stop the mongo database:
- **Linux**
```shell
sudo systemctl stop mongod
```
- **Mac OS**
```shell
brew services stop mongodb-community@5.0
```
# Testing the project
## Unit testing
For testing, run this command in the root folder of the project:
```shell
pytest
```
## Coverage
Testing coverage can also be achieved by:
```shell
pytest --cov
```
