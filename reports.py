import re
import dropbox
import json
import time
import os.path
from datetime import date
from constants import APP_KEY, APP_SECRET, ACCESS_TOKEN
import dateutil.parser

DEBUG = True

FLOW = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
AUTHORIZE_URL = FLOW.start()
CLIENT = dropbox.client.DropboxClient(ACCESS_TOKEN)

class Snapshots(object):
    """ Container class for multiple Reporter Snapshots can be used to filter """

    @staticmethod
    def getClient(path):
        """ Gets folder metadata obj
        Returns: dict
        """
        folderMetadata = CLIENT.metadata(path)
        return folderMetadata

    @staticmethod
    def getAllReports():
        """ Returns all uploaded Report objects """
        reports = []
        folderMetadata = Snapshots.getClient('/Apps/Reporter-App')
        if(DEBUG):
            start = time.time()

        for fileO in folderMetadata['contents']:
            f, metadata = CLIENT.get_file_and_metadata(fileO['path'])
            if(os.path.splitext(fileO['path'])[1] != "json"):
                for snapshot in json.loads(f.read())['snapshots']:
                    r = Report(snapshot)
                    reports.append(r)

        end = time.time()
        if(DEBUG):
            print("Query time :: " + str(end - start))
        return reports

    @staticmethod
    def getLatestReport():
        """ Returns latest Report object """
        folderMetadata = Snapshots.getClient('/Apps/Reporter-App')
        if(DEBUG):
            start = time.time()
        fileO = folderMetadata['contents'][-1]
        f, metadata = CLIENT.get_file_and_metadata(fileO['path'])
        if(os.path.splitext(fileO['path'])[1] != "json"):
            for snapshot in json.loads(f.read())['snapshots']:
                r = Report(snapshot)

        end = time.time()
        if(DEBUG):
            print("Query time :: " + str(end - start))
        return r

    @staticmethod
    def getTodaysReports():
        reports = []
        today = date.today()
        todayStr = today.strftime("%Y-%m-%d")
        if(DEBUG):
            start = time.time()
        folderMetadata = Snapshots.getClient('/Apps/Reporter-App')
        fileObjs = folderMetadata['contents']
        for fileO in fileObjs:
            if(re.match(".+/{0}-reporter-export.json".format(todayStr)
, fileO['path'])):
                f, metadata = CLIENT.get_file_and_metadata(fileO['path'])
                for snapshot in json.loads(f.read())['snapshots']:
                    r = Report(snapshot)
                    reports.append(r)
        end = time.time()
        if(DEBUG):
            print("Query time :: " + str(end - start))
        return reports

class Report(object):
    def __init__(self, data):
        self.__data = data

    @property
    def battery(self):
        """ Gets recorded battery level
        Returns: int.
        """
        return self.__data['battery']

    @property
    def responses(self):
        """ Typed question responses.
        Returns: dict
        """
        if(self.__data.has_key("responses")):
            return self.__data['responses']

    @property
    def weather(self):
        """ Gets snapshots recorded weather metrics.
        Returns: dict.
        """
        if(self.__data.has_key("weather")):
            return self.__data['weather']
        else:
            return {}

    @property
    def placemark(self):
        if(self.__data.has_key("location")):
            return self.__data["location"]["placemark"]

    @property
    def longitude(self):
        """ Gets longitude
        Returns: float
        """
        if(self.__data.has_key("location")):
            if(self.__data['location'].has_key("longitude")):
                return self.__data['location']['longitude']
            else:
                return None

    @property
    def latitude(self):
        """ Gets latitude
        Returns: float
        """
        if(self.__data.has_key("location")):
            if(self.__data['location'].has_key("latitude")):
                return self.__data['location']['latitude']
            else:
                return None

    @property
    def timestamp(self):
        if(self.__data.has_key("location")):
            return self.__data['location']['timestamp']
        else:
            return None

    @property
    def date(self):
        if(self.__data.has_key("date")):
            return dateutil.parser.parse(self.__data['date']).strftime("%Y-%m-%d %H:%M")
        else:
            return None

    @property
    def audio(self):
        if self.__data.has_key('audio'):
            return self.__data['audio']['avg']

    @property
    def connection(self):
        """ Phone connection status
        Returns: int
        """
        if(self.__data.has_key("connection")):
            return self.__data['connection']

    @property
    def data(self):
        return self.__data

    @property
    def cleanData(self):
        clean = {}
        clean['location'] = self.location
        clean['date'] = self.date
        clean['responses'] = self.responses
        return clean

    @property
    def location(self):
        return [self.longitude, self.latitude]

    @property
    def responses(self):
        answers = {}
        for response in self.data['responses']:
            answers[response['questionPrompt']] = []
            if 'numericResponse' in response:
                answers[response['questionPrompt']] = response['numericResponse']
            if 'answeredOptions' in response:
                answers[response['questionPrompt']] = response['answeredOptions']
            if 'textResponses' in response:
                answers[response['questionPrompt']] = response['textResponses']
            if 'tokens' in response:
                answers[response['questionPrompt']] = response['tokens']
        return answers

if __name__ == "__main__":
    snapshots = Snapshots()
    reports = Snapshots.getLatestReport()
    import pprint as pp
    print(reports.responses)
    #pp.pprint(reports.data)
