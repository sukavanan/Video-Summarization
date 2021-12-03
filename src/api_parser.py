'''
 # @ Author: Shivesh M M
 # @ Create Time: 2020-05-03 04:30:22
 # @ Modified by: Shivesh M M
 # @ Description:
 '''

from youtube_transcript_api import YouTubeTranscriptApi
from functools import reduce
from datetime import datetime, timedelta


def compute_end_time(start_time, duration):
    start_time = datetime.strptime(start_time, '%H:%M:%S.%f')
    duration = duration * 1000
    return start_time + timedelta(milliseconds=duration)

def secondsToStr(t):
    return "%02d:%02d:%02d.%03d" % reduce(lambda ll,b : divmod(ll[0],b) + ll[1:], [(t*1000,),1000,60,60])

def parse_subtitle_api(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    intermediate = []
    for idx, i in enumerate(transcript):
        new_d = {}
        new_d['index'] = idx+1
        new_d['start_time'] = secondsToStr(i['start'])
        new_d['end_time'] = datetime.strftime(compute_end_time(new_d['start_time'], i['duration']), '%H:%M:%S.%f')[:-3]
        new_d['duration'] = i['duration']
        new_d['text'] = i['text']
        intermediate.append(new_d)
    return intermediate
    # with open(f'../intermediate/{video_id}_parsed.json', 'w') as f:
    #     json.dump(intermediate, f)