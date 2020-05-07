print("[INFO] Importing modules.")
import argparse, glob, json, os
import time as t
from pprint import pprint
import subprocess

from parse_subs import parse_subtitle, parse_subtitle_yt
from text_learning_condensed import return_clips
from api_parser import parse_subtitle_api

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
    # Create videofiles.txt to enable final video combination (RACE CONDITION WITH ASSIGN WORKERS)
    with open('../intermediate/videofiles.txt', 'w') as f:
        for entry in clip_data:
            f.write(f"file \'{entry['clip_no']}.mp4\'\n")
    os.system(f"ffmpeg -nostats -loglevel 0 -f concat -i ../intermediate/videofiles.txt -c copy -fflags +genpts {output_path}")
    print(f"[INFO] {round(t.time()-start_time, 0)} seconds using {encoder}")
    if len(file_list) > 1:
        print("[INFO] Cleaning Intermediate folder")
        files = glob.glob('../intermediate/*')
        for file in files:
            os.remove(file)

print("[INFO] Finished Imports.")

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--youtube", help="Youtube link of a video to download and parse.")
parser.add_argument("-e", "--encoder", help="Encoder to use.", default="h264_videotoolbox")
parser.add_argument("-p", "--use-youtube-parser", help="Manually use the youtube subtitle parser.", action="store_true")
parser.add_argument("-a", "--use-api-parser", help="Use a different parser that downloads subtitles directly using an XML format. More accurate.", action="store_true")
args = parser.parse_args()

if args.use_youtube_parser:
    print("[INFO] Manually using Youtube Parser")
if args.use_api_parser:
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
    if not args.use_api_parser:
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
    else:
        output = parse_subtitle_api(video)
    # Write the parsed subtitle file to an intermediate.
    with open(f"../intermediate/{video}_parsed.json", "w") as f:
        json.dump(output, f)
    print(f"[INFO] Converted {video}\'s subtitles to intermediate format")
    return_clips(f"../intermediate/{video}_parsed.json", output_path=f"../intermediate/{video}_clip_list.json")
    print(f"[INFO] Generated {video}\'s clip data")
    start_time = t.time()
    print(f"[INFO] Starting Subclip generation for {video}")
    input_video_path = file_list[video]['video']
    clip_data_path = f"../intermediate/{video}_clip_list.json"
    output_path=f"../outputs/{video}_summary.mp4"
    encoder = args.encoder
    with open(clip_data_path, 'r') as f:
        clip_data = json.load(f)
        clip_data = round_durations(get_clip_duration(clip_data))
    assign_workers(input_video_path, clip_data, output_path, encoder)
    