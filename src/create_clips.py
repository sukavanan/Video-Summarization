import json
import os
import time
import multiprocessing as mp
import atexit
import time as t
from common_functions import round_durations, get_clip_duration, assign_workers, worker_encode
import logging

start_time = t.time()

encoder = 'h264_videotoolbox'

logger = logging.Logger("GeneralLogger")

def exit_handler():
	logger.info("Creating concatendated video output...")
	os.system('ffmpeg -f concat -i ../intermediate/videofiles.txt -c copy -fflags +genpts ../outputs/final.mp4')
	logger.info(f"{round(t.time()-start_time, 0)} seconds using {encoder}")

atexit.register(exit_handler)


if __name__ == "__main__":
	# start_time = time.time()
	input_video_path = '../inputs/How\ to\ Move\ the\ Sun\ -\ Stellar\ Engines.mp4'
	logger.info("Loading clip data...")
	with open('../intermediate/clip_data.json', 'r') as f:
		clip_data = json.load(f)
	clip_data = round_durations(clip_data)
	with mp.Pool(None) as pool:
		assign_workers(pool, worker_encode, encoder, input_video_path, clip_data)
	
	# Create videofiles.txt to enable final video combination
	with open('../intermediate/videofiles.txt', 'w') as f:
		for entry in clip_data:
			f.write(f"file \'{entry['clip_no']}.mp4\'\n")