# voltcraft.pps

Python module for controlling Voltcraft PPS powersupplies.
<br>Available at [www.conrad.com](https://www.conrad.com/search?search=voltcraft%20pps)

```python
from voltcraft.pps import PPS

supply = PPS(port="/dev/ttyUSB0", reset=True)

supply.voltage(10.0)
supply.current(2.0)
supply.output(1)
```


