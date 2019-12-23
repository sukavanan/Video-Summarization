import json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f','--filename', required=True, help='.srt file to parse')
args = parser.parse_args()
with open(args.f) as f:
	pass