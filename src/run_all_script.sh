#!/bin/zsh
echo Parsing subtitles
python3 parse_subs.py -f ../inputs/How\ to\ Move\ the\ Sun\ -\ Stellar\ Engines.en.vtt -o ../intermediate/output.json
echo Learning from subtitles
python3 text_learning.py
echo Calling create_clips.py
python3 create_clips.py