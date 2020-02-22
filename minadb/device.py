import subprocess
import typing
import time

try:
    from loguru import logger as logging
except ImportError:
    import logging

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


class _Process(object):
    def __init__(self, raw: typing.List[str]):
        self.raw: typing.List[str] = raw
        self.raw_str: str = "".join(raw)
        # todo index sometimes is buggy
        self.pid: int = int(raw[1])
        self.ppid: int = int(raw[2])


class ADBDevice(_BaseADBDevice):
    def ps(self) -> typing.List[_Process]:
        raw: str = self.shell(["ps"])
        proc_list: typing.List[str] = raw.split("\n")[1:-1]
        proc_list: typing.List[typing.List[str]] = [
            [i for i in each.split(" ") if i] for each in proc_list
        ]
        proc_list: typing.List[_Process] = [_Process(each) for each in proc_list]
        return proc_list

    def kill_process_by_id(self, process_id: int, signal: int = -2) -> str:
        return self.shell(["kill", str(signal), process_id])

    def kill_process_by_name(self, process_name: str, signal: int = -2):
        for each in self.ps():
            if process_name in each.raw_str:
                logging.info(f"found process ({each.pid}): {each.raw_str}")
                return self.kill_process_by_id(each.pid, signal)
        logging.warning(f"no process named: {process_name}")

    def screen_record(self) -> typing.Callable:
        device_path = f"/data/local/tmp/{int(time.time())}.mp4"
        full_cmd = self.build_shell_cmd(["screenrecord", device_path])
        # start recording process
        proc = subprocess.Popen(full_cmd)
        # wait for starting
        time.sleep(0.2)
        assert proc.poll() is None, "screen record start failed"
        logging.info("screen record started")

        def stop(pc_path: str = None) -> str:
            if proc.poll() is not None:
                logging.warning("screen record process already stopped")
            else:
                proc.terminate()
                proc.kill()
            self.kill_process_by_name("screenrecord")
            return self.pull(device_path, pc_path)

        return stop
