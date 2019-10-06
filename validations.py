import argparse

def isValidDataName(parser, arg):
    if arg not in ["diabetes", "posts", "unknown1", "unknown2"]:
        parser.error("Dataset %s does not exist." % arg)
    else:
        return arg

def isValidDirection(parser, arg):
    if arg not in ["up", "down"]:
        parser.error("Direction %s is not valid. Type 'up' or 'down'." % arg)
    else:
        return arg

def isValidBide(parser, arg):
    if arg not in ["true", "false", "0", "1"]:
        parser.error("BIDE usage decision %s is not valid. Type 'true' or 'false' or '1' or '0'." % arg)
    else:
        return arg

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("file", help="Data set name: diabetes, posts, unknown1 or unknown2.", type=lambda arg: isValidDataName(parser, arg))
    parser.add_argument("direction", help="Direction of search: up or down.", type=lambda arg: isValidDirection(parser, arg))

    parser.add_argument("-t", "--threshold", help="Support measure threshold.", type=int, default=10)
    parser.add_argument("-m", "--minlen", help="Minumum length of pattern.", type=int, default=1)
    parser.add_argument("-u", "--user", help="User number.", type=int, default=-1)
    parser.add_argument("-b", "--bide", help="Whether to use BIDE algorithm.", type=lambda arg: isValidBide(parser, arg), default="false")

    args = parser.parse_args()
    return args
