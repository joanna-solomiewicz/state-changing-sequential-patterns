import sys
from prefixspan import PrefixSpan
from diabetes import prepareDataDiabetes, eventsDictionary

def minePatterns(sequences, threshold):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(threshold)
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


def main(direction):

    # prepare raw data in expected format
    # states has date_time, value, user
    # events has data_time, code, user
    events, states = prepareDataDiabetes()

    # statesSubsequences[user from list][sequences of user from tuple == 0 ([[seq],[seq],[seq]], user)][subsequence from list]
    statesSubsequences = getStatesSubsequences(direction, states)

    # eventsSubsequences[user from list][dataframe of eventsSubsequence]    subsequences of events
    # eventsCodesSubsequences[user from list][event codes subsequence]      only codes from subsequences of events
    eventsSubsequences, eventsCodesSubsequences = getEventsSubsequences(statesSubsequences, events)
    patternsUser1 = minePatterns(eventsCodesSubsequences[0], 20)
    print(patternsUser1)

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print("Please provide required parameters.")
        sys.exit()
    direction = sys.argv[1]
    main(direction)