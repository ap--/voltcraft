# voltcraft.pps

[![PyPI](https://img.shields.io/pypi/v/voltcraft)](https://pypi.org/project/voltcraft/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/voltcraft?label=pypi)](https://pypi.org/project/voltcraft/)
[![MIT license](http://img.shields.io/badge/license-MIT-yellowgreen.svg)](http://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/ap--/voltcraft.svg)](https://github.com/ap--/voltcraft/issues)
[![Github Sponsors](https://img.shields.io/badge/github-sponsors-blue)](https://github.com/sponsors/ap--)

Python module for controlling Voltcraft PPS powersupplies.
<br>Available at [www.conrad.com](https://www.conrad.com/search?search=voltcraft%20pps)

```python
from voltcraft.pps import PPS

supply = PPS(port="/dev/ttyUSB0", reset=True)

supply.voltage(10.0)
supply.current(2.0)
supply.output(1)
```
