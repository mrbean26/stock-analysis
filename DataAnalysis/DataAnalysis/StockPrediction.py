import datetime
from numpy import array, prod, sum

class LagrangePoly:
    def __init__(self, X, Y):
        self.n = len(X)
        self.X = array(X)
        self.Y = array(Y)

    def basis(self, x, j):
        b = [(x - self.X[m]) / (self.X[j] - self.X[m])
             for m in range(self.n) if m != j]
        return prod(b, axis=0) * self.Y[j]

    def interpolate(self, x):
        b = [self.basis(x, j) for j in range(self.n)]
        return sum(b, axis=0)

def GetLagrangianCurve(xTimeValues, yValues):
    # remove repetitions
    newXValues = []
    newYValues = []

    resultantXValues = []

    step = int(len(xTimeValues) / 50)
    if len(xTimeValues) < 50:
        step = 1

    for i in range(0, len(xTimeValues), step):
        unixTime = datetime.datetime.timestamp(xTimeValues[i])

        if unixTime in newXValues:
            continue
        
        newXValues.append(float(unixTime))
        newYValues.append(yValues[i])
        resultantXValues.append(xTimeValues[i])

    lp = LagrangePoly(newXValues, newYValues)
    returnedYValues = lp.interpolate(newXValues)

    return [resultantXValues, returnedYValues]

