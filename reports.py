import re
import dropbox
import json
import time
import os.path
from datetime import date
from reporter_api.constants import APP_KEY, APP_SECRET, ACCESS_TOKEN
import dateutil.parser
from itertools import groupby

DEBUG = True

FLOW = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
AUTHORIZE_URL = FLOW.start()
CLIENT = dropbox.client.DropboxClient(ACCESS_TOKEN)

#TODO support collector
#TODO support the weight file
#TODO fix quote marks

def log(msg):
    if DEBUG:
        print("reporter_api :: {0}".format(msg))

class Fetcher(object):
    """
    Container class for multiple Reporter Snapshots can be used to filter
    """
    FILE_SUFFIX = ".json"

    @staticmethod
    def getClient(path):
        """
        Gets folder metadata obj
        Returns: `dict`
        """
        folderMetadata = CLIENT.metadata(path)
        return folderMetadata

    @staticmethod
    def getAllReports(reportCount=None):
        """
        Returns all uploaded Report objects
        """
        reports = []
        folderMetadata = Fetcher.getClient("/Apps/Reporter-App")
        if DEBUG:
            start = time.time()

        counter = 0
        for metaFile in folderMetadata["contents"]:
            if os.path.splitext(metaFile["path"])[1] == Fetcher.FILE_SUFFIX:
                f, metadata = CLIENT.get_file_and_metadata(metaFile["path"])
                reportObj = Report(eval(f.read()))
                end = time.time()

                reports.append(reportObj)
                if reportCount != None:
                    if counter == reportCount:
                        break

                counter += 1

        log("Query time :: " + str(end - start))
        return reports

    @staticmethod
    def getHealthKit(date):
        folderMetadata = Fetcher.getClient("/healthkit")
        if(DEBUG):
            start = time.time()
        results = CLIENT.search("/healthkit", date)

        if results != []:
            f, metadata = CLIENT.get_file_and_metadata(results[0]["path"])
            dataDict = eval(f.read())
            return dataDict

    @staticmethod
    def getLatestReport():
        """ Returns latest Report object """
        folderMetadata = Fetcher.getClient("/Apps/Reporter-App")
        if(DEBUG):
            start = time.time()

        for metaFile in reversed(folderMetadata["contents"]):
            if os.path.splitext(metaFile["path"])[1] == Fetcher.FILE_SUFFIX:
                f, metadata = CLIENT.get_file_and_metadata(metaFile["path"])
                reportObj = Report(eval(f.read()))
                end = time.time()
                log("Query time :: " + str(end - start))
                return reportObj

        return None

    #TODO make this convenience function
    @staticmethod
    def getTodaysReports():
        reports = []
        today = date.today()
        todayStr = today.strftime("%Y-%m-%d")
        if(DEBUG):
            start = time.time()
        folderMetadata = Snapshots.getClient("/Apps/Reporter-App")
        fileObjs = folderMetadata["contents"]
        for fileO in fileObjs:
            if(re.match(".+/{0}-reporter-export.json".format(todayStr)
, fileO["path"])):
                f, metadata = CLIENT.get_file_and_metadata(fileO["path"])
                for snapshot in json.loads(f.read())["snapshots"]:
                    r = Report(snapshot)
                    reports.append(r)
        end = time.time()
        if(DEBUG):
            log("Query time :: " + str(end - start))
        return reports

class Report(object):
    def __init__(self, data):
        self.__data = data
        self.__setup()

    def __setup(self):
        self.__snapshots = []
        for snapshot in self.__data["snapshots"]:
            snapshotObj = Snapshot(snapshot)
            self.__snapshots.append(snapshotObj)

        healthInfo = Fetcher.getHealthKit(self.date)
        if healthInfo != None:
            for snapshot in self.__snapshots:
                snapshot.weight = healthInfo['weight']

    @property
    def snapshots(self):
        return self.__snapshots

    @property
    def questions(self):
        return self.__data["questions"]

    @property
    def date(self):
        if "snapshots" in self.__data:
            if self.__data["snapshots"] != []:
                matchObj = re.match("(.+)T", self.__data["snapshots"][0]['date'])
                return matchObj.groups()[0]
        else:
            return None

    def __str__(self):
        if "snapshots" in self.__data:
            if self.__data["snapshots"] != []:
                return self.__data["snapshots"][0]["date"]

        return str()

class Snapshot(object):
    def __init__(self, data):
        self.__data = data
        self.__setup()

    def __setup(self):
        self.__weight = None

    @property
    def battery(self):
        """
        Gets recorded battery level
        Returns: `int`
        """
        return self.__data["battery"]

    @property
    def responses(self):
        """
        Typed question responses.
        Returns: `dict`
        """
        if responses in self.__data:
            return self.__data["responses"]

    @property
    def weather(self):
        """ Gets snapshots recorded weather metrics.
        Returns: dict.
        """
        if "weather" in self.__data:
            return self.__data['weather']
        else:
            return {}

    @property
    def placemark(self):
        if "location" in self.__data:
            return self.__data["location"]["placemark"]

    @property
    def longitude(self):
        """ Gets longitude
        Returns: float
        """
        if "location" in self.__data:
            if "longitude" in self.__data['location']:
                return self.__data['location']['longitude']
            else:
                return None

    @property
    def latitude(self):
        """ Gets latitude
        Returns: float
        """
        if "location" in self.__data:
            if "latitude" in self.__data['location']:
                return self.__data['location']['latitude']
            else:
                return None

    @property
    def timestamp(self):
        if "location" in self.__data:
            return self.__data['location']['timestamp']
        else:
            return None

    @property
    def date(self):
        if "date" in self.__data:
            return dateutil.parser.parse(self.__data['date']).strftime("%Y-%m-%d %H:%M")
        else:
            return None

    @property
    def audio(self):
        if "audio" in self.__data:
            return self.__data["audio"]["avg"]

    @property
    def connection(self):
        """
        Phone connection status
        Returns: `int`
        """
        if "connection" in self.__data:
            return self.__data["connection"]

    @property
    def data(self):
        return self.__data

    @property
    def cleanData(self):
        clean = {}
        clean["location"] = self.location
        clean["date"] = self.date
        clean["responses"] = self.responses
        return clean

    @property
    def longlat(self):
        return [self.longitude, self.latitude]

    @property
    def country(self):
        """
        Gets country
        Returns: `string`
        """
        if "location" in self.__data:
            if "country" in self.__data["location"]:
                return self.__data["location"]["country"]
            elif "placemark" in self.__data["location"]:
                if "country" in self.__data["location"]["placemark"]:
                    return self.__data["location"]["placemark"]["country"]
        return None

    @property
    def altitude(self):
        """
        Gets altitude
        Returns: `float`
        """
        if "location" in self.__data:
            if "altitude" in self.__data["location"]:
                return self.__data["location"]["altitude"]
        else:
            return None

    @property
    def steps(self):
        """
        Gets step count
        Returns: `int`
        """
        if "steps" in self.__data:
            return self.__data["steps"]
        else:
            return None

    @property
    def humidity(self):
        if "weather" in self.__data:
            if "relativeHumidity" in self.__data["weather"]:
                return self.__data["weather"]["relativeHumidity"]

    @property
    def tempC(self):
        if "weather" in self.__data:
            if "tempC" in self.__data["weather"]:
                return self.__data["weather"]["tempC"]

    @property
    def weather(self):
        if "weather" in self.__data:
            if "weather" in self.__data["weather"]:
                return self.__data["weather"]["weather"]

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, weightIn):
        self.__weight = weightIn

    @property
    def responses(self):
        answers = {}
        if "responses" in self.__data:
            for response in self.data["responses"]:
                answers[response["questionPrompt"]] = []
                if "numericResponse" in response:
                    answers[response["questionPrompt"]] = response["numericResponse"]
                if "answeredOptions" in response:
                    answers[response["questionPrompt"]] = response["answeredOptions"]
                if "textResponses" in response:
                    answers[response["questionPrompt"]] = response["textResponses"]
                if "tokens" in response:
                    answers[response["questionPrompt"]] = response["tokens"]
        return answers





















#    cleanedCountries = [x for x in countries if x is not None]
#
#    print(cleanedCountries)
#    countryDict = {}
#    for key, group in groupby(cleanedCountries):
#        countryDict[key] = len(list(group))
##
#    print(countryDict)
    #fetcher.getHealthKit("2016-02-19")
