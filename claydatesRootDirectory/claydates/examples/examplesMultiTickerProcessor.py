# Example usage for the MultiTickerProcessor class
# ====================================================================================================================
from claydates import MultiTickerProcessor

# ====================================================================================================================
# 1.) MultiTickerProcessor

# You only need to specify the tickerSymbols, tickInterval, and numberOfUnits parameters. The rest are optional.
# Can handle one, some, or many ticker symbols. The limitation here though with many is speed, due to the 8 API call/min ceiling.
multiTickerProcessor = MultiTickerProcessor(['QQQ','SPY','IWM','DIA'], '1min', 390)

# Shown in this implementation below with all parameters specified:
# Also here, is additional information on some of the more obscure sounding arguments:
# numberOfUnits ––––– Used to determine how many units of data to request from the API. Twelvedata's maximum request amount is 5000 units, 8 times per minute.
# percentageChange –– Is used to determine whether or not to compute and use percentage change data. The default is False, but can be changed to True. Some charts will seem unaffected by this, which is expected. Don't sweat it if you encounter this issue. Everything should be working as intended.
# logMissingData –––– If True, logs missing data and lag time to a csv file titled 'missingDataLog.csv', whcih is located in the datasets folder.
# mockResponse –––––– Is to be used for testing. It is set to True in the source code of the tests in the tests folder, but can be switched to False there to mock a response from the API call.
multiTickerProcessor = MultiTickerProcessor(tickerSymbols = ['QQQ','SPY','IWM','DIA'], tickInterval = '1min', numberOfUnits = 1170,
                                        percentageChange = True, timeZone = 'America/New_York', quoteCurrency = 'USD',
                                        logMissingData = True, mockResponse = False)

# ====================================================================================================================
# 2.) dateMatcher

# Method for matching one or more dataframe(s) by date. Is set to drop any data where the dataframe dates are inconsistent with one another, but this functionality can be toggled off by setting the dropMissing keyword argument to False.
# Optional arguments:
# dropMissing –––––– Used to determine whether or not missing data units in the individual frames should be concatenated as is (set argument equal to False), or dropped out from all of the dataframes (set argument equal to True, or pass no argument).
multiTickerProcessor.dateMatcher(dropMissing = True)

# ====================================================================================================================
# 3.) unalteredFrames

# Method for returning a list of dataframe(s) or array(s) containing the unaltered frame(s) originally returned from the SingleTickerProcessor class instantiation(s). This method does not modify the frame(s).
# Optional arguments:
# dataType –––––– Used to determine whether or not to return the frame(s) as a list of pandas dataframes, or a list of numpy array objects. Acceptable keyword arguments are 'pandas' or 'numpy'.
multiTickerProcessor.unalteredFrames(dataType = 'pandas')

# ====================================================================================================================
# 4.) missingUnitsIncluded

# Method for returning a list of dataframe(s) or array(s) containing the requested frame(s) and including any missing data.
# Optional arguments:
# dataType ––––––––––––––––– Used to determine whether or not to return the frame(s) as a list of pandas dataframes, or a list of numpy array objects. Acceptable keyword arguments are 'pandas' or 'numpy'.
# interpolationMethod –––––– Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
# matchDates ––––––––––––––– Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
multiTickerProcessor.missingUnitsIncluded(dataType = 'pandas', interpolationMethod = None, matchDates = False)

# ====================================================================================================================
# 5.) missingUnitsExcluded

# Optional arguments:
# dataType ––––––––––––––––– Used to determine whether or not to return the frame(s) as a list of pandas dataframes, or a list of numpy array objects. Acceptable keyword arguments are 'pandas' or 'numpy'.
# matchDates ––––––––––––––– Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
multiTickerProcessor.missingUnitsExcluded(dataType = 'pandas', matchDates = True)

# ====================================================================================================================
# 6.) missingPercentages

# Method to be used for printing information on missing data for the requested tickers. Also used for logging information if the logMissingData instance attribute is set to True during instantiation.
# Optional arguments:
#onlyPrint –––––––––––––– Used to specify whether or not the method is to be used to print missing data percentage and lag time, or to return it to be used for logging purposes.
multiTickerProcessor.missingPercentages(onlyPrint = True)

# QQQ:                                    # Example output, excluding the output returned for IWM and DIA (assuming one instantiated the class as implemented with the parameters from example 1).
# Missing: 0.00%
# Data Lagged by: 0 days 00:00:42

# SPY:
# Missing: 0.00%
# Data Lagged by: 0 days 00:00:42

# ====================================================================================================================
