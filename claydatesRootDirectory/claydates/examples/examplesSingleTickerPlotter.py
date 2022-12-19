# Example usage for the SingleTickerPlotter class
# ====================================================================================================================
from claydates import SingleTickerPlotter

# ====================================================================================================================
# 1.) SingleTickerPlotter (class)

# You only need to specify the tickerSymbol, tickInterval, and numberOfUnits parameters. The rest are optional.
singleTickerPlotter = SingleTickerPlotter('QQQ', '1min', 1170)

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
singleTickerPlotter = SingleTickerPlotter(tickerSymbol = 'QQQ', tickInterval = '1min', numberOfUnits = 1170,
                                        percentageChange = True, timeZone = 'America/New_York', quoteCurrency = 'USD',
                                        logMissingData = True, mockResponse = False, spacingFactor = 14, 
                                        seriesType = 'Close', scalerRange = (0,1), binningFactor = 10,
                                        figureSize = [14.275,9.525], labelsize = 16, color = 'black')

# ====================================================================================================================
# 2.) datetimeHandler (method)

# Returns a dataframe with missing data values included as NaNs corresponding to the dates and times of those missing data units.
singleTickerPlotter.datetimeHandler('missingDataIncludedInFrame') 
# Determines and returns the percentage of missing data units included in the dataframe created upon instantiation of the class. In other words, how many units of data are missing from the dataframe.
singleTickerPlotter.datetimeHandler('missingPercentage')
# Determines and returns the lag time of thetime series dataframe created upon instantiation of the class In other words, how many units of time behind the current time is the dataframe.
singleTickerPlotter.datetimeHandler('lagTime')

# ====================================================================================================================
# 3.) unalteredFrameGetter (method)

# Returns a copy of the original unaltered version of the time series dataframe created upon instantiation of the class.
singleTickerPlotter.unalteredFrameGetter()

# ====================================================================================================================
# 4.) standardSinglePlot (method)

# Takes no direct argument(s). Is used to chart the original unaltered version of the time series dataframe created upon instantiation of the class. Do note that missing data units are not represented in this chart.
singleTickerPlotter.standardSinglePlot()

# ====================================================================================================================
# 5.) missingDataPlot (method)

# Takes no direct argument(s). Is used to chart missing data units alongside the original time series data. There will be gaps shown in the time series where the spaces are, and the missing data will be shown along the x-axis at the highest y value. 
singleTickerPlotter.missingDataPlot()

# ====================================================================================================================
# 6.) interpolatedSinglePlot (method)

# Used to plot the time series data with the missing values interpolated using the processs specified by one of two keyword argument parameters.
# Takes in input the following keyword argument: methodology
# methodology –––––– Used to specify how to interpolate the data. Acceptable parameters are either 'linear' or 'cubic'.
singleTickerPlotter.interpolatedSinglePlot(methodology = 'linear')
singleTickerPlotter.interpolatedSinglePlot(methodology = 'cubic')

# ====================================================================================================================
# 7.) profileProcessor (method)

# This method is used to return a histogram as a pandas dataframe. Please do note that the number of bins returned is (numberOfBins - 1). This method is used mainly for the singleProfilePlot(), but could be useful for other projects as well.
# Takes in input the following three arguments: numberOfBins, methodology, interpolation:
# numberOfBins –––––– Used to specify how many bins to chunk the data into.
# methodology ––––––– Used to specify how to process the data. The options are 'count', 'price', and 'volume'.
# interpolation ––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
singleTickerPlotter.profileProcessor(numberOfBins = 10, methodology = 'count', interpolation = 'linear')

#    Midpoints  countTradedAtMidpoint  Proportions              # Example output from the call above
# 0   273.7410                    303     0.259196
# 1   275.8030                    173     0.147990
# 2   277.8655                    205     0.175364
# 3   279.9280                     60     0.051326
# 4   281.9900                     14     0.011976
# 5   284.0520                     13     0.011121
# 6   286.1145                     73     0.062447
# 7   288.1770                     55     0.047049
# 8   290.2390                    273     0.233533

# ====================================================================================================================
# 8.) singleProfilePlot (method)

# Takes in input the following four arguments: seriesType, binningType, methodology, numberOfBins. The rest are optional:
# seriesType ––––––––– Used to specify whether or not to interpolate. The options are 'standard' or 'interpolated'. if standard, the data will not be interpolated.
# binningType –––––––– Used to specify how the data is to be binned. The options are 'standard', 'missingLength', or 'custom'.
# methodology –––––––– Used to specify how to process the data. The options are 'count', 'price', or 'volume'.
# numberOfBins ––––––– Used to specify how many bins to chunk the data into.
# scaledX –––––––––––– Used to specify whether or not to scale the x-axis. The options are True or False.
# scaledY –––––––––––– Used to specify whether or not to scale the y-axis. The options are True or False.
# interpolation –––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
singleTickerPlotter.singleProfilePlot(seriesType = 'standard', binningType = 'standard', methodology = 'price',
                                      numberOfBins = None, scaledX = True, scaledY = False, interpolation = None)

# ====================================================================================================================
# 9.) externalWindowSinglePlot (method)

# Takes no direct arguments. Is used to chart the original unaltered version of the time series dataframe created upon instantiation of the class, but in an external interactive window. Do note that missing data units are not represented in this chart. 
singleTickerPlotter.externalWindowSinglePlot()

# ====================================================================================================================
# 10.) liveSinglePlot (method)

# Optional arguments:
# numberOfUpdates ––––––––––––––––– The number of times to update the chart. The default is 14400, which is equal to 10 calendar days.
# interactiveExternalWindow ––––––– If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
# updateInterval –––––––––––––––––– The number of seconds to wait between updates. The default is 55 seconds, which should be sufficient to avoid any issues with the API's 60 second rate limit. There is also a 40 second waiting period declared in the __init__ for SingleTickerProcessor
singleTickerPlotter.liveSinglePlot(numberOfUpdates = 14400, interactiveExternalWindow = False, secondsToSleep = 55)

# ====================================================================================================================
