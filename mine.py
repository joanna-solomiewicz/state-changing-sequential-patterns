import pandas as pd

def main():
    diabetes = pd.read_csv("data/diabetes/data-01", sep="\t", header = None, names=["date", "time", "code", "value"], parse_dates={"datetime": ["date", "time"]})
    diabetes = diabetes.sort_values(by = ["datetime"], ascending = True)
    code_mask = (diabetes["code"] >= 48) & (diabetes["code"] <= 64)
    events = diabetes[code_mask]
    states = diabetes[~code_mask]

if __name__ == "__main__":
    main()