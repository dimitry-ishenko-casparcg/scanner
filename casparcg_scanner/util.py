import json
import math
import subprocess

from datetime import datetime
from pathlib import Path

def get_info(path: Path):
    res = subprocess.run(
        [ "ffprobe", "-hide_banner", "-i", path, "-show_streams", "-show_format", "-print_format", "json" ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=True, timeout=10
    )
    info = json.loads(res.stdout)
    if not info.get("streams"): raise ValueError("no media streams")

    return info

def get_cinf(name: str, size: int, time: int, info: dict):
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

def get_media_info(name: str, path: Path, size: int, time: float, info: dict):
    fmt = info.get("format", {})
    return json.dumps({
        "name": name,
        "path": str(path),
        "size": size,
        "time": int(time * 1000),
        "field_order": "unknown", # TODO

        "streams": [
            {
                "codec": {
                    "long_name": s.get("codec_long_name"),
                    "type": s.get("codec_type"),
                    "time_base": s.get("codec_time_base"),
                    "tag_string": s.get("codec_tag_string"),
                    "is_avc": s.get("is_avc"),
                },

                # video
                "width": s.get("width"),
                "height": s.get("height"),
                "sample_aspect_ratio": s.get("sample_aspect_ratio"),
                "display_aspect_ratio": s.get("display_aspect_ratio"),
                "pix_fmt": s.get("pix_fmt"),
                "bits_per_raw_sample": s.get("bits_per_raw_sample"),
                "frame_rate": s.get("avg_frame_rate") or s.get("r_frame_rate"),

                # audio
                "sample_fmt": s.get("sample_fmt"),
                "sample_rate": s.get("sample_rate"),
                "channels": s.get("channels"),
                "channel_layout": s.get("channel_layout"),
                "bits_per_sample": s.get("bits_per_sample"),

                # common
                "time_base": s.get("time_base"),
                "start_time": s.get("start_time"),
                "duration_ts": s.get("duration_ts"),
                "duration": s.get("duration"),
                "bit_rate": s.get("bit_rate"),
                "max_bit_rate": s.get("max_bit_rate"),
                "nb_frames": s.get("nb_frames"),
            }
            for s in info.get("streams", [])
        ],

        "format": {
            "name": fmt.get("format_name"),
            "long_name": fmt.get("format_long_name"),
            "size": fmt.get("size"),

            "start_time": fmt.get("start_time"),
            "duration": fmt.get("duration"),
            "bit_rate": fmt.get("bit_rate"),
            "max_bit_rate": fmt.get("max_bit_rate"),
        }
    })

def generate_thumbnail(name: str, path: Path, info: dict):
    video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video: return None, None

    duration = float(video.get("duration") or info.get("format", {}).get("duration") or "0")
    attached_pic = video.get("disposition", {}).get("attached_pic") == 1

    def grab_frame(path: Path, vf: str = None):
        res = subprocess.run(
            [ "ffmpeg", "-hide_banner", "-i", path,
                "-vf", ",".join(filter(None, [vf, "scale=256:-1"])),
                "-frames:v", "1", "-threads", "1", "-f", "image2pipe", "-vcodec", "png", "-"
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True, timeout=10
        )
        return res.stdout

    image = b""
    if duration > 0.1 and not attached_pic:
        try: image = grab_frame(path, "select='gt(scene,0.4)'")
        except subprocess.TimeoutExpired: pass
    if not image: image = grab_frame(path)

    size = len(image)
    if not size: return None, None
    time = datetime.now().strftime("%Y%m%dT%H%M%S")

    return f'"{name}" {time} {size}', image
