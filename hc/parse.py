import re

from . import config, vars
from .error import ParseError
from collections import OrderedDict

probe_re = re.compile(r'Z:([^\s]+) C:([^\s]+)')

# designator regexp
# X123.12 = ('X', 123.12)
# G0 = ('G', 0)
des_re = r'([{}])(-?\d+\.?\d*)'
axes_re = re.compile(des_re.format(''.join(vars.axes_designators)))
params_re = re.compile(des_re.format(''.join(vars.param_designators)))


def probe_linuxcnc(x):
    """
    Parse LinuxCNC probe result: 'Z: -4.3393123'

    Returns float in mm
    """

    try:
        return float(x[2:])
    except:
        ParseError('Unable to parse linuxcnc probe response: "{}"'.format(x))


def probe_smoothie(x):
    """
    Parse probe result: 'Z:4.3393 C:44434'

    Returns tuple of (z, c) floats of (mm, count)
    """

    x = x.strip()
    match = probe_re.match(x)

    if match is None:
        raise ParseError('Unable to parse probe response: "{}"'.format(x))

    z, c = match.groups()
    return (float(z), int(c))


def probe(x):
    """
    Parse probe according to flavor
    """

    f = config.get('flavor', default='smoothie')
    if f == 'smoothie':
        return probe_smoothie(x)[0]
    elif f == 'linuxcnc':
        return probe_linuxcnc(x)


def parse_re(input, target_re):
    """
    Run re.findall with `target_re` regexp on given `input`

    Return found targets as OrderedDict with float values.

    parse_re("G0 S3 P0.1") = {'S': 3, 'P': 0.1}

    """
    x = input.strip()
    res = target_re.findall(x)
    return OrderedDict(map(lambda x: (x[0], float(x[1])), res))


def params(input):
    return parse_re(input, params_re)


def axes(input):
    """
    Parse gcode coordinates: 'G0 X13 Y10 F500'

    Returns list of tuples of found axis movements, e.g.:
    [('X', 13), ('Y', 10)]
    """
    return parse_re(input, axes_re)


def xyz(input):
    """
    Return tuple of parsed floats from `x`.
    (30.123, 48.0, 1)

    Contains None if there's no movement of the axis
    (None, None, 1)
    """
    needle = ['X', 'Y', 'Z']
    ax = axes(input)
    out = []
    for i in needle:
        if i in ax:
            out.append(ax[i])
        else:
            out.append(None)

    return tuple(out)
