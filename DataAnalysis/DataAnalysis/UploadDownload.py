import requests
import datetime
import re

import DataPlotter

URL = "https://pastebin.com/api/api_login.php"
parameters = { 'api_dev_key': 'db8bca2c177aa989270f1d2c931ae94f',
               'api_user_name' : 'mrbean26',
               'api_user_password' : 'Bonkers12' }

userKey = requests.post(URL, data = parameters).text

def UploadData(ticker, xValues, yValues):
    xValueString = ""
    yValueString = ""

    alreadyAddedTimes = [] # to reduce file size

    for i in range(len(xValues)):
        unixTimestamp = round(datetime.datetime.timestamp(xValues[i]))

        if unixTimestamp in alreadyAddedTimes:
            continue
        alreadyAddedTimes.append(unixTimestamp)

        xValueString += str(unixTimestamp)
        yValueString += str(yValues[i])

        xValueString += ","
        yValueString += ","

    xValueString = xValueString[:-1]
    yValueString = yValueString[:-1]
    
    fileLines = xValueString + "\n" + yValueString
    fileTitle = str(datetime.date.today()) + "_" + ticker
    
    # pastebin POST request
    URL = "https://pastebin.com/api/api_post.php"
    parameters = { 'api_dev_key': 'db8bca2c177aa989270f1d2c931ae94f',
                   'api_option' : 'paste',
                   'api_paste_code' : fileLines,
                   'api_paste_name' : fileTitle,
                   'api_user_key' : userKey,
                    }
    
    x = requests.post(URL, data = parameters)
    print(x.text)

def DownloadData():
    # list pastes
    URL = "https://pastebin.com/api/api_post.php"
    parameters = { 'api_dev_key': 'db8bca2c177aa989270f1d2c931ae94f',
                   'api_option' : 'list',
                   'api_results_limit' : '100',
                   'api_user_key' : userKey,
                    }


    xmlLines = requests.post(URL, data = parameters).text.split("\n")
    dataDictionary = {}

    currentKey = ""
    for i in range(len(xmlLines)):
        if "paste_key" in xmlLines[i]:
            currentKey = re.search('>(.*)<', xmlLines[i]).group(1)
        if "paste_title" in xmlLines[i]:
            currentTitle = re.search('>(.*)<', xmlLines[i]).group(1)

            dataDictionary[currentKey] = currentTitle

    # offer
    dictItems = list(dataDictionary.values())
    dictKeys = list(dataDictionary.keys())

    for i in range(len(dictItems)):
        print(i + 1, ":", dictItems[i])
    
    Choice = -1
    while Choice == -1:
        try:
            Choice = int(input("Enter file choice number: ")) - 1
        except:
            print("Please enter only an integer")

    chosenPasteKey = dictKeys[Choice]

    # get paste
    URL = "https://pastebin.com/api/api_raw.php"
    parameters = { 'api_dev_key': 'db8bca2c177aa989270f1d2c931ae94f',
                   'api_option' : 'show_paste',
                   'api_paste_key' : chosenPasteKey,
                   'api_user_key' : userKey,
                    }
    x = requests.post(URL, data = parameters)
    pasteData = x.text.split("\n")
    
    pasteData[0] = pasteData[0].split(",")
    pasteData[1] = pasteData[1].split(",")

    # decode data
    xValues = []
    yValues = []

    for i in range(len(pasteData[0])):
        unixTime = int(pasteData[0][i])
        stockPrice = float(pasteData[1][i])
        
        xValues.append(datetime.datetime.fromtimestamp(unixTime))
        yValues.append(stockPrice)

    isLiveData = True
    timeDifference = (xValues[0] - xValues[-1]).total_seconds()

    if timeDifference > 1.5 * 24 * 60 * 60:
        # historical data
        isLiveData = False

    DataPlotter.PlotDownloadedData(xValues, yValues, isLiveData, dictItems[Choice])

