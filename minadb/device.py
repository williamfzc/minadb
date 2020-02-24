import subprocess
import typing
import time

try:
    from loguru import logger as logging
except ImportError:
    import logging

from minadb.utils import run_cmd, run_cmd_no_wait


class _BaseADBDevice(object):
    def __init__(self, serial_no: str = None):
        # should not do the real check (connected or not) here
        self.serial_no: str = serial_no or ""
        if self.serial_no:
            self.basic_cmd: typing.List[str] = ["adb", "-s", self.serial_no]
        else:
            self.basic_cmd: typing.List[str] = ["adb"]

    def build_shell_cmd(self, cmd: typing.Union[str, typing.List[str]]) -> typing.List[str]:
        if isinstance(cmd, str):
            cmd = cmd.split()
        return [*self.basic_cmd, "shell", *cmd]

    def build_no_shell_cmd(self, cmd: typing.Union[str, typing.List[str]]) -> typing.List[str]:
        if isinstance(cmd, str):
            cmd = cmd.split()
        return [*self.basic_cmd, *cmd]

    def shell(self, cmd: typing.Union[str, typing.List[str]], no_wait: bool = False) -> typing.Union[str, subprocess.Popen]:
        run = run_cmd_no_wait if no_wait else run_cmd
        return run(self.build_shell_cmd(cmd))

    def no_shell(self, cmd: typing.Union[str, typing.List[str]], no_wait: bool = False) -> typing.Union[str, subprocess.Popen]:
        run = run_cmd_no_wait if no_wait else run_cmd
        return run(self.build_no_shell_cmd(cmd))

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
        return self.shell(["kill", signal, process_id])

    def kill_process_by_name(self, process_name: str, signal: int = -2):
        for each in self.ps():
            if process_name in each.raw_str:
                logging.info(f"found process ({each.pid}): {each.raw_str}")
                return self.kill_process_by_id(each.pid, signal)
        logging.warning(f"no process named: {process_name}")

    def screen_record(self) -> typing.Callable:
        device_path = f"/data/local/tmp/{int(time.time())}.mp4"
        proc = self.shell(["screenrecord", device_path], no_wait=True)
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

    def set_wifi(self, status: bool) -> str:
        return self.shell(["svc", "wifi", "enable" if status else "disable"])

    def set_bluetooth(self, status: bool) -> str:
        return self.shell(["svc", "bluetooth", "enable" if status else "disable"])

    def keyevent(self, key_code: int) -> str:
        return self.shell(["input", "keyevent", str(key_code)])

    def force_stop(self, package: str) -> str:
        return self.shell(["am", "force-stop", package])

    def get_width_and_height(self) -> typing.List[int]:
        content = self.shell(["wm", "size"])
        return [int(each) for each in content.split()[-1].split("x")[:2]]

    def input_text(self, text: str) -> str:
        return self.shell(["input", "text", f"\"{text}\""])

    def input_tap(self, x: int, y: int) -> str:
        return self.shell(["input", "tap", x, y])

    def input_swipe(self, x1: int, y1: int, x2: int, y2: int) -> str:
        return self.shell(["input", "swipe", x1, y1, x2, y2])

    # alias
    tap = input_tap
    click = input_tap
    swipe = input_swipe
