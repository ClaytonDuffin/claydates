from distutils.sysconfig import get_python_lib
from sysconfig import get_python_version
import time
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
from matplotlib.ticker import MultipleLocator
plt.rc('figure', max_open_warning = 0)
from typing import Optional, Callable, Union
from claydates.processors.singleTickerProcessor import SingleTickerProcessor

class SingleTickerPlotter(SingleTickerProcessor):
    
    '''
    Class used for plotting time series data. Also can be used for logging the quality of data received from the API call to a csv file.
    It is also used to iteratively construct one or more time series objects of the SingleTickerPlotter class in multiTickerPlotter.py.
    It is the child class of SingleTickerProcessor, and the parent class of multiTickerPlotter.
    
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
        Is used for testing. It is set to True in the source code of the tests in the tests folder, and can be switched to False there to mock a response from the API call.
    spacingFactor : int, optional
        Is used to determine the spacing between the x-axis and y-axis major ticks. If you want to change the spacing, you can do so by specifying a different value for this parameter. If it is set larger to a value larger than 10, the x-axis tick labels will rotate. This is to prevent overlap.
    seriesType : str, optional
        Is used to determine which series of data to plot. The options are 'Open', 'High', 'Low', 'Close', and 'Volume'. The default is 'Close'.
    scalerRange : tuple, optional
        Is used to determine the range of the y, and in some cases x axes for some of the plots which allow you to scale the axes. The default is (0,1). If you want to change the range, you can do so by specifying a different value for this parameter.
    binningFactor : int, optional
        Is used to determine the number of bins for the various types of histogram charts which can be specified in the singleProfilePlot's arguments. The default is 10, which seems to work fairly nice. If you want to change the number of bins, you can do so by specifying a different value for this parameter. This will be used as the denominator for binning data in singleProfilePlot.
    figureSize : tuple, optional
        Is used to determine the size of the figures. The default is [14.275,9.525], but can be changed. You may encounter some issues with the external/interactive window plots depending on your screen size, so to fix this, adjust the lines that say "plt.get_current_fig_manager().window.setGeometry(0,0, 1435, 952)" in the singleProfilePlot function.
    labelSize : int, optional
        is used to determine the size of the labels on the x and y axes. The default is 16, but can be changed.
    color : str, optional
        is used to determine the color of the plots. The default is 'black', but can be changed by passing a different color for this argument. Color can also be changed more dynamically in the interactive external windows thanks to matplotlib in Figure Options -> Curves.
'''

    def __init__(self,
                 tickerSymbol: str,
                 tickInterval: int,
                 numberOfUnits: int,
                 percentageChange: Optional[bool] = None,
                 timeZone: Optional[str] = None,
                 quoteCurrency: Optional[str] = None,
                 logMissingData: Optional[bool] = False,
                 mockResponse: Optional[bool] = False,
                 spacingFactor: Optional[int] = None,
                 seriesType: Optional[str] = 'Close',
                 scalerRange: Optional[tuple] = None,
                 binningFactor: Optional[int] = None,
                 figureSize: Optional[list[float]] = None,
                 labelsize: Optional[int] = None,
                 color: Optional[str] = None) -> None:
        
        '''initializes the SingleTickerProcessor (inherited) and SingleTickerPlotter classes. Defines attributes for SingleTickerPlotter.'''

        super().__init__(tickerSymbol, tickInterval, numberOfUnits,
                         percentageChange, timeZone, quoteCurrency,
                         logMissingData, mockResponse)
        
        self._seriesType = seriesType.title() 
        self._maxPercentageChange = (self._assetTimeSeries[self._seriesType].pct_change().cumsum().max()) - (self._assetTimeSeries[self._seriesType].pct_change().cumsum().min())
        self._maxPriceChange = (self._assetTimeSeries[self._seriesType].max()) - (self._assetTimeSeries[self._seriesType].min())
        self._timeSeriesWithMissingData = self.datetimeHandler('missingDataIncludedInFrame')
        self._lengthWithMissingData = len(self._timeSeriesWithMissingData)
        self._scalerRange = scalerRange or (0, 1)
        self._majorTickSpacingFactor = spacingFactor or 10
        self._binningFactor = binningFactor or 10 
        self._figureSize = figureSize or [14.275,9.525]
        self._labelsize = labelsize or 16
        self._color = color or 'black'
    
    
    def minMaxScaler(self,
                     frame: pd.DataFrame) -> pd.DataFrame:
        
        '''
        Scales the data to the range specified in the constructor, self._scalerRange. Takes in input one argument, frame, which is a pandas DataFrame. Returns the scaled pandas DataFrame.
        
        Parameters
        ----------
        frame : pd.DataFrame
            The DataFrame to be scaled.
        '''

        freshlyScaled = []
        for i in frame:
            newLower, newUpper, oldLower, oldUpper =  self._scalerRange[0], self._scalerRange[1], frame[i].min(), frame[i].max()
            freshlyScaled.append((frame[i] - oldLower) / (oldUpper - oldLower) * (newUpper - newLower) + newLower)
    
        return (pd.DataFrame(freshlyScaled).T)


    def variableXMajorFormatter(method) -> Callable:

        '''Custom decorator for the standardSinglePlot, missingDataSinglePlot, and interpolatedSinglePlot methods. Determines spacing between x-axis major ticks, based on self._majorTickSpacingFactor.'''
        
        def plotWrapper(*args,
                        **kwargs) -> Callable:

            classAttributes = args[0]
            currentAxis = plt.gca()
            
            step = (round(classAttributes._lengthWithMissingData, -(len(str((classAttributes._lengthWithMissingData))) - 1)) / classAttributes._majorTickSpacingFactor)
            currentAxis.xaxis.set_major_locator(MultipleLocator(step))

            plt.tick_params(labelsize = classAttributes._labelsize, labelright = True)
            plt.minorticks_on()
            
            return (method(*args, **kwargs))
        
        return (plotWrapper)
    
    
    def variableYMajorFormatter(method) -> Callable:

        '''Custom decorator for the standardSinglePlot, missingDataSinglePlot, and interpolatedSinglePlot methods. Determines spacing between y-axis major ticks, based on self._majorTickSpacingFactor.'''

        def plotWrapper2(*args,
                         **kwargs) -> Callable:
            
            classAttributes = args[0]
            currentAxis = plt.gca()
            
            if classAttributes._percentageChange:
                for i in range(-5, 10):
                    step = round((classAttributes._maxPercentageChange / classAttributes._majorTickSpacingFactor), i)
                currentAxis.yaxis.set_major_locator(MultipleLocator(step))
            
            if not classAttributes._percentageChange:
                for i in range(-5, 10):
                    step = round((classAttributes._maxPriceChange / classAttributes._majorTickSpacingFactor), i)
                currentAxis.yaxis.set_major_locator(MultipleLocator(step))
               
            plt.tick_params(labelsize = classAttributes._labelsize, labelright = True)
            plt.minorticks_on()

            return (method(*args, **kwargs))
        return (plotWrapper2)


    @variableXMajorFormatter
    @variableYMajorFormatter
    def standardSinglePlot(self) -> None:

        '''Takes no direct arguments. Is used to chart the original unaltered version of the time series dataframe created upon instantiation of the class. Do note that missing data units are not represented in this chart.'''

        if self._percentageChange:
            ax1 = self._assetTimeSeries[self._seriesType].pct_change().cumsum().plot(color = self._color, figsize = self._figureSize, label = self._tickerSymbol, linewidth = 1)
            ax1.set_title(self._tickerSymbol, fontsize = 16)
            ax1.axhline(0,linewidth = .75, color = 'firebrick')
        
        elif (self._percentageChange == False):
            ax1 = self._assetTimeSeries[self._seriesType].plot(color = self._color, figsize = self._figureSize, label = self._tickerSymbol, linewidth = 1)   
            ax1.set_title(self._tickerSymbol, fontsize = 16)

        if (self._majorTickSpacingFactor > 10):
            plt.xticks(rotation = -45)
    
        if (self._lengthWithMissingData > (self._numberOfUnits * 2)):
            step = (round(self._numberOfUnits, -(len(str((self._numberOfUnits))) - 1)) / self._majorTickSpacingFactor)
            ax1.xaxis.set_major_locator(MultipleLocator(step))
    
        ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
        ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
        plt.pause(0.01)
        

    @variableXMajorFormatter
    @variableYMajorFormatter
    def missingDataSinglePlot(self) -> None:
    
        '''Takes no direct arguments. Is used to chart missing data units alongside the original time series data. There will be gaps shown in the time series where the spaces are, and the missing data will be shown along the x-axis at the highest y value.'''

        timeSeriesWithMissingData = self._timeSeriesWithMissingData.copy(deep = True)

        if self._percentageChange:
            
            filledData  = pd.DataFrame(timeSeriesWithMissingData[timeSeriesWithMissingData[self._seriesType].isna()][self._seriesType].pct_change().cumsum().fillna(timeSeriesWithMissingData[self._seriesType].pct_change().cumsum().max())).rename(columns = {(self._seriesType) : 'Filling'})
            compositeData = pd.concat([timeSeriesWithMissingData[self._seriesType].pct_change().cumsum(), filledData], axis = 1)
            compositeData[self._seriesType][compositeData.Filling.notnull()] = np.nan
            
            ax1 = compositeData[self._seriesType].plot(color = self._color, figsize = self._figureSize, linewidth = 1)   
            ax2 = compositeData['Filling'].plot(color = self._color, figsize = self._figureSize, linewidth = 3) 
            ax1.set_title(self._tickerSymbol, fontsize = 16)

        elif (self._percentageChange == False):
            
            filledData  = pd.DataFrame(timeSeriesWithMissingData[timeSeriesWithMissingData[self._seriesType].isna()][self._seriesType].fillna(timeSeriesWithMissingData[self._seriesType].max())).rename(columns = {(self._seriesType) : 'Filling'})
            compositeData = pd.concat([timeSeriesWithMissingData,filledData], axis = 1)
            
            ax1 = compositeData[self._seriesType].plot(color = self._color, figsize = self._figureSize, linewidth = 1)   
            ax2 = compositeData['Filling'].plot(color = self._color, figsize = self._figureSize, linewidth = 3) 
            ax1.set_title(self._tickerSymbol, fontsize = 16)
           
        if (self._majorTickSpacingFactor > 10):
            plt.xticks(rotation = -45)
            
        ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
        ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
        plt.pause(0.01)


    @variableXMajorFormatter
    @variableYMajorFormatter
    def interpolatedSinglePlot(self,
                               methodology: Optional[str] = None) -> None:
        
        '''
        Used to plot the time series data with the missing values interpolated using the processs specified by one of two keyword arguments. The one direct keyword argument is: methodology, and the parameters are 'linear' or 'cubic'.
            
        Parameters
        ----------
        methodology : str, optional
            Methodology to use for interpolation. Can be either 'linear' or 'cubic'.
        '''
    
        timeSeriesWithMissingData = self._timeSeriesWithMissingData.copy(deep = True)

        if self._percentageChange:
            if (methodology == 'linear'):
                ax1 = timeSeriesWithMissingData[self._seriesType].interpolate(method = 'linear').pct_change().cumsum().plot(color = self._color, figsize = self._figureSize, linewidth = 1)
                ax1.set_title(self._tickerSymbol, fontsize = 16)
            if (methodology == 'cubic'):
                ax1 = timeSeriesWithMissingData[self._seriesType].interpolate(method = 'cubic').pct_change().cumsum().plot(color = self._color, figsize = self._figureSize, linewidth = 1)
                ax1.set_title(self._tickerSymbol, fontsize = 16)

        elif (self._percentageChange == False):
            if (methodology == 'linear'):
                ax1 = timeSeriesWithMissingData[self._seriesType].interpolate(method = 'linear').plot(color = self._color, figsize = self._figureSize, linewidth = 1)
                ax1.set_title(self._tickerSymbol, fontsize = 16)
            if (methodology == 'cubic'):
                ax1 = timeSeriesWithMissingData[self._seriesType].interpolate(method = 'cubic').plot(color = self._color, figsize = self._figureSize, linewidth = 1)
                ax1.set_title(self._tickerSymbol, fontsize = 16)
                
        if (self._majorTickSpacingFactor > 10):
            plt.xticks(rotation = -45)
            
        if (methodology == 'cubic') or (methodology == 'linear'):
            ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
            ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
            plt.pause(0.01)
        else:
            plt.close()
            raise ValueError('Invalid argument(s). Valid arguments are: \'linear\' or \'cubic\'')


    def profileProcessor(self,
                         numberOfBins: int,
                         methodology: str,
                         interpolation: str) -> pd.DataFrame:
        
        '''
        This method is used to return a histogram as a pandas dataframe. Please do note that the number of bins returned is (numberOfBins - 1).
        
        Parameters
        ----------
        numberOfBins : int
            Used to specify how many bins to chunk the data into.
        methodology : str
            Used to specify how to process the data. The options are 'count', 'price', and 'volume'.
        interpolation : str
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        '''

        priceAndVolume = []
                
        if (interpolation == None):
            timeSeriesWithoutMissingData = self._assetTimeSeries.copy(deep = True)

            for index, values in enumerate(zip(timeSeriesWithoutMissingData[self._seriesType], (timeSeriesWithoutMissingData['Volume']))):
                priceAndVolume.append(values)
            priceAndVolumeDataFrame = pd.DataFrame(priceAndVolume)

            sums = priceAndVolumeDataFrame.groupby(pd.cut(priceAndVolumeDataFrame[0], np.linspace(self._assetTimeSeries[self._seriesType].min(), self._assetTimeSeries[self._seriesType].max(), num = numberOfBins))).sum()
            counts = priceAndVolumeDataFrame.groupby(pd.cut(priceAndVolumeDataFrame[0], np.linspace(self._assetTimeSeries[self._seriesType].min(), self._assetTimeSeries[self._seriesType].max(), num = numberOfBins))).count()
        
        elif (interpolation == 'linear'):
            timeSeriesWithMissingData = self._timeSeriesWithMissingData.copy(deep = True)
            
            for index, values in enumerate(zip(timeSeriesWithMissingData[self._seriesType].interpolate(method='linear'), (timeSeriesWithMissingData['Volume'].interpolate(method = 'linear')))):
                priceAndVolume.append(values)
            priceAndVolumeDataFrame = pd.DataFrame(priceAndVolume)
            
            sums = priceAndVolumeDataFrame.groupby(pd.cut(priceAndVolumeDataFrame[0], np.linspace(timeSeriesWithMissingData[self._seriesType].min(), timeSeriesWithMissingData[self._seriesType].max(), num = numberOfBins))).sum()
            counts = priceAndVolumeDataFrame.groupby(pd.cut(priceAndVolumeDataFrame[0], np.linspace(timeSeriesWithMissingData[self._seriesType].min(), timeSeriesWithMissingData[self._seriesType].max(), num = numberOfBins))).count()
        
        elif (interpolation == 'cubic'):
            timeSeriesWithMissingData = self._timeSeriesWithMissingData.copy(deep = True)
            
            for index, values in enumerate(zip(timeSeriesWithMissingData[self._seriesType].interpolate(method='cubic'), (timeSeriesWithMissingData['Volume'].interpolate(method = 'cubic')))):
                priceAndVolume.append(values)
            priceAndVolumeDataFrame = pd.DataFrame(priceAndVolume)
            
            sums = priceAndVolumeDataFrame.groupby(pd.cut(priceAndVolumeDataFrame[0], np.linspace(timeSeriesWithMissingData[self._seriesType].min(), timeSeriesWithMissingData[self._seriesType].max(), num = numberOfBins))).sum()
            counts = priceAndVolumeDataFrame.groupby(pd.cut(priceAndVolumeDataFrame[0], np.linspace(timeSeriesWithMissingData[self._seriesType].min(), timeSeriesWithMissingData[self._seriesType].max(), num = numberOfBins))).count()
            
        else:
            raise ValueError('Invalid argument(s). Valid arguments for interpolation are: None, or \'linear\' or \'cubic\'')

        midpoints, volumeSums, priceSums, countSums = [], [], [], []
        for i in sums.index:
            midpoints.append(i.mid)
        for i in sums[1]:
            volumeSums.append(i) 
        for i in sums[0]:
            priceSums.append(i) 
        for i in counts[1]:
            countSums.append(i) 
            
        volumeFrame = pd.DataFrame({'Midpoints' : midpoints, 'VolumeTradedAtMidpoint' : volumeSums})
        volumeFrame['Proportions'] = volumeFrame['VolumeTradedAtMidpoint'] / volumeFrame['VolumeTradedAtMidpoint'].sum()
        priceFrame = pd.DataFrame({'Midpoints' : midpoints, 'rawPriceSummationTradedAtMidpoint' : priceSums})
        priceFrame['Proportions'] = priceFrame['rawPriceSummationTradedAtMidpoint'] / priceFrame['rawPriceSummationTradedAtMidpoint'].sum()
        countFrame = pd.DataFrame({'Midpoints' : midpoints, 'countTradedAtMidpoint' : countSums})
        countFrame['Proportions'] = countFrame['countTradedAtMidpoint'] / countFrame['countTradedAtMidpoint'].sum()
    
        if (methodology == 'volume'):
            return (volumeFrame)
        elif (methodology == 'price'):
            return (priceFrame)
        elif (methodology == 'count'):
            return (countFrame)
        else:
            raise ValueError('Invalid argument(s). Valid arguments for methodology are: \'volume\' or \'price\' or \'count\'')


    def printAndPass(self, 
                    **kwargs: bool) -> None:
    
        '''Method to be used in singleProfilePlot. Prints a message and passes if the user passes an unacceptable parameter for seriesType or binningType.'''
        
        #could define a method to do this, and then use it before the return statements or plots of the other functions to check that the code ran up unto that point at least.
        for key, value in kwargs.items():
            if (value == True):
                pass
            return

        print('\nNote: Faulty User-Input:\nEither you passed an unacceptable parameter for seriesType, which accepts parameters \'standard\' or \'interpolated\', or you passed an unacceptable parameter for binningType, which accepts parameters \'standard\' or \'missingLength\' or \'custom\', or, you are trying to use custom binning without passing a numberOfBins parameter.')
        pass
   
    
    def singleProfilePlot(self,
                          seriesType: str,
                          binningType: str,
                          methodology: str,
                          numberOfBins: Union[int, None],
                          scaledX: Optional[bool] = True,
                          scaledY: Optional[bool] = True,
                          interpolation: Optional[str] = None) -> None: 
        
        '''
        This method is used to return a histogram as a pandas dataframe. Please do note that the number of bins returned is (numberOfBins - 1).
        
        Parameters
        ----------
        seriesType : str
            Used to specify whether or not to interpolate. The options are 'standard' or 'interpolated'. If standard, the data will not be interpolated.
        binningType : str
            Used to specify how the data is to be binned. The options are 'standard', 'missingLength', or 'custom'.
        methodology : str
            Used to specify how to process the data. The options are 'count', 'price', or 'volume'.
        numberOfBins : int or None
            Used to specify how many bins to chunk the data into.
        scaledX : bool, optional
            Used to specify whether or not to scale the x-axis.
        scaledY : bool, optional
            Used to specify whether or not to scale the y-axis.
        interpolation : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        '''
    
        def singleProfilePlotSyntaxShortener(seriesType: str,
                                             binningType: str,
                                             methodology: str,
                                             numberOfBins: Union[str, None],
                                             scaledX: Optional[bool] = True,
                                             scaledY: Optional[bool] = True,
                                             interpolation: Optional[str] = None) -> None:

            '''This method is used to shorten the syntax of singleProfilePlot.
            
            Parameters
            ----------
            seriesType : str
                Used to specify whether or not to interpolate. The options are 'standard' or 'interpolated'. if standard, the data will not be interpolated.
            binningType : str
                Used to specify how the data is to be binned. The options are 'standard', 'missingLength', or 'custom'.
            methodology : str
                Used to specify how to process the data. The options are 'count', 'price', or 'volume'.
            numberOfBins : int or None
                Used to specify how many bins to chunk the data into.
            scaledX : bool, optional
                Used to specify whether or not to scale the x axis.
            scaledY : bool, optional
                Used to specify whether or not to scale the y axis.
            interpolation : str, optional
                Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
            '''

            if (binningType == 'standard'):
                if (numberOfBins != None):
                    print('\nNote: standard binningType computation does not use the numberOfBins argument which was passed: numberOfBins argument has now been set to None for your convenience')
                    numberOfBins = None
                    pass
                numberOfBins = int((self._numberOfUnits) / self._binningFactor)
                standardFrame = self.profileProcessor(numberOfBins, methodology, interpolation)
                if scaledX:
                    if scaledY:
                        standardFrame['ProportionsScaled'] = self.minMaxScaler(standardFrame)['Proportions']
                        standardFrameForPlot = pd.concat([round(standardFrame['Midpoints'], 3), round(standardFrame['ProportionsScaled'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = round(self.minMaxScaler(standardFrameForPlot.reset_index()), 3).set_index('Midpoints').plot.barh(color = self._color, figsize = self._figureSize)
                    else:
                        standardFrame['ProportionsScaled'] = self.minMaxScaler(standardFrame)['Proportions']
                        standardFrameForPlot = pd.concat([round(standardFrame['Midpoints'], 3), round(standardFrame['ProportionsScaled'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = self.minMaxScaler(standardFrameForPlot).plot.barh(color = self._color, figsize = self._figureSize)
                else:
                    if scaledY:
                        standardFrameForPlot = pd.concat([round(standardFrame['Midpoints'], 3), round(standardFrame['Proportions'], 3)], axis = 1)
                        standardFrameForPlot = standardFrameForPlot.reset_index()
                        proportions = standardFrameForPlot['Proportions']
                        standardFrameForPlot = self.minMaxScaler(standardFrameForPlot)
                        standardFrameForPlot['Proportions'] = proportions
                        standardFrameForPlot = pd.concat([round(standardFrameForPlot['Midpoints'], 3), round(standardFrameForPlot['Proportions'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = standardFrameForPlot.plot.barh(color = self._color, figsize = self._figureSize)
                    else:
                        standardFrameForPlot = pd.concat([round(standardFrame['Midpoints'], 3), round(standardFrame['Proportions'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = standardFrameForPlot.plot.barh(color = self._color, figsize = self._figureSize)
                    
            if (binningType == 'missingLength'):
                if (numberOfBins != None):
                    print('\nNote: missingLength binningType computation does not use the numberOfBins argument which was passed: numberOfBins argument has now been set to None for your convenience')
                    numberOfBins = None
                    pass
                numberOfBins = int((self._lengthWithMissingData) / self._binningFactor)
                missingLengthFrame = self.profileProcessor(numberOfBins, methodology, interpolation)
                if scaledX:
                    if scaledY:
                        missingLengthFrame['ProportionsScaled'] = self.minMaxScaler(missingLengthFrame)['Proportions']
                        missingLengthFrameForPlot = pd.concat([round(missingLengthFrame['Midpoints'], 3), round(missingLengthFrame['ProportionsScaled'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = round(self.minMaxScaler(missingLengthFrameForPlot.reset_index()), 3).set_index('Midpoints').plot.barh(color = self._color, figsize = self._figureSize)
                    else:
                        missingLengthFrame['ProportionsScaled'] = self.minMaxScaler(missingLengthFrame)['Proportions']
                        missingLengthFrameForPlot = pd.concat([round(missingLengthFrame['Midpoints'], 3), round(missingLengthFrame['ProportionsScaled'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = self.minMaxScaler(missingLengthFrameForPlot).plot.barh(color = self._color, figsize = self._figureSize)
                else:
                    if scaledY:
                        missingLengthFrameForPlot = pd.concat([round(missingLengthFrame['Midpoints'], 3), round(missingLengthFrame['Proportions'], 3)], axis = 1)
                        missingLengthFrameForPlot = missingLengthFrameForPlot.reset_index()
                        proportions = missingLengthFrameForPlot['Proportions']
                        missingLengthFrameForPlot = self.minMaxScaler(missingLengthFrameForPlot)
                        missingLengthFrameForPlot['Proportions'] = proportions
                        missingLengthFrameForPlot = pd.concat([round(missingLengthFrameForPlot['Midpoints'], 3), round(missingLengthFrameForPlot['Proportions'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = missingLengthFrameForPlot.plot.barh(color = self._color, figsize = self._figureSize)                  
                    else:
                        missingLengthFrameForPlot = pd.concat([round(missingLengthFrame['Midpoints'],3), round(missingLengthFrame['Proportions'], 3)], axis = 1).set_index('Midpoints')
                        ax1 = missingLengthFrameForPlot.plot.barh(color = self._color, figsize = self._figureSize)

            if (binningType == 'custom'):
                if (numberOfBins == None):
                    print('\nNote: in order to use a custom number of bins for singleProfilePlot, you must first set the numberOfBins parameter equal to an integer value.')
                    pass
                else:
                    customFrame = self.profileProcessor(numberOfBins, methodology, interpolation)
                    if scaledX:
                        if scaledY:
                            customFrame['ProportionsScaled'] = self.minMaxScaler(customFrame)['Proportions']
                            customFrameForPlot = pd.concat([round(customFrame['Midpoints'], 3), round(customFrame['ProportionsScaled'], 3)], axis = 1).set_index('Midpoints')
                            ax1 = round(self.minMaxScaler(customFrameForPlot.reset_index()), 3).set_index('Midpoints').plot.barh(color = self._color, figsize = self._figureSize)
                        else:
                            customFrame['ProportionsScaled'] = self.minMaxScaler(customFrame)['Proportions']
                            customFrameForPlot = pd.concat([round(customFrame['Midpoints'], 3), round(customFrame['ProportionsScaled'], 3)], axis = 1).set_index('Midpoints')
                            ax1 = self.minMaxScaler(customFrameForPlot).plot.barh(color = self._color, figsize = self._figureSize)
                    else:
                        if scaledY:
                            customFrameForPlot = pd.concat([round(customFrame['Midpoints'], 3), round(customFrame['Proportions'], 3)], axis = 1)
                            customFrameForPlot = customFrameForPlot.reset_index()
                            proportions = customFrameForPlot['Proportions']
                            customFrameForPlot = self.minMaxScaler(customFrameForPlot)
                            customFrameForPlot['Proportions'] = proportions
                            customFrameForPlot = pd.concat([round(customFrameForPlot['Midpoints'], 3), round(customFrameForPlot['Proportions'], 3)], axis = 1).set_index('Midpoints')
                            ax1 = customFrameForPlot.plot.barh(color = self._color, figsize = self._figureSize)  
                        else:
                            customFrameForPlot = pd.concat([round(customFrame['Midpoints'], 3), round(customFrame['Proportions'], 3)], axis = 1).set_index('Midpoints')
                            ax1 = customFrameForPlot.plot.barh(color = self._color, figsize = self._figureSize)
            
            if (binningType == 'standard'):
                try:
                    ax1.yaxis.set_major_locator(MultipleLocator(int(len(standardFrameForPlot) / self._majorTickSpacingFactor)))
                except ValueError:
                    ax1.yaxis.set_major_locator(MultipleLocator(1))
                except UnboundLocalError:
                    self.printAndPass()
    
            if (binningType == 'missingLength'):
                try:
                    ax1.yaxis.set_major_locator(MultipleLocator(int(len(missingLengthFrameForPlot) / self._majorTickSpacingFactor)))
                except ValueError:
                    ax1.yaxis.set_major_locator(MultipleLocator(1))
                except UnboundLocalError:
                    self.printAndPass()
    
            if (binningType == 'custom'):
                try:
                    ax1.yaxis.set_major_locator(MultipleLocator(int(len(customFrameForPlot) / self._majorTickSpacingFactor)))
                except ValueError:
                    ax1.yaxis.set_major_locator(MultipleLocator(1))
                except UnboundLocalError:
                    self.printAndPass()
            
            try:
                if scaledX:
                    ax1.xaxis.set_major_locator(MultipleLocator((self._scalerRange[1]- self._scalerRange[0]) / 4))
                ax1.set_title((self._tickerSymbol + ' – ' + methodology.title() + ' Profile'), fontsize = 16)
                ax1.minorticks_on()
                ax1.tick_params(labelsize = self._labelsize, labelright = True)
                ax1.set_ylabel('')
                ax1.legend('')
                ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
                ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
                plt.pause(0.01)
            except UnboundLocalError:
                self.printAndPass()
                
        if (seriesType == 'standard'):
            if (interpolation != None):
                print('\nNote: standard seriesType computation does not use interpolation but interpolation argument was passed: interpolation argument has now been set to None for your convenience')
                interpolation = None
                singleProfilePlotSyntaxShortener(seriesType, binningType, methodology, 
                                                 numberOfBins, scaledX, scaledY, interpolation)
            else:
                singleProfilePlotSyntaxShortener(seriesType, binningType, methodology,
                                                 numberOfBins, scaledX, scaledY, interpolation)
                
        if (seriesType == 'interpolated'):
            if (interpolation == None):
                print('\nNote: in order to use interpolated functionality for singleProfilePlot, you must first set the interpolation argument equal to either \'linear\' or \'cubic\'')
                pass
            else:
                singleProfilePlotSyntaxShortener(seriesType, binningType, methodology,
                                                 numberOfBins, scaledX, scaledY, interpolation)
            
            
    def externalWindowSinglePlot(self) -> None:

        '''Takes no direct arguments. Is used to chart the original unaltered version of the time series dataframe created upon instantiation of the class, but in an external interactive window. Do note that missing data units are not represented in this chart.'''
    
        get_ipython().run_line_magic('matplotlib','qt') 
        print('\nNote: to switch back to inline plotting when you are finished, run \n%matplotlib inline')

        if self._percentageChange:
            ax1 = self._assetTimeSeries[self._seriesType].pct_change().cumsum().plot(color = self._color, figsize = self._figureSize, label = self._tickerSymbol, linewidth = 1)
            ax1.set_title(self._tickerSymbol, fontsize = 16)
            for i in range(-5, 10):
                step = round((self._maxPercentageChange / self._majorTickSpacingFactor), i)
            ax1.yaxis.set_major_locator(MultipleLocator(step))
        elif (self._percentageChange == False):
            ax1 = self._assetTimeSeries[self._seriesType].plot(color = self._color, figsize = self._figureSize, label = self._tickerSymbol, linewidth = 1)   
            ax1.set_title(self._tickerSymbol, fontsize = 16)
            for i in range(-5, 10):
                step = round((self._maxPriceChange / self._majorTickSpacingFactor), i)
            ax1.yaxis.set_major_locator(MultipleLocator(step))
           
        if (self._majorTickSpacingFactor > 10):
            plt.xticks(rotation = -45)
   
        if (self._lengthWithMissingData > (self._numberOfUnits * 2)):
            step = (round(self._numberOfUnits, -(len(str((self._numberOfUnits))) - 1)) / self._majorTickSpacingFactor)
            ax1.xaxis.set_major_locator(MultipleLocator(step))
   
        xStep = (round(self._lengthWithMissingData, -(len(str((self._lengthWithMissingData))) - 1)) / self._majorTickSpacingFactor)
        ax1.xaxis.set_major_locator(MultipleLocator(xStep))
        ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
        ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
        plt.tick_params(labelsize = self._labelsize, labelright = True)
        plt.minorticks_on()
        plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)
        
        
    def liveSinglePlot(self,
                       numberOfUpdates: Optional[int] = 14400,
                       interactiveExternalWindow: Optional[bool] = False,
                       secondsToSleep: Optional[int] = 55) -> None:

        '''
        Method used to update a chart in live-time, either in an external window, or inline.
        

        Parameters
        ----------
        numberOfUpdates: int or None, optional
            The number of times to update the chart. The default is 14400, which is equal to 10 calendar days (assuming 1 min per update).
        interactiveExternalWindow: bool, optional
            If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
        secondsToSleep: int, optional
            The number of seconds to wait between updates. The default is 55 seconds, which should be sufficient
            to avoid any issues with the API's 60 second rate limit. There is also a 40 second waiting period declared in the __init__ for
            SingleTickerProcessor, which results from the API throwing an error.
        '''
                
        def countdownForLiveSinglePlot(timeToCount: int,
                                       updateCount: int) -> None:
            
            '''
            Method used to countdown the time between updates.

            Parameters
            ----------      
            timeToCount: int
                The number of seconds to count down from, which is equal to liveSinglePlot's secondsToSleep.
            updateCount: int
                The number of times the chart has been updated.
            '''
    
            print('\nFinished Update #' + str(updateCount))
            print('Next update will be initiated in: ')
            while timeToCount:
                minutes, seconds = divmod(timeToCount, 60)
                timeFormat = '{:02d}:{:02d}'.format(minutes, seconds)
                print(timeFormat, end='\n')
                time.sleep(1)
                timeToCount -= 1
            print('Waiting on data...')

        count = 0
        print('\nEntered live charting mode: use command c, or interrupt kernel to exit.')
        if interactiveExternalWindow:
            get_ipython().run_line_magic('matplotlib','qt')
            print('\nNote: to switch back to inline plotting when you are finished, run \nplt.switch_backend(\'module://ipykernel.pylab.backend_inline\')')

            for i in range(numberOfUpdates):
                count += 1
                self.standardSinglePlot()
                plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)
                countdownForLiveSinglePlot((secondsToSleep), count)
                time.sleep(secondsToSleep) 
                self._assetTimeSeries = self.apiCall()
        else:
            for i in range(numberOfUpdates):
                count += 1
                self.standardSinglePlot()
                countdownForLiveSinglePlot((secondsToSleep), count)
                time.sleep(secondsToSleep) 
                self._assetTimeSeries = self.apiCall()
            