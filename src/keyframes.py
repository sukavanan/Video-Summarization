import json
import time as t
from datetime import date, datetime, time, timedelta
from common_functions import round_durations, assign_workers, worker_encode, cleanup_intermediate
import os
import multiprocessing as mp
import atexit

start_time = t.time()

def exit_handler():
	print("Creating concatendated video output...")
	os.system('ffmpeg -nostats -loglevel 0 -f concat -i ../intermediate/videofiles.txt -c copy -fflags +genpts ../outputs/final.mp4')
	print(f"{round(t.time()-start_time, 0)} seconds using keyframes")
	cleanup_intermediate()

atexit.register(exit_handler)

def add_keyframes(clip_data, video, output):
	keyframe_list = []
	for i in clip_data:
		keyframe_list.append(i['clip_start'])
		keyframe_list.append(i['clip_end'])
	keyframe_list_str = ",".join(keyframe_list)
	command = f"ffmpeg -i {video} -c:a copy -c:v copy -force_key_frames {keyframe_list_str} {output}"
	os.system(command)

def cut_video_at_keyframes(clip_data, ip_video): 
	pass

if __name__ == "__main__":
	# start_time = time.time()
	input_video_path = "../inputs/How\ to\ Move\ the\ Sun\ -\ Stellar\ Engines.mp4"
	output_video_path = "../inputs/How\ to\ Move\ the\ Sun\ -\ Stellar\ Engines_keyframed.mp4"
	print("Loading clip data...")
	with open('../intermediate/clip_data.json', 'r') as f:
		clip_data = json.load(f)
	clip_data = round_durations(clip_data)
	add_keyframes(clip_data, input_video_path, output_video_path)
	with mp.Pool(None) as pool:
		assign_workers(pool, worker_encode, 'copy', output_video_path, clip_data)
	# Create videofiles.txt to enable combination
	with open('../intermediate/videofiles.txt', 'w') as f:
		for entry in clip_data:
			f.write(f"file \'{entry['clip_no']}.mp4\'\n")