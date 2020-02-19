import subprocess
import typing


def run_cmd(cmd: typing.List[str], no_decode: bool = None) -> typing.Union[bytes, str]:
    r = subprocess.check_output(cmd)
    if no_decode:
        return r
    return r.decode()
