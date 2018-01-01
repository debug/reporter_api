from reporter_api.reports import Mode, Series
import pygal
series = Series(Mode.LOCAL)

config = pygal.Config()

happyValues = []
dates = []

for report in series.reportObjs:
    for snapshot in report.snapshots:
        if unicode("How happy are you?") in snapshot.responses.keys():
            happyValues.append(int(snapshot.responses[unicode("How happy are you?")]))


config.style = pygal.style.DarkStyle
bar_chart = pygal.Bar(config)
bar_chart.title = "Happiness by time."
bar_chart.x_labels = dates
bar_chart.add('Happiness', happyValues)

bar_chart.render_to_file("/Users/Dom/Desktop/moo.svg")
