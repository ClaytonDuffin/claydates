import datetime
import time
import requests
import unittest
from claydates import SingleTickerProcessor

class TestSingleTickerProcessor(unittest.TestCase):
    
    @classmethod
    def setUpClass(self) -> None:
        try:
            start = time.time()
            while ((time.time() - start) < 20):
                self._testObject = SingleTickerProcessor('QQQ', '1min', 25, mockResponse = True)
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
            self.assertTrue((self._testObject.unalteredFrameGetter()['Close'].iloc[-1] < 286) and (self._testObject.unalteredFrameGetter()['Close'].iloc[-1] > 285))
        elif (self._testObject._mockResponse == False):
            self.assertGreaterEqual(self.len((self._testObject._assetTimeSeries), 2))


    def testInfoForLogEntries(self) -> None:   
        
        logEntry = self._testObject.infoForLogEntries()
        self.assertEqual(type(logEntry), list)
        self.assertEqual(type(logEntry[0]), str)
        self.assertEqual(type(logEntry[1]), str)
        self.assertEqual(type(logEntry[2]), str)
        self.assertEqual(type(logEntry[3]), str)
        
        
    # This would be a better way to test some of the following methods, though I had trouble implementing it. kept getting "AssertionError: Expected 'mock' to be called once. Called 0 times."
    # def testLogDataCharacteristics(self) -> None:
    # from unittest.mock import patch
    # from unittest import mock
    #     self._testObject.logDataCharacteristics() 
    #     self.assertTrue(os.path.isfile('datasets/dataCharacteristicsLog.csv'))
    #     self.assertTrue(os.path.getsize('datasets/dataCharacteristicsLog.csv') > 0)
        
        
if __name__ == '__main__':
    unittest.main()
