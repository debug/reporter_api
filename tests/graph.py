from reporter_api.reports import Fetcher

def plotDonut():
    fetcher = Fetcher()
    reports = fetcher.getAllReports()
    countries = []

    for report in reports:
        for snapshot in report.snapshots:
            log(snapshot.date)
            log(snapshot.responses)
            log(snapshot.battery)
            countries.append(snapshot.country)
            log(snapshot.weight)
            log(snapshot.altitude)
            log(snapshot.connection)
            log(snapshot.steps)
            log(snapshot.humidity)
            log(snapshot.tempC)
            log(snapshot.weather)
            print("\n\n")

if __name__ == "__main__":
    pass
