import reporter_api.reports as reports
from reporter_api.reports import Fetcher
from reporter_api.datamodel import ReportSeries

from math import pi, sin, cos

from bokeh.util.browser import view
from bokeh.colors import skyblue, seagreen, tomato, orchid, firebrick, lightgray
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.models.glyphs import Wedge, AnnularWedge, ImageURL, Text
from bokeh.models import ColumnDataSource, Plot, Range1d
from bokeh.resources import INLINE
from bokeh.sampledata.browsers import browsers_nov_2013, icons

from bokeh.charts import Area, show, output_file, defaults
from bokeh.layouts import row

def graphWeightVsHappiness():

    fetcher = Fetcher()
    reportObjs = fetcher.getAllReports()
    happiness = []
    weight = []

    for report in reportObjs:
        for snapshot in report.snapshots:
            #reports.log(snapshot.date)
            happiness.append(snapshot.responses['How happy are you?'])
            weight.append(snapshot.weight)
            #reports.log(snapshot.battery)
            #countries.append(snapshot.country)
            #reports.log(snapshot.weight)
            #reports.log(snapshot.altitude)
            #reports.log(snapshot.connection)
            #reports.log(snapshot.steps)
            #reports.log(snapshot.humidity)
            #reports.log(snapshot.tempC)
            #reports.log(snapshot.weather)
            #print("\n")

    print(weight)
    print(happiness)

    defaults.width = 400
    defaults.height = 400

    # create some example data
    data = dict(
        python=[2, 3, 7, 5, 26, 221, 44, 233, 254, 265, 266, 267, 120, 111],
        pypy=[12, 33, 47, 15, 126, 121, 144, 233, 254, 225, 226, 267, 110, 130],
        jython=[22, 43, 10, 25, 26, 101, 114, 203, 194, 215, 201, 227, 139, 160],
    )

    area1 = Area(data, title="Area Chart", legend="top_left",
                 xlabel='time', ylabel='memory')

    area2 = Area(data, title="Stacked Area Chart", legend="top_left",
                 stack=True, xlabel='time', ylabel='memory')

    output_file("area.html", title="area.py example")

    #show(row(area1, area2))

def plotDonut():
    fetcher = Fetcher()
    reportObjs = [fetcher.getLatestReport()]
    countries = []

    for report in reportObjs:
        for snapshot in report.snapshots:
            reports.log(snapshot.date)
            reports.log(snapshot.responses)
            reports.log(snapshot.battery)
            countries.append(snapshot.country)
            reports.log(snapshot.weight)
            reports.log(snapshot.altitude)
            reports.log(snapshot.connection)
            reports.log(snapshot.steps)
            reports.log(snapshot.humidity)
            reports.log(snapshot.tempC)
            reports.log(snapshot.weather)
            print("\n")

    f = ReportSeries([], [])

    series = f.series()

    #df = browsers_nov_2013
    #print(type(df))
    xdr = Range1d(start=-2, end=2)
    ydr = Range1d(start=-2, end=2)

    plot = Plot(x_range=xdr, y_range=ydr, plot_width=800, plot_height=800)
    plot.title.text = "Web browser market share (November 2013)"
    #plot.toolbar_location = None

    colors = {"Chrome": seagreen, "Firefox": tomato, "Safari": orchid, "Opera": firebrick, "IE": skyblue, "Other": lightgray}
    #s = pd.Series(np.random.randn(5), index=['a', 'b', 'c', 'd', 'e'])

    print(dir(series))
    b()

    aggregated = series.groupby("Browser").agg(sum)

    selected = aggregated[aggregated.Share >= 1].copy()
    selected.loc["Other"] = aggregated[aggregated.Share < 1].sum()
    browsers = selected.index.tolist()

    radians = lambda x: 2*pi*(x/100)
    angles = selected.Share.map(radians).cumsum()

    end_angles = angles.tolist()
    start_angles = [0] + end_angles[:-1]

    browsers_source = ColumnDataSource(dict(
        start  = start_angles,
        end    = end_angles,
        colors = [colors[browser] for browser in browsers ],
    ))

    glyph = AnnularWedge(x=0, y=0, line_color="white",
        line_width=2, start_angle="start", end_angle="end", fill_color="colors", inner_radius=.3, outer_radius=.8)

    print(dir(glyph))

    #glyph = AnnularWedge(x=0, y=0, inner_radius=1, outer_radius=1.5, start_angle="start", end_angle="end", line_color="white", line_width=2, fill_color="fill")


    plot.add_glyph(browsers_source, glyph)


    doc = Document()
    doc.add_root(plot)

    doc.validate()
    filename = "donut.html"
    with open(filename, "w") as f:
        f.write(file_html(doc, INLINE, "Donut Chart"))
    print("Wrote %s" % filename)
    view(filename)

if __name__ == "__main__":
    #    plotDonut()
    graphWeightVsHappiness()
