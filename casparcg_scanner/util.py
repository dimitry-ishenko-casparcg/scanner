import json
import math
import subprocess

from datetime import datetime
from lxml import etree, html
from pathlib import Path

def get_scanner_paths(config_path: Path):
    root = etree.parse(config_path).getroot()
    if root.tag != "configuration":
        raise ValueError(f"Invalid root tag <{root.tag}>")

    def get_path(path, fallback):
        val = root.findtext(path, default="").strip()
        # If 'Path(...)' is absolute, 'config_path' will be ignored.
        return config_path.parent / Path(val or fallback)

    return {
        "font_path": get_path("paths/font-path", "font"),
        "media_path": get_path("paths/media-path", "media"),
        "template_path": get_path("paths/template-path", "template")
    }

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

def get_info(path: Path):
    res = subprocess.run(
        [ "ffprobe", "-hide_banner", "-i", path, "-show_streams", "-show_format", "-print_format", "json" ],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, check=True
    )
    info = json.loads(res.stdout)
    return info if info.get("streams") else None

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

    res = subprocess.run(
        [ "ffmpeg", "-hide_banner", "-i", path,
            "-vf", "scale=256:-1" if duration < 0.1 or attached_pic else "select='gt(scene,0.4)',scale=256:-1",
            "-frames:v", "1", "-threads", "1", "-f", "image2pipe", "-vcodec", "png", "-"
        ],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        check=True
    )

    image = res.stdout
    size = len(image)
    if not size: return None, None
    time = datetime.now().strftime("%Y%m%dT%H%M%S")

    return f'"{name}" {time} {size}', image
