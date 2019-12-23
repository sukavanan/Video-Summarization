import argparse
import json
import logging
import os
import re
from itertools import groupby

# Initialize objects

logger = logging.Logger('Logger')
parser = argparse.ArgumentParser()
parser.add_argument('-f','--filename', required=True, help='.srt file to parse')
parser.add_argument('-o','--output', help='Output json file, default is \'output.json\'')
args = parser.parse_args()

# Check input validity

if not os.path.exists(args.filename):
	logger.error("ERROR: Input file doesn't exist")
	exit(-1)

# .srt and .vtt handler

def parse_subtitle(filename, vtt=False):
	output_subtitle = []
	read_lines = []
	# Read file in chunks. Helps handle large files.
	with open(filename, 'r') as file:
		chunk = []
		for line in file:
			if line == '\n':
				read_lines.append(''.join(chunk))
				chunk = []
			else:
				chunk.append(line.strip('\ufeff\t '))
	if not vtt:
		for line in read_lines:
			subtitle_element = dict()
			matches = re.match(r"([0-9]+)\n(.*?)-->(.*?)\n((?:\n|.)*?)\n$", line)
			if matches is not None:
				subtitle_element['index'] = matches.group(1).strip()
				subtitle_element['start_time'] = matches.group(2).strip()
				subtitle_element['end_time'] = matches.group(3).strip()
				subtitle_element['text'] = matches.group(4).strip()
				output_subtitle.append(subtitle_element)
	else:
		count=1
		for line in read_lines:
			subtitle_element = dict()
			matches = re.match(r"(.*?)-->(.*?)\n((?:\n|.)*?)\n$", line)
			if matches is not None:
				subtitle_element['index'] = count
				subtitle_element['start_time'] = matches.group(1).strip()
				subtitle_element['end_time'] = matches.group(2).strip()
				subtitle_element['text'] = matches.group(3).strip()
				output_subtitle.append(subtitle_element)
				count+=1
	
	return output_subtitle

# Main

if __name__ == "__main__":

	if os.path.splitext(args.filename)[1] == '.srt':
		output = parse_subtitle(args.filename)
	elif os.path.splitext(args.filename)[1] == '.vtt':
		output = parse_subtitle(args.filename, vtt=True)
	else:
		logger.error("ERROR: Unsupported filetype")
	
	if args.output is None:
		with open(os.path.join(os.path.split(args.filename)[0], 'output.json'), 'w') as f:
			json.dump(output, f)
	else:
		with open(args.output, 'w') as f:
			json.dump(output, f)
