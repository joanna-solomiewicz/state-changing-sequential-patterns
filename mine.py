import sys
from prefixspan import PrefixSpan
from diabetes import prepareDataDiabetes, eventsDictionary
import numpy as np
import time
from datetime import date
from os import path

def minePatterns(sequences, threshold, ifclosed):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(threshold, closed = ifclosed)
    return patterns

# get monotonic subsequences - increasing or decreasing
def getStatesSubsequences(direction, states):
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
def addScoreToPatterns(patterns, userEventsSubsequences):
    patterns_w_score = []
    for pattern in patterns:
        score = 0.0
        # for every pattern check in how many sequences it appears and add all differences as score measure
        for subsequence in userEventsSubsequences:
            # if subsequence["code"].tolist() == pattern[1]: #only checks if pattern == subsequence, not if pattern in subsequence
            # if (all([checkIfElementInList(elem, subsequence["code"].tolist()) for elem in pattern[1]]) and ):
            if (checkIfPatternElementsInSequence(pattern[1], subsequence["code"].tolist()) and checkIfPatternElementsInSequenceInOrder(pattern[1], subsequence["code"].tolist())):
                score = score + subsequence.iloc[0]["difference"]
        pattern = pattern + (score,)
        patterns_w_score.append(pattern)
    return patterns_w_score


def main(direction, bide, filepath):

    # prepare raw data in expected format
    # states has date_time, value
    # events has data_time, code
    events, states = prepareDataDiabetes(filepath)

    # statesSubsequences [[seq],[seq],[seq]]
    statesSubsequences = getStatesSubsequences(direction, states)

    # eventsSubsequences[dataframe of eventsSubsequence]    subsequences of events
    # eventsCodesSubsequences[event codes subsequence]      only codes from subsequences of events
    eventsSubsequences, eventsCodesSubsequences = getEventsSubsequences(statesSubsequences, events)
    # start = time.time()
    patterns = minePatterns(eventsCodesSubsequences, 10, bide)
    # end = time.time()
    # print("Optimized: ", end-start)

    patternsScore = addScoreToPatterns(patterns, eventsSubsequences)
    print(patternsScore)

    # events["date"] = np.nan
    # events["date"] = events.apply(lambda row: row["date_time"].date(), axis = 1)

    # events_sequences = []
    # events_by_day = events.groupby("date")
    # for day, group in events_by_day: 
    #     group.reset_index(drop=True, inplace=True)
    #     events_in_day = group["code"].tolist()
    #     events_sequences.append(events_in_day)

    # start = time.time()
    # patternsUser1_1 = minePatterns(events_sequences, 20, bide)
    # end = time.time()
    # print("Not optimized: ", end-start)

    # print(patternsUser1_1)

def inputHandling(argv):
    if len(argv) < 3:
        print("Please provide required parameters.")
        sys.exit()
    if argv[1] not in ["up", "down"]:
        print("Bad direction argument. Use \"up\" or \"down\".")
        sys.exit()
    if argv[2] not in ["true", "false", 1, 0]:
        print("Bad BIDE argument. Use \"true\" or 1, or \"false\" or 0.")
        sys.exit()
    if not path.exists(argv[3]) or not path.isfile(argv[3]):
        print("Data path does not exist or is not a file.")
        sys.exit()

if __name__ == "__main__": 
    inputHandling(sys.argv)
    direction = sys.argv[1]
    bide = sys.argv[2]
    filepath = sys.argv[3]
    main(direction, bide, filepath)