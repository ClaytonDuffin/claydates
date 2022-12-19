import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import csv
import os
import sys
from typing import Optional, Callable, Union
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from claydates.processors.singleTickerProcessor import SingleTickerProcessor


class MultiTickerProcessor():

    '''
    Class for gathering and processing time series data for one or more ticker symbols. 
    Creates a list of SingleTickerProcessor class objects, and then organizes data in accordance with the various arguments passed or not passed to the various methods belonging to the class.
    It is the parent class of MultiTickerPlotter.
    
    Parameters
    ----------
    tickerSymbols : list[str]
        One or more ticker symbol(s) of the asset(s) or currency pair(s) to be processed.
    tickInterval : str
        The interval of time between each data point. Options are: '1min', '5min', '15min', '30min', '45min', '1h', '2h', '4h', '8h', '1day', '1week', and '1month'.
    numberOfUnits : int
        The number of units of data to request from the API. Twelvedata's maximum request amount is 5000 units, 8 times per minute.
    percentageChange : bool, optional
        uUed to determine whether or not to compute and use percentage change data. The default is False, but can be changed to True. Some charts will seem unaffected by this, which is expected. Don't sweat it if you encounter this. Everything should be working as intended. 
    timeZone : str, optional 
        The time zone of the data. The default is 'America/New_York'.
    quoteCurrency : str, optional
        The quote currency of the data. The default is 'USD'.
    logMissingData : bool, optional
        If True, logs missing data and lag time to a csv file titled 'missingDataLog.csv' in the datasets folder. The default is False, but I encourage using this functionality.
    mockResponse : bool, optional
        Is used for testing. It is set to True in the source code of the tests in the tests folder, and can be switched to False there to mock a response from the API call.
    '''

    def __init__(self,
                 tickerSymbols: list[str],
                 tickInterval: int,
                 numberOfUnits: int,
                 percentageChange: Optional[bool] = None,
                 timeZone: Optional[str] = None,
                 quoteCurrency: Optional[str] = None,
                 logMissingData: Optional[bool] = False,
                 mockResponse: Optional[bool] = False) -> None:
    
        '''Initializes the MultiTickerProcessor class and defines some of its attributes.'''

        self._tickerSymbols = tickerSymbols
        
        self._tickerObjects = []
        for symbol in tickerSymbols:
            self._tickerObjects.append(SingleTickerProcessor(symbol, tickInterval, numberOfUnits,
                                                             percentageChange, timeZone, quoteCurrency,
                                                             logMissingData, mockResponse))
   
    @staticmethod
    def disableConsolePrinting() -> None:
    
        '''Method used to toggle off printing functionality in the console.'''
        
        sys.stdout = open(os.devnull, 'w')


    @staticmethod
    def enableConsolePrinting() -> None:
        
        '''Method used to restore printing functionality in the console.'''

        sys.stdout = sys.__stdout__
    
    
    def dateMatcher(self,
                    dropMissing: Optional[bool] = True) -> list[pd.DataFrame]:
    
        '''
        Method for matching one or more dataframe(s) by date. Is set to drop any data where the dataframe dates are inconsistent with one another, but this functionality can be toggled off by setting the dropMissing keyword argument to False. Returns a list of dataframes.
        
        Parameters
        ----------
        dropMissing : bool, optional
            Used to determine whether or not missing data units in the individual frames should be concatenated as is (set argument equal to False), or dropped out from all of the dataframes (set argument equal to True, or pass no argument).
        '''
        
        compositeFrames, compositeFrameLengths, newCompositeFrames = [], [], []
        if dropMissing:
            for index, timeSeriesObject in enumerate(self._tickerObjects):
                if (index == 0):
                    compositeFrames.append((timeSeriesObject.datetimeHandler('missingDataIncludedInFrame').dropna(axis = 0).reset_index(drop = True)))
                else:
                    compositeFrames.append(pd.merge(left = compositeFrames[-1], left_on = 'Date',
                                                    right = (timeSeriesObject.datetimeHandler('missingDataIncludedInFrame').dropna(axis = 0).reset_index(drop = True)), right_on = 'Date'))
        if not dropMissing:
            for index, timeSeriesObject in enumerate(self._tickerObjects):
                if (index == 0):
                    compositeFrames.append((timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')))
                else:
                    compositeFrames.append(pd.merge(left = compositeFrames[-1], left_on = 'Date',
                                                    right = (timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')), right_on = 'Date'))
        
        for index, individualFrame in enumerate(compositeFrames):
            compositeFrameLengths.append((index, len(individualFrame.columns)))
        desiredData = compositeFrames[sorted(compositeFrameLengths, key = lambda x: x[1], reverse = True)[0][0]]
        desiredData.columns = np.arange(len(desiredData.columns))
        dateFrame = pd.DataFrame(desiredData[1])
        del desiredData[0]
        del desiredData[1]
        
        if (len(self._tickerSymbols) > 1):
            desiredData = desiredData.drop(list(range(7,desiredData.shape[1],6)), axis=1)
            desiredData.columns = np.arange(len(desiredData.columns))
            for index, gap in enumerate(list(range(0, desiredData.shape[1],5))):
                if (index == 0):
                    newCompositeFrames.append(desiredData.iloc[:,0 : 5])
                else:
                    newCompositeFrames.append(desiredData.iloc[:,gap : (gap + 5)])
            for index, individualFrame in enumerate(newCompositeFrames):
                try:
                    individualFrame.insert(0,'Date', dateFrame)
                    individualFrame.columns = ['Date','Open','High','Low','Close','Volume']
                except ValueError:
                    individualFrame.insert(1,'Open', compositeFrames[1][7])
                    individualFrame.columns = ['Date','Open','High','Low','Close','Volume']
        else:
            desiredData.columns = np.arange(len(desiredData.columns))
            newCompositeFrames.append(desiredData)
            newCompositeFrames[0].insert(0,'Date', dateFrame)
            newCompositeFrames[0].columns = ['Date','Open','High','Low','Close','Volume']
    
        return (newCompositeFrames)


    def unalteredFrames(self,
                        dataType: Optional[str] = 'pandas') -> Union[list[pd.DataFrame], list[np.ndarray]]:
        
        '''
        Method for returning a list of dataframe(s) or array(s) containing the unaltered frame(s) originally returned from the SingleTickerProcessor class instantiation(s). This method does not modify the frame(s).
        
        Parameters
        ----------
        dataType : str, optional
            Used to determine whether or not to return the frame(s) as a list of pandas dataframes, or a list of numpy array objects. Acceptable keyword arguments are 'pandas' or 'numpy'.
        '''
        
        unalteredTimeSeriesFrames = []
        if (dataType == 'pandas'):
            for timeSeriesObject in self._tickerObjects:
                unalteredTimeSeriesFrames.append((timeSeriesObject.unalteredFrameGetter()))
        elif (dataType == 'numpy'):
            for timeSeriesObject in self._tickerObjects:
                unalteredTimeSeriesFrames.append((timeSeriesObject.unalteredFrameGetter().to_numpy()))
        else:
            raise ValueError('Invalid argument(s). Valid arguments are: \'pandas\' or \'numpy\'')
        return (unalteredTimeSeriesFrames)
    
    
    def missingUnitsIncluded(self,
                             dataType: Optional[str] = 'pandas',
                             interpolationMethod: Optional[str] = None,
                             matchDates: Optional[bool] = False) -> Union[list[pd.DataFrame], list[np.ndarray]]:
        
        '''
        Method for returning a list of dataframe(s) or array(s) containing the requested frame(s) and including any missing data.
        
        Parameters
        ----------
        
        dataType : str, optional
            Used to determine whether or not to return the frame(s) as a list of pandas dataframes, or a list of numpy array objects. Acceptable keyword arguments are 'pandas' or 'numpy'.
        interpolationMethod : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
        '''
        
        if (matchDates == True) and (interpolationMethod != None):
            print('\nNote: matchDates computation does not use interpolation but interpolation argument was passed: interpolation argument has now been set to None for your convenience')
        
        if (interpolationMethod == None):
            missingUnitsNotInterpolated = []
            if (dataType == 'pandas'):
                for timeSeriesObject in self._tickerObjects:
                    missingUnitsNotInterpolated.append((timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')))
            elif (dataType == 'numpy'):
                for timeSeriesObject in self._tickerObjects:
                    missingUnitsNotInterpolated.append((timeSeriesObject.datetimeHandler('missingDataIncludedInFrame').to_numpy()))
            else:
                raise ValueError('Invalid argument(s). Valid arguments are: \'pandas\' or \'numpy\'')
            if (matchDates == True):
                return self.dateMatcher(dropMissing = False)
            elif (matchDates == False):
                return (missingUnitsNotInterpolated)      
            else:
                raise ValueError('Invalid argument(s). Valid arguments are: True or False')
        
        elif (interpolationMethod == 'linear'):
            missingUnitsInterpolated = []
            if (dataType == 'pandas'):
                for index, timeSeriesObject in enumerate(self._tickerObjects):
                    tempFrame = timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')
                    dates = tempFrame['Date']
                    del tempFrame['Date']
                    newFrame = (tempFrame).interpolate(method = 'linear')
                    newFrame.insert(0, 'Date', dates)
                    missingUnitsInterpolated.append(newFrame)
            elif (dataType == 'numpy'):
                for index, timeSeriesObject in enumerate(self._tickerObjects):
                    tempFrame = timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')
                    dates = tempFrame['Date']
                    del tempFrame['Date']
                    newFrame = (tempFrame).interpolate(method = 'linear')
                    newFrame.insert(0, 'Date', dates)
                    missingUnitsInterpolated.append(newFrame.to_numpy())
            else:
                raise ValueError('Invalid argument(s). Valid arguments are: \'pandas\' or \'numpy\'')
            return (missingUnitsInterpolated)
        
        elif (interpolationMethod == 'cubic'):
            missingUnitsInterpolated = []
            if (dataType == 'pandas'):
                for index, timeSeriesObject in enumerate(self._tickerObjects):
                    tempFrame = timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')
                    dates = tempFrame['Date']
                    del tempFrame['Date']
                    newFrame = (tempFrame).interpolate(method = 'cubic')
                    newFrame.insert(0, 'Date', dates)
                    missingUnitsInterpolated.append(newFrame)
            elif (dataType == 'numpy'):
                for index, timeSeriesObject in enumerate(self._tickerObjects):
                    tempFrame = timeSeriesObject.datetimeHandler('missingDataIncludedInFrame')
                    dates = tempFrame['Date']
                    del tempFrame['Date']
                    newFrame = (tempFrame).interpolate(method = 'cubic')
                    newFrame.insert(0, 'Date', dates)
                    missingUnitsInterpolated.append(newFrame.to_numpy())
            else:
                raise ValueError('Invalid argument(s). Valid arguments are: \'pandas\' or \'numpy\'')
            return (missingUnitsInterpolated)
         
        else:
            raise ValueError('Invalid argument(s). Valid arguments are: None or \'linear\' or \'cubic\'')
        

    def missingUnitsExcluded(self,
                             dataType: Optional[str] = 'pandas',
                             matchDates: Optional[bool] = True) -> Union[Callable[[bool], list[pd.DataFrame]],
                                                                         list[pd.DataFrame], list[np.ndarray]]:
    
        '''
        Method for returning a list of dataframe(s) or array(s) containing the requested frame(s) but excluding any missing data.
        
        Parameters
        ----------
        dataType : str, optional
            Used to determine whether or not to return the frame(s) as a list of pandas dataframes, or a list of numpy array objects. Acceptable keyword arguments are 'pandas' or 'numpy'.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. 
        '''
        
        if matchDates:
            if (dataType == 'pandas'):
                return (self.dateMatcher())
            
            elif (dataType == 'numpy'):
                numpyFrames = []
                for i, j in enumerate(self.dateMatcher()):
                    numpyFrames.append(j.to_numpy())
                return (numpyFrames)
            else:
                raise ValueError('Invalid argument(s). Valid arguments are: \'pandas\' or \'numpy\'')

        elif not matchDates:
            compositeFrames = []
            if (dataType == 'pandas'):
                for timeSeriesObject in self._tickerObjects:
                    compositeFrames.append((timeSeriesObject.datetimeHandler('missingDataIncludedInFrame').dropna(True).reset_index(drop=True)))
            elif (dataType == 'numpy'):
                for timeSeriesObject in self._tickerObjects:
                    compositeFrames.append((timeSeriesObject.datetimeHandler('missingDataIncludedInFrame').dropna(True).reset_index(drop=True)).to_numpy())
            return (compositeFrames)
        
        else:
            raise ValueError('Invalid argument(s). Valid arguments are: True or False')

        
    def missingPercentages(self,
                           onlyPrint: Optional[bool] = True) -> Union[None, list[list[float, str]]]:
        
        '''
        Method to be used for printing information on missing data for the requested tickers. Also used for logging information if the logMissingData instance attribute is set to True during instantiation.
        
        Parameters
        ----------
        onlyPrint : bool
            Used to specify whether or not the method is to be used to print missing data percentage and lag time, or to return it to be used for logging purposes.
        '''

        if onlyPrint:
            for index, timeSeriesObject in enumerate(self._tickerObjects):
                print('\n' + timeSeriesObject._tickerSymbol + ':')
                timeSeriesObject.datetimeHandler('missingPercentage')
        else:
            missingPercentages, lagTimes = [], []
            self.disableConsolePrinting()
            for index, timeSeriesObject in enumerate(self._tickerObjects):
                missingPercentages.append(timeSeriesObject.datetimeHandler('missingPercentage'))
            for index, timeSeriesObject in enumerate(self._tickerObjects):
                lagTimes.append(timeSeriesObject.datetimeHandler('lagTime'))
            self.enableConsolePrinting()

            return ([list(item) for item in zip(missingPercentages, lagTimes)])


