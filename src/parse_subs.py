import argparse
import json
import logging
import os
import re
from itertools import groupby
from datetime import datetime, date, time

# Initialize objects

# logger = logging.Logger('Logger')
# parser = argparse.ArgumentParser()
# parser.add_argument('-f','--filename', required=True, help='.srt file to parse')
# parser.add_argument('-o','--output', help='Output json file, default is \'output.json\'')
# args = parser.parse_args()

# Check input validity

# if not os.path.exists(args.filename):
# 	logger.error("ERROR: Input file doesn't exist")
# 	exit(-1)

# .srt and .vtt handler

def compute_duration(start_time, end_time):
	# Difference of end_time and start_time
	start_time = time.fromisoformat(start_time.replace(',','.'))
	end_time = time.fromisoformat(end_time.replace(',','.'))

	difference = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
	return round(difference.seconds+difference.microseconds/1000000, 3)

# For youtube autogenerated
def parse_subtitle_yt(filename, vtt=False):
	output_subtitle = []
	# Currently only for SRT
	if not vtt:
		with open(filename) as f:
		# Parse the file content
			content = f.read()
			count = 1
			for s in re.sub('\r\n', '\n', content).split('\n\n'):
				st = s.split('\n')
				if len(st)>=3:
					split = st[1].split(' --> ')
					output_subtitle.append({'index': int(st[0]),
								'start_time': split[0].strip(),
								'end_time': split[1].strip(),
								'text': ' '.join(j for j in st[2:len(st)]),
								'duration':  compute_duration(split[0].strip(), split[1].strip())
								})
				if len(st)==2:
					split = st[1].split(' --> ')
					output_subtitle.append({'index': int(st[0]),
								'start_time': split[0].strip(),
								'end_time': split[1].strip(),
								'text': '',
								'duration':  compute_duration(split[0].strip(), split[1].strip())
								})
				count+=1
			return output_subtitle
	else:
		with open(filename) as f:
			output_subtitle = []
			content = f.read()
			count=1
			for s in content.split('\n\n'):
				subtitle_element = dict()
				s+='\n'
				matches = re.match(r"(.*?)-->(.*?) align:start position:0%((?:\n|.)*?)\n$", s)
				if matches is not None:
					subtitle_element['index'] = count
					subtitle_element['start_time'] = matches.group(1).strip()
					subtitle_element['end_time'] = matches.group(2).strip()
					subtitle_element['duration'] = compute_duration(subtitle_element['start_time'], subtitle_element['end_time'])
					if subtitle_element['duration'] != 0.01:
						subtitle_element['text'] =  re.sub(r"\<(.*?)\>", "", matches.group(3).strip())
						output_subtitle.append(subtitle_element)
						count+=1
		return output_subtitle
def parse_subtitle(filename, vtt=False):
	output_subtitle = []
	read_lines = []
	
	###
	# Read file in chunks. Helps handle large files.
	###

	with open(filename, 'r') as file:
		chunk = []
		for line in file:
			if line == '\n':
				read_lines.append(''.join(chunk))
				chunk = []
			else:
				chunk.append(line.strip('\ufeff\t '))
	# .srt files
	if not vtt:
		for line in read_lines:
			subtitle_element = dict()
			matches = re.match(r"([0-9]+)\n(.*?)-->(.*?)\n((?:\n|.)*?)\n$", line)
			if matches is not None:
				subtitle_element['index'] = int(matches.group(1).strip())
				subtitle_element['start_time'] = matches.group(2).strip()
				subtitle_element['end_time'] = matches.group(3).strip()
				subtitle_element['duration'] = compute_duration(subtitle_element['start_time'], subtitle_element['end_time'])
				subtitle_element['text'] = matches.group(4).strip()
				output_subtitle.append(subtitle_element)
	else:
		# .vtt files
		count=1
		for line in read_lines:
			subtitle_element = dict()
			matches = re.match(r"(.*?)-->(.*?)\n((?:\n|.)*?)\n$", line)
			if matches is not None:
				subtitle_element['index'] = count
				subtitle_element['start_time'] = matches.group(1).strip()
				subtitle_element['end_time'] = matches.group(2).strip()
				subtitle_element['duration'] = compute_duration(subtitle_element['start_time'], subtitle_element['end_time'])
				subtitle_element['text'] = matches.group(3).strip()
				output_subtitle.append(subtitle_element)
				count+=1
	
	return output_subtitle

# Main

if __name__ == "__main__":
	with open(args.filename) as f:
		if "align:start position:0%" in f.read():
			print("Autogenerated mess.")
			exit()

	if os.path.splitext(args.filename)[1] == '.srt':
		output = parse_subtitle(args.filename)
	elif os.path.splitext(args.filename)[1] == '.vtt':
		output = parse_subtitle(args.filename, vtt=True)
	else:
		print("ERROR: Unsupported filetype")
	
	if args.output is None:
		if os.path.exists('./intermediate/'):
			with open('./intermediate/output.json', 'w') as f:
				json.dump(output, f)
		else:		
			with open(os.path.join(os.path.split(args.filename)[0], 'output.json'), 'w') as f:
				json.dump(output, f)
	else:
		with open(args.output, 'w') as f:
			json.dump(output, f)
