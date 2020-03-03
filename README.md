# minadb

![PyPI](https://img.shields.io/pypi/v/minadb)

min adb client implemented with subprocess, nothing special but useful and stable.

## goal

i am tired of so many different kinds of adb clients, and now I need a simple/lightweight/stable version for some normal cases.

as you can see, this repo will keep using subprocess to make it simple and origin, and no fucking additional (sometimes buggy) socket and something else confused.

## usage

this repo aims at making everything simple enough.

```python
from minadb import ADBDevice
from minadb import ADBClient

# client
cli = ADBClient()
d_list = cli.devices()
print(d_list)
# [['123456F', 'device']]

# device
d = ADBDevice("123456F")
# or only one device connected, you can ignore the serial no
d = ADBDevice()

resp = d.shell(["am", "start", "com.android.camera"])
print(resp)
```

and some built-in functions please read the code directly.

```python
d.set_bluetooth(True)
d.set_wifi(True)
d.click(100, 200)
d.swipe(100, 200, 400, 400)

# ...
```

## notice

- i know some other python packages are designed to be used in production.
- they are good, i know, and i have paid a lot on these packages.
- i am tired of weird bugs.
- this repo may have some origin bugs from adb, of course.

## development

- this package should be very very easy to be hacked.
- just fork, add some adb command, and PR if you want.
- feel free to build it together.

## license

MIT
