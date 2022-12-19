import datetime
import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
plt.rc('figure', max_open_warning = 0)
from twelvedata import TDClient
import pandas_market_calendars as mktCal
from typing import Optional, Callable, Union
pd.options.mode.chained_assignment = None
import os 
import inspect
import csv

class SingleTickerProcessor():

    '''
    Class used for gathering and cleaning time series data. Determines where there might be any missing dates coming in from the API call. Also can be used for logging the quality of data received from the API call to a CSV file, to be reviewed at a later date
    It is used to iteratively construct one or more time series objects of the SingleTickerProcessor class in multiTickerProcessor.py.
    It is also the parent class of the SingleTickerPlotter class, which is the parent of the multiTickerPlotter class.
    
    Parameters
    ----------
    tickerSymbol : str
        The ticker symbol of the asset or currency pair to be processed.
    tickInterval : str
        The interval of time between each data point. Options are: '1min', '5min', '15min', '30min', '45min', '1h', '2h', '4h', '8h', '1day', '1week', and '1month'.
    numberOfUnits : int
        The number of units of data to request from the API. Twelvedata's maximum request amount is 5000 units, 8 times per minute.
    percentageChange : bool, optional
        Used to determine whether or not to compute and use percentage change data. The default is False, but can be changed to True. Some charts will seem unaffected by this, which is expected. Don't sweat it if you encounter this. Everything should be working as intended. 
    timeZone : str, optional 
        The time zone of the data. The default is 'America/New_York'.
    quoteCurrency : str, optional
        The quote currency of the data. The default is 'USD'.
    logMissingData : bool, optional
        If True, logs missing data and lag time to a csv file titled 'missingDataLog.csv' in the datasets folder. The default is False, but I encourage using this functionality.
    mockResponse : bool, optional
        Backend argument. Is used for testing. It is locally set to True directly in the source code of the tests in the tests folder, and can be switched to False there to mock a response from the API call.
    '''

    def __init__(self,
                 tickerSymbol: str,
                 tickInterval: int,
                 numberOfUnits: int,
                 percentageChange: Optional[bool] = None,
                 timeZone: Optional[str] = None,
                 quoteCurrency: Optional[str] = None,
                 logMissingData: Optional[bool] = False,
                 mockResponse: Optional[bool] = False) -> None:

        '''Initializes the SingleTickerProcessor class and defines some of its attributes.'''
        
        self._tickerSymbol = tickerSymbol
        self._tickInterval = tickInterval
        self._numberOfUnits = numberOfUnits 
        self._percentageChange = percentageChange or False 
        self._timeZone = timeZone or 'America/New_York'
        self._currencyPairsfilePath = (str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) + '/datasets/currencyPairs.txt')
        self._currencyPairs = open(self._currencyPairsfilePath, 'r').read().split(',') 
    
        if (quoteCurrency == None):
            self._quoteCurrency = '/USD'
        else:
            self._quoteCurrency = ('/' + quoteCurrency)
        
        self._apiKeyfilePath = (str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) + '/datasets/key.txt')
        self._apiKey = open(self._apiKeyfilePath, 'r').read()
        if self._apiKey == '':
            print('Please obtain an API key from https://twelvedata.com/ and add it to the KEY.txt file.')
        
        self._mockResponse = mockResponse
        if mockResponse:
            self._assetTimeSeriesfilePath = (str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) + '/datasets/exampleSet.csv')
            self._assetTimeSeries = pd.read_csv(self._assetTimeSeriesfilePath, index_col = [0])
            self._assetTimeSeries['Date'] = pd.to_datetime(self._assetTimeSeries['Date'])
        else:
            try:
                self._assetTimeSeries = self.apiCall()        
            except:
                print('\nOne of two problems occured. Either the 8 call/min API ceiling was exceeded,\nor there was an InvalidApiKeyError thrown, which will be stated above if this is the case:\nsleeping for 40 seconds before proceeding...')
                time.sleep(40)
                self._assetTimeSeries = self.apiCall()
            
        self._intermediaryInterval = self.interval()
        self._intermediaryUnits = self.units()

        if logMissingData:
            self.logDataCharacteristics()
            
    def apiCall(self) -> pd.DataFrame:

        '''Method used to call upon the Twelvedata API to gather desired time series data.'''

        td = TDClient(apikey= str(self._apiKey))
        
        if self._tickerSymbol in self._currencyPairs:
            self._tickerSymbol = (self._tickerSymbol + self._quoteCurrency)    
        
        timeSeries = td.time_series(symbol = self._tickerSymbol,
                                    interval = self._tickInterval,
                                    outputsize = self._numberOfUnits,
                                    timezone = self._timeZone).as_pandas().iloc[::-1].reset_index()
    
        if (len(self._tickerSymbol) > 4):
            timeSeries.columns = ['Date','Open','High','Low','Close']
        else:
            timeSeries.columns = ['Date','Open','High','Low','Close','Volume']
        
        if (len(timeSeries) < self._numberOfUnits):
            print('Was only able to gather ' + str((len(timeSeries)) + ' of the ' + str(self._numberOfUnits) + ' desired units for ' + self._tickerSymbol))
        
        return (timeSeries)
    
    
    def interval(self) -> int:

        '''Method used to remove string characters from the tickInterval parameter, and return an integer value. So if someone passes "45min" as the tickInterval, this method will return 45.'''
        
        for i in range(1,3):
            try:
                timeInterval = int(self._tickInterval[0:i])
            except:
                pass
        return (timeInterval)
    
    
    def units(self) -> str:
        
        '''Method used to do some more parsing so that the TwelveData API can interpret which tickInterval is being passed.'''

        for i in range(2,3):
            try:
                timeUnit = (self._tickInterval[-i:])
                timeUnit = ''.join([char for char in timeUnit if not char.isdigit()])
                if timeUnit == 'h':
                    return ('hours')
                if timeUnit == 'in':
                    return ('minutes')
                if timeUnit == 'ay':
                    return ('days')
                if timeUnit == 'ek':
                    return ('weeks')
                if timeUnit == 'th':
                    return ('months')
            except:
                print('Passed invalid time unit(s) to the constructor. Please correct the error when reinstantiating the class.')


    def marketCalendarInterval(self) -> str:

        '''Method used to do some more parsing so that pandas market-calendars package can interpret which tickInterval is being passed.'''

        for i in range(1,3):
            try:
                timeInterval = int(self._tickInterval[0:i])
            except:
                pass
        
        if (self.units() == 'minutes'):
            return (str(timeInterval) + 'm')
        if (self.units() == 'days'):
            return (str(timeInterval) + 'd')


    @staticmethod
    def isNowInTimePeriod(startTime: datetime.time,
                          endTime: datetime.time,
                          currentTime: datetime.time) -> bool: 
        
        '''Method used to determine if a given time (the last unit of the dataframe) is within standard market hours.
        
         Parameters
        ----------
        startTime: str
            09:30.
            
        endTime: pd.DataFrame
            16:00.
            
        currentTime: bool, optional
            The last unit of the dataframe being examined.
        '''
        
        if startTime < endTime: 
            return currentTime >= startTime and currentTime <= endTime 
        else: 
            return currentTime >= startTime or currentTime <= endTime
    
    
    def outputForDatetimeHandler(self,
                                 desiredOutput: str,
                                 missingDataHolidaysExcluded: pd.DataFrame,
                                 silencePrint: Optional[bool] = False) -> pd.DataFrame:
        
        '''
        Method used to shorten the syntax of the datetimeHandler method. Returns the desired output in the datetimeHandler method.
                
        Parameters
        ----------
        desiredOutput: str
            The desired output from the datetimeHandler method. The options are 'missingPercentage','missingDataIncludedInFrame', and 'lagTime'.
            
        missingDataHolidaysExcluded: pd.DataFrame
            The dataframe to be taken in input that is already being handled and generated within the datetimeHandler method.
            
        silencePrint: bool, optional
            If True, the method will not print anything to the console. This is provided and used for testing, as well as multi-plot processing.
        '''

        if (desiredOutput == 'missingPercentage'):
            if (len(self._tickerSymbol) <= 4):
                if not silencePrint:
                    print( 'Missing: ' + '%.2f' % ((len(missingDataHolidaysExcluded) - (len(self._assetTimeSeries))) / (len(self._assetTimeSeries)) * 100) + '%')
                    if ((self.isNowInTimePeriod(datetime.time(9,30), datetime.time(16,00),datetime.datetime.now().time())) == False):
                        print('Data Lagged by: 0 days 00:00:00')
                    else:
                        print('Data Lagged by: ' + str(datetime.datetime.now() - missingDataHolidaysExcluded['Date'].iloc[-1])[0:15])
                    return ((len(missingDataHolidaysExcluded) - (len(self._assetTimeSeries))) / (len(self._assetTimeSeries)))        
                else:
                    return ((len(missingDataHolidaysExcluded) - (len(self._assetTimeSeries))) / (len(self._assetTimeSeries)))        
            else:
                if not silencePrint:
                    print( 'Missing: ' + '%.2f' % ((len(missingDataHolidaysExcluded) - (len(self._assetTimeSeries))) / (len(self._assetTimeSeries)) * 100) + '%')
                    print('Data Lagged by: ' + str(datetime.datetime.now() - missingDataHolidaysExcluded.index[-1])[0:15])
                    return ((len(missingDataHolidaysExcluded) - (len(self._assetTimeSeries))) / (len(self._assetTimeSeries)))
                else:
                    return ((len(missingDataHolidaysExcluded) - (len(self._assetTimeSeries))) / (len(self._assetTimeSeries)))
            
        elif (desiredOutput == 'missingDataIncludedInFrame'):
            return (missingDataHolidaysExcluded.reset_index())

        elif (desiredOutput == 'lagTime'):
            if (len(self._tickerSymbol) <= 4):
                if ((self.isNowInTimePeriod(datetime.time(9,30), datetime.time(16,00),datetime.datetime.now().time())) == False):
                    return ('0 days 00:00:00')
                else:
                    return ((str(datetime.datetime.now() - missingDataHolidaysExcluded['Date'].iloc[-1])[0:15]))
            else:
                return ((str(datetime.datetime.now() - missingDataHolidaysExcluded.index[-1])[0:15]))
        else:
            print('Invalid argument(s) being cast to parameter(s).')

        
    def datetimeHandler(self,
                        desiredOutput: str,
                        silencePrint: Optional[bool] = False) -> Callable[[str, pd.DataFrame], pd.DataFrame]:

        '''
        Method used to determine whether or not data is missing. Returns the output from the outputForDatetimeHandler method to shorten syntax and achieve intended functionality.

        desiredOutput: str
            The desired output from the datetimeHandler method. The options are 'missingPercentage','missingDataIncludedInFrame', and 'lagTime'.
            
        silencePrint: bool, optional
            If True, the method will not print anything to the console. This is provided and used for testing, as well as multi-plot processing.
        '''
        
        earliestPoint, latestPoint = min(self._assetTimeSeries.Date), max(self._assetTimeSeries.Date)
        allUnitsInFrame = []

        while (earliestPoint <= latestPoint):
            allUnitsInFrame.append(earliestPoint.strftime("%Y-%m-%d %H:%M:%S"))
            if self._intermediaryUnits == 'hours':
                earliestPoint += timedelta(hours = self._intermediaryInterval)
            if self._intermediaryUnits == 'minutes':
                earliestPoint += timedelta(minutes = self._intermediaryInterval)
            if self._intermediaryUnits == 'days':
                earliestPoint += timedelta(days = self._intermediaryInterval)
            if self._intermediaryUnits == 'weeks':
                earliestPoint += timedelta(weeks = self._intermediaryInterval)
            if self._intermediaryUnits == 'months':
                earliestPoint += relativedelta(months = (self._intermediaryInterval))
        
        mergingDataWithTime = (pd.to_datetime(pd.DataFrame(allUnitsInFrame, columns = ['Date']).stack()).unstack()).set_index('Date').join(self._assetTimeSeries.set_index('Date'))#saw bug workaround on github that said stack and then unstack...interestingly, this worked.
        
        if (len(self._tickerSymbol) <= 4):
            if (self._intermediaryUnits == 'weeks') or (self._intermediaryUnits == 'months'):
                missingDataHolidaysExcluded = mergingDataWithTime.copy(deep = True)
                return (self.outputForDatetimeHandler(desiredOutput, missingDataHolidaysExcluded, silencePrint))
            elif (self._intermediaryUnits == 'days'):
                mergingDataWithTime = mergingDataWithTime[mergingDataWithTime.index.dayofweek < 5]
                missingDataHolidaysExcluded = (mergingDataWithTime[~(mergingDataWithTime.index.isin(mktCal.date_range(((mktCal.get_calendar('NYSE')).schedule(start_date = min(mergingDataWithTime.index), end_date = max(mergingDataWithTime.index))), frequency = (self.marketCalendarInterval()))))].reset_index())
                return (self.outputForDatetimeHandler(desiredOutput, missingDataHolidaysExcluded, silencePrint))
            else:
                mergingDataWithTime = (pd.DataFrame((mergingDataWithTime.index[mergingDataWithTime.index.indexer_between_time('09:30', '15:59')]), columns = ['Date'])).set_index('Date').join(self._assetTimeSeries.set_index('Date'))
                mergingDataWithTime = mergingDataWithTime[mergingDataWithTime.index.dayofweek < 5]
                missingDataHolidaysExcluded = (mergingDataWithTime[~(mergingDataWithTime.index.isin(mktCal.date_range(((mktCal.get_calendar('NYSE')).schedule(start_date = min(mergingDataWithTime.index), end_date = max(mergingDataWithTime.index))), frequency = (self.marketCalendarInterval()))))].reset_index())
                return (self.outputForDatetimeHandler(desiredOutput, missingDataHolidaysExcluded, silencePrint))
        else:
            if (self._intermediaryUnits == 'weeks') or (self._intermediaryUnits == 'months'):
                missingDataHolidaysExcluded = mergingDataWithTime
                missingDataHolidaysExcluded['Volume'] = 0.00
                return (self.outputForDatetimeHandler(desiredOutput, missingDataHolidaysExcluded, silencePrint))
            else:
                missingDataHolidaysExcluded = mergingDataWithTime.copy(deep = True)
                missingDataHolidaysExcluded['Volume'] = 0.00
                return (self.outputForDatetimeHandler(desiredOutput, missingDataHolidaysExcluded, silencePrint))
        
        
    def unalteredFrameGetter(self) -> pd.DataFrame:

        '''Method used to return a copy of the original version of the dataframe created upon instantiation of the class, self._assetTimeSeries.'''
            
        originalTimeSeries = (self._assetTimeSeries.copy(deep = True))
        return (originalTimeSeries)


    def infoForLogEntries(self) -> list[str, Callable[str, str], Callable[str, str], str]:

        '''Method used to return a list of information (ticker symbol, missing percentage of data, lag time of data, and total number of units called) which will be used to create a log entry for the missingDataLog.csv file. '''
      
        return ([self._tickerSymbol, str(self.datetimeHandler('missingPercentage', silencePrint = True)), self.datetimeHandler('lagTime'), str(self._numberOfUnits)])


    def logDataCharacteristics(self) -> None:

        '''Method used to create a log entry to the missingDataLog.csv file. Determines whether or not the file exists, and then if it does, itappends the information to the end of the file. If the file does not exist, the method creates a new file and writes the header row, then appends the information to the end of the file. '''
        if (os.path.isfile((str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) + '/datasets/missingDataLog.csv')) == False):
            with open((str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) + '/datasets/missingDataLog.csv'), 'w', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(['tickerSymbol', 'missingDataPercentage', 'lagTime', 'numberOfUnits'])
                writer.writerow(self.infoForLogEntries())
        else:
            with open((str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) + '/datasets/missingDataLog.csv'), 'a', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(self.infoForLogEntries())
