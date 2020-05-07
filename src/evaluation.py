import glob, subprocess, os, json
from parse_subs import parse_subtitle, parse_subtitle_yt
from text_learning_condensed import return_clips
from create_clips import start_clip_generation
from api_parser import parse_subtitle_api

file_id = ''
proportion = 0.2
flexibility = 3

# for path in glob.glob('../inputs/*'):
#     manual = False
#     auto = False
#     try:
#         ans = subprocess.check_output(f"youtube-dl --no-warnings --list-subs https://www.youtube.com/watch?v={path.split('/')[-1].split('.')[0]}", shell=True)
#         if "has no subtitles" in str(ans):
#             pass
#         else:
#             manual = True
#         if "has no automatic captions" in str(ans):
#             continue
#         else:
#             auto = True
#         if auto or manual:
#             print("[INFO] Downloading Video and Subtitle")
#             os.system(f"youtube-dl --write-sub --write-auto-sub --sub-format srt --sub-lang en --skip-download https://www.youtube.com/watch?v={path.split('/')[-1].split('.')[0]} -o \'../inputs/%(id)s.%(ext)s\'")
#     except:
#         print(f"Failing on https://www.youtube.com/watch?v={path.split('/')[-1].split('.')[0]}")
if __name__ == "__main__":
    file_list = {}
    files = glob.glob('../inputs/' + file_id + "*")

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
        try:
            print(f"[INFO] Processing subtitle: \"{video}\"")
            output = parse_subtitle_api(video)
            # if file_list[video]['sub'].split('/')[-1].split('.')[-1] == 'srt':
            #     output = parse_subtitle_yt(file_list[video]['sub'])
            # else:
            #     output = parse_subtitle_yt(file_list[video]['sub'], True)

            # if len(output) == 0:
            #     output = parse_subtitle(file_list[video]['sub'], True)
            # Write the parsed subtitle file to an intermediate.
            with open(f"../intermediate/{video}_parsed.json", "w") as f:
                json.dump(output, f)
        except:
            print("Missing Subtitle, skipping.")

        print(f"[INFO] Converted {video}\'s subtitles to intermediate format")
        a = str(subprocess.check_output('ffprobe -i  "'+file_list[video]['video']+'" 2>&1 |grep "Duration"',shell=True)) 
        a = a.split(",")[0].split("Duration:")[1].strip()
        h, m, s = a.split(':')
        duration = int(int(h) * 3600 + int(m) * 60 + float(s))
        print(f"[INFO] Target length: {int(duration*proportion)} seconds")
        try:
            return_clips(f"../intermediate/{video}_parsed.json", output_path=f"../intermediate/{video}_clip_list.json", flexibility=flexibility, length=int(duration*proportion))
        except ValueError:
            print("Skip.")
        print(f"[INFO] Generated {video}\'s clip data")
        print(f"[INFO] Starting Subclip generation for {video}")
        # start_clip_generation(file_list[video]['video'], clip_data_path=f"../intermediate/{video}_clip_list.json", encoder="h264_videotoolbox", output_path=f"../outputs/{video}_summary.mp4")
        # if len(file_list) > 1:
        #     print("[INFO] Cleaning Intermediate folder")
        #     files = glob.glob('../intermediate/*')
        #     for file in files:
        #         if "clip_list" not in file:
        #             os.remove(file)
