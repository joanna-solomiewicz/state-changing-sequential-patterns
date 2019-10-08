import pandas as pd

statesDictionary = {
    "A":    1,
    "B":    2,
    "C":    3
}

def prepareDataAnonymizedSet2(user):
    anonymizedset = readData(user)
    events, states = splitEventsStatesAnonymizedSet2(anonymizedset)
    return events, states

def readData(user):
    return pd.DataFrame(readCSV(user))

def readCSV(user):
    anonymizedset = pd.read_csv("./data/classes.csv", sep=",", parse_dates=["Date"])
    if user != -1:
        anonymizedset = anonymizedset[anonymizedset.UserId == user]
    anonymizedset = anonymizedset.sort_values(by = ["Date"], ascending = True)
    anonymizedset.reset_index(drop=True, inplace=True)
    mapping = [statesDictionary.get(entry.loc["Class"]) for _, entry in anonymizedset.iterrows()]
    anonymizedset.insert(3, "state_mapping", mapping)
    anonymizedset = anonymizedset.drop(columns = ["UserId", "Class"])
    anonymizedset = anonymizedset.rename(columns={"Date": "date_time", "Product": "code", "state_mapping": "value"})
    return anonymizedset
    
def splitEventsStatesAnonymizedSet2(dataframe):
    events = dataframe.loc[:,["date_time", "code"]]
    states = dataframe.loc[:,["date_time", "value"]]
    return events, states 
