# Live Scraping
from os import times
from threading import currentThread
from urllib.error import HTTPError
import requests
import json

from datetime import datetime
from pytz import timezone

# Historical Scraping
from urllib.request import urlretrieve

# Live Data
requestHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}

offsetFromEndTime = 0
amountRequested = 1000000000 # Seemingly the limit
amountRequested = 5

storedLiveStockData = {}

def getJSONfromURL(URL):
    x = requests.get(URL, headers=requestHeaders)
    data = json.loads(x.text)

    return data

def GetStockRows(timeString, rowsPerBlock, offsetPerBlock, ticker, storeDictionaryKey = True):
    # generate dictionary key
    dictionaryKey = timeString + "," + str(rowsPerBlock) + "," + str(offsetPerBlock) + "," + ticker
    if (storeDictionaryKey == True) and (dictionaryKey in storedLiveStockData.keys()):
        return storedLiveStockData[dictionaryKey]
    print("Searching now, back from", timeString)
    
    # find data
    URL = "https://api.nasdaq.com/api/quote/" + ticker + "/realtime-trades?&limit=" + str(rowsPerBlock) + "&offset=" + str(offsetPerBlock) + "&fromTime=" + timeString
    data = getJSONfromURL(URL)
    
    statusCode = data["status"]["rCode"]
    if statusCode != 200:
        print("Error when retrieving live data:", data["status"]["bCodeMessage"][0]["errorMessage"])
        return None

    allData = data['data']['rows'] # contains time, price, volume
    
    returnedData = []
    for i in range(len(allData)):
        newItem = [datetime.strptime(allData[i]["nlsTime"].strip(), "%H:%M:%S").replace(year = 2000), float(allData[i]["nlsPrice"].replace("$",""))]

        returnedData.append(newItem)
    
    # place in dictionary
    storedLiveStockData[dictionaryKey] = returnedData

    return returnedData

def GetLiveCryptoData(ticker):
    # an example of a ticker is BTC-USD
    URL = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker + "?region=US&lang=en-US&includePrePost=false&interval=1m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance"
    data = getJSONfromURL(URL)

    if data["chart"]["error"] is not None:
        print("Error:", data["chart"]["error"]["description"])
        return None

    data = data["chart"]["result"][0]

    timestampValues = [datetime.utcfromtimestamp(item) for item in data["timestamp"]]
    closeValues = data["indicators"]["quote"][0]["close"]

    returnedTimestamps = []
    returnedValues = []

    for i in range(len(timestampValues)):
        if closeValues[i] == None:
            continue
        returnedTimestamps.append(timestampValues[i])
        returnedValues.append(closeValues[i])

    return [returnedTimestamps, returnedValues]

def GetStockDataRecursivley(currentHour, currentMinute, rowsPerBlock, offsetPerBlock, ticker, firstCall = False):
    stringTime = ""
    
    if currentHour == 9:
        stringTime = "09:"
    else:
        stringTime = str(currentHour) + ":"
    if currentMinute >= 30:
        stringTime += "30"
    else:
        stringTime += "00"

    stockData = GetStockRows(stringTime, rowsPerBlock, offsetPerBlock, ticker, (not firstCall))

    if currentHour - 1 <= 8 or (currentHour == 9 and currentMinute - 30 < 30):
        return stockData
    else:
        if currentMinute - 30 >= 0:
            return stockData + GetStockDataRecursivley(currentHour, currentMinute - 30, rowsPerBlock, 0, ticker)
        else:
            return stockData + GetStockDataRecursivley(currentHour - 1, 30 + currentMinute, rowsPerBlock, 0, ticker)

def IsMarketOpen():
    marketOpen = True

    tz = timezone('EST')
    c = datetime.now(tz)
    
    # check if market open
    dayOfWeek = c.weekday()

    currentHour = int(c.strftime('%H'))
    currentMinute = int(c.strftime('%M'))
    
    if (dayOfWeek == 5 or dayOfWeek == 6):
        marketOpen = False
    else:
        if (currentHour < 9 or currentHour >= 16):
            marketOpen = False
        if (currentHour == 9 and currentMinute <= 30):
            marketOpen = False

    return marketOpen

def GetLiveStockDataQueryHourMinute():
    tz = timezone('EST')
    c = datetime.now(tz)
    
    # check if market open
    dayOfWeek = c.weekday()
    marketOpen = IsMarketOpen()

    currentHour = int(c.strftime('%H'))
    currentMinute = int(c.strftime('%M'))
    
    # if market closed, get previous days data
    if marketOpen == False:
        currentHour = 16 # this means whole day will be scanned, backwards from 5pm
        currentMinute = 0
   
    return currentHour, currentMinute
       
def GetLiveStockData(rowsPerBlock, offsetPerBlock, ticker):
    if rowsPerBlock > 1000000000:
        print("Rows per block above NASDAQ limit")
        return None

    currentHour, currentMinute = GetLiveStockDataQueryHourMinute()

    return GetStockDataRecursivley(currentHour, currentMinute, rowsPerBlock, offsetPerBlock, ticker, True)

# Historical Data
def GetHistoricalStockData(ticker, startDate, endDate, isCrypto = False):
    assetClassString = "stocks"
    if isCrypto == True:
        assetClassString = "crypto"

    URL = "https://api.nasdaq.com/api/quote/" + ticker + "/historical?assetclass=" + assetClassString + "&fromdate=" + startDate + "&limit=1000000000&todate=" + endDate
    data = getJSONfromURL(URL)

    statusCode = data["status"]["rCode"]
    if statusCode != 200:
        print("Error when retrieving live data:", data["status"]["bCodeMessage"][0]["errorMessage"])
        return None

    returnedData = []
    allRows = data['data']['tradesTable']['rows']
    
    if allRows == None:
        print("No data retrieved.")
        return None

    for i in range(len(allRows)):
        newItem = [datetime.strptime(allRows[i]["date"].strip(), "%m/%d/%Y"), float(allRows[i]["close"].replace("$","").replace(",", ""))]

        returnedData.append(newItem)

    return returnedData

# Combined
def GetStockData(live, ticker, rowsPerBlock = 30, offsetPerBlock = 0, 
                    startDate = "2014-01-01", endDate = "2024-01-13", isCrypto = False):
    if live == True:
        return GetLiveStockData(rowsPerBlock, offsetPerBlock, ticker)
    else:
        return GetHistoricalStockData(ticker, startDate, endDate, isCrypto)

# Stock Attributes
def GetStockAttributes(ticker):
    URL = "https://api.nasdaq.com/api/quote/" + ticker + "/summary?assetclass=stocks"
    data = getJSONfromURL(URL)

    peRatio = data["data"]["summaryData"]["PERatio"]["value"]
    fiftyTwoWeekHighLow = data["data"]["summaryData"]["FiftTwoWeekHighLow"]["value"]
    marketCap = data["data"]["summaryData"]["MarketCap"]["value"]
    oneYearTarget = data["data"]["summaryData"]["OneYrTarget"]["value"]
    industry = data["data"]["summaryData"]["Industry"]["value"]

    return {"P/E" : peRatio, "52W" : fiftyTwoWeekHighLow, "MktCap" : marketCap, 
            "1yTarg" : oneYearTarget, "Industry" : industry}