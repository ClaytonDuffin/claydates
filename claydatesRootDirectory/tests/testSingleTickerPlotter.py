import datetime
import time
import requests
import unittest
from claydates import SingleTickerPlotter

class TestSingleTickerPlotter(unittest.TestCase):
    
    @classmethod
    def setUpClass(self) -> None:
        try:
            start = time.time()
            while ((time.time() - start) < 20):
                self._testObject = SingleTickerPlotter('QQQ', '1min', 25, mockResponse = True)
                break
            if (self._testObject == None):
                self.fail()
        except ConnectionError:
            self.fail()


    def test_apiCall(self) -> None:
        
        self.assertEqual(str(requests.get('https://api.twelvedata.com/time_series?symbol=QQQ&interval=1min&apikey=your_api_key')),
                         '<Response [200]>')
    
    
    def test_timeSeriesData(self) -> None:
        
        if (self._testObject._mockResponse == True):
            self.assertGreater(self._testObject._assetTimeSeries.Close.sum(),
                               0)
        else:
            self.assertGreater(self._testObject.apiCall().Close.sum(),
                               0)
        
        
    def test_interval(self) -> None:
        
        if isinstance(self._testObject.interval(), int):
            self.assertLessEqual(self._testObject.interval(),
                                 45)
        else:
            self.fail()


    def test_units(self) -> None:
        
        if isinstance(self._testObject.units(), str):
            self.assertGreater(len(self._testObject.units()),
                                2)
        else:
            self.fail()
    

    def test_MarketCalendarInterval(self) -> None:
        
        if (self._testObject.marketCalendarInterval() in ['1d','1m']):
            self.assertEqual(len(self._testObject.marketCalendarInterval()),
                                2)
        else:
            self.fail()


    def test_isNowInTimePeriod(self) -> None:

        with self.subTest():
            self.assertTrue(self._testObject.isNowInTimePeriod((datetime.datetime.now() - datetime.timedelta(minutes = 2)).time(), (datetime.datetime.now() + datetime.timedelta(minutes = 2)).time(), datetime.datetime.now().time()))
        with self.subTest():
            self.assertFalse(self._testObject.isNowInTimePeriod((datetime.datetime.now() - datetime.timedelta(minutes = 2)).time(), (datetime.datetime.now() + datetime.timedelta(minutes = 2)).time(), (datetime.datetime.now() + datetime.timedelta(minutes = 4)).time()))


    def test_profileProcessor(self) -> None:

        self.assertTrue(callable(self._testObject.outputForDatetimeHandler))
        self.assertTrue((str(self._testObject.outputForDatetimeHandler))[0:60] == '<bound method SingleTickerProcessor.outputForDatetimeHandler')


    def test_datetimeHandler(self) -> None:
        
        mockResponseRunningOK = False
        if (self._testObject._mockResponse == True):
            if ((self._testObject.datetimeHandler('missingPercentage', silencePrint = True)) <= 0.05) and ((self._testObject.datetimeHandler('missingPercentage', silencePrint = True)) >= 0.04):
                if (len(self._testObject.datetimeHandler('missingDataIncludedInFrame')) >= len(self._testObject._assetTimeSeries)):
                    if (len(self._testObject.datetimeHandler('lagTime')) >= 15):
                        if (len(self._testObject.datetimeHandler('missingDataIncludedInFrame').columns) == 6) or (len(self._testObject.datetimeHandler('missingDataIncludedInFrame').columns) == 7):
                            mockResponseRunningOK = True
            self.assertTrue(mockResponseRunningOK)
            
        elif (self._testObject._mockResponse == False):
            if isinstance((self._testObject.datetimeHandler('missingPercentage', silentPrint = True)), float):
                if (len(self._testObject.datetimeHandler('missingDataIncludedInFrame')) >= len(self._testObject._assetTimeSeries)):
                    if (len(self._testObject.datetimeHandler('missingDataIncludedInFrame').columns) == 6) or (len(self._testObject.datetimeHandler('missingDataIncludedInFrame').columns) == 7):
                        self.assertGreaterEqual((len(self._testObject.datetimeHandler('lagTime'))), 15)
        else:
            self.fail()


    def test_unalteredFrameGetter(self):

        if (self._testObject._mockResponse == True):
            self.assertTrue((self._testObject.unalteredFrameGetter()[self._testObject._seriesType].iloc[-1] < 286) and (self._testObject.unalteredFrameGetter()[self._testObject._seriesType].iloc[-1] > 285))
        elif (self._testObject._mockResponse == False):
            self.assertGreaterEqual(self.len((self._testObject._assetTimeSeries), 2))


    def test_instanceVariables(self):
            
            seriesTypePassing = False
            if (self._testObject._seriesType in ['Open', 'High', 'Low', 'Close']):
                seriesTypePassing = True
            self.assertTrue(seriesTypePassing)

            self.assertGreater(self._testObject._maxPercentageChange, -1.01)
            self.assertLess(self._testObject._maxPriceChange, 5000)
            self.assertGreaterEqual(len(self._testObject._timeSeriesWithMissingData), 2)

    # This would be a better way to test some of the following methods, though I had trouble implementing it. kept getting "AssertionError: Expected 'mock' to be called once. Called 0 times."
    # from unittest.mock import patch
    # from unittest import mock
    # @patch('plotters.singleTickerPlotter.SingleTickerPlotter')
    # def test_standardSinglePlot(self, *args) -> None:
    #     mockObject = mock.MagicMock()
    #     #mockObject.standardSinglePlot()
    #     mockObject.return_value.assert_called_once_with(color = self._testObject._color, figsize = self._testObject._figureSize, label = self._testObject._tickerSymbol, linewidth = 1)

    def test_printAndPass(self) -> None:

        self.assertTrue(callable(self._testObject.printAndPass))
        self.assertTrue((str(self._testObject.printAndPass))[0:46] == '<bound method SingleTickerPlotter.printAndPass')

        # Have provided an example here of a nifty solution that could be implemented to the rest of the following methods. Uses an optional keyword argument to ensure that the code is getting
        # to the point where it needs to to complete various tasks. Refer to the printAndPass method in singleTickerPlotter.py for more ideas on how to further implement this procedure,
        # It wouldn't be a perfect solution, but it would be a lot better than just checking to see if the method is callable and if it's name and type is correct. 
        # The best route to take is probably to use mocking and patches, per the test_standardSinglePlot method example above that is commented out.
        try:
            self._testObject.printAndPass(forTesting = True)
        except: 
            self.fail()


    def test_XAndYMajorFormatterDecorators(self):
        
        self.assertTrue(callable(self._testObject.variableXMajorFormatter()))
        self.assertTrue(callable(self._testObject.variableYMajorFormatter()))
        self.assertTrue((str(self._testObject.variableXMajorFormatter))[0:57] == '<bound method SingleTickerPlotter.variableXMajorFormatter')
        self.assertTrue((str(self._testObject.variableYMajorFormatter))[0:57] == '<bound method SingleTickerPlotter.variableYMajorFormatter')


    def test_standardSinglePlot(self) -> None:

        self.assertTrue(callable(self._testObject.standardSinglePlot))
        self.assertTrue((str(self._testObject.standardSinglePlot))[0:78] == '<bound method SingleTickerPlotter.variableXMajorFormatter.<locals>.plotWrapper')


    def test_standardSinglePlot(self) -> None:

        self.assertTrue(callable(self._testObject.standardSinglePlot))
        self.assertTrue((str(self._testObject.standardSinglePlot))[0:78] == '<bound method SingleTickerPlotter.variableXMajorFormatter.<locals>.plotWrapper')


    def test_interpolatedSinglePlot(self) -> None:

        self.assertTrue(callable(self._testObject.interpolatedSinglePlot))
        self.assertTrue((str(self._testObject.standardSinglePlot))[0:78] == '<bound method SingleTickerPlotter.variableXMajorFormatter.<locals>.plotWrapper')


    def test_profileProcessor(self) -> None:

        self.assertTrue(callable(self._testObject.profileProcessor))
        self.assertTrue((str(self._testObject.profileProcessor))[0:50] == '<bound method SingleTickerPlotter.profileProcessor')
        

    def test_profileProcessor(self) -> None:

        self.assertTrue(callable(self._testObject.singleProfilePlot))
        self.assertTrue((str(self._testObject.singleProfilePlot))[0:51] == '<bound method SingleTickerPlotter.singleProfilePlot')


    def test_externalWindowSinglePlot(self) -> None:

        self.assertTrue(callable(self._testObject.externalWindowSinglePlot))
        self.assertTrue((str(self._testObject.externalWindowSinglePlot))[0:58] == '<bound method SingleTickerPlotter.externalWindowSinglePlot')


    def test_liveSinglePlot(self) -> None:

        self.assertTrue(callable(self._testObject.liveSinglePlot))
        self.assertTrue((str(self._testObject.liveSinglePlot))[0:48] == '<bound method SingleTickerPlotter.liveSinglePlot')


if __name__ == '__main__':
    unittest.main()
