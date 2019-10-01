from validations import parseArguments
from prefixspan import PrefixSpan
from diabetes import prepareDataDiabetes, eventsDictionary
import numpy as np
from time import time
from datetime import date
import pandas as pd

def minePatterns(sequences, threshold, ifclosed):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(threshold, closed = ifclosed)
    return patterns

def groupDataFrameByDate(df):
    df["date"] = np.nan
    df["date"] = df.apply(lambda row: row["date_time"].date(), axis = 1)
    df_by_date = df.groupby("date")
    return df_by_date

# get monotonic subsequences - increasing or decreasing
def getStatesSubsequences(direction, states):
    subsequences = []
    sequence = []

    # grouping sequential database into sequences by date
    states_by_date = groupDataFrameByDate(states)

    for _, group in states_by_date:   # _ is a date we group by, group is dataframe of measurements in that group (single sequence)
        group.reset_index(drop=True, inplace=True)
        for idx, measurement in group.iterrows(): # idx is an index of iterator, measurement is a row in our states sequence
            if(idx == 0 or 
                (direction == "up" and states.iloc[idx-1]["value"] <= measurement["value"]) or  # when dir is up
                (direction == "down" and states.iloc[idx-1]["value"] >= measurement["value"])): # when dir is down
                sequence.append(measurement.copy())
            else:
                subsequences.append(sequence.copy())
                sequence.clear()
                sequence.append(measurement.copy())
        subsequences.append(sequence.copy())
        sequence.clear()
    return subsequences

# get event subsequences during state subsequences change timeframe
def getEventsSubsequences(stateSubsequences, events):
    eventsSubsequences = []
    eventsCodesSubsequences = []
    for stateSubsequence in stateSubsequences:
        minTimestamp = stateSubsequence[0]["date_time"]
        maxTimestamp = stateSubsequence[-1]["date_time"]
        difference = stateSubsequence[-1]["value"] - stateSubsequence[0]["value"]
        subEvents = events[(events.date_time >= minTimestamp) & (events.date_time <= maxTimestamp)].copy()
        if(len(subEvents) == 0 or difference == 0):  # only consider subsequences that have a change
            continue
        subEvents["difference"] = difference
        eventsSubsequences.append(subEvents)
        eventsCodesSubsequences.append(subEvents["code"].tolist())

    return eventsSubsequences, eventsCodesSubsequences

def getElementIndex(element, list):
    try:
        return list.index(element)
    except ValueError:
        return -1

# check if all pattern elements are in sequence
def checkIfPatternElementsInSequence(pattern, sequence):
    return all([True if elem >= 0 else False for elem in [getElementIndex(elem, sequence) for elem in pattern]])

# check if all pattern elements are in correct order in sequence
def checkIfPatternElementsInSequenceInOrder(pattern, sequence):
    sequence_copy = sequence.copy()
    for index, _ in enumerate(pattern):
        if len(pattern) == 1:
            elementIndexInSequence = getElementIndex(pattern[index], sequence_copy)
            if elementIndexInSequence < 0:
                return False
        if index < len(pattern) - 1:
            elementIndexInSequence = getElementIndex(pattern[index], sequence_copy)
            sequence_copy = sequence_copy[elementIndexInSequence+1:]
            nextElementIndexInSequence = getElementIndex(pattern[index+1], sequence_copy)
            if elementIndexInSequence < 0 or nextElementIndexInSequence < 0:
                return False
    return True

# add a score measure to patterns - score is a sum of state differences in sequences where a pattern occurs
def addMeasuresToPatterns(patterns, eventsSubsequences, events):
    # grouping sequential database into sequences by date
    events_by_date = groupDataFrameByDate(events)

    allSequencesCount = len(events_by_date)
    patternsWithMeasures = []

    for pattern in patterns:
        score = 0.0
        occurInAll = 0
        # for every pattern check in how many state changing sequences it appears and sum all differences as score measure
        for subsequence in eventsSubsequences:
            if (checkIfPatternElementsInSequence(pattern[1], subsequence["code"].tolist()) and checkIfPatternElementsInSequenceInOrder(pattern[1], subsequence["code"].tolist())):
                score = score + subsequence.iloc[0]["difference"]
        # for every pattern check in how many sequences it appears
        for _, sequence in events_by_date:
            sequence.reset_index(drop=True, inplace=True)
            if (checkIfPatternElementsInSequence(pattern[1], sequence["code"].tolist()) and checkIfPatternElementsInSequenceInOrder(pattern[1], sequence["code"].tolist())):
                occurInAll = occurInAll + 1
        
        # calculate the measures
        occurInChange = pattern[0]
        support = occurInChange / allSequencesCount
        confidence = occurInChange / occurInAll
        pattern = pattern + (score, support, confidence, )
        patternsWithMeasures.append(pattern)

    return patternsWithMeasures

def dataMining(events, states, direction, threshold, bide):
    # statesSubsequences [[seq],[seq],[seq]]
    statesSubsequences = getStatesSubsequences(direction, states)

    # eventsSubsequences[dataframe of eventsSubsequence]    subsequences of events
    # eventsCodesSubsequences[event codes subsequence]      only codes from subsequences of events
    eventsSubsequences, eventsCodesSubsequences = getEventsSubsequences(statesSubsequences, events)
    # start = time()
    patterns = minePatterns(eventsCodesSubsequences, threshold, bide)
    # end = time()
    # print("Optimized: ", end-start)

    # result is list of tuples (numberOfOccurencesOfPatternInChangeEvents, pattern, score, support, confidence)
    patternsScore = addMeasuresToPatterns(patterns, eventsSubsequences, events)
    print(patternsScore)
    return patternsScore

def getOppositeDirection(direction):
    directions = ["up", "down"]
    directions.remove(direction)
    return directions[0]

def patternsToCSV(patterns, filename = "patterns.csv"):
    df = pd.DataFrame(patterns)
    df.to_csv(filename, index = False, header = ["occurencesInChangeEvents", "pattern", "score", "support", "confidence"])

def main(filepath, direction, threshold, bide):

    # prepare raw data in expected format
    # states has date_time, value
    # events has data_time, code
    events, states = prepareDataDiabetes(filepath)

    patternsScore = dataMining(events, states, direction, threshold, bide)
    patternsToCSV(patternsScore, "patterns.csv")
    patternsScoreOpposite = dataMining(events, states, getOppositeDirection(direction), threshold, bide)
    patternsToCSV(patternsScoreOpposite, "patterns_opposite.csv")

    # events_sequences = []
    # for day, group in events_by_day: 
    #     group.reset_index(drop=True, inplace=True)
    #     events_in_day = group["code"].tolist()
    #     events_sequences.append(events_in_day)

    # start = time()
    # patternsUser1_1 = minePatterns(events_sequences, 20, bide)
    # end = time()
    # print("Not optimized: ", end-start)

    # print(patternsUser1_1)

if __name__ == "__main__": 
    args = parseArguments()
    main(args.filepath, args.direction, args.threshold, args.bide)
