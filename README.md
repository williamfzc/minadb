# minadb

the simplest adb package. implemented with subprocess, and nothing special but useful.

## goal

i am tired of so many different kinds of adb clients, and now I need a simple/lightweight/stable version for some normal cases.

as you can see, this repo will keep using subprocess to make it simple and origin, and no fucking additional (sometimes buggy) socket and something else confused.

## usage

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
resp = d.shell(["am", "start", "com.android.camera"])
print(resp)
```

and some built-in functions please read the code directly.

## notice

- i know some python packages are designed to be used in production.
- they are good, i know, and i have paid a lot on these packages.
- i am tired of weird bugs.

## development

- this package should be very very easy to be hacked.
- just fork, add some adb command, and PR if you want.
- feel free to build it together.

## license

MIT
