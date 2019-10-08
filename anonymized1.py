import pandas as pd

def prepareDataAnonymizedSet1(user):
    anonymizedset = readData(user)
    events, states = splitEventsStatesAnonymizedSet1(anonymizedset)
    return events, states

def readData(user):
    return pd.DataFrame(readCSV(user))

def readCSV(user):
    anonymizedset = pd.read_csv("./data/events.csv", sep=",", parse_dates=[["Date", "Time"]])
    if user != -1:
        anonymizedset = anonymizedset[anonymizedset.UserId == user]
    anonymizedset = anonymizedset.sort_values(by = ["Date_Time"], ascending = True)
    anonymizedset.reset_index(drop=True, inplace=True)
    anonymizedset = anonymizedset.drop(columns = ["UserId"])
    anonymizedset = anonymizedset.rename(columns={"Date_Time": "date_time", "Event": "code", "Action": "value"})
    return anonymizedset
    
def splitEventsStatesAnonymizedSet1(dataframe):
    events = dataframe.loc[:,["date_time", "code"]]
    states = dataframe.loc[:,["date_time", "value"]]
    return events, states 
