# Example usage for the MultiTickerPlotter class
# ====================================================================================================================
from claydates import MultiTickerPlotter

# ====================================================================================================================
# 1.) MultiTickerPlotter (class)

# You only need to specify the tickerSymbols, tickInterval, and numberOfUnits parameters. The rest are optional.
# Can handle one, some, or many ticker symbols. The limitation here though with many is speed, due to the 8 API call/min ceiling.
multiTickerPlotter = MultiTickerPlotter(['QQQ','SPY','IWM','DIA'], '1min', 390)

# Shown in this implementation below with all parameters specified:
# Also here, is additional information on some of the more obscure sounding arguments:
# numberOfUnits ––––– Used to determine how many units of data to request from the API. Twelvedata's maximum request amount is 5000 units, 8 times per minute.
# percentageChange –– Is used to determine whether or not to compute and use percentage change data. The default is False, but can be changed to True. Some charts will seem unaffected by this, which is expected. Don't sweat it if you encounter this. Everything should be working as intended.
# logMissingData –––– If True, logs missing data and lag time to a csv file titled 'missingDataLog.csv', whcih is located in the datasets folder.
# mockResponse –––––– Is to be used for testing. It is set to True in the source code of the tests in the tests folder, but can be switched to False there to mock a response from the API call.
# spacingFactor ––––– Is used to determine the spacing between the x-axis and y-axis major ticks. If you want to change the spacing, you can do so by specifying a different value for this parameter. If it is set larger to a value larger than 10, the x-axis tick labels will rotate. This is to prevent overlap.
# seriesType –––––––– Is used to determine which series of data to plot. The options are 'Open', 'High', 'Low', 'Close', and 'Volume'. The default is 'Close'.
# scalerRange ––––––– Is used to determine the range of the y, and in some cases x axes for some of the plots which allow you to scale the axes. The default is (0,1). If you want to change the range, you can do so by specifying a different value for this parameter.
# binningFactor ––––– Is used to determine the number of bins for the various types of histogram charts which can be specified in the singleProfilePlot's arguments. The default is 10, which seems to work fairly nice. If you want to change the number of bins, you can do so by specifying a different value for this parameter. This will be used as the denominator for binning data in singleProfilePlot.
# figureSize –––––––– Is used to determine the size of the figures. The default is [14.275,9.525], but can be changed. You may encounter some issues with the external/interactive window plots depending on your screen size, so to fix this, adjust the lines that say "plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)" accordingly."
# labelsize ––––––––– Is used to determine the size of the labels on the x and y axes. The default is 16, but can be changed.
# color ––––––––––––– Is used to determine the color of the plots. The default is 'black', but can be changed by passing a different color for this argument. Color can also be changed more dynamically in the interactive external windows thanks to matplotlib in Figure Options -> Curves
multiTickerPlotter = MultiTickerPlotter(tickerSymbols = ['QQQ','SPY','IWM','DIA'], tickInterval = '1min', numberOfUnits = 1170,
                                        percentageChange = True, timeZone = 'America/New_York', quoteCurrency = 'USD',
                                        logMissingData = True, mockResponse = False, spacingFactor = 14, 
                                        seriesType = 'Close', scalerRange = (0,1), binningFactor = 10,
                                        figureSize = [14.275,9.525], labelsize = 16, color = 'black')

# ====================================================================================================================
# 2.) standardMultiPlot (method)

# Takes in input one argument: method. The rest are optional.
# method ––––––––––––––––––––––––-–– Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded
# matchDates ––––––––––––––––––––-–– Determines whether or not to ensure that all the date/time units are matching for the data.
# interpolationMethod –––––––––––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
# interactiveExternalWindow ––––––-– If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
# scaled ––––––––––––––––––––––––––– Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled
# plotTitle –––––––––––––––––––––––– Used to pass a custom title, if desired. Takes in input the string that would compose the title (see examples folder for more information).
multiTickerPlotter.standardMultiPlot(method = multiTickerPlotter.missingUnitsExcluded, matchDates = True, interpolationMethod = None,
                                     interactiveExternalWindow = False, scaled = True, plotTitle = 'Example Plot')

# ====================================================================================================================
# 3.) cyclePlot (method)

# Takes in input one argument: method. The rest are optional.      
# Method for plotting the time series dataframe(s) individually, one after another. One figure is closed out as the next is opened, until they are cycled through.
# method ––––––––––––––––––––––––-–– Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded
# matchDates ––––––––––––––––––––-–– Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
# interpolationMethod –––––––––––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
# interactiveExternalWindow –––––-–– If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
# scaled ––––––––––––––––––––––––––– Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled
# plotTitle –––––––––––––––––––––––– Used to pass a custom title, if desired. Takes in input the string that would compose the title (see examples folder for more information).
# secondsToPauseFor –––––––––––––-–– Determines how long to "hover" over one chart until the next chart replaces it. In other words, defines the time between chart updates.

multiTickerPlotter.cyclePlot(method = multiTickerPlotter.missingUnitsExcluded, matchDates = True, interpolationMethod = None, 
                             interactiveExternalWindow = False, scaled = True, secondsToPauseFor = 15)

# ====================================================================================================================
# 4.) profileCyclerPlot (method)

# Takes in input the following three arguments: numberOfBins, methodology, interpolation. The rest are optional
# This method is used to cycle through various histogram(s), plotting one after another.
# seriesType ––––––––––––––––––––– Used to specify whether or not to interpolate data. The options are 'standard' or 'interpolated'. if standard, the data will not be interpolated.
# binningType –––––––––––––––––––– Used to specify how the data is to be binned. The options are 'standard', 'missingLength', or 'custom'.
# methodology –––––––––––––––––––– Used to specify how to process the data. The options are 'count', 'price', or 'volume'.
# numberOfBins ––––––––––––––––––– Used to specify how many bins to chunk the data into.
# scaledX –––––––––––––––––––––––– Used to specify whether or not to scale the x axis.
# scaledY –––––––––––––––––––––––– Used to specify whether or not to scale the y axis.
# interpolation –––––––––––––––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
multiTickerPlotter.profileCyclerPlot('standard','standard', methodology = 'price', numberOfBins = None,
                                       scaledX = True, scaledY = True, interpolation = None)

# ====================================================================================================================
# 5.) multipleExternalWindowsPlot (method)

# Takes in input one argument: method. The rest are optional.      
# Method for plotting the time series dataframe(s) in individual external windows. The idea behind this is one could drag the plots over to another screen if desired.
# method –––––––––––––––––––––––––– Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded
# matchDates –––––––––––––––––––––– Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
# interpolationMethod ––––––––––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
# interactiveExternalWindow ––––––– If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
# scaled –––––––––––––––––––––––––– Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled
multiTickerPlotter.multipleExternalWindowsPlot(method = multiTickerPlotter.missingUnitsExcluded, matchDates = True, interpolationMethod = None,
                                              interactiveExternalWindow = False, scaled = True)

# ====================================================================================================================
# 6.) liveMultiPlot (method)

# Takes in input one argument: method. The rest are optional.
# method –––––––––––––––––––––––––– Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded
# matchDates –––––––––––––––––––––– Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
# interpolationMethod ––––––––––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
# interactiveExternalWindow ––––––– If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
# scaled –––––––––––––––––––––––––– Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled
# numberOfUpdates ––––––––––––––––– The number of times to update the chart. The default is 14400, which is equal to 10 calendar days.
# secondsToSleepFor ––––––––––––––– The number of seconds to wait between updates. The default is 55 seconds, which should be sufficient to avoid any issues with the API's 60 second rate limit. There is also a 40 second waiting period declared in the __init__ for SingleTickerProcessor
multiTickerPlotter.liveMultiPlot(method = multiTickerPlotter.missingUnitsExcluded, matchDates = True, interpolationMethod = None,
                                interactiveExternalWindow = False, scaled = True, numberOfUpdates = 14400, secondsToSleepFor = 55)

# ====================================================================================================================


