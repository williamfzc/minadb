import subprocess
import typing
from minadb.device import logging


def run_cmd(cmd: typing.List[str], no_decode: bool = None) -> typing.Union[bytes, str]:
    cmd = [str(each) for each in cmd]
    logging.info(f"run command: {cmd}")
    try:
        r = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logging.error(e.output)
        raise e
    if no_decode:
        return r
    return r.decode()


def run_cmd_no_wait(cmd: typing.List[str]) -> subprocess.Popen:
    return subprocess.Popen(cmd)
