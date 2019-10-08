# State-changing event sequential patterns
This project implements a solution for finding event sequential patterns which have a desired effect on object's state. So far four data sets have been implemented. Diabetes database, which describes treatment of 70 patients diagnosed with diabetes, posts database which represents te marketing campaign of online retail sellers and also two anonymized datasets of events and classes.

# Getting started
This is what you need to run this project.

## Prerequisites
* Python version 3.7.1 or higher
* pip package installer

Make sure you installed the correct version (and have it in your PATH environment variable):
```
python --version
pip --version
```

## Installing
After making sure you have the specified python version, install these libraries:
```
pip install pandas
pip install numpy
pip install prefixspan
```

## Running the project
The project requires 2 parameters - data set name and direction.
There are also 4 optional parameters - threshold, minimum pattern length, user, BIDE.

There are four data sets implemented. Their names are *diabetes*, *posts*, *anonymized1* and *anonymized2*.

Direction specifies which state changes are examined, increasing or decreasing. They should be provided as *up* or *down*.

Threshold refers to minimum number of occurences of pattern to be considered frequent.

Minumum pattern length is the minimum number of elements a pattern has to have.

By default the entire data set is processed. By providing the user id it can be narrowed down to only that user's history.

BIDE parameter states whether to use BIDE algorithm instead of PrefixSpan. It should be given as *true* or *1* for using BIDE, or *false* or *0* for using PrefixSpan.

To run the project go to the project folder and type:
```
python mine.py <dataset> <direction> -t <threshold> -m <min_length> -u <user> -b <BIDE>
```
Example:
```
python mine.py diabetes up -t 30 -m 2 -u 1 -b true
```


## Result
As a result, the program creates a CSV file with patterns meeting set criteria.

# Testing different parameters
In order to experiment with PrefixSpan parameters you can modify this line of minePatterns function:
```
patterns = ps.frequent(threshold, closed = ifclosed)
```
according to the documentation [on this page](https://pypi.org/project/prefixspan/).