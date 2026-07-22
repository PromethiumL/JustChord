# JustChord
[![version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://semver.org) [![python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org)

A real-time MIDI visualization tool for chords with a grand staff view.

Uses RtMidi for the driver and PyQt6 for the widgets.

![](./sample.png)

## Features
- Chord recognition
- Customizable chord dictionary
- Automatic key detection
- Roman-numeral (functional harmony) display
- Individually customizable widgets
- Built-in virtual MIDI keyboard with playback

## Requirements
- Python **3.13** (requires ≥ 3.12)
- [`uv`](https://docs.astral.sh/uv/) for dependency management

## Installation

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/), then sync the environment:

```bash
$ uv sync
```

This creates a virtual environment and installs the dependencies (`pyqt6`, `python-rtmidi`).

## Usage

Launch it with either:

```bash
$ uv run justchord
```

or

```bash
$ uv run main.py
```

- Two widgets: the staff and the chords. Drag them wherever you want.
- **Right-click** on each widget for more options: color, font, MIDI device selection etc.
- Use the mouse wheel to adjust window opacity.

### Keyboard shortcuts
- `Tab` switch the active window
- `Ctrl + R` toggle Roman-numeral (functional harmony) notation
- number keys: set the tonic by the number of fifths in key signatures (press `S` for sharps)
- `Space` : simulates the sustain pedal on the virtual MIDI keyboard

## Configuration

Settings and the chord dictionary live in `.jsonc` files under `data/` (JSON with comments):

- `data/config.jsonc` : core behaviors (default key, auto key detection, slash chords, excluded intervals) plus chord-label and staff display options.
- `data/chords.jsonc` : the chord dictionary. Add a new entry by copying an existing line and giving it a set of `intervals`, a `name`, and a `complexity`.

## Current Development

I'm still improving the architecture of this, but don't have recent plans for major updates.

Please feel free to open issues or feature requests.
