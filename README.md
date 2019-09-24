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
The project requires 2 parameters - direction and BIDE.

Direction specifies which state changes are examined, increasing or decreasing. They should be provided as *up* or *down*.

BIDE parameter states whether to use BIDE algorithm instead of PrefixSpan. It should be given as *true* or *1* for using BIDE, or *false* or *0* for using PrefixSpan.

To run the project go to the project folder and type:
```
python mine.py <direction> <BIDE>
```
Example:
```
python mine.py up true
```


## Result
As a result, the program prints all found patterns.

# Testing different parameters
In order to experiment with PrefixSpan parameters you can modify this line of main function:
```
print(ps.frequent(2))
```
according to the documentation [on this page](https://pypi.org/project/prefixspan/).