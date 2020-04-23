import json
import os
import time
import multiprocessing as mp
import atexit
import time as t
from common_functions import round_durations, assign_workers, worker_encode, get_clip_duration, cleanup_intermediate, VIDEO_NAME, ENCODER
import logging

start_time = t.time()


# # This worker runs the ffmpeg job using an os.system call
# def worker_encode(file_name, start_time, end_time, output_file_name):
# 	# ffmpeg -i {input.mp4} -ss {start_time} -t {end_time} output.mp4
# 	os.system(f"ffmpeg -nostats -loglevel 0 -i {file_name} -ss {start_time} -to {end_time} -b:v 750k -c:v {ENCODER} -c:a copy {output_file_name}")

# # This function assigns the ffmpeg job to multiple workers
# def assign_workers(pool, ip_video, data):
# 	import concurrent.futures as cf
# 	with cf.ProcessPoolExecutor(None) as pp:
# 		for entry in data:
# 			output_file_name = f"../intermediate/{entry['clip_no']}.mp4"
# 			start_time = entry['clip_start']
# 			end_time = entry['clip_end']
# 			pp.submit(worker_encode, ip_video, start_time, end_time, output_file_name)

def exit_handler():
	print("Creating concatenated video output...")
	os.system('ffmpeg -nostats -loglevel 0 -f concat -i ../intermediate/videofiles.txt -c copy -fflags +genpts ../outputs/final.mp4')
	print(f"{round(t.time()-start_time, 0)} seconds using {ENCODER}")
	cleanup_intermediate()

atexit.register(exit_handler)


if __name__ == "__main__":
	# start_time = time.time()
	input_video_path = os.path.join('../inputs/', VIDEO_NAME)
	print("Loading clip data...")
	with open('../intermediate/clip_data.json', 'r') as f:
		clip_data = json.load(f)
	clip_data = round_durations(get_clip_duration(clip_data))
	with mp.Pool(None) as pool:
		assign_workers(pool, worker_encode, ENCODER, input_video_path, clip_data)
	
	# Create videofiles.txt to enable final video combination
	with open('../intermediate/videofiles.txt', 'w') as f:
		for entry in clip_data:
			f.write(f"file \'{entry['clip_no']}.mp4\'\n")