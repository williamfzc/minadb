import subprocess
import typing
from minadb.device import logging


def run_cmd(cmd: typing.List[str], no_decode: bool = None) -> typing.Union[bytes, str]:
    cmd = [str(each) for each in cmd]
    logging.info(f"run command: {cmd}")
    r = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if no_decode:
        return r
    return r.decode()
