import json
import os
import time
import multiprocessing as mp
import time as t
from common_functions import round_durations, get_clip_duration, cleanup_intermediate
import logging

start_time = t.time()

def ffmpeg_worker(file_path, start_time, end_time, output_file_path, encoder):
	"""
	This worker will call the ffmpeg module to crop videos and extract subclips.
	"""
	file_path = file_path.replace(' ', r'\ ')
	os.system(f"ffmpeg -hide_banner -loglevel panic -i {file_path} -ss {start_time} -to {end_time} -b:v 750k -c:v {encoder} -c:a copy {output_file_path}")


def assign_workers(ip_video_path, clip_data, output_path, encoder):
	import concurrent.futures as cf
	with cf.ProcessPoolExecutor(None) as executor:
		for entry in clip_data:
			executor.submit(ffmpeg_worker, ip_video_path, entry['clip_start'], entry['clip_end'], f"../intermediate/{entry['clip_no']}.mp4", encoder)
	os.system(f"ffmpeg -nostats -loglevel 0 -f concat -i ../intermediate/videofiles.txt -c copy -fflags +genpts {output_path}")
	print(f"[INFO] {round(t.time()-start_time, 0)} seconds using {encoder}")

def start_clip_generation(input_video_path, clip_data_path, encoder, output_path):
	with open(clip_data_path, 'r') as f:
		clip_data = json.load(f)
	clip_data = round_durations(get_clip_duration(clip_data))

	assign_workers(input_video_path, clip_data, output_path, encoder)
	# Create videofiles.txt to enable final video combination (RACE CONDITION WITH ASSIGN WORKERS)
	with open('../intermediate/videofiles.txt', 'w') as f:
		for entry in clip_data:
			f.write(f"file \'{entry['clip_no']}.mp4\'\n")

if __name__ == "__main__":
	# start_time = time.time()
	input_video_path = os.path.join('../inputs/How to Move the Sun - Stellar Engines.mp4')
	start_clip_generation('../inputs/How to Move the Sun - Stellar Engines.mp4', '../intermediate/How to Move the Sun - Stellar Engines_clips.json', 'h264_videotoolbox')
	cleanup_intermediate()