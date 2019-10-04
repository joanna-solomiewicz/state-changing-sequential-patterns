import pandas as pd

def prepareDataUnknownSet(filepath):
    unknownset = readData(filepath)
    events, states = splitEventsStatesUnknownSet(unknownset)
    return events, states

def readData(filepath):
    return pd.DataFrame(readCSV(filepath))

def readCSV(filename):
    unknownset = pd.read_csv(filename, sep=",", parse_dates=[["Date", "Time"]], dayfirst=False)
    unknownset = unknownset.sort_values(by = ["Date_Time"], ascending = True)
    unknownset.reset_index(drop=True, inplace=True)
    unknownset = unknownset.drop(columns = ["UserId"])
    unknownset = unknownset.rename(columns={"Date_Time": "date_time", "Event": "code", "Action": "value"})
    return unknownset
    
def splitEventsStatesUnknownSet(dataframe):
    events = dataframe.loc[:,["date_time", "code"]]
    states = dataframe.loc[:,["date_time", "value"]]
    return events, states 
