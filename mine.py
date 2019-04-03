import sys
import pandas as pd
from prefixspan import PrefixSpan
import numpy as np
from additional_types import value
from diabetes import prepareDataDiabetes, eventsDictionary

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
                if(measurement["discret_val"] == to_level):
                    fromPosition = False
                    subsequences.append(sequence)
            #not adding sequence yet, if value.low we start adding and clear any previous one (that didn't contain change)
            else:
                if(measurement["discret_val"] == from_level):
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
        eventsInTimeRange = eventsOfTimeRange(events, timeRanges[i])
        if len(eventsInTimeRange) != 0:
            listOfEvents.append(eventsInTimeRange)
    return listOfEvents

def getEventsLowToNormal(events, states):
    states_by_day = states.groupby("date")
    subsequences = subsequencesInStates(states_by_day, value.low, value.normal)
    timeRanges = timeRangesOfSubsequences(subsequences)
    finalEvents = eventsOfTimeRanges(events, timeRanges)
    return finalEvents

def getEventsNormalToLow(events, states):
    states_by_day = states.groupby("date")
    subsequences = subsequencesInStates(states_by_day, value.normal, value.low)
    timeRanges = timeRangesOfSubsequences(subsequences)
    finalEvents = eventsOfTimeRanges(events, timeRanges)
    return finalEvents

# funciton that maps codes in result patterns to their equivalent description
def describePatterns(patterns):
    described_patterns = patterns
    for i, result_tuple in enumerate(described_patterns):
        for j, item in enumerate(result_tuple[2]):
            described_patterns[i][2][j] = eventsDictionary[item]
    return described_patterns

def minePatterns(sequences, threshold):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(threshold)
    return patterns

def addConfidenceOfPositivePatterns(positive_patterns, negative_patterns):
    pattern_with_conf = []
    for positive in positive_patterns:
        for negative in negative_patterns:
            positive_threshold = positive[0]
            positive_pattern = positive[1]
            negative_threshold = negative[0]
            negative_pattern = negative[1]
            # if a pattern also appears in negative patterns, update it's confidence
            if(positive_pattern == negative_pattern):
                value = positive_threshold/(positive_threshold+negative_threshold)
                pattern_with_conf.append((value, positive_threshold, positive_pattern))
                break
        # if a pattern doesn't appear in negative patterns
        else:
            value = positive_threshold/positive_threshold
            pattern_with_conf.append((value, positive_threshold, positive_pattern))
    return pattern_with_conf

def addConfidenceOfNegativePatterns(negative_patterns, positive_patterns):
    pattern_with_conf = []
    for negative in negative_patterns:
        for positive in positive_patterns:
            negative_threshold = negative[0]
            negative_pattern = negative[1]
            positive_threshold = positive[0]
            positive_pattern = positive[1]
            # if a pattern also appears in positive patterns, update it's confidence
            if(negative_pattern == positive_pattern):
                value = negative_threshold/(positive_threshold+negative_threshold)
                pattern_with_conf.append((value, negative_threshold, negative_pattern))
                break
        # if a pattern doesn't appear in positive patterns
        else:
            value = negative_threshold/negative_threshold
            pattern_with_conf.append((value, negative_threshold, negative_pattern))
    return pattern_with_conf

def patternsToCSV(patterns, filename = "patterns.csv"):
    df = pd.DataFrame(patterns)
    df.to_csv(filename, index = False, header = ["confidence", "support", "pattern"])

# 
def getEvents(events, states, value_from, value_to):
    states_by_day = states.groupby("date")
    subsequences = subsequencesInStates(states_by_day, value_from, value_to)
    timeRanges = timeRangesOfSubsequences(subsequences)
    finalEvents = eventsOfTimeRanges(events, timeRanges)
    return finalEvents

def getStatesSubsequences(direction, states):
    subsequences_by_user = []
    states_by_user = states.groupby("user")
    for user, group in states_by_user:   # user is a user we group by, group is dataframe of measurements in that group
        group.reset_index(drop=True, inplace=True)
        subsequences_by_user.append((getStatesSubsequencesOfUser(direction, group), user))
    return subsequences_by_user

def getStatesSubsequencesOfUser(direction, states):
    subsequences = []
    sequence = []
    for idx, measurement in states.iterrows(): # idx is an index of iterator, measurement is a row in our user states
        if(idx == 0 or 
            (direction == "up" and states.iloc[idx-1]["value"] <= measurement["value"]) or  # when dir is up
            (direction == "down" and states.iloc[idx-1]["value"] >= measurement["value"])): # when dir is down
            sequence.append(measurement.copy())
        else:
            subsequences.append(sequence.copy())
            sequence.clear()
            sequence.append(measurement.copy())
    return subsequences


def main(direction):

    events, states = prepareDataDiabetes()

    statesSubsequences = getStatesSubsequences(direction, states)
    # statesSubsequences[user from list][sequences of user from tuple == 0][pattern from list]
    print(statesSubsequences[0][0][0])

    # positiveEvents = getEvents(events, states, value_from, value_to)
    # print(positiveEvents)
    # positivePatterns = minePatterns(positiveEvents, 100)
    # print(positivePatterns)

    # negativeEvents = getEvents(events, states, value_to, value_from)
    # negativePatterns = minePatterns(negativeEvents, 100)
    # print(negativePatterns)


    # # mine positive patterns
    # print("Getting events low to normal...")
    # eventsLowToNormal = getEventsLowToNormal(events, states)
    # print("Mining low to normal...")
    # patterns_positive = minePatterns(eventsLowToNormal, 100)

    # # mine negative patterns
    # print("Getting events normal to low...")
    # eventsNormalToLow = getEventsNormalToLow(events, states)
    # print("Mining normal to low...")
    # patterns_negative = minePatterns(eventsNormalToLow, 100)

    # # add confidence measure to patterns
    # print("Adding positive confidence...")
    # positive_with_conf = addConfidenceOfPositivePatterns(patterns_positive, patterns_negative)
    # print("Adding negative confidence...")
    # negative_with_conf = addConfidenceOfPositivePatterns(patterns_negative, patterns_positive)

    # # print patterns as codes
    # print("\nPositive patterns: conf supp pattern\n", positive_with_conf)
    # print("\nNegative patterns: conf supp pattern\n", negative_with_conf)

    # print("Describing patterns...")
    # patterns_positive_described = describePatterns(positive_with_conf)
    # patterns_negative_described = describePatterns(negative_with_conf)
    # # print patterns as text
    # print("\nPositive patterns: conf supp pattern\n", patterns_positive_described)
    # print("\nNegative patterns: conf supp pattern\n", patterns_negative_described)

    # patternsToCSV(patterns_positive_described, "positive_patterns.csv")
    # patternsToCSV(patterns_negative_described, "negative_patterns.csv")

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print("Please provide required parameters.")
        sys.exit()
    direction = sys.argv[1]
    main(direction)