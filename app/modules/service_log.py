import pymongo.errors
from app.helpers.mongo_connection import MongoConnection
from app.helpers.telegram import exception_handler
from jdatetime import datetime


class Log:

    def __init__(self, service_input, service_output, action):
        self.service_input = service_input
        self.service_output = service_output
        self.action = action
        self.log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def insert_log(self):
        try:
            with MongoConnection() as mongo:
                result = mongo.log.insert_one(
                    {
                        "service_input": self.service_input,
                        "service_output": self.service_output,
                        "action": self.action,
                        "log_date": self.log_date

                    }
                )
        except pymongo.errors.OperationFailure:
            exception_handler()
            return False
        else:
            return True if result.acknowledged else False
