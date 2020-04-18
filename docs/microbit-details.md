# The Micro:Bit side of things:

## Detailed install

## Code details

### Animation requirements

The "busy" and "free" are intended built as short animations to meet the following requirements:

* Don't be too distracting
* Animate slightly so we can tell the code is running and not frozen
* Be visible from from 8 meters away
* Look correct even if MicroBit is oriented "upside down" or rotated 90 degrees for easier placement in the environment.

### Additional animations

Currently only 2 animations are in the current implementation a lightly pulsing "X" and a rotating circle.

More animations could easily be added and associated to different numbers. Supporting more than 10 animations would require recoding the
parsing algorithms to look at more than one character in the command string from the serial port.

