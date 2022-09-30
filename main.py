#    Copyright 2022 Lipatov Alexander
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import logging
import os
import shutil
import threading
import time
from pathlib import Path
from urllib.request import urlretrieve

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("wget")

accepted_size: int = 0
hf_total_size: str = "?"
done: bool = False

def sizeof_fmt(num: int, suffix: str = "B") -> str:
    """
    Returns human friendly formatted size

    :param num: number of bytes
    :param suffix: default "B"
    :return: human readable size string
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

def reporthook(blocknum: int, bs: int, size: int):
    """
    Hook that is going to be executed after every block read.
    There is accumulated values for logging intime

    :param blocknum: block number
    :param bs: block size
    :param size: total size
    """
    global accepted_size
    global hf_total_size

    if hf_total_size == "?":
        hf_total_size = sizeof_fmt(size)

    accepted_size += bs

def log_accepted_size(interval: int = 1):
    """
    Function that logging download process endlessly
    
    :param interval: sleep interval in seconds
    """
    while True:
        logger.info("Currently downladed: %s of %s", sizeof_fmt(accepted_size), hf_total_size)
        time.sleep(interval)
        
        global done
        if done:
            break
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='lightweight wget tool')
    parser.add_argument("url", type=str, help="remote file destination")
    parser.add_argument("--out", type=str, required=False, help="optional file path to downloaded file")

    args = parser.parse_args()

    thread = threading.Thread(
        target=log_accepted_size,
    )

    thread.start()

    try:
        url: str = args.url

        tmp_path, msg = urlretrieve(url, reporthook=reporthook)

        desired_location = Path.cwd() / Path(os.path.split(url)[1])
        if args.out:
            desired_location = args.out

        shutil.move(tmp_path, desired_location)

        logger.info("Done, file: %s", desired_location)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        done = True