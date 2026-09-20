import json
import math
import subprocess

from datetime import datetime
from lxml import html
from pathlib import Path

def get_name_type(path: Path, base_path: Path, types = None):
    type_ = path.suffix.lower()[1:]
    if types is not None and type_ not in types: return None, None
    if type_ == "htm": type_ = "html"

    name = str(path.relative_to(base_path).with_suffix("")).upper().replace("\\", "/")
    return name, type_

def get_gdd(path: Path):
    tree = html.parse(path)
    scripts = tree.xpath("//script[@name='graphics-data-definition']")
    if not scripts: return None

    src = scripts[0].get("src")
    if src: gdd = (path.parent / src).read_text(encoding="utf8")
    else: gdd = scripts[0].text

    json.loads(gdd) # test gdd
    return gdd.strip()

def get_info(file: Path):
    res = subprocess.run(
        [ "ffprobe", "-hide_banner", "-i", file, "-show_streams", "-show_format", "-print_format", "json" ],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, check=True
    )
    data = json.loads(res.stdout)
    return data if data.get("streams") else None

def get_cinf(name, size, time, info):
    streams = info.get("streams", [])

    video = next((s for s in streams
        if s.get("codec_type") == "video" and s.get("disposition", {}).get("attached_pic") != 1), None
    )
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

    clip = {
        "name": name,
        "type": "STILL",
        "size": size,
        "time": datetime.fromtimestamp(time).strftime("%Y%m%d%H%M%S"),
        "frames": 0,
        "time_base": "0/1"
    }

    if video:
        duration = float(info.get("format", {}).get("duration", 0))
        stream_duration = float(video.get("duration", duration))

        if stream_duration >= 0.1 and video.get("codec_name") != "gif":
            clip["type"] = "MOVIE"

            frame_rate = video.get("avg_frame_rate", "0/0")
            if frame_rate == "0/0": frame_rate = video.get("r_frame_rate", "0/0")
            frame_rate = frame_rate.split("/")

            if len(frame_rate) == 2 and frame_rate[0] != "0":
                clip["time_base"] = f"{frame_rate[1]}/{frame_rate[0]}"
            else:
                clip["time_base"] = video.get("time_base", "0/1")

            num, den = map(int, clip["time_base"].split("/"))
            if num: clip["frames"] = math.floor((duration * den) / num)

    elif audio:
        clip["type"] = "AUDIO"
        clip["time_base"] = audio.get("time_base", "0/1")

    return '"{name}" {type} {size} {time} {frames} {time_base}'.format(**clip)
