import pandas as pd

statesDictionary = {
    "A":    1,
    "B":    2,
    "C":    3
}

def prepareDataUnknownSet2(filepath):
    unknownset = readData(filepath)
    events, states = splitEventsStatesUnknownSet2(unknownset)
    return events, states

def readData(filepath):
    return pd.DataFrame(readCSV(filepath))

def readCSV(filename):
    unknownset = pd.read_csv(filename, sep=",", parse_dates=["Date"], dayfirst=False)
    unknownset = unknownset.sort_values(by = ["Date"], ascending = True)
    unknownset.reset_index(drop=True, inplace=True)
    mapping = [statesDictionary.get(entry.loc["Class"]) for _, entry in unknownset.iterrows()]
    unknownset.insert(3, "state_mapping", mapping)
    unknownset = unknownset.drop(columns = ["UserId", "Class"])
    unknownset = unknownset.rename(columns={"Date": "date_time", "Product": "code", "state_mapping": "value"})
    return unknownset
    
def splitEventsStatesUnknownSet2(dataframe):
    events = dataframe.loc[:,["date_time", "code"]]
    states = dataframe.loc[:,["date_time", "value"]]
    return events, states 
