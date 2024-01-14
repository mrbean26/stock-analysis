from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
import matplotlib.dates

import StockScraper
import time

from datetime import datetime
from pytz import timezone

import StockPrediction

lastTicker = ""
xValues = []
yValues = []

figureClosed = False
def FigureCloseEvent(event):
    global figureClosed
    figureClosed = True

def SetupFigure(xValues, yValues, dateFormatting):
    fig, ax = pyplot.subplots(figsize=(8,6), facecolor = '#b8b8b8')
    
    line, = ax.plot(xValues, yValues, '-', color = '#000000', label = "Actual")
    lagrangianFitLine, = ax.plot([], [], '-', color = '#ff0000', label = "Lagrangian Fit")

    fig.canvas.mpl_connect('close_event', FigureCloseEvent)
    fig.legend(bbox_to_anchor = (0.8, 0.1), loc = "upper left")

    ax.set_facecolor('#a1a1a1')

    pyplot.gcf().autofmt_xdate()
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(dateFormatting))

    return fig, ax, line, lagrangianFitLine,

def PlotHistoricalData(startDate, endDate, ticker, isCrypto):
    global xValues
    global yValues
    global lastTicker

    lastTicker = ticker
    data = StockScraper.GetStockData(False, ticker, 0, 0, startDate, endDate, isCrypto)

    if data is None:
        print("Error retrieving stock data.")
        return

    xValues = [item[0] for item in data]
    yValues = [item[1] for item in data]

    fig, ax, line, lagrangianFitLine = SetupFigure(xValues, yValues, '%Y/%m/%d')

    lagrangianFitData = StockPrediction.GetLagrangianCurve(xValues, yValues)
    lagrangianFitLine.set_data(lagrangianFitData[0], lagrangianFitData[1])

    fig.text(0.05, 0.95, "Stock: " + ticker)
    fig.text(0.05, 0.925, "From: " + startDate)
    fig.text(0.05, 0.9, "To: " + endDate)

    fig.text(0.4, 0.95, "Current Price: " + str(yValues[0]))

    fig.text(0.05, 0.05, "Data Points: " + str(len(xValues)))

    pyplot.show()

def PlotLiveCryptoData(ticker):
    global figureClosed
    global xValues
    global yValues
    global lastTicker

    lastTicker = ticker
    figureClosed = False

    fig, ax, line, lagrangianFitLine, = SetupFigure([], [], '%H:%M:%S')

    stockNameText = fig.text(0.05, 0.95, "Stock: " + ticker)
    currentPriceText = fig.text(0.05, 0.925, "CurrentPrice")
    currentTimeText = fig.text(0.05, 0.9, "CurrentTime")

    fpsText = fig.text(0.05, 0.075, "FPS")
    stockTimeText = fig.text(0.05, 0.05, "StockTime")
    dataPointCountText = fig.text(0.4, 0.05, "Data Points")

    tz = timezone('GMT')
    
    startTime = time.time()
    lastStockTime = time.time()
    lastStockCount = 0

    while figureClosed == False:
        # Actual Stock Values
        liveCryptoValues = StockScraper.GetLiveCryptoData(ticker)
        
        if liveCryptoValues is None:
            print("Error retrieving stock data.")
            return
        
        xValues = liveCryptoValues[0]
        yValues = liveCryptoValues[1]
        
        line.set_data(xValues, yValues)

        lagrangianFitData = StockPrediction.GetLagrangianCurve(xValues, yValues)
        lagrangianFitLine.set_data(lagrangianFitData[0], lagrangianFitData[1])

        # Accomodating Values
        currentPriceText.set_text("Current Price: $" + str(yValues[0]))
        
        c = datetime.now(tz)
        currentTimeText.set_text("GMT Time: " + c.strftime("%H:%M:%S.%f")[:-3])

        # Extra Values
        elapsedTime = time.time() - startTime
        fps = 1 / elapsedTime
        startTime = time.time()
        
        fpsText.set_text("FPS: " + str(fps)[0 : 4])

        newStockCount = len(xValues)
        if newStockCount != lastStockCount:
            lastStockTime = time.time()
            lastStockCount = newStockCount
        
        stockTimeText.set_text("Time since last stock update: " + str((time.time() - lastStockTime))[0 : 4])
        dataPointCountText.set_text("Data points: " + str(len(xValues)))

        # Draw
        pyplot.draw()
        ax.relim()
        ax.autoscale()
        
        pyplot.pause(0.1)

def PlotLiveData(ticker):
    global figureClosed
    global xValues
    global yValues
    global lastTicker

    lastTicker = ticker
    figureClosed = False

    fig, ax, line, lagrangianFitLine, = SetupFigure([], [], '%H:%M:%S')

    stockNameText = fig.text(0.05, 0.95, "Stock: " + ticker)
    industryText = fig.text(0.05, 0.925, "Industry")
    peText = fig.text(0.05, 0.9, "P/E")
    yearHighText = fig.text(0.4, 0.9, "52W")
    marketCapText = fig.text(0.4, 0.95, "MktCap")
    yearTargetText = fig.text(0.4, 0.925, "YrTarget")
    currentPriceText = fig.text(0.75, 0.95, "CurrentPrice")
    currentTimeText = fig.text(0.75, 0.925, "CurrentTime")

    fpsText = fig.text(0.05, 0.075, "FPS")
    stockTimeText = fig.text(0.05, 0.05, "StockTime")
    dataPointCountText = fig.text(0.4, 0.05, "Data Points")
    marketOpenText = fig.text(0.4, 0.075, "MktOpen")

    tz = timezone('EST')
    
    startTime = time.time()
    lastStockTime = time.time()
    lastStockCount = 0

    while figureClosed == False:
        # Actual Stock Values
        liveStockValues = StockScraper.GetStockData(True, ticker, 1000000000, 0)

        if liveStockValues is None:
            print("Error retrieving stock data.")
            return

        xValues = [item[0] for item in liveStockValues]
        yValues = [item[1] for item in liveStockValues]

        line.set_data(xValues, yValues)

        lagrangianFitData = StockPrediction.GetLagrangianCurve(xValues, yValues)
        lagrangianFitLine.set_data(lagrangianFitData[0], lagrangianFitData[1])

        # Accomodating Values
        liveStockInfo = StockScraper.GetStockAttributes(ticker)

        industryText.set_text("Industry: " + liveStockInfo["Industry"])
        peText.set_text("P/E: " + str(liveStockInfo["P/E"]))
        yearHighText.set_text("Yr High/Low: " + liveStockInfo["52W"])
        marketCapText.set_text("Mkt Cap: " + liveStockInfo["MktCap"])
        yearTargetText.set_text("Yr Target: " + liveStockInfo["1yTarg"])
        currentPriceText.set_text("Current Price: $" + str(yValues[0]))
        
        c = datetime.now(tz)
        currentTimeText.set_text("EST Time: " + c.strftime("%H:%M:%S.%f")[:-3])

        # Extra Values
        elapsedTime = time.time() - startTime
        fps = 1 / elapsedTime
        startTime = time.time()
        
        fpsText.set_text("FPS: " + str(fps)[0 : 4])

        newStockCount = len(xValues)
        if newStockCount != lastStockCount:
            lastStockTime = time.time()
            lastStockCount = newStockCount
        
        stockTimeText.set_text("Time since last stock update: " + str((time.time() - lastStockTime))[0 : 4])
        dataPointCountText.set_text("Data points: " + str(len(xValues)))
        marketOpenText.set_text("Mkt Open: " + str(StockScraper.IsMarketOpen()))

        # Display
        pyplot.draw()
        ax.relim()
        ax.autoscale()
        
        pyplot.pause(0.1)

def PlotDownloadedData(xValues, yValues, isLiveData, title):
    fig, ax, line, lagrangianFitLine = SetupFigure(xValues, yValues, '%H:%M:%S')

    lagrangianFitData = StockPrediction.GetLagrangianCurve(xValues, yValues)
    lagrangianFitLine.set_data(lagrangianFitData[0], lagrangianFitData[1])

    fig.text(0.5, 0.95, title, verticalalignment='center', horizontalalignment='center')
    
    if isLiveData:
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S'))
    else:
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y/%m/%d'))

    pyplot.show()
