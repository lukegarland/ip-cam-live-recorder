# ip-cam-live-recorder
To run on windows:
```
    recorder.exe field_key start_time record_duration output_file_name
```

```start_time```: in format 'HH:MM:SS'
```record_duration```: in seconds
possible ```field_key``` are: ```BOARDWALK```, ```FOOTHILLS```, ```FIELDSAFE```, ```ASPENAIR```

To run on linux or from source code:
Install ffmpeg and python binding (```sudo apt-get install ffmpeg``` and ```pip3 install ffmpeg-python```), then run:
```
    python3 recorder.py field_key start_time record_duration output_file_name
```
