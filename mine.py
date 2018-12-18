import pandas as pd
from enum import Enum

class glucose(Enum):
    low = 0
    normal = 1
    high = 2

def discretizeGlucose(dataframe):
    high_mask = dataframe["value"] > 200
    normal_mask = (dataframe["value"] <= 200) & (dataframe["value"] >= 80)
    low_mask = dataframe["value"] < 80
    dataframe.loc[high_mask, "value"] = glucose.high
    dataframe.loc[normal_mask, "value"] = glucose.normal
    dataframe.loc[low_mask, "value"] = glucose.low
    return dataframe

def splitEventsStates(dataframe):
    code_mask = (dataframe["code"] >= 48) & (dataframe["code"] <= 64)
    events = dataframe[code_mask]
    states = dataframe[~code_mask]
    return events, states 

def main():
    diabetes = pd.read_csv("data/diabetes/data-01", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates=["date", "time"])
    diabetes["time"] = diabetes["time"].apply(lambda x: x.strftime("%H:%M:%S"))
    diabetes = diabetes.sort_values(by = ["date", "time"], ascending = True)
    diabetes = discretizeGlucose(diabetes)
    events, states = splitEventsStates(diabetes)
    states_by_day = states.groupby("date")
    for _, group in states_by_day:
        print(group)

if __name__ == "__main__":
    main()