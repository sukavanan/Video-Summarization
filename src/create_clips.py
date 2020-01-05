import json
import os
import time
import multiprocessing as mp
import atexit
import time as t
from datetime import date, datetime, time, timedelta

start_time = t.time()

encoder = 'h264_videotoolbox'

def exit_handler():
	os.system('ffmpeg -f concat -i ../intermediate/videofiles.txt -c copy -fflags +genpts ../output/final.mp4')
	print(f"{round(t.time()-start_time, 0)} using {encoder}")

atexit.register(exit_handler)

def worker(file_name, start_time, end_time, output_file_name):
	# ffmpeg -i {input.mp4} -ss {start_time} -t {end_time} output.mp4
	os.system(f"ffmpeg -i {file_name} -ss {start_time} -t {end_time} -b:v 750k -c:v {encoder} -c:a copy {output_file_name}")

def assign_workers(pool, ip_video, data):
	import concurrent.futures as cf
	with cf.ProcessPoolExecutor(None) as pp:
		for entry in data:
			output_file_name = f"../intermediate/{entry['clip_no']}.mp4"
			start_time = entry['clip_start']
			end_time = entry['duration']
			pp.submit(worker, ip_video, start_time, end_time, output_file_name)

def get_clip_duration(clip_list):
	for entry in clip_list:
		end_time = time.fromisoformat(entry['clip_end'].replace(',','.'))
		start_time = time.fromisoformat(entry['clip_start'].replace(',','.'))
		difference = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
		entry['duration'] = (datetime.combine(date.min, time.min) + difference).strftime('%H:%M:%S')
		# total_duration += round(difference.seconds+difference.microseconds/1000000, 3)
	return clip_list

def round_durations(clip_list):
	for entry in clip_list:
		entry['clip_start'] = entry['clip_start'].split('.')[0]
		end_time = time.fromisoformat(entry['clip_end'].split('.')[0])
		endtime = datetime.combine(date.min, end_time) + timedelta(seconds=1)
		entry['clip_end'] = str(endtime.time())
	return clip_list

if __name__ == "__main__":
	# start_time = time.time()
	input_video_path = '../inputs/How\ to\ Move\ the\ Sun\ -\ Stellar\ Engines.mp4'
	print("Loading clip data...")
	with open('../intermediate/clip_data.json', 'r') as f:
		clip_data = json.load(f)
	clip_data = get_clip_duration(round_durations(clip_data))
	with mp.Pool(None) as pool:
		assign_workers(pool, input_video_path, clip_data)
	with open('../intermediate/videofiles.txt', 'w') as f:
		for entry in clip_data:
			f.write(f"file \'{entry['clip_no']}.mp4\'\n")
