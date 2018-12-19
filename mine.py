import pandas as pd
from enum import Enum

class glucose(Enum):
    low = 0
    normal = 1
    high = 2

def discretizeGlucose(dataframe):
    high_mask = dataframe["value"] > 200
    normal_mask = (dataframe["value"] <= 200) & (dataframe["value"] >= 80)
    low_mask = dataframe["value"] < 80
    dataframe.loc[high_mask, "value"] = glucose.high
    dataframe.loc[normal_mask, "value"] = glucose.normal
    dataframe.loc[low_mask, "value"] = glucose.low
    return dataframe

def splitEventsStates(dataframe):
    code_mask = (dataframe["code"] >= 48) & (dataframe["code"] <= 64)
    events = dataframe[code_mask]
    states = dataframe[~code_mask]
    return events, states 

# function that finds subsequences which contain a change of state from low to normal in a single day sequence of a patient
def subsequencesInStatesLowToNormal(states_by_day):
    subsequences = []
    for _, group in states_by_day:   # _ is a day we group by, group is dataframe of measurements in that group
        lowPosition = False
        sequence = []
        for _, measurement in group.iterrows(): # _ is an index of iterator, measurement is a row in our group
            #already adding sequence, keep adding till glucose raises
            if (lowPosition):
                sequence.append(measurement)
                if(measurement["value"] == glucose.normal):
                    lowPosition = False
                    subsequences.append(sequence)
            #not adding sequence yet, if glucose.low we start adding and clear any previous one (that didn't contain change)
            else:
                if(measurement["value"] == glucose.low):
                    lowPosition = True
                    sequence.clear()
                    sequence.append(measurement)
    return subsequences

def timeRangeOfSubsequence(subsequence):
    timeRange = []
    first = (subsequence[0].loc["date"], subsequence[0].loc["time"])
    timeRange.append(first)
    lastIndex = len(subsequence) - 1
    last = (subsequence[lastIndex].loc["date"], subsequence[lastIndex].loc["time"])
    timeRange.append(last)
    return timeRange

def timeRangesOfSubsequences(subsequences):
    timeRanges = []
    for i in range(0, len(subsequences)):
        timeRanges.append(timeRangeOfSubsequence(subsequences[i]))
    return timeRanges

def main():
    diabetes = pd.read_csv("data/diabetes/data-01", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates=["date", "time"])
    diabetes["time"] = diabetes["time"].apply(lambda x: x.time())
    diabetes["date"] = diabetes["date"].apply(lambda x: x.date())
    diabetes = diabetes.sort_values(by = ["date", "time"], ascending = True)
    diabetes = discretizeGlucose(diabetes)
    events, states = splitEventsStates(diabetes)
    states_by_day = states.groupby("date")
    subsequencesLowToNormal = subsequencesInStatesLowToNormal(states_by_day)

if __name__ == "__main__":
    main()