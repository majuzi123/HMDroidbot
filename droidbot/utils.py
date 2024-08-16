import re
import functools
from datetime import datetime
import warnings

# logcat regex, which will match the log message generated by `adb logcat -v threadtime`
LOGCAT_THREADTIME_RE = re.compile('^(?P<date>\S+)\s+(?P<time>\S+)\s+(?P<pid>[0-9]+)\s+(?P<tid>[0-9]+)\s+'
                                  '(?P<level>[VDIWEFS])\s+(?P<tag>[^:]*):\s+(?P<content>.*)$')


def lazy_property(func):
    attribute = '_lazy_' + func.__name__

    @property
    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, attribute):
            setattr(self, attribute, func(self))
        return getattr(self, attribute)

    return wrapper


def parse_log(log_msg):
    """
    parse a logcat message
    the log should be in threadtime format
    @param log_msg:
    @return:
    """
    m = LOGCAT_THREADTIME_RE.match(log_msg)
    if not m:
        return None
    log_dict = {}
    date = m.group('date')
    time = m.group('time')
    log_dict['pid'] = m.group('pid')
    log_dict['tid'] = m.group('tid')
    log_dict['level'] = m.group('level')
    log_dict['tag'] = m.group('tag')
    log_dict['content'] = m.group('content')
    datetime_str = "%s-%s %s" % (datetime.today().year, date, time)
    log_dict['datetime'] = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")

    return log_dict


def get_available_devices():
    """
    Get a list of device serials connected via adb
    :return: list of str, each str is a device serial number
    """
    import subprocess
    r = subprocess.check_output(["adb", "devices"])
    if not isinstance(r, str):
        r = r.decode()
    devices = []
    for line in r.splitlines():
        segs = line.strip().split()
        if len(segs) == 2 and segs[1] == "device":
            devices.append(segs[0])
    return devices


def weighted_choice(choices):
    import random
    total = sum(choices[c] for c in list(choices.keys()))
    r = random.uniform(0, total)
    upto = 0
    for c in list(choices.keys()):
        if upto + choices[c] > r:
            return c
        upto += choices[c]


def safe_re_match(regex, content):
    if not regex or not content:
        return None
    else:
        return regex.match(content)


def md5(input_str):
    import hashlib
    return hashlib.md5(input_str.encode('utf-8')).hexdigest()

def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"Function '{func.__name__}' is deprecated: {reason}", DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator