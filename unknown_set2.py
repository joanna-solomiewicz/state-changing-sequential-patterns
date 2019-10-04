import pandas as pd

statesDictionary = {
    "A":    1,
    "B":    2,
    "C":    3
}

def prepareDataUnknownSet2(user):
    unknownset = readData(user)
    events, states = splitEventsStatesUnknownSet2(unknownset)
    return events, states

def readData(user):
    return pd.DataFrame(readCSV(user))

def readCSV(user):
    unknownset = pd.read_csv("./data/classes.csv", sep=",", parse_dates=["Date"], dayfirst=False)
    if user != -1:
        unknownset = unknownset[unknownset.UserId == user]
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
