import typing

from minadb.utils import run_cmd


class ADBClient(object):
    def devices(self) -> typing.List[typing.List[str]]:
        output = str(run_cmd(["adb", "devices"]))
        raw_device_list = [each.split("\t") for each in output.split("\n")[1:] if each]

        # [['123456E', 'device'], ['123456F', 'offline']]
        return raw_device_list
