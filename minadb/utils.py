import subprocess
import typing


def run_cmd(cmd: typing.List[str], no_decode: bool = None) -> typing.Union[bytes, str]:
    r = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if no_decode:
        return r
    return r.decode()
