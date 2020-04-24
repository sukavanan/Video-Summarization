import os, glob, json
from pprint import pprint


from parse_subs import parse_subtitle

file_list = {}
files = glob.glob('../inputs/*')
if len(files) == 0:
    print("[WARNING] Input folder empty. Checking for Youtube URL in argument")
else:
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

for video in list(file_list.keys()):
    print(f"[INFO] Processing subtitle: \"{video}\"")
    if file_list[video]['sub'].split('/')[-1].split('.')[-1] == 'srt':
        output = parse_subtitle(file_list[video]['sub'])
    else:
        output = parse_subtitle(file_list[video]['sub'], True)
    with open(f"../intermediate/{video}.json", "w") as f:
        json.dump(output, f)

print(f"[INFO] Converted {len(list(file_list.keys()))} subtitles to intermediate format")

