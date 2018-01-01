import re
import time
import os.path
import json
import glob

import dateutil.parser

import dropbox
from dropbox.exceptions import HttpError
from tqdm import tqdm

from reporter_api.constants import ACCESS_TOKEN, APP_PATH

DEBUG = True

class Mode:
    DROPBOX = 0
    LOCAL = 1


def log(msg):
    if DEBUG:
        print("reporter_api :: {0}".format(msg))


class Series(object):

    def __init__(self, mode=None):
        if mode == None:
            self.__mode = Mode.DROPBOX

        elif mode == Mode.LOCAL:
            self.__mode = Mode.LOCAL

        elif mode == Mode.DROPBOX:
            self.__mode = Mode.DROPBOX

        self.__setup()

    def __setup(self):
        if self.__mode == 0:
            self.__db = dropbox.Dropbox(ACCESS_TOKEN)
            self.__listFolderObj = self.__db.files_list_folder("/{0}".format(APP_PATH))

    def __fetchLocal(self):
        reportObjs = []
        home = os.path.expanduser("~")
        dropboxPath = os.path.join(str(home), "Dropbox", str(APP_PATH))
        files = glob.glob("{path}/*.json".format(path=dropboxPath))
        files.sort()

        if(DEBUG):
            start = time.time()

        for file in tqdm(files):
            fh = open(file, 'r')
            data = json.loads(fh.read())
            reportObjs.append(Report(data, file))

        end = time.time()
        log("Query time :: " + str(end - start))

        return reportObjs

    def __fetchDropbox(self):
        reporterObjs = []

        if(DEBUG):
            start = time.time()

        for i in tqdm(self.__listFolderObj.entries):
            if os.path.splitext(i.path_display)[1] == ".json":
                try:
                    md, res = self.__db.files_download(i.path_display)
                except HttpError as err:
                    print('*** HTTP error', err)
                    return None

                data = res.content
                reporterObj = Report(json.loads(data))
                reporterObjs.append(reporterObj)

        end = time.time()
        log("Query time :: " + str(end - start))

        return reporterObjs

    @property
    def reportObjs(self):
        if self.__mode == 0:
            reports = self.__fetchDropbox()
        else:
            reports = self.__fetchLocal()
            pass

        return reports

    @property
    def latestReport(self):
        """ Returns latest Report object """

        if self.__mode == 0:
            md, res = self.__db.files_download(self.__listFolderObj.entries[-1].path_display)
            data = res.content
            return Report(json.loads(data))


class Report(object):

    def __init__(self, data, filePath=None):
        self.__data = data
        self.__filePath = filePath
        self.__setup()

    def __setup(self):
        self.__snapshots = []
        for snapshot in self.__data["snapshots"]:
            snapshotObj = Snapshot(snapshot, parent=self)
            self.__snapshots.append(snapshotObj)

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

    @property
    def filePath(self):
        return self.__filePath


class Snapshot(object):

    def __init__(self, data, parent=None):
        self.__data = data
        self.__parent = parent
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

    @property
    def report(self):
        return self.__parent

if __name__ == "__main__":
    series = Series(Mode.DROPBOX)
    series.latestReport
