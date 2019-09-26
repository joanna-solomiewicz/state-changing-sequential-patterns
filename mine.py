import sys
from prefixspan import PrefixSpan
from diabetes import prepareDataDiabetes, eventsDictionary
import numpy as np
import time
from datetime import date

def minePatterns(sequences, threshold, ifclosed):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(threshold, closed = ifclosed)
    return patterns

# get monotonic subsequences of every user - increasing or decreasing
def getStatesSubsequences(direction, states):
    subsequences_by_user = []
    states_by_user = states.groupby("user")
    for user, group in states_by_user:   # user is a user we group by, group is dataframe of measurements in that group
        group.reset_index(drop=True, inplace=True)
        subsequences_by_user.append((getStatesSubsequencesOfUser(direction, group), user))
    return subsequences_by_user

# get monotonic subsequences of user - increasing or decreasing
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

# get event subsequences of every user during state subsequences change timeframe
def getEventsSubsequences(stateSubsequences, events):
    eventsSubsequences = []
    eventsCodesSubsequences = []
    for stateSubsequencesOfUser, user in stateSubsequences:
        userEventsSubsequences = []
        userEventsCodesSubsequences = []
        userEvents = events[events.user == user]
        userEvents.reset_index(drop=True, inplace=True)
        for stateSubsequenceOfUser in stateSubsequencesOfUser:
            minTimestamp = stateSubsequenceOfUser[0]["date_time"]
            maxTimestamp = stateSubsequenceOfUser[-1]["date_time"]
            difference = stateSubsequenceOfUser[-1]["value"] - stateSubsequenceOfUser[0]["value"]
            subEvents = userEvents[(userEvents.date_time >= minTimestamp) & (userEvents.date_time <= maxTimestamp)].copy()
            if(len(subEvents) == 0 or difference == 0):  # only consider subsequences that have a change
                continue
            subEvents["difference"] = difference
            userEventsSubsequences.append(subEvents)
            userEventsCodesSubsequences.append(subEvents["code"].tolist())
        eventsSubsequences.append(userEventsSubsequences)
        eventsCodesSubsequences.append(userEventsCodesSubsequences)

    return eventsSubsequences, eventsCodesSubsequences

# def checkIfElementInList(element, list):
#     try:
#         list.index(element)
#         return True
#     except ValueError:
#         return False

def getElementIndex(element, list):
    try:
        return list.index(element)
    except ValueError:
        return -1

# def checkIfAllElementsPositive(list):
#     return all([getElementIndex(elem, list) for elem in list])

# check if all pattern elements are in sequence
def checkIfPatternElementsInSequence(pattern, sequence):
    return all([True if elem > 0 else False for elem in [getElementIndex(elem, sequence) for elem in pattern]])

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
                # print("Indexes:\t", elementIndexInSequence, " > ", nextElementIndexInSequence)
                # print("Pattern:\t", pattern)
                # print("Sequence:\t", sequence)
                return False
    return True

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


def main(direction, bide):

    # prepare raw data in expected format
    # states has date_time, value, user
    # events has data_time, code, user
    events, states = prepareDataDiabetes()

    # statesSubsequences[user from list][sequences of user from tuple == 0 ([[seq],[seq],[seq]], user)][subsequence from list]
    statesSubsequences = getStatesSubsequences(direction, states)

    # eventsSubsequences[user from list][dataframe of eventsSubsequence]    subsequences of events
    # eventsCodesSubsequences[user from list][event codes subsequence]      only codes from subsequences of events
    eventsSubsequences, eventsCodesSubsequences = getEventsSubsequences(statesSubsequences, events)
    # print(eventsSubsequences[0])
    # print(eventsCodesSubsequences[0])
    # start = time.time()
    patternsUser1 = minePatterns(eventsCodesSubsequences[0], 10, bide)
    # end = time.time()
    # print("Optimized: ", end-start)

    patternsUser1Score = addScoreToPatterns(patternsUser1, eventsSubsequences[0])
    print(patternsUser1Score)

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

if __name__ == "__main__": 
    inputHandling(sys.argv)
    direction = sys.argv[1]
    bide = sys.argv[2]
    main(direction, bide)