import DataPlotter
import UploadDownload

def GetYNInput(message):
    while True:
        returned = input(message)

        if returned == "Y" or returned == "N":
            return returned
        print("Enter only Y or N")

while True:
    print("---------Stock Analysis---------")
    
    # Start
    loadNewData = GetYNInput("Get new stock data (Y/N)? ") == "Y"

    if loadNewData == False:
        UploadDownload.DownloadData()
        continue

    # Stock Data Download
    ticker = input("Enter the ticker to display: ")
    isCrypto = GetYNInput("Is this a crypto ticker (Y/N)? ") == "Y"
    live = GetYNInput("Live data (Y/N)? ")

    if live == "Y":
        if isCrypto:
            DataPlotter.PlotLiveCryptoData(ticker)
            print("---------Displaying Data---------")
        else:
            DataPlotter.PlotLiveData(ticker)
            print("---------Displaying Data---------")
    else:
        print("---------When entering dates, include 0's---------")
        startDate = input("Enter start date (Y-M-D): ")
        endDate = input("Enter end date (Y-M-D): ")

        DataPlotter.PlotHistoricalData(startDate, endDate, ticker, isCrypto)

        print("---------Displaying Data---------")

    saveData = GetYNInput("Do you wish to save the graph data (Y/N)? ") == "Y"
    if saveData == True:
        UploadDownload.UploadData(ticker, DataPlotter.xValues, DataPlotter.yValues)












