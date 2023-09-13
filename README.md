# voltcraft.pps

[![PyPI](https://img.shields.io/pypi/v/voltcraft)](https://pypi.org/project/voltcraft/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/voltcraft?label=pypi)](https://pypi.org/project/voltcraft/)
[![MIT license](http://img.shields.io/badge/license-MIT-yellowgreen.svg)](http://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/ap--/voltcraft.svg)](https://github.com/ap--/voltcraft/issues)
[![Github Sponsors](https://img.shields.io/badge/github-sponsors-blue)](https://github.com/sponsors/ap--)

Python module for controlling Voltcraft PPS and DPPS powersupplies.
<br>Available at [www.conrad.com (PPS)](https://www.conrad.com/search?search=voltcraft%20pps)
and [www.conrad.com (DPPS)](https://www.conrad.com/search?search=voltcraft%20dpps)

```python
from voltcraft.pps import PPS

supply = PPS(port="/dev/ttyUSB0", reset=True)

supply.voltage(10.0)
supply.current(2.0)
supply.output(1)
```

Install via:
```console
pip install voltcraft
```

There's no documentation, but the module is tiny, so please just read the [voltcraft/pps.py](voltcraft/pps.py) :sparkling_heart:

It is also possible to use this module as a command-line tool

```shell
$ py -m voltcraft COM3
MODEL=DPPS3230
IMAX=31.5
VMAX=32.2
IMULT=10.0
limits=(32.2, 31.5)
reading=(14.01, 2.13, 'CV')

$ py -m voltcraft COM3 off

$ py -m voltcraft COM3 read
reading=(3.14, 0.0, 'CV')

$ py -m voltcraft COM3 read
reading=(1.7, 0.0, 'CV')
```
