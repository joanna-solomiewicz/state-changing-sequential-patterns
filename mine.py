import sys
from prefixspan import PrefixSpan
from diabetes import prepareDataDiabetes, eventsDictionary

def minePatterns(sequences, threshold):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(threshold)
    return patterns

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

def getEventsSubsequences(stateSubsequences, events):
    eventsSubsequences = []
    for stateSubsequencesOfUser, user in stateSubsequences:
        userEventsSubsequences = []
        userEvents = events[events.user == user]
        userEvents.reset_index(drop=True, inplace=True)
        for stateSubsequenceOfUser in stateSubsequencesOfUser:
            minTimestamp = stateSubsequenceOfUser[0]["date_time"]
            maxTimestamp = stateSubsequenceOfUser[-1]["date_time"]
            difference = stateSubsequenceOfUser[-1]["value"] - stateSubsequenceOfUser[0]["value"]
            subEvents = userEvents[(userEvents.date_time >= minTimestamp) & (userEvents.date_time <= maxTimestamp)].copy()
            subEvents["difference"] = difference
            userEventsSubsequences.append(subEvents["code"].tolist())
        eventsSubsequences.append(userEventsSubsequences)

    return eventsSubsequences


def main(direction):

    events, states = prepareDataDiabetes()

    statesSubsequences = getStatesSubsequences(direction, states)
    # statesSubsequences[user from list][sequences of user from tuple == 0][subsequence from list]
    # print(statesSubsequences[0][0][0])

    eventsSubsequences = getEventsSubsequences(statesSubsequences, events)
    print(minePatterns(eventsSubsequences[0], 50))
    print(minePatterns(eventsSubsequences[1], 50))

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print("Please provide required parameters.")
        sys.exit()
    direction = sys.argv[1]
    main(direction)