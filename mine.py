import pandas as pd
from enum import Enum
from prefixspan import PrefixSpan
import numpy as np

class glucose(Enum):
    low = 0
    normal = 1
    high = 2

eventsDictionary = {
    33: "Regular insulin dose",
    34: "NPH insulin dose",
    35: "UltraLente insulin dose",
    48: "Unspecified blood glucose measurement",
    57: "Unspecified blood glucose measurement",
    58: "Pre-breakfast blood glucose measurement",
    59: "Post-breakfast blood glucose measurement",
    60: "Pre-lunch blood glucose measurement",
    61: "Post-lunch blood glucose measurement",
    62: "Pre-supper blood glucose measurement",
    63: "Post-supper blood glucose measurement",
    64: "Pre-snack blood glucose measurement",
    65: "Hypoglycemic symptoms",
    66: "Typical meal ingestion",
    67: "More-than-usual meal ingestion",
    68: "Less-than-usual meal ingestion",
    69: "Typical exercise activity",
    70: "More-than-usual exercise activity",
    71: "Less-than-usual exercise activity",
    72: "Unspecified special event"
}

def discretizeGlucose(dataframe):
    high_mask = dataframe["value"] > 200
    normal_mask = (dataframe["value"] <= 200) & (dataframe["value"] >= 80)
    low_mask = dataframe["value"] < 80
    dataframe.loc[high_mask, "value"] = glucose.high
    dataframe.loc[normal_mask, "value"] = glucose.normal
    dataframe.loc[low_mask, "value"] = glucose.low
    return dataframe

def prepareData():
    diabetes = pd.read_csv("data/diabetes_merged.csv", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates=["date", "time"])
    diabetes["time"] = diabetes["time"].apply(lambda x: x.time())
    diabetes["date"] = diabetes["date"].apply(lambda x: x.date())
    diabetes = diabetes.sort_values(by = ["date", "time"], ascending = True)
    diabetes = discretizeGlucose(diabetes)
    events, states = splitEventsStates(diabetes)
    return events, states

def splitEventsStates(dataframe):
    code_mask = (dataframe["code"] >= 48) & (dataframe["code"] <= 64)
    events = dataframe[code_mask]
    states = dataframe[~code_mask]
    return events, states 

# function that finds subsequences which contain a change of state from one to another in a single day sequence of a patient
def subsequencesInStates(states_by_day, from_level, to_level):
    subsequences = []
    for _, group in states_by_day:   # _ is a day we group by, group is dataframe of measurements in that group
        fromPosition = False
        sequence = []
        for _, measurement in group.iterrows(): # _ is an index of iterator, measurement is a row in our group
            #already adding sequence, keep adding till glucose raises
            if (fromPosition):
                sequence.append(measurement)
                if(measurement["value"] == to_level):
                    fromPosition = False
                    subsequences.append(sequence)
            #not adding sequence yet, if glucose.low we start adding and clear any previous one (that didn't contain change)
            else:
                if(measurement["value"] == from_level):
                    fromPosition = True
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

def eventsOfTimeRange(events, timeRange):
    day = timeRange[0][0]
    minTime = timeRange[0][1]
    maxTime = timeRange[1][1]
    return events.loc[(events["date"] == day) & (events["time"] >= minTime) & (events["time"] <= maxTime)]["code"].tolist()

def eventsOfTimeRanges(events, timeRanges):
    listOfEvents = []
    for i in range(0, len(timeRanges)):
        listOfEvents.append(eventsOfTimeRange(events, timeRanges[i]))
    return listOfEvents

def getEventsLowToNormal(events, states):
    states_by_day = states.groupby("date")
    subsequences = subsequencesInStates(states_by_day, glucose.low, glucose.normal)
    timeRanges = timeRangesOfSubsequences(subsequences)
    finalEvents = eventsOfTimeRanges(events, timeRanges)
    return finalEvents

# funciton that maps codes in result patterns to their equivalent description
def describePatterns(patterns):
    described_patterns = patterns
    for i, result_tuple in enumerate(described_patterns):
        for j, item in enumerate(result_tuple[1]):
            described_patterns[i][1][j] = eventsDictionary[item]
    return described_patterns

def minePatterns(sequences):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(3)
    return patterns

def main():
    events, states = prepareData()
    eventsLowToNormal = getEventsLowToNormal(events, states)
    patterns = minePatterns(eventsLowToNormal)
    patterns_described = describePatterns(patterns)
    print(patterns_described)

if __name__ == "__main__":
    main()