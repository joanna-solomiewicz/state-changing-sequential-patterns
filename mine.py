from validations import parseArguments
from prefixspan import PrefixSpan
from diabetes import prepareDataDiabetes, eventsDictionary
from posts import prepareDataPosts
from anonymized1 import prepareDataAnonymizedSet1
from anonymized2 import prepareDataAnonymizedSet2
import numpy as np
from time import time
from datetime import date
import pandas as pd
import datetime

def minePatterns(sequences, threshold, minlen, ifclosed):
    ps = PrefixSpan(sequences)
    ps.minlen = minlen
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
                if(len(sequence) > 1): subsequences.append(sequence.copy())
                sequence.clear()
                sequence.append(measurement.copy())
        if(len(sequence) > 1): subsequences.append(sequence.copy())
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
            sequence = sequence["code"].tolist()
            while (checkIfPatternElementsInSequence(pattern[1], sequence) and checkIfPatternElementsInSequenceInOrder(pattern[1], sequence)):
                occurInAll = occurInAll + 1
                if(len(pattern[1]) <= len(sequence) and getElementIndex(pattern[1][-1], sequence) > -1):
                    sequence = sequence[getElementIndex(pattern[1][-1], sequence)+1:]
                    if(len(sequence) < len(pattern[1])): 
                        break
        
        # calculate the measures
        occurInChange = pattern[0]
        support = occurInChange / allSequencesCount
        supportAll = occurInAll / allSequencesCount
        confidence = support / supportAll
        pattern = pattern + (score, support, confidence, )
        patternsWithMeasures.append(pattern)

    return patternsWithMeasures

def dataMining(events, states, direction, threshold, minlen, bide):
    # statesSubsequences [[seq],[seq],[seq]]
    statesSubsequences = getStatesSubsequences(direction, states)
    print("States subsequences done\t", datetime.datetime.now())

    # eventsSubsequences[dataframe of eventsSubsequence]    subsequences of events
    # eventsCodesSubsequences[event codes subsequence]      only codes from subsequences of events
    eventsSubsequences, eventsCodesSubsequences = getEventsSubsequences(statesSubsequences, events)
    print("Event subsequences done\t\t", datetime.datetime.now())
    patterns = minePatterns(eventsCodesSubsequences, threshold, minlen, bide)
    print("Patterns done\t\t\t", datetime.datetime.now())

    # result is list of tuples (numberOfOccurencesOfPatternInChangeEvents, pattern, score, support, confidence)
    patternsMeasures = addMeasuresToPatterns(patterns, eventsSubsequences, events)
    print("Measures done\t\t\t", datetime.datetime.now())
    return patternsMeasures

def getOppositeDirection(direction):
    directions = ["up", "down"]
    directions.remove(direction)
    return directions[0]

def patternsToCSV(patterns, filename = "patterns.csv"):
    df = pd.DataFrame(patterns)
    if df.empty:
        print("No patterns found.")
    else:
        df.to_csv(filename, index = False, header = ["allOccurences", "pattern", "score", "support", "confidence"])

def updatePatternsByOppositeResults(patterns, patternsOpposite):
    patternsUpdatedScore = []
    for pattern in patterns:
        oppositeExists = False
        for patternOpposite in patternsOpposite:
            if(pattern[1] == patternOpposite[1]):
                pattern = list(pattern)
                pattern[2] = (pattern[2] + patternOpposite[2]) / (pattern[0] + patternOpposite[0])
                pattern[0] = pattern[0] + patternOpposite[0]
                pattern = tuple(pattern)
                oppositeExists = True
                break
        if not oppositeExists:
            pattern = list(pattern)
            pattern[2] = pattern[2] / pattern[0]
            pattern = tuple(pattern)

        patternsUpdatedScore.append(pattern)
    return patternsUpdatedScore
    

def main(file, direction, threshold, minlen, user, bide):
    print("Start\t\t\t\t", datetime.datetime.now())

    # prepare raw data in expected format
    # states has date_time, value
    # events has data_time, code
    if (file == 'diabetes'): events, states = prepareDataDiabetes(user)
    elif (file == 'posts'): events, states = prepareDataPosts()
    elif (file == 'anonymized1'): events, states = prepareDataAnonymizedSet1(user)
    elif (file == 'anonymized2'): events, states = prepareDataAnonymizedSet2(user)
    print("Preparing done\t\t\t", datetime.datetime.now())

    patterns = dataMining(events, states, direction, threshold, minlen, bide)
    print("Pattern mining done\t\t", datetime.datetime.now())
    patternsOpposite = dataMining(events, states, getOppositeDirection(direction), threshold, minlen, bide)
    print("Opposite pattern mining done\t", datetime.datetime.now())
    patternsUpdatedScore = updatePatternsByOppositeResults(patterns, patternsOpposite)
    print("Updates pattens done\t\t", datetime.datetime.now())

    patternsToCSV(patternsUpdatedScore, "patterns.csv")
    print("Done\t\t\t\t", datetime.datetime.now())

    # events_sequences = [group["code"].tolist() for _, group in groupDataFrameByDate(events)]
    # patterns = minePatterns(events_sequences, threshold, minlen, bide)
    # print(patterns)
    # print("Done\t\t\t\t", datetime.datetime.now())

if __name__ == "__main__": 
    args = parseArguments()
    main(args.file, args.direction, args.threshold, args.minlen, args.user, args.bide)
