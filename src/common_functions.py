'''
 # @ Author: Shivesh M M
 # @ Create Time: 2020-01-10 21:52:54
 # @ Modified by: Shivesh M M
 # @ Description:
 '''

from datetime import date, datetime, time, timedelta
import os
import sys
import glob
import json

# VIDEO_NAME = "How\ to\ Move\ the\ Sun\ -\ Stellar\ Engines.mp4"
VIDEO_NAME = "Hypothesis\ testing-II.mp4"


# If there's at most `flexibility` unselected elements between selected indices, select all of them.
FLEXIBILITY = 3
TARGET_LENGTH = 33 # (only a guideline) Crop might be longer including the important pieces between subs.

# This function stores the duration of the clip in a duration entry of the clip_list
def get_clip_duration(clip_list):
	for entry in clip_list:
		end_time = time.fromisoformat(entry['clip_end'].replace(',','.'))
		entry['clip_end'] = entry['clip_end'].replace(',','.')
		start_time = time.fromisoformat(entry['clip_start'].replace(',','.'))
		entry['clip_start'] = entry['clip_start'].replace(',','.')
		difference = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
		entry['duration'] = (datetime.combine(date.min, time.min) + difference).strftime('%H:%M:%S')
		# total_duration += round(difference.seconds+difference.microseconds/1000000, 3)
	return clip_list

# Function to cleanup the intermediate folder
def cleanup_intermediate():
	if query_yesno('Clean up the intermediate folder?'):
			files = glob.glob('../intermediate/*')
			for file in files:
				os.remove(file)


def dump_list_of_strings(file_name, output_path):
	'''get_list_of_strings Function definition. '''
	loaded_val = json.load(open(file_name))
	ans = []
	for i in loaded_val:
		ans.append(i['text'])
	import pickle
	pickle.dump(ans, open(output_path, 'wb'))

###
#  This function floors start timestamp and ceils end timestamps
# 	Start: 00:06:01.123 -> 00:06:01
# 	End: 00:06:54.123 -> 00:06:55
def round_durations(clip_list):
	for entry in clip_list:
		entry['clip_start'] = entry['clip_start'].split('.')[0]
		end_time = time.fromisoformat(entry['clip_end'].split('.')[0])
		endtime = datetime.combine(date.min, end_time) + timedelta(seconds=1)
		entry['clip_end'] = str(endtime.time())
	return clip_list

def query_yesno(question, default="yes"):
	valid = {"yes": True, "y": True, "ye": True,
			 "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Invalid input. Enter one of these: [yes/no/y/n]\n")