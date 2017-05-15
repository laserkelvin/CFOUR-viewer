# FigureSettings.py

from plotly.offline import plot
from plotly.graph_objs import Scatter, Figure
from plotly.tools import make_subplots
from plotly.utils import PlotlyJSONEncoder
import plotly.plotly as pltly

import numpy as np
from scipy.constants import golden_ratio

import json

#init_notebook_mode(connected=False)


def GenerateColours(DataFrame=None, NumPlots=None, Colormap=["div", "Spectral"]):
    """ Generates a set of colours for Plotly

        Takes input as number of plots (integer)
        and a list containing the type of colourmap
        and the specific colourmap.

        Choices are:

        "div" - Diverging
                When plotting data that is supposed to
                highlight a middle ground; i.e.
                contrast between max and min data,
                effectively to show how the data
                deviates from the norm.
        ['RdYlBu','Spectral','RdYlGn','PiYG','PuOr','PRGn','BrBG','RdBu','RdGy']

        "seq" - Sequential
                When plotting data that is gradually
                changing smoothly. Should be used
                to map quanitative data.
        ['Reds','YlOrRd','RdPu','YlOrBr',
         'Greens','YlGnBu','GnBu','BuPu',
         'Greys','Oranges','OrRd','BuGn',
         'PuBu','PuRd','Blues','PuBuGn','YlGn','Purples']

        "qual" - Qualitative
                 When plotting data that does not
                 depend on intensity, rather to
                 highlight the different types of
                 data.

        ['Pastel2', 'Paired', 'Pastel1',
         'Set1', 'Set2', 'Set3', 'Dark2', 'Accent']

        Returns a dictionary with keys as columns.
    """
    if DataFrame is None and NumPlots is None:
        print("DataFrame and NPlots unspecified. Returning one colour!")
        NPlots = 1
    elif NumPlots is None:
        NPlots = len(DataFrame.keys())       # Get the number plots to make
    elif DataFrame is None:
        NPlots = NumPlots

    """ Three cases depending on the number of plots """
    if NPlots == 1:  # Just red for one plot
        Colors = ["#d7191c"]# ['rgb(252,141,89)']
    elif NPlots == 2:  # Red and blue for two plots
        Colors = ['#d7191c', '#2b83ba']
    elif NPlots == 3:  # Add blue to avoid yellow...
        Colors = ['#d7191c', '#1a9641', '#2b83ba']
    else:  # For n > 2, moar colours
        import colorlover as cl
        Colors = cl.scales[str(NPlots)][Colormap[0]][Colormap[1]]

    OutColors = dict()

    if DataFrame is None:
        for Index in range(NPlots):
            OutColors[Index] = Colors[Index]

    elif DataFrame is not None:
        for Index, Column in enumerate(DataFrame.keys()):        # Set colours
            OutColors[Column] = Colors[Index]

    return OutColors


def GenerateSymbols(DataFrame=None, NPlots=None):
    """ Function that will generate up to five symbols """
    OutSymbols = {}
    Symbols = ["circle",
               "square",
               "triangle-up",
               "hexagon",
               "diamond"
               ]
    if DataFrame is None and NPlots is not None:
        for Index in range(NPlots):
            OutSymbols[Index] = Symbols[Index]
    elif DataFrame is not None:
        NPlots = len(DataFrame.keys())
        for Index, Key in enumerate(DataFrame.keys()):
            OutSymbols[Key] = Symbols[Index]

    return OutSymbols


def GenerateColourMap(Data, Colormap=["div", "Spectral"]):
    """ Generate a linearly spaced colourmap """
    IntensityValues = np.linspace(0., 1., 5)   # Z scale cmap is normalised
    Colors = cl.scales["5"][Colormap[0]][Colormap[1]]
    Map = []
    for Index, Value in enumerate(IntensityValues):
        Map.append([Value, Colors[Index]])
    return Map


def GenerateAnnotation(X, Y, Text=None, Arrow=True):
    """ Generates a default arrow pointing
        downwards to a specified x,y point.

        Arguments include what text to display,
        and whether or not to display the arrowhead.

        This returns a dictionary, which should be appended
        to the layout["annotations"] list.
    """
    Annotation = {
        "x": X,
        "y": Y,
        "xref": "x",
        "yref": "y",
        "text": Text,
        "showarrow": Arrow,
        "arrowhead": 2.,
        "arrowsize": 1.5,
        "arrowwidth": 1.,
        "ax": 0.,
        "ay": -100.,
        "font": {
            "size": 14.,
            "color": "rgb(0, 0, 0)"
        },
        "align": "center"
    }
    return Annotation


def DefaultLayoutSettings(Format="Notebook", Grid=True):
    """ The default layout settings, such as Axis
        labels, plot background colour and size

        This will set up the plot with the idea of
        "themes", so that I can easily go between
        different audiences for the plot.

        Has the option to display the x/y grid - this is
        something I hop around a lot...

        Returns a dictionary called "LayoutSettings"

        Any modifications can be made to the dictionary prior
        to being plot.
    """
    if Format is "Notebook":
        """ This plot takes up the width of a Notebook cell. """
        TitleFont = 18.
        TickFont = 14.
        Width = 900.
        Height = Width / golden_ratio
    elif Format is "Paper":
        """ This is for publications. Will need fine-tuning."""
        TitleFont = 12.
        TickFont = 12.
        Width = 450.      # converts to 1.5in at 300 dpi
        Height = 450.

    LayoutSettings = {
        "xaxis": {
            "title": "X Axis",
            "titlefont": {
                "size": TitleFont,
            },
            "tickfont": {
                "size": TickFont
            }
        },
        "yaxis": {
            "title": "Y Axis",
            "titlefont": {
                "size": TitleFont,
            },
            "tickfont": {
                "size": TickFont
            }
        },
        "plot_bgcolor": "rgb(229, 229, 229)",
        "autosize": False,
        "width": Width,
        "height": Height,
        "legend": {
            "traceorder": "normal",
            "bgcolor": "rgb(229, 229, 229)",
            "borderwidth": 1.,
        },
        #"annotations": dict()
    }

    if Grid is True:
        """ To show the x/y axis grids """
        LayoutSettings["xaxis"]["showgrid"] = True
        LayoutSettings["xaxis"]["gridwidth"] = 2
        LayoutSettings["xaxis"]["gridcolor"] = "#bdbdbd"
        LayoutSettings["yaxis"]["showgrid"] = True
        LayoutSettings["yaxis"]["gridwidth"] = 2
        LayoutSettings["yaxis"]["gridcolor"] = "#bdbdbd"
    elif Grid is False:
        LayoutSettings["xaxis"]["showgrid"] = False
        LayoutSettings["yaxis"]["showgrid"] = False

    return LayoutSettings


def GenerateSubPlotObject(ColumnNames, NRows, NCols, Orientation="Square"):
    """ This generates an instance of a subplot object.

        By specifying the names of each plot, the number of rows and
        columns you want, it will return a matrix for you to populate
        with plots using the SubplotObject.append_trace() method.

    """
    SubplotObject = make_subplots(
            rows=NRows,
            cols=NCols,
            horizontal_spacing=0.1,
            vertical_spacing=0.1,
            shared_xaxes=True,
            shared_yaxes=True,
            print_grid=True,
            subplot_titles=ColumnNames
        )
    return SubplotObject


def MakeSubplot(DataFrame,
                NRows,
                NCols,
                YErr=None,
                Orientation="Square",
                Connected=False,
                Axes=["X", "Y"]):
    """ Function for generating a matrix of subplots, based on a single
        DataFrame.

        Arguments are a DataFrame, where the index corresponds to the x
        axis values, and each column as y. The product of the columns and rows
        specified must equal the number of DataFrame columns.

        Since this function doesn't return a Layout dict directly, the
        optional argument Axes can be supplied with a 2-tuple list of
        strings, corresponding to the x and y axis labels.
    """

    Check = NRows * NCols
    if len(DataFrame.keys()) != Check:
        print("Number of rows/columns inconsistent with DataFrame!")
        pass
    else:
        """ Figure out how many plots, and what they're called """
        NPlots = len(DataFrame.keys())
        ColumnNames = list(DataFrame.keys())

        if Orientation == "Landscape":
            Width = 900.
            Height = Width / golden_ratio
        elif Orientation == "Portrait":
            Height = 700.
            Width = Height / golden_ratio
        elif Orientation == "Square":
            Height = 600.
            Width = Height

        """ Calculate the range that we should plot, pad by 10% of values """
        XRange = [min(DataFrame.index) + min(DataFrame.index) * 0.1,
                  max(DataFrame.index) + max(DataFrame.index) * 0.1
                  ]
        YRange = [min(DataFrame.min()) + min(DataFrame.min()) * 0.1,
                  max(DataFrame.max()) + max(DataFrame.max()) * 0.1
                  ]

        """ Create an instance of subplot """
        SubplotObject = GenerateSubPlotObject(ColumnNames,
                                              NRows,
                                              NCols,
                                              Orientation)

        """ Formulate the subplot matrix into rows/columns """
        PlotMatrix = np.reshape(range(NPlots), (NRows, NCols))
        """ This iterator will keep track of what plot is where """
        Iterator = np.nditer(PlotMatrix, flags=["multi_index"])
        while not Iterator.finished:     # Loop over plots
            RowIndex, ColumnIndex = Iterator.multi_index
            RowIndex = RowIndex + 1
            ColumnIndex = ColumnIndex + 1
            Index = Iterator.value       # get the flat plot number
            Column = ColumnNames[Index]  # get the dataframe column name
            if YErr is not None:
                Plot = DefaultScatterObject(DataFrame.index,
                                            DataFrame[Column],
                                            YErr=YErr[Column],
                                            Colour='rgb(103,169,207)',
                                            Connected=Connected,
                                            Name=Column,
                                            )
            elif YErr is None:
                Plot = DefaultScatterObject(DataFrame.index,
                                            DataFrame[Column],
                                            Colour='rgb(103,169,207)',
                                            Connected=Connected,
                                            Name=Column,
                                            )
            SubplotObject.append_trace(Plot, RowIndex, ColumnIndex)
            Iterator.iternext()

        """ Set the figure size and turn the legend off """
        SubplotObject["layout"].update(width=Width,
                                       height=Height,
                                       showlegend=False
                                       )

        """ Set up axes labels and ranges to be consistent """
        for Row in range(1, NRows + 1):
            SubplotObject["layout"]["yaxis" + str(Row)].update(
                {
                    "title": Axes[1],
                    "range": YRange
                }
            )
            for Column in range(1, NCols + 1):
                SubplotObject["layout"]["xaxis" + str(Column)].update(
                    {
                        "title": Axes[0],
                        "range": XRange
                    }
                )
    return SubplotObject


def DefaultScatterObject(X, Y, Colour="rgb(103,169,207)", Name=None,
                         Symbol="circle", YErr=None, Connected=False):
    """ This is the function I will default to for generating a quick scatter
        plot. All you need to supply is x and y arrays.

        Optional arguments are the colour, the name of the trace, the
        symbols used to plot, the Y-error values, and whether or not
        we're using a continous plot (instead of a scatter plot).

        Colours can be produced by the GenerateColours() function.

        Returns a Scatter object.
    """
    if Connected is True:
        Mode = "lines"
    elif Connected is False:
        Mode = "markers"
    ScatterObject = Scatter(
        {
            "x": X,
            "y": Y,
            "marker": {
                "symbol": Symbol,
                "line": {
                    "width": 1.,
                    "color": "rgb(0, 0, 0)"
                },
                "size": 10.,
                "color": Colour,
                "opacity": 0.7,
            },
            "line": {
                "width": 1.5
            },
            "error_y": {
                "type": "data",
                "array": YErr,
                "visible": True,
                "color": Colour,
            },
            "mode": Mode,
            "name": Name
        }
    )
    return ScatterObject


def ContinousErrorObject(X, Y, YErr, Colour="rgb(103,169,207)", Name=None):
    UpperY = Y + np.abs(YErr)
    LowerY = Y - np.abs(YErr)
    Plot = DefaultScatterObject(X=X, Y=Y, Colour=Colour, Name=Name, Connected=True)
    UpperPlot = DefaultScatterObject(X=X, Y=UpperY, Colour=Colour, Name=None, Connected=True)
    LowerPlot = DefaultScatterObject(X=X, Y=LowerY, Colour=Colour, Name=None, Connected=True)
    Plot["line"]["width"] = 3.

    UpperPlot["line"] = Line(width=0.)
    #UpperPlot["fillcolor"] = Colour
    UpperPlot["fill"] = "tonexty"
    UpperPlot["opacity"] = 0.01
    UpperPlot["showlegend"] = False
    LowerPlot["hoverinfo"] = "none"

    LowerPlot["line"] = Line(width=0.)
    #LowerPlot["fillcolor"] = Colour
    LowerPlot["fill"] = "tonexty"
    LowerPlot["opacity"] = 0.01
    LowerPlot["showlegend"] = False
    LowerPlot["hoverinfo"] = "none"

    return [Plot, UpperPlot, LowerPlot]


def MultiDFPlots(DataFrameList, ColourList=None, SymbolList=None, Connected=False):
    Plots = list()
    NPlots = len(DataFrameList)

    if ColourList is None:
        ColourList = GenerateColours(NumPlots=NPlots)

    if SymbolList is None:
        SymbolList = GenerateSymbols(NPlots=NPlots)

    for Index, DataFrame in enumerate(DataFrameList):
        Name = DataFrame.keys()[0]
        if "YErr" in DataFrame.keys():
            YErr = DataFrame["YErr"]
        else:
            YErr = None
        Plots.append(
                DefaultScatterObject(
                        X=DataFrame.index,
                        Y=DataFrame[Name],
                        Name=Name,
                        Colour=ColourList[Index],
                        Connected=Connected,
                        Symbol=SymbolList[Index],
                        YErr=YErr
                    )
            )
    return Plots


def plotize(data, layout=None):
    """Plot with Plotly.js using the Plotly JSON Chart Schema

    http://help.plot.ly/json-chart-schema/

    This function is for displaying plots in nteract
    """
    if layout is None:
        layout = DefaultLayoutSettings()

    redata = json.loads(json.dumps(data, cls=PlotlyJSONEncoder))
    relayout = json.loads(json.dumps(layout, cls=PlotlyJSONEncoder))

    bundle = {}
    bundle['application/vnd.plotly.v1+json'] = {
        'data': redata,
        'layout': relayout,
    }

    IPython.display.display(bundle, raw=True)


def save_plotly_html(figure, filename):
    """ This function will export a plotly plot as HTML """
    with open(filename, "w+") as WriteFile:
        WriteFile.write(
                figure,
                output="div",
                auto_open=False
            )


def save_plotly_png(figure, filename):
    pltly.image.save_as(figure, filename=filename, format="png")
