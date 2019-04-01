import pandas as pd
from additional_types import value 

eventsDictionary = {
    33: "Regular insulin dose",
    34: "NPH insulin dose",
    35: "UltraLente insulin dose",
    48: "Unspecified blood glucose measurement",
    57: "Unspecified blood glucose measurement",
    58: "Pre-breakfast blood glucose measurement",
    59: "Post-breakfast blood glucose measurement",
    60: "Pre-lunch blood glucose measurement",
    61: "Post-lunch blood glucose measurement",
    62: "Pre-supper blood glucose measurement",
    63: "Post-supper blood glucose measurement",
    64: "Pre-snack blood glucose measurement",
    65: "Hypoglycemic symptoms",
    66: "Typical meal ingestion",
    67: "More-than-usual meal ingestion",
    68: "Less-than-usual meal ingestion",
    69: "Typical exercise activity",
    70: "More-than-usual exercise activity",
    71: "Less-than-usual exercise activity",
    72: "Unspecified special event"
}

def prepareDataDiabetes():
    diabetes = pd.read_csv("data/diabetes_merged.csv", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates=["date", "time"])
    diabetes["time"] = diabetes["time"].apply(lambda x: x.time())
    diabetes["date"] = diabetes["date"].apply(lambda x: x.date())
    diabetes = diabetes.sort_values(by = ["date", "time"], ascending = True)
    # diabetes = discretizeGlucose(diabetes)
    events, states = splitEventsStatesDiabetes(diabetes)
    return events, states

# TO BE DELETED
def discretizeGlucose(dataframe):
    dataframe["discret_val"] = ""
    high_mask = dataframe["value"] > 200
    normal_mask = (dataframe["value"] <= 200) & (dataframe["value"] >= 80)
    low_mask = dataframe["value"] < 80
    dataframe.loc[high_mask, "discret_val"] = value.high.value
    dataframe.loc[normal_mask, "discret_val"] = value.normal.value
    dataframe.loc[low_mask, "discret_val"] = value.low.value
    return dataframe

def splitEventsStatesDiabetes(dataframe):
    code_mask = (dataframe["code"] >= 48) & (dataframe["code"] <= 64)
    events = dataframe[~code_mask]
    states = dataframe[code_mask]
    return events, states 