## Just Chord! 1.1.0
- Virtual MIDI keyboard! with `space` key as the sustain pedal.

## Just Chord! 1.0.11
- Fixed some wrong chord name.

## Just Chord! 1.0.10
- Fixed wrong accidental displaying bug. 

## Just Chord! 1.0.9
- Improvement on performance of `staffwidget` by reusing vacant widgets for less reloading.
- Slightly adjusted the offset of double-flat accidental sign.

## Just Chord! 1.0.8
- Greatly boosted performance by replacing all the `eval` calls to `dict` queries.
- Fixed the bug of midi selection not working

## Just Chord! 1.0.1
- Added midi in selection dialog
- Windows opacity. Adjusted by mouse wheel.
- Frameless main window, thus nicer appearance

## Just Chord! 1.0
- I finally decide to rename it to `Just Chord` and publish it on github. It's hard to give it a new name!
- Added context menu for `chordwindow`

## ChordBar 0.11
- Added auto key detection using 'window' method.
- Added key signature support to staff window
- Merged windows one main window.
- Now in staff window, note with accidental can be simplified according to the key signature.
- Fixed the bug that some notes won't turn off when monitor receives new MIDI messages.
- Improvement on the constructors using config variable.

## ChordBar 0.10
- TODO: add keyboardWidget

## ChordBar 0.9
- Added StaffWindow
- Deprecated widget manager
- Less running resource when monitoring MIDI activities.
- Added MIDI message queue
- Change chord data to string
- Optimized for chord data
- Added functions to calculate accurate name of a chord tone
- Bugs:
    - No support for complex accidental signatures
    - Unstable accidental sign position

## Chord Indicator 0.7
- Draggable!
- make the classes in separate files.
- Testing the analysis of chord progression no GUI now.


## Chord Indicator 0.6
- More standardized numerals
- fixed the bug when switching between sharp/flat

## Chord Indicator 0.5
- Use `Tab` to switch active windows.
- Added roman style for functional harmony (I IV V...), toggled with `Ctrl + R`,
  and you can set the tonal by press the number of the key signatures. 
  (if sharp press `S`)
- More scales...

## Chord Indicator 0.4
- Now the `MainWindow` is changed to `Widget` for better layout.
- The Chord's name now is a pair (root, name)
- Bigger root note and auto repainting.
- Rest Chords showed below (optional)

## Chord Indicator 0.3
- the chordlabel was separated into `MainWindow`'s subclass `ChordWindow`
- deleted the `InitRtMidi` thread and made it synchronized

## Chord Indicator 0.2
- GUI with PyQt
- More chords
- Better chord indentification and judgement
