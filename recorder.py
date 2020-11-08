from time import sleep
from typing import List
import ffmpeg
import os
from datetime import datetime, timedelta
import time
import sys
import subprocess
import requests
import re


def get_raw_stream_URL(field_url):
    r = requests.get(field_url)
    token = re.findall(r"token = \'[0-9a-z]+\'", r.text)[0][7:].strip().strip("'")
    alias = re.findall(r"alias = \'[0-9a-z]+\'", r.text)[0][7:].strip().strip("'")

    get_stream_state_url = f"https://g1.ipcamlive.com/player/getcamerastreamstate.php?&token={token}&alias={alias}&targetdomain=www.ipcamlive.com"
    stream_info = requests.get(get_stream_state_url).json()
    stream_id = stream_info['details']['streamid']
    address = stream_info['details']['address']

    return f"{address}streams/{stream_id}/stream.m3u8" 


def generate_ffmpeg_cmd(input_url: str, duration: int, title: str) -> List[str]:
    argv = sys.argv
    stream = ffmpeg.input(input_url,hide_banner=None)
    stream = ffmpeg.output(stream, title, t=int(duration), crf=20, metadata='title=' + title, preset="fast", vcodec="copy", reconnect_delay_max=10)
    return stream.compile()


def main():

    field_urls = {
        "BOARDWALK": "https://www.ipcamlive.com/5f9c45a574ffd",
        "FOOTHILLS": "https://www.ipcamlive.com/5f9c47a768cc0",
        "FIELDSAFE": "https://www.ipcamlive.com/5f863adf8e4ba",
        "ASPENAIR": "https://www.ipcamlive.com/5f9c4643bf178"
    }

    if len(sys.argv) != 5:
        print("\nIncorrect Command line arguments. Format is 'python recorder.py field_key start_time(in format 'HH:MM:SS') record_duration (in seconds) outputfilename.mp4'\n\nFor example to record boardwalk field for one hour at 7 PM:\npython recorder.py BOARDWALK 17:00:00 3600 boardwalk_video.mp4\n\n")
        raise Exception("Wrong Command Line Args")

    field_url = field_urls.get(sys.argv[1].upper())
    if field_url is None:
        raise Exception(f"Field key is wrong. Available options are: {list(field_urls.keys())}")
    
    raw_stream_url = get_raw_stream_URL(field_url)
    
    startTime = datetime.combine(datetime.now().date(), datetime.strptime(sys.argv[2], '%H:%M:%S').time())
    endTime = startTime + timedelta(seconds=int(sys.argv[3]))
    
    start_delay = (startTime - datetime.now()).total_seconds()
    if start_delay > 0:
        print(f"Waiting {start_delay} seconds until {sys.argv[2]}")
        time.sleep(start_delay)

    cmd = generate_ffmpeg_cmd(raw_stream_url, int(sys.argv[3]), sys.argv[4])
    status = subprocess.call(cmd)
    
    # If ffmpeg returns non-zero status, try again (max 10 times)
    i = 1
    while i < 10 and (endTime - datetime.now()).total_seconds() > 1:
        time.sleep(5)
        updated_duration = (endTime - datetime.now()).seconds
        raw_stream_url = get_raw_stream_URL(field_url)
        cmd = generate_ffmpeg_cmd(raw_stream_url, updated_duration, sys.argv[4] + f"_{i}")
        status = subprocess.call(cmd)
        i += 1
        

if __name__ == '__main__':
    """
    argument format is:
    python recorder.py field_key start_time record_duration output_file_name
    start_time: in format 'HH:MM:SS'
    record_duration: in seconds
    """

    main()
