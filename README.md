A script that generates midi drum, bass and lead sequences, in a 4:4 time signature

# Quick Start:

- Run with defaults: `./generateMidi.py`  
- help: `./generateMidi.py -?`
- `./generateMidi.py --scale <scale> --root <root> --BPM <bpm> --RAND <randomization> --PORT <port> --DRUMS <tab file> --FILL <tab file> --PROGRESSIONS <progressions file> --ARP <arpeggiator sequence> --BASS-ARP <arpeggiator sequence> --SLOWED <slowed value>`  

## Arguments 

- scale: major, minor, melodicminor, harmonicminor, pentatonicmajor, bluesmajor, pentatonicminor, bluesminor, augmented, diminished, chromatic, wholehalf, halfwhole, wholetone, augmentedfifth, japanese, oriental, ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian  
- root: c,c#,d,d#,e,f,f#,g,g#,a,a#,b  
- randomization: 1-5 (1 = most, 5 = least, default = 2)  
- port: midi port name (chose midi device when prompted) 
- tab file: a file containing drum tabs, with soxteenth divisions, and labels: BD, SD, HH, C1  
- progressions file: a file containing cord progressions e.g `i-vi-iv-v`
- arpeggiator sequence e.g. `1-3--53-`
- slowed value specifies how many bars until a possible cord change

# defaults

## Progressions

`i-vi-iv-v`  
`ii-iii-i-i`  
`iv-iii-ii-i`  
`iii-v-i-i`  
`ii-v-i-i`  
`i-iv-ii-v`  
`i-v-vi-iv`  
`i-vi-ii-v`  
`v-iv-i-i`  

## Drum tabs
`C1|----------------|------x---------|--------------x-|--------------x-|`  
`HH|x-x-x-x-x-x-x-x-|x-x-x---x-x-x-x-|x-x-x-x-x-x-x---|x-x-x---x-x-x---|`  
`SD|----o-------o---|----o-------o---|----o-------o---|----o-------o---|`  
`BD|o-----o---o-----|o-----o---o-----|o-----o-o-------|o-----o---o-----|`

## Fill tabs

`C1|------------x-x-|------x-------x-|--------x-x-x-x-|------------x-x-|`  
`HH|x-x-x-x-x-x-----|x-x-x---x-x-x---|x-x-x-x---------|x-x-x-x-x-x-----|`  
`SD|----o-------o-o-|----o-------o---|----o-------o-o-|----o-------o-o-|`  
`BD|o-----o---o-----|o-----o-o-o---o-|o-----o-o-------|o---------o-----|`

# dependencies:

- mido
- apscheduler

# MIDI Mapping

|  Instrument | Channel | Key      |
|-------------|---------|----------|
| Bass Drum   | 1       | 36 (C2)  |
| Snare Drum  | 1       | 38 (D2)  |
| Hi-Hat      | 1       | 42 (F#2) |
| Cymbal      | 1       | 49 (C#3) |
| Ride1†      | 1       | 51 (D#3) |
| Bass        | 2       |  -       |
| Pad         | 3       |  -       |
| Lead ditty  | 4       |  -       |

† Intendend to be used as sample triggers.
