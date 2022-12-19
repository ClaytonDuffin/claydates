from distutils.sysconfig import get_python_lib, get_python_inc
from sysconfig import get_python_version
import pandas as pd
pd.options.mode.chained_assignment = None
import matplotlib.pyplot as plt; plt.rcdefaults()
from matplotlib.ticker import MultipleLocator
plt.rc('figure', max_open_warning = 0)
from typing import Optional, Callable, Union  
import os
from claydates.plotters.singleTickerPlotter import SingleTickerPlotter
from claydates.processors.multiTickerProcessor import MultiTickerProcessor


class MultiTickerPlotter(SingleTickerPlotter, MultiTickerProcessor):
    
    '''
    Class for gathering and processing time series data for multiple ticker symbols. 
    Creates a list of SingleTickerPlotter class objects, and then organizes data in accordance with the various arguments passed or not passed to the various methods belonging to the SingleTickerPlotter class.
    It is the child class of MultiTickerProcessor and SingleTickerPlotter.
    
    Parameters
    ----------
    tickerSymbols : list[str]
        One or more ticker symbol(s) of the asset(s) or currency pair(s) to be processed.
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
        Is used to determine the size of the labels on the x and y axes. The default is 16, but can be changed.
    color : str, optional
        Is used to determine the color of the plots. Color can also be changed more dynamically in the interactive external windows thanks to matplotlib in Figure Options -> Curves
    '''
    
    def __init__(self,
                 tickerSymbols: list[str],
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

        '''Initializes the MultiTickerPlotter class. Defines its attributes.'''
        
        self._seriesType = seriesType
        self._figureSize = figureSize or [14.275,9.525]
        self._scalerRange = scalerRange or (0, 1)
        self._majorTickSpacingFactor = spacingFactor or 10
        self._labelsize = labelsize or 16
        self._tickerSymbols = tickerSymbols
        
        self._tickerObjects = []
        for symbol in tickerSymbols:
            self._tickerObjects.append(SingleTickerPlotter(symbol, tickInterval, numberOfUnits,
                                                           percentageChange, timeZone, quoteCurrency,
                                                           logMissingData, mockResponse, spacingFactor,
                                                           seriesType, scalerRange, binningFactor,
                                                           figureSize, labelsize, color))
    

    def multiPlotSyntaxShortener(self,
                            method: Callable,
                            pause: bool,
                            matchDates: Optional[bool] = True,
                            interpolationMethod: Optional[str] = None,
                            interactiveExternalWindow: Optional[bool] = False,
                            scaled: Optional[bool] = False,
                            secondsToPauseFor: Optional[float] = 0.01,
                            forMultiWindow: Optional[bool] = False,
                            plotTitle: Optional[str] = None) -> None:
        
        '''
        Method used to generate plots in standardMultiPlot, cyclePlot, and liveMultiPlot. It is structured this way (as a separate method) to shorten the syntax of those methods.
        
        Parameters
        ----------
        method : Callable
            Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded.
        pause : bool
            Strictly a backend argument. allows for differentiation in calling plt.pause. Used for directing flow of figure plotting procedures, and to direct the flow of the program to various branches of this method during runtime.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
        interpolationMethod  : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        interactiveExternalWindow: bool, optional
            If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
        scaled : bool, optional
            Uses min max scaling to scale data into a range specified by self._scalerRange. 
        secondsToPauseFor : float, optional
            Used for plt.pause parameters in some cases, but the main usage case for this argument is in cyclePlot, to pause the plot for a number of seconds before moving onto the next one.
        forMultiWindow : bool, optional
            Strictly a backend argument used for directing the flow of the program. This is especially important for the multipleExternalWindowsPlot and profileCyclerPlot methods.
        plotTitle : str, optional
            Used to pass a custom title for the standardMultiPlot method.
        '''
        
        if (method == self.unalteredFrames):
            print(method)
            timeSeriesData = (method())
        
        if (method == self.missingUnitsIncluded):
            if matchDates:
                timeSeriesData = (method(matchDates = matchDates))
            else:
                if (interpolationMethod == None):
                    timeSeriesData = method(matchDates = False)
                elif (interpolationMethod == 'linear'):
                    timeSeriesData = (method(interpolationMethod = 'linear'))
                elif (interpolationMethod == 'cubic'):
                    timeSeriesData = (method(interpolationMethod = 'cubic'))
                else:
                    raise ValueError('Invalid argument(s). Valid arguments are: None or \'linear\' or \'cubic\'')
                    
        if (method == self.missingUnitsExcluded):
            if matchDates:
                timeSeriesData = (method(matchDates = matchDates))
            else:
                timeSeriesData = (method())
            
        if not scaled:
            maximumPercentageChanges = []
            for index, timeSeriesFrame in enumerate(timeSeriesData):
                maximumPercentageChanges.append([index, (timeSeriesFrame[self._seriesType].pct_change().cumsum().max()) - (timeSeriesFrame[self._seriesType].pct_change().cumsum().min())])
            maximumChange = max(map(lambda x: x[1], maximumPercentageChanges))
        
        for index, timeSeriesFrame in enumerate(timeSeriesData):
            
            if (pause == True):
                plt.figure(index + 1)
            del timeSeriesFrame['Date']
            
            if scaled:
                scaledData = (self.minMaxScaler(timeSeriesFrame.pct_change().cumsum().fillna(0)))
                if (pause == True):
                    ax1 = scaledData[self._seriesType].plot(color = 'black', figsize = self._figureSize)
                    ax1.set_title(self._tickerSymbols[index], fontsize = 16)
                else:
                    ax1 = scaledData[self._seriesType].plot(label = self._tickerSymbols[index], figsize = self._figureSize)
                    ax1.set_title(plotTitle, fontsize = 16)
            else:
                if (pause == True):
                    ax1 = timeSeriesFrame[self._seriesType].pct_change().cumsum().plot(color = 'black', figsize = self._figureSize)
                    ax1.set_title(self._tickerSymbols[index], fontsize = 16)
                    ax1.axhline(0, linewidth = 1, color = 'firebrick')
                else:
                    ax1 = timeSeriesFrame[self._seriesType].pct_change().cumsum().plot(label = self._tickerSymbols[index], figsize = self._figureSize)
                    ax1.axhline(0, linewidth = 1, color = 'firebrick')
                    ax1.set_title(plotTitle, fontsize = 16)

                    
            xStep = (round((len(timeSeriesFrame)), -(len(str(((len(timeSeriesFrame))))) - 1)) / self._majorTickSpacingFactor)
            ax1.xaxis.set_major_locator(MultipleLocator(xStep))
            
            if scaled:
                maximumChange = (scaledData[self._seriesType].max()) - (scaledData[self._seriesType].min())

            for i in range(-5, 10):
                step = round((maximumChange / self._majorTickSpacingFactor), i)
            ax1.yaxis.set_major_locator(MultipleLocator(step))
            
            if (self._majorTickSpacingFactor > 10):
                plt.xticks(rotation = -45)
            ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
            ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
            if (pause == False):
                plt.legend(loc = "upper left", fontsize = 10)
            plt.tick_params(labelsize = self._labelsize, labelright = True)
            plt.minorticks_on()
            
            if (secondsToPauseFor == 0):
                secondsToPauseFor = 0.01
            
            if (forMultiWindow!= False):
                plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)
                plt.pause(0.01)
            else:
                if (pause == True) and (interactiveExternalWindow == False):
                    plt.pause(secondsToPauseFor)
                if (pause == True) and (interactiveExternalWindow == True):
                    plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)
                    plt.pause(secondsToPauseFor)
                    plt.close('all')
                if (pause == False) and (interactiveExternalWindow == True):
                    plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)

                  
    def standardMultiPlot(self,
                          method: Callable,
                          matchDates: Optional[bool] = True,
                          interpolationMethod: Optional[str] = None,
                          interactiveExternalWindow: Optional[bool] = False,
                          scaled: Optional[bool] = False,
                          plotTitle: Optional[str] = None) -> None:
        
        '''
        Method for plotting the ticker symbols side-by-side in various ways. 
        
        Parameters
        ----------
        method : Callable
            Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
        interpolationMethod  : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        interactiveExternalWindow: bool, optional
            If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
        scaled : bool, optional
            Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled.
        plotTitle : str, optional
            Used to pass a custom title if desired. Takes in input the string that would compose the title (see examples folder for more information).
        '''

        if interactiveExternalWindow:
            get_ipython().run_line_magic('matplotlib','qt')
            print('\nNote: to switch back to inline plotting when you are finished, run \n%matplotlib inline')
            if scaled:
                self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates,
                                              interpolationMethod = interpolationMethod, interactiveExternalWindow = interactiveExternalWindow,
                                              scaled = scaled, secondsToPauseFor = 0, plotTitle = plotTitle)
                                             
            else:
                self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates,
                                              interpolationMethod = interpolationMethod, interactiveExternalWindow = interactiveExternalWindow,
                                              scaled = scaled, secondsToPauseFor = 0, plotTitle = plotTitle)
        else:
            if scaled:
                self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates,
                                              interpolationMethod = interpolationMethod, interactiveExternalWindow = interactiveExternalWindow,
                                              scaled = scaled, secondsToPauseFor = 0, plotTitle = plotTitle)
            else:                
                self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates,
                                              interpolationMethod = interpolationMethod, interactiveExternalWindow = interactiveExternalWindow,
                                              scaled = scaled, secondsToPauseFor = 0, plotTitle = plotTitle)

    
    def cyclePlot(self,
                  method: Callable,
                  matchDates: Optional[bool] = True,
                  interpolationMethod: Optional[str] = None,
                  interactiveExternalWindow: Optional[bool] = False,
                  scaled: Optional[bool] = False,
                  secondsToPauseFor: Optional[float] = 0.01) -> None:
        
        '''
        Method for plotting the time series dataframe(s) individually, one after another. One figure is closed out as the next is opened, until they are cycled through. 
        
        Parameters
        ----------
        method : Callable
            Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
        interpolationMethod  : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        interactiveExternalWindow: bool, optional
            If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
        scaled : bool, optional
            Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled.
        secondsToPauseFor : float, optional
            Determines how long to "hover" over one chart until the next chart replaces it. In other words, defines the time between chart updates.
        '''
            
        if interactiveExternalWindow:
            get_ipython().run_line_magic('matplotlib','qt')
            print('\nNote: to switch back to inline plotting when you are finished, run \n%matplotlib inline')
            if scaled:
                self.multiPlotSyntaxShortener(method, pause = True, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                              interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = secondsToPauseFor)
            else:
                self.multiPlotSyntaxShortener(method, pause = True, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                              interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = secondsToPauseFor)
        else:       
            if scaled:
                self.multiPlotSyntaxShortener(method, pause = True, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                              interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = secondsToPauseFor)
            else:                
                self.multiPlotSyntaxShortener(method, pause = True, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                              interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = secondsToPauseFor)

     
    def profileCyclerPlot(self,
                          seriesType: str,
                          binningType: str,
                          methodology: str,
                          numberOfBins: Union[int, None],
                          scaledX: Optional[bool] = True,
                          scaledY: Optional[bool] = True,
                          interpolation: Optional[str] = None) -> None:
        
        '''
        This method is used to cycle through various histograms which can be specified using the parameters. They plot one after another.
        
        Parameters
        ----------
        seriesType : str
            Used to specify whether or not to interpolate data. The options are 'standard' or 'interpolated'. if standard, the data will not be interpolated.
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
        
        indexList = []
        for index, timeSeriesObject in enumerate(self._tickerObjects):
            indexList.append(index)
        
        for index, timeSeriesObject in enumerate(self._tickerObjects):
            if (index == min(indexList)):
                self.disableConsolePrinting()
            if (index == max(indexList)):
                self.enableConsolePrinting()
            timeSeriesObject.singleProfilePlot(seriesType, binningType, methodology,
                                               numberOfBins, scaledX, scaledY, interpolation)
        
        
    def multipleExternalWindowsPlot(self,
                                    method: Callable,
                                    matchDates: Optional[bool] = True,
                                    interpolationMethod: Optional[str] = None,
                                    interactiveExternalWindow: Optional[bool] = False,
                                    scaled: Optional[bool] = False) -> None:
                
        '''
        Method for plotting the time series dataframe(s) in individual external windows. The idea behind this is one could drag the plots over to another screen if desired. 
        
        Parameters
        ----------
        method : Callable
            Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
        interpolationMethod  : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        interactiveExternalWindow: bool, optional
            If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
        scaled : bool, optional
            Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled.
        '''
        
        get_ipython().run_line_magic('matplotlib','qt')
        print('\nNote: to switch back to inline plotting when you are finished, run \n%matplotlib inline')
 
        if scaled:
            self.multiPlotSyntaxShortener(method, pause = True, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                          interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = 0, 
                                          forMultiWindow = True)
        else:                
            self.multiPlotSyntaxShortener(method, pause = True, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                          interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = 0, 
                                          forMultiWindow = True)
  

    def liveMultiPlot(self,
                       method: Callable,
                       matchDates: Optional[bool] = True,
                       interpolationMethod: Optional[str] = None,
                       interactiveExternalWindow: Optional[bool] = False,
                       scaled: Optional[bool] = False,
                       numberOfUpdates: Optional[int] = 14400,
                       secondsToSleepFor: Optional[int] = 55) -> None:
        
        '''
        Method used to update a chart in live-time, either in an external window, or inline (assuming 1 min per update).
        

        Parameters
        ----------
        method : Callable
            Determines where to get the data from. The options are the three methods defined in MultiTickerProcessor: unalteredFrames, missingUnitsIncluded, and missingUnitsExcluded.
        matchDates : bool, optional
            Determines whether or not to ensure that all the date/time units are matching for the data. If set to True, dateMatcher will be returned with the dropMissing argument set to False.
        interpolationMethod  : str, optional
            Used to specify how to interpolate the data, if at all. The options are 'linear', 'cubic', or None.
        interactiveExternalWindow: bool, optional
            If True, the plot will be displayed in an external window. If False, the plot will be displayed inline.
        scaled : bool, optional
            Uses min-max scaling to scale data into a range specified by self._scalerRange. If True, data will be scaled.
        numberOfUpdates: int or None, optional
            The number of times to update the chart. The default is 14400, which is equal to 10 calendar days.
        secondsToSleepFor: int, optional
            The number of seconds to wait between updates. The default is 55 seconds, which should be sufficient
            to avoid any issues with the API's 60 second rate limit. There is also a 40 second waiting period declared in the __init__ for
            SingleTickerProcessor, which results from the API throwing an error.
        '''
        
            
        def countdownForLiveMultiPlot(timeToCount: int,
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
            print('\nNote: to switch back to inline plotting when you are finished, run \n%matplotlib inline')
        
            for i in range(numberOfUpdates):
                count += 1
                if scaled:
                    self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                                  interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = 0)
                    plt.pause(0.01)
                else:                
                    self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                                  interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = 0)             
                    plt.pause(0.01)
                plt.get_current_fig_manager().window.setGeometry(0,0, 1435,952)
                countdownForLiveMultiPlot((secondsToSleepFor), count)
                time.sleep(secondsToSleepFor)
        else:
            for i in range(numberOfUpdates):
                count += 1
                if scaled:
                    self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                                  interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = 0)
                    plt.pause(0.01)
                else:                
                    self.multiPlotSyntaxShortener(method, pause = False, matchDates = matchDates, interpolationMethod = interpolationMethod,
                                                  interactiveExternalWindow = interactiveExternalWindow, scaled = scaled, secondsToPauseFor = 0)
                    plt.pause(0.01)

                countdownForLiveMultiPlot((secondsToSleepFor), count)
                time.sleep(secondsToSleepFor)

