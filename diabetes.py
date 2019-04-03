import pandas as pd

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
    diabetes1 = pd.read_csv("data/diabetes/data-01", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates=[["date", "time"]])
    diabetes2 = pd.read_csv("data/diabetes/data-02", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates=[["date", "time"]])
    diabetes1 = diabetes1.sort_values(by = ["date_time"], ascending = True)
    diabetes2 = diabetes2.sort_values(by = ["date_time"], ascending = True)
    diabetes1["user"] = 1
    diabetes2["user"] = 2
    diabetes = pd.concat([diabetes1, diabetes2])
    events, states = splitEventsStatesDiabetes(diabetes)
    events = events.drop(columns="value")
    states = states.drop(columns="code")
    return events, states

def splitEventsStatesDiabetes(dataframe):
    code_mask = (dataframe["code"] >= 48) & (dataframe["code"] <= 64)
    events = dataframe[~code_mask]
    events.reset_index(drop=True, inplace=True)
    states = dataframe[code_mask]
    states.reset_index(drop=True, inplace=True)
    return events, states 