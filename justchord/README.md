# JustChord

A real-time (Midi) visualization tool for chords with grand staff view.

Uses RtMidi for driver and PyQt for widgets 

## Features

- Chord Recognition
- Customize chord dictionary
- Auto Key detection
- Individual customizable widgets

## Installation

on Python 3.6 or above, install `python-rtmidi` and `pyqt5`:

```bash
$ pip3 -r install requirements.txt
```

 Then launch it by:

```
$ python3 main.py
```
- Two widgets: staff and chords are on the left and right by default. Drag them to where ever you want.

- Right click on chords (only chords, currently) for more options. 

- Default midi input port can be modified in `gui.py`

- The Chord dictionary is stored in `./core/constants.py`. You can add new entry by copy/paste an existing line.

## Current Development

I'm still trying to improve on details, and make this program's logical structure better to understand.

Please feel free to create issues or make any comments. 

