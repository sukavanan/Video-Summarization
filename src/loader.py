print("[INFO] Importing modules.")
import argparse, glob, json, os
from pprint import pprint
from create_clips import start_clip_generation

from parse_subs import parse_subtitle, parse_subtitle_yt
from text_learning_condensed import return_clips

print("[INFO] Finished Imports.")

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--youtube", help="Youtube link of a video to download and parse.")
parser.add_argument("-e", "--encoder", help="Encoder to use.", default="h264_videotoolbox")
parser.add_argument("-p", "--use-youtube-parser", help="Manually use the youtube subtitle parser.", action="store_true")
args = parser.parse_args()

if args.use_youtube_parser:
	print("[INFO] Manually using Youtube Parser")

manual = False
auto = False
file_list = {}
files = glob.glob('../inputs/*')
if len(files) == 0:
	print("[WARNING] Input folder empty. Checking for Youtube URL in argument")
	if args.youtube == None:
		print("[ERROR] No youtube link found. Exiting.")
		exit()
	import subprocess
	ans = subprocess.check_output(f"youtube-dl --no-warnings --list-subs {args.youtube}", shell=True)
	if "has no subtitles" in str(ans):
		print("[WARNING] No manual subtitles found. Checking for automatic subtitles")
	else:
		manual = True
		print("Subs found.")
	if "has no automatic captions" in str(ans):
		print("[ERROR] No auto-generated subtitles found. Exiting.")
		exit()
	else:
		auto = True
		print("Auto-subs found.")
	print("[INFO] Downloading Video and Subtitle")
	os.system(f"youtube-dl -f \'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/mp4\' {args.youtube} -o \'../inputs/%(title)s.%(ext)s\' --write-sub --write-auto-sub --sub-lang en --sub-format srt")
files = glob.glob('../inputs/*') 
print("[INFO] Using videos from input folder")
for file in files:
	filename = file.split('/')[-1].split('.')[0]
	if filename not in file_list:
		file_list[filename] = {}
	if file.split('/')[-1].split('.')[-1] == 'mp4':
		file_list[filename]['video'] = file
	elif file.split('/')[-1].split('.')[-1] in ['srt', 'vtt']:
		file_list[filename]['sub'] = file
	# file_list[filename] = file_dict
print(f"[INFO] Found {len(list(file_list.keys()))} Videos")

# for video in list(file_list.keys()):
for video in file_list:
	print(f"[INFO] Processing subtitle: \"{video}\"")
	if file_list[video]['sub'].split('/')[-1].split('.')[-1] == 'srt':
		if not auto and not args.use_youtube_parser:
			output = parse_subtitle(file_list[video]['sub'])
		else:
			output = parse_subtitle_yt(file_list[video]['sub'])
	else:
		if not auto and not args.use_youtube_parser:
			output = parse_subtitle(file_list[video]['sub'], True)
		else:
			output = parse_subtitle_yt(file_list[video]['sub'], True)
			

	# Write the parsed subtitle file to an intermediate.
	with open(f"../intermediate/{video}_parsed.json", "w") as f:
		json.dump(output, f)
	print(f"[INFO] Converted {video}\'s subtitles to intermediate format")
	return_clips(f"../intermediate/{video}_parsed.json", output_path=f"../intermediate/{video}_clip_list.json")
	print(f"[INFO] Generated {video}\'s clip data")
	print(f"[INFO] Starting Subclip generation for {video}")
	start_clip_generation(file_list[video]['video'], clip_data_path=f"../intermediate/{video}_clip_list.json", encoder=args.encoder, output_path=f"../outputs/{video}_summary.mp4")
	if len(file_list) > 1:
		print("[INFO] Cleaning Intermediate folder")
		files = glob.glob('../intermediate/*')
		for file in files:
			os.remove(file)