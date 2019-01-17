# State-changing event sequential patterns
This project implements a solution for finding event sequential patterns which have a desired effect on object's state. So far it works on a diabetes database, which describes treatment of 70 patients diagnosed with diabetes.

# Getting started
This is what you need to run this project.

## Prerequisites
* Python version 3.7.1

Make sure you installed correct version (and have it in your PATH environment variable):
```
python -V
```

## Installing
After making sure you have the specified python version, install these libraries:
```
pip install pandas
pip install numpy
pip install prefixspan
```

## Running the project
To run the project go to the project folder and type:
```
python mine.py
```

## Result
As a result, the program prints all found patterns.

# Testing different parameters
In order to experiment with PrefixSpan parameters you can modify this line of main function:
```
print(ps.frequent(2))
```
according to the documentation [on this page](https://pypi.org/project/prefixspan/).