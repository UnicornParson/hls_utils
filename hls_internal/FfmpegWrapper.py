## example ffprobe.exe -loglevel quiet -show_format -show_streams -print_format json $Fname
import sys
import subprocess
import os
from pathlib import Path
from typing import NamedTuple

class MediaFileInfo(NamedTuple):
    return_code: int
    json: str
    error: str

class FFmpegWrapper:
    def __init__(self) -> None:
        self.ffprobeCmd = "ffprobe"
        self.ffmpegCmd = "ffmpeg"


    def getFinfo(self, file_path: str) -> MediaFileInfo:
        if not file_path or not os.path.isfile(file_path):
            return None

        command_array = [self.ffprobeCmd,
                        "-loglevel", "quiet",
                        "-print_format", "json",
                        "-show_format",
                        "-show_streams",
                        file_path]
        result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return MediaFileInfo(return_code=result.returncode,
                            json=result.stdout,
                            error=result.stderr)