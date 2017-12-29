import pandas as pd
from itertools import groupby
import numpy

class ReportSeries(object):
    def __init__(self, reports, attributes):
        if isinstance(reports, list) != True and isinstance(attributes, list) != True:
            raise TypeError("arguments must be of type list()")

        self.__reports = attributes
        self.__attributes = attributes

    def conform(self):
        cleanedCountries = [x for x in countries if x is not None]
        countryDict = {}
        for key, group in groupby(cleanedCountries):
            countryDict[key] = len(list(group))

    def series(self):
        series = pd.Series([10, 15, 20, 25, 30], index=['a', 'b', 'c', 'd', 'e'])
        return series
