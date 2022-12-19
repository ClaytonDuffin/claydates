# Example usage for the SingleTickerPlotter class
# ====================================================================================================================
from claydates import SingleTickerProcessor

# ====================================================================================================================
# 1.) SingleTickerProcessor (class))

# You only need to specify the tickerSymbol, tickInterval, and numberOfUnits parameters. The rest are optional.
singleTickerProcessor = SingleTickerProcessor('QQQ', '1min', 1170)

# Shown in this implementation below with all parameters specified:
# Also here, is additional information on some of the more obscure sounding arguments:
# numberOfUnits ––––––– Used to determine how many units of data to request from the API. Twelvedata's maximum request amount is 5000 units, 8 times per minute.
# percentageChange –––– Is used to determine whether or not to compute and use percentage change data. The default is False, but can be changed to True. Some charts will seem unaffected by this, which is expected. Don't sweat it if you encounter this. Everything should be working as intended.
# logMissingData –––––– If True, logs missing data and lag time to a csv file titled 'missingDataLog.csv', whcih is located in the datasets folder.
# mockResponse –––––––– Is to be used for testing. It is set to True in the source code of the tests in the tests folder, but can be switched to False there to mock a response from the API call.
singleTickerProcessor = SingleTickerProcessor(tickerSymbol = 'QQQ', tickInterval = '1min', numberOfUnits = 1170,
                                            percentageChange = True, timeZone = 'America/New_York', quoteCurrency = 'USD',
                                            logMissingData = True, mockResponse = False)

# ====================================================================================================================
# 2.) datetimeHandler (method)

# Returns a dataframe with missing data values included as NaNs corresponding to the dates and times of those missing data units.
singleTickerProcessor.datetimeHandler('missingDataIncludedInFrame') 
# Determines and returns the percentage of missing data units included in the dataframe created upon instantiation of the class. In other words, how many units of data are missing from the dataframe.
singleTickerProcessor.datetimeHandler('missingPercentage')
# Determines and returns the lag time of thetime series dataframe created upon instantiation of the class. In other words, how many units of time behind the current time is the dataframe.
singleTickerProcessor.datetimeHandler('lagTime')

# ====================================================================================================================
# 3.) unalteredFrameGetter (method)

# Returns a copy of the original unaltered version of the dataframe created upon instantiation of the class.
singleTickerProcessor.unalteredFrameGetter()

# ====================================================================================================================




