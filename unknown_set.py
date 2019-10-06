import pandas as pd

def prepareDataUnknownSet(user):
    unknownset = readData(user)
    events, states = splitEventsStatesUnknownSet(unknownset)
    return events, states

def readData(user):
    return pd.DataFrame(readCSV(user))

def readCSV(user):
    unknownset = pd.read_csv("./data/events.csv", sep=",", parse_dates=[["Date", "Time"]])
    if user != -1:
        unknownset = unknownset[unknownset.UserId == user]
    unknownset = unknownset.sort_values(by = ["Date_Time"], ascending = True)
    unknownset.reset_index(drop=True, inplace=True)
    unknownset = unknownset.drop(columns = ["UserId"])
    unknownset = unknownset.rename(columns={"Date_Time": "date_time", "Event": "code", "Action": "value"})
    return unknownset
    
def splitEventsStatesUnknownSet(dataframe):
    events = dataframe.loc[:,["date_time", "code"]]
    states = dataframe.loc[:,["date_time", "value"]]
    return events, states 
