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
        if currentMinute - 30 > 0:
            return stockData + GetStockDataRecursivley(currentHour, currentMinute - 30, rowsPerBlock, offsetPerBlock, ticker)
        else:
            return stockData + GetStockDataRecursivley(currentHour - 1, 30 + currentMinute, rowsPerBlock, offsetPerBlock, ticker)




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

    if (currentHour - 1 <= 8 or (currentHour == 9 and currentMinute - 30 < 30)) and offsetPerBlock > 4000:
        return stockData
    else:
        if offsetPerBlock < 5000:
            return stockData + GetStockDataRecursivley(currentHour, currentMinute, rowsPerBlock, offsetPerBlock + 250, ticker)

        if currentMinute - 30 > 0:
            return stockData + GetStockDataRecursivley(currentHour, currentMinute - 30, rowsPerBlock, 0, ticker)
        else:
            return stockData + GetStockDataRecursivley(currentHour - 1, 30 + currentMinute, rowsPerBlock, 0, ticker)