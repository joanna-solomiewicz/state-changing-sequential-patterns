import pandas as pd

eventsDictionary = {
    "link":     1,
    "photo":    2,
    "status":   3,
    "video":    4
}

def prepareDataPosts(filepath):
    posts = readData(filepath)
    events, states = splitEventsStatesPosts(posts)
    return events, states

def readData(filepath):
    return pd.DataFrame(readCSV(filepath))

def readCSV(filename):
    posts = pd.read_csv(filename, sep=",", parse_dates=["status_published"], dayfirst=False)
    posts = posts.sort_values(by = ["status_published"], ascending = True)
    posts.reset_index(drop=True, inplace=True)
    reaction = [sum(entry[5:9]) - sum(entry[10:12]) for _, entry in posts.iterrows()]
    mapping = [eventsDictionary.get(entry.loc["status_type"]) for _, entry in posts.iterrows()]
    posts.insert(3, "reaction", reaction)
    posts.insert(3, "event_mapping", mapping)
    posts = posts.drop(columns = ["status_id","status_type","num_reactions","num_comments","num_shares","num_likes","num_loves","num_wows","num_hahas","num_sads","num_angrys","Column1","Column2","Column3","Column4"])
    posts = posts.rename(columns={"status_published": "date_time", "event_mapping": "code", "reaction": "value"})
    return posts
    
def splitEventsStatesPosts(dataframe):
    events = dataframe.loc[:,["date_time", "code"]]
    states = dataframe.loc[:,["date_time", "value"]]
    return events, states 