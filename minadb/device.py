import subprocess
import typing
import time

from minadb.utils import run_cmd


class _BaseADBDevice(object):
    def __init__(self, serial_no: str):
        self.serial_no: str = serial_no
        self.basic_cmd: typing.List[str] = ["adb", "-s", self.serial_no]

    def build_shell_cmd(self, cmd: typing.List[str]) -> typing.List[str]:
        return [*self.basic_cmd, "shell", *cmd]

    def build_no_shell_cmd(self, cmd: typing.List[str]) -> typing.List[str]:
        return [*self.basic_cmd, *cmd]

    def shell(self, cmd: typing.List[str]) -> str:
        return run_cmd(self.build_shell_cmd(cmd))

    def no_shell(self, cmd: typing.List[str]) -> str:
        return run_cmd(self.build_no_shell_cmd(cmd))

    def push(self, pc_path: str, device_path: str) -> str:
        cmd = ["push", pc_path, device_path]
        return run_cmd(self.build_no_shell_cmd(cmd))

    def pull(self, device_path: str, pc_path: str) -> str:
        cmd = ["pull", device_path, pc_path]
        return run_cmd(self.build_no_shell_cmd(cmd))


class ADBDevice(_BaseADBDevice):
    def screen_record(self) -> typing.Callable:
        device_path = f"/data/local/tmp/{int(time.time())}.mp4"
        full_cmd = self.build_shell_cmd(["screenrecord", device_path])
        proc = subprocess.Popen(full_cmd)
        time.sleep(0.1)
        assert proc.poll() is None, "screen record start failed"

        def stop(pc_path: str = None) -> str:
            proc.terminate()
            proc.kill()

            # todo at least system6
            self.shell(["pkill", "screenrecord"])

            return self.pull(device_path, pc_path)

        return stop
