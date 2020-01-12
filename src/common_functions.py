from datetime import date, datetime, time, timedelta
import os

# This worker runs the ffmpeg job using an os.system call
def worker_encode(file_name, start_time, end_time, output_file_name, encoder):
	# ffmpeg -i {input.mp4} -ss {start_time} -t {end_time} output.mp4
	os.system(f"ffmpeg -i {file_name} -ss {start_time} -to {end_time} -b:v 750k -c:v {encoder} -c:a copy {output_file_name}")

# This function assigns the ffmpeg job to multiple workers
def assign_workers(pool, worker, encoder, ip_video, data):
	import concurrent.futures as cf
	with cf.ProcessPoolExecutor(None) as pp:
		for entry in data:
			output_file_name = f"../intermediate/{entry['clip_no']}.mp4"
			start_time = entry['clip_start']
			end_time = entry['clip_end']
			pp.submit(worker, ip_video, start_time, end_time, output_file_name, encoder)

# This function stores the duration of the clip in a duration entry of the clip_list
def get_clip_duration(clip_list):
	for entry in clip_list:
		end_time = time.fromisoformat(entry['clip_end'].replace(',','.'))
		start_time = time.fromisoformat(entry['clip_start'].replace(',','.'))
		difference = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
		entry['duration'] = (datetime.combine(date.min, time.min) + difference).strftime('%H:%M:%S')
		# total_duration += round(difference.seconds+difference.microseconds/1000000, 3)
	return clip_list

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