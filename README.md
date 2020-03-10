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

lots of built-in functions:

```python
d.set_bluetooth(True)
d.set_wifi(True)
d.click(100, 200)
d.swipe(100, 200, 400, 400)

# ...
```

and more:

```python
['am_force_stop',
 'am_instrument',
 'am_kill',
 'am_start',
 'app_clear',
 'app_stop',
 'center_point',
 'clean_recent',
 'clear_cache',
 'click',
 'current',
 'current_activity',
 'current_app',
 'force_home',
 'force_stop',
 'get_width_and_height',
 'getprop',
 'input_keyevent',
 'input_swipe',
 'input_tap',
 'input_text',
 'install',
 'is_installed',
 'is_package_installed',
 'is_screen_on',
 'keyevent',
 'kill_process_by_id',
 'kill_process_by_name',
 'list_package',
 'open_browser',
 'play_audio',
 'play_music',
 'play_video',
 'pm_clear',
 'pm_disable',
 'pm_enable',
 'pm_list_package',
 'press_back',
 'press_home',
 'press_menu',
 'press_recent',
 'press_switch',
 'ps',
 'ratio2position',
 'screen_record',
 'screencap',
 'screenshot',
 'set_bluetooth',
 'set_wifi',
 'smart_swipe',
 'svc_bluetooth',
 'svc_wifi',
 'swipe',
 'switch_to_previous_app',
 'tap',
 'uninstall',
 'window_size',
 'wm_size',
 ...
]
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
