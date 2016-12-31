import pandas as pd


class ReportSeries(object):
    def __init__(self, reports, attributes):
        self.__reports = attributes
        self.__attributes = attributes

    def conform(self):
        cleanedCountries = [x for x in countries if x is not None]
        countryDict = {}
        for key, group in groupby(cleanedCountries):
            countryDict[key] = len(list(group))

    def series(self):
        s = pd.Series(np.random.randn(5), index=['a', 'b', 'c', 'd', 'e'])
