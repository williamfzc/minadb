import argparse

from minadb import ADBDevice


def main():
    parser = argparse.ArgumentParser(description="minadb cli")
    parser.add_argument("-s", "--serial_no", nargs="?")
    parser.add_argument("-c", "--command", nargs="*")
    args = parser.parse_args()

    serial_no = args.serial_no
    command = args.command
    if not command:
        raise RuntimeError("no command")
    func = command[0]
    extras = command[1:]
    device = ADBDevice(serial_no)
    assert hasattr(device, func), f"no function named {func}"
    getattr(device, func)(*extras)


if __name__ == "__main__":
    main()
