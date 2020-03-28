import subprocess
import typing
import time
import os

try:
    from loguru import logger as logging
except ImportError:
    import logging

from minadb.utils import run_cmd, run_cmd_no_wait


class _BaseADBDevice(object):
    """
    foundation part
    """

    def __init__(self, serial_no: str = None):
        # should not do the real check (connected or not) here
        self.serial_no: str = serial_no or ""
        if self.serial_no:
            self.basic_cmd: typing.List[str] = ["adb", "-s", self.serial_no]
        else:
            self.basic_cmd: typing.List[str] = ["adb"]

    def build_shell_cmd(
        self, cmd: typing.Union[str, typing.List[str]]
    ) -> typing.List[str]:
        if isinstance(cmd, str):
            cmd = cmd.split()
        return [*self.basic_cmd, "shell", *cmd]

    def build_no_shell_cmd(
        self, cmd: typing.Union[str, typing.List[str]]
    ) -> typing.List[str]:
        if isinstance(cmd, str):
            cmd = cmd.split()
        return [*self.basic_cmd, *cmd]

    def shell(
        self, cmd: typing.Union[str, typing.List[str]], no_wait: bool = False
    ) -> typing.Union[str, subprocess.Popen]:
        run = run_cmd_no_wait if no_wait else run_cmd
        return run(self.build_shell_cmd(cmd))

    def no_shell(
        self, cmd: typing.Union[str, typing.List[str]], no_wait: bool = False
    ) -> typing.Union[str, subprocess.Popen]:
        run = run_cmd_no_wait if no_wait else run_cmd
        return run(self.build_no_shell_cmd(cmd))

    def push(self, pc_path: str, device_path: str) -> str:
        cmd = ["push", pc_path, device_path]
        return run_cmd(self.build_no_shell_cmd(cmd))

    def pull(self, device_path: str, pc_path: str) -> str:
        cmd = ["pull", device_path, pc_path]
        return run_cmd(self.build_no_shell_cmd(cmd))

    def forward(self, local: str, remote: str, no_rebind: bool = None) -> str:
        """
        adb forward

        # local:  pc
        # remote: android
        """
        if no_rebind:
            return self.no_shell(["forward", "--no-rebind", local, remote])
        return self.no_shell(["forward", local, remote])

    def forward_remove(self, connection_name: str) -> str:
        return self.no_shell(["forward", "--remove", connection_name])

    def forward_remove_all(self) -> str:
        return self.no_shell(["forward", "--remove-all"])

    def forward_list(self) -> typing.List[typing.List[str]]:
        fl = self.no_shell(["forward", "--list"])
        return [each.split() for each in fl.split("\n") if each]

    def reverse(self, remote: str, local: str, no_rebind: bool = None) -> str:
        """
        adb reverse

        # local:  pc
        # remote: android
        """
        if no_rebind:
            return self.no_shell(["reverse", "--no-rebind", local, remote])
        return self.no_shell(["reverse", local, remote])

    def reverse_remove(self, connection_name: str) -> str:
        return self.no_shell(["reverse", "--remove", connection_name])

    def reverse_remove_all(self) -> str:
        return self.no_shell(["reverse", "--remove-all"])

    def reverse_list(self) -> typing.List[typing.List[str]]:
        fl = self.no_shell(["reverse", "--list"])
        return [each.split() for each in fl.split("\n") if each]


class _Process(object):
    def __init__(self, raw: typing.List[str]):
        self.raw: typing.List[str] = raw
        self.raw_str: str = " ".join(raw)
        # todo index sometimes is buggy
        self.pid: int = int(raw[1])
        self.ppid: int = int(raw[2])


class OriginADBDevice(_BaseADBDevice):
    """
    common api layer
    same as adb command
    """

    def ps(self) -> typing.List[_Process]:
        raw: str = self.shell(["ps"])
        proc_list: typing.List[str] = raw.split("\n")[1:-1]
        proc_list: typing.List[typing.List[str]] = [
            [i for i in each.split(" ") if i] for each in proc_list
        ]
        proc_list: typing.List[_Process] = [_Process(each) for each in proc_list]
        return proc_list

    def svc_wifi(self, status: bool) -> str:
        return self.shell(["svc", "wifi", "enable" if status else "disable"])

    def svc_bluetooth(self, status: bool) -> str:
        return self.shell(["svc", "bluetooth", "enable" if status else "disable"])

    def wm_size(self) -> typing.List[int]:
        content = self.shell(["wm", "size"])
        return [int(each) for each in content.split()[-1].split("x")[:2]]

    def input_keyevent(self, key_code: int) -> str:
        return self.shell(["input", "keyevent", str(key_code)])

    def input_text(self, text: str) -> str:
        return self.shell(["input", "text", f'"{text}"'])

    def input_tap(self, x: int, y: int) -> str:
        return self.shell(["input", "tap", x, y])

    def input_swipe(self, x1: int, y1: int, x2: int, y2: int) -> str:
        return self.shell(["input", "swipe", x1, y1, x2, y2])

    def am_force_stop(self, package_name: str) -> str:
        return self.shell(["am", "force-stop", package_name])

    def am_kill(self, package_name: str, *options) -> str:
        return self.shell(["am", "kill", *options, package_name])

    def am_start(self, package_name: str, *options) -> str:
        return self.shell(["am", "start", *options, package_name])

    def am_instrument(self, args: typing.Union[str, list], no_wait: bool = None) -> str:
        prefix = ["am", "instrument"]
        if isinstance(args, list):
            return self.shell([*prefix, *args], no_wait=no_wait)
        return self.shell(" ".join(prefix) + " " + args, no_wait=no_wait)

    def pm_clear(self, package_name: str) -> str:
        return self.shell(["pm", "clear", package_name])

    def pm_list_package(self) -> typing.List[str]:
        package_list = self.shell(["pm", "list", "package"]).split(os.linesep)
        return [each.split(":")[1] for each in package_list if each]

    def pm_disable(self, package_name: str) -> str:
        return self.shell(["pm", "disable", package_name])

    def pm_enable(self, package_name: str) -> str:
        return self.shell(["pm", "enable", package_name])

    def install(self, pc_path: str, flag: typing.List[str] = None) -> str:
        if not flag:
            flag: typing.List[str] = ["-r", "-d"]
        return self.no_shell(["install", *flag, pc_path])

    def uninstall(self, package_name, flag: typing.List[str]) -> str:
        if not flag:
            # -k
            flag: typing.List[str] = []
        return self.no_shell(["uninstall", *flag, package_name])

    def getprop(self, name: str = None) -> typing.Union[typing.Dict[str, str], str]:
        if name:
            return self.shell(["getprop", name])
        raw = self.shell(["getprop"])
        raw = [each.split(":") for each in raw.split(os.linesep) if each]

        result = dict()
        for each in raw:
            try:
                result[each[0][1:-1]] = each[1].lstrip()[1:-1]
            except IndexError:
                logging.warning(f"format error: {each}")
        return result

    def uiautomator_dump(self, path: str = "/data/local/tmp/layout.xml") -> str:
        return self.shell(["uiautomator", "dump", path])

    def cat(self, path: str) -> str:
        return self.shell(["cat", path])


class ADBDevice(OriginADBDevice):
    """
    high level and custom api layer
    support more complex functions
    """

    def press_home(self) -> str:
        return self.keyevent(3)

    def press_back(self) -> str:
        return self.keyevent(4)

    def press_menu(self) -> str:
        return self.keyevent(187)

    def switch_to_previous_app(self, duration: float = 1.0):
        self.press_menu()
        time.sleep(duration)
        self.press_menu()

    def is_package_installed(self, package_name: str) -> bool:
        return package_name in self.pm_list_package()

    def kill_process_by_id(self, process_id: int, signal: int = None) -> str:
        if not signal:
            return self.shell(["kill", process_id])
        return self.shell(["kill", signal, process_id])

    def kill_process_by_name(self, process_name: str, signal: int = None):
        for each in self.ps():
            if process_name in each.raw_str:
                logging.info(f"found process ({each.pid}): {each.raw_str}")
                return self.kill_process_by_id(each.pid, signal)
        logging.warning(f"no process named: {process_name}")

    def force_home(self, loop_time: int = 3):
        for _ in range(loop_time):
            self.press_back()
            self.press_home()

    def clean_recent(self, duration: float = 1.0):
        self.force_home()
        launcher = self.current_app()
        self.switch_to_previous_app()
        time.sleep(duration)
        cur = self.current_app()
        while cur != launcher:
            self.pm_disable(cur)
            self.pm_enable(cur)
            time.sleep(duration)
            self.switch_to_previous_app()
            time.sleep(duration)
            cur = self.current_app()

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

    def is_screen_on(self) -> bool:
        output = self.shell(["dumpsys", "power"])
        return "mHoldingDisplaySuspendBlocker=true" in output

    def open_browser(self, url: str) -> str:
        return self.shell(
            ["am", "start", "-a", "android.intent.action.VIEW", "-d", url]
        )

    def current(self) -> typing.List[str]:
        raw = self.shell(["dumpsys", "window", "windows"])
        flag = "mCurrentFocus"
        for each_line in raw.split(os.linesep):
            if flag in each_line:
                logging.debug(each_line)
                return each_line.split()[-1][:-1].split("/")
        raise RuntimeError("current status is empty")

    def current_app(self) -> str:
        return self.current()[0]

    def current_activity(self) -> str:
        return self.current()[1]

    def ratio2position(self, x: float, y: float) -> typing.Tuple:
        w, h = self.get_width_and_height()
        return w * x, h * y

    def center_point(self) -> typing.Tuple[float]:
        return self.ratio2position(0.5, 0.5)

    def smart_swipe(self, from_: str, to: str, ratio: float = 0.25) -> str:
        assert 0 <= ratio <= 0.5, "ratio range (float): [0, 0.5]. default: 0.25"
        half = 0.5
        point_dict = {
            "c": (half, half),
            "w": (half - ratio, half),
            "e": (half + ratio, half),
            "n": (half, half - ratio),
            "s": (half, half + ratio),
        }

        return self.swipe(
            *self.ratio2position(*point_dict[from_]),
            *self.ratio2position(*point_dict[to]),
        )

    def screenshot(self, to_sdcard: str = None, to_pc: str = None):
        sdcard_path = r"/data/local/tmp/minadb_shot.png"
        if to_sdcard:
            sdcard_path = to_sdcard

        self.shell(["screencap", "-p", sdcard_path])
        if to_pc:
            self.pull(sdcard_path, to_pc)

    def play_audio(self, source_path: str) -> str:
        return self.shell(
            [
                "am",
                "start",
                "-a",
                "android.intent.action.VIEW",
                "-t",
                "audio/mp3",
                "-d",
                f"file://{source_path}",
            ]
        )

    def play_video(self, source_path: str) -> str:
        return self.shell(
            [
                "am",
                "start",
                "-a",
                "android.intent.action.VIEW",
                "-t",
                "video/*",
                "-d",
                f"file://{source_path}",
            ]
        )

    def dump_ui(self) -> str:
        path = r"/data/local/tmp/layout.xml"
        self.uiautomator_dump(path)
        return self.cat(path)

    # alias
    tap = click = OriginADBDevice.input_tap
    swipe = OriginADBDevice.input_swipe
    window_size = get_width_and_height = OriginADBDevice.wm_size
    force_stop = app_stop = OriginADBDevice.am_force_stop
    clear_cache = app_clear = OriginADBDevice.pm_clear
    list_package = OriginADBDevice.pm_list_package
    keyevent = OriginADBDevice.input_keyevent
    set_bluetooth = OriginADBDevice.svc_bluetooth
    set_wifi = OriginADBDevice.svc_wifi
    is_installed = is_package_installed
    press_recent = press_switch = press_menu
    screencap = screenshot
    play_music = play_audio
