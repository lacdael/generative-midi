#!/usr/bin/env python3
# coding: utf-8

# # Gerative Midi
# 
# Python code to generate continuious music sequences.

from random import randint
import time
import traceback
import pygame.midi

progressions = [
    "i-vi-iv-v",
    "ii-iii-i-i",
    "iv-iii-ii-i",
    "iii-v-i-i",
    "ii-v-i-i",
    "i-iv-ii-v",
    "i-v-vi-iv",
    "i-vi-ii-v",
    "v-iv-i-i"];

progressions = [ progressions[i].split("-") for i in range(0,len(progressions)) ];

SCALES = {
  'major': (2, 2, 1, 2, 2, 2, 1),
  'minor': (2, 1, 2, 2, 1, 2, 2),
  'melodicminor': (2, 1, 2, 2, 2, 2, 1),
  'harmonicminor': (2, 1, 2, 2, 1, 3, 1),
  'pentatonicmajor': (2, 2, 3, 2, 3),
  'bluesmajor': (3, 2, 1, 1, 2, 3),
  'pentatonicminor': (3, 2, 2, 3, 2),
  'bluesminor': (3, 2, 1, 1, 3, 2),
  'augmented': (3, 1, 3, 1, 3, 1),
  'diminished': (2, 1, 2, 1, 2, 1, 2, 1),
  'chromatic': (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
  'wholehalf': (2, 1, 2, 1, 2, 1, 2, 1),
  'halfwhole': (1, 2, 1, 2, 1, 2, 1, 2),
  'wholetone': (2, 2, 2, 2, 2, 2),
  'augmentedfifth': (2, 2, 1, 2, 1, 1, 2, 1),
  'japanese': (1, 4, 2, 1, 4),
  'oriental': (1, 3, 1, 1, 3, 1, 2),
  'ionian': (2, 2, 1, 2, 2, 2, 1),
  'dorian': (2, 1, 2, 2, 2, 1, 2),
  'phrygian': (1, 2, 2, 2, 1, 2, 2),
  'lydian': (2, 2, 2, 1, 2, 2, 1),
  'mixolydian': (2, 2, 1, 2, 2, 1, 2),
  'aeolian': (2, 1, 2, 2, 1, 2, 2),
  'locrian': (1, 2, 2, 1, 2, 2, 2),
}

_BASS_MIDI_KEYS = {"c":36,"c#":37,"d":38,"d#":39,"e":40,"f":41,"f#":42,"g":43,"g#":44,"a":45,"a#":46,"b":47};
_LEAD_MIDI_KEYS = {"c":60,"c#":61,"d":62,"d#":63,"e":64,"f":65,"f#":66,"g":67,"g#":68,"a":69,"a#":70,"b":71};

def getMidiKey( scale, ind, root):
    if scale not in SCALES:
        return 0;
    i = 0;
    if ind == "i":
        return root;
    elif ind == "ii":
        return root + SCALES[ scale ][0];
    elif ind == "iii":
        return root + sum(SCALES[ scale ][0:2]);
    elif ind == "iv":
        return root + sum(SCALES[ scale ][0:3]);
    elif ind == "v":
        return root + sum(SCALES[ scale ][0:4]);                      
    elif ind == "vi":
        return root + sum(SCALES[ scale ][0:5]);


#ARGUMENTS
SCALE = 'pentatonicmajor';
ROOT = "c";
BPM = 86
MIDI_PORT = 0;
_RAND = 2;

drumTabs = """
C1|----------------|------x---------|--------------x-|--------------x-|
HH|x-x-x-x-x-x-x-x-|x-x-x---x-x-x-x-|x-x-x-x-x-x-x---|x-x-x---x-x-x---|
SD|----o-------o---|----o-------o---|----o-------o---|----o-------o---|
BD|o-----o---o-----|o-----o---o-----|o-----o-o-------|o-----o---o-----|"""

drumFillTabs = """
C1|------------x-x-|------x-------x-|--------x-x-x-x-|------------x-x-|
HH|x-x-x-x-x-x-----|x-x-x---x-x-x---|x-x-x-x---------|x-x-x-x-x-x-----|
SD|----o-------o-o-|----o-------o---|----o-------o-o-|----o-------o-o-|
BD|o-----o---o-----|o-----o-o-o---o-|o-----o-o-------|o---------o-----|"""


ROOT_BASS = _BASS_MIDI_KEYS[ ROOT ];
ROOT_LEAD = _LEAD_MIDI_KEYS[ ROOT ];

def getCord( r):
    if not hasattr(getCord,"pnt"):
        getCord.pnt = 0
    if not hasattr(getCord,"progPnt"):
        getCord.progPnt = 0
    cord = progressions[ getCord.progPnt ][ getCord.pnt ];
    if randint(0,r) == 0:
        tries = 0;
        while tries < 10:
            tries += 1;
            newProgPnt = randint(0,len(progressions) - 1);
            if progressions[ getCord.progPnt ][ getCord.pnt ] in progressions[ newProgPnt ]:
                newPnt = 0;
                for ii in range(0, len( progressions[ newProgPnt ])):
                    if progressions[ getCord.progPnt ][ getCord.pnt ] == progressions[ newProgPnt ][ ii ]:
                        newPnt = ii;
                        break;
                getCord.progPnt = newProgPnt;
                newPnt += 1
                if newPnt >= len( progressions[ getCord.progPnt ] ):
                    newPnt = 0;
                getCord.pnt = newPnt;
        if tries == 10:
            getCord.pnt +=1;
    else:
        getCord.pnt +=1;
    if getCord.pnt >= len(progressions[ getCord.progPnt ]):
        getCord.pnt = 0;
    return cord;

def parseTab( s ):
    tmpDrums = list(filter(None,s.splitlines()));
    tmp = {};
    for i in range(0, len(tmpDrums)):
        lbl , pattern = tmpDrums[i].split("|",1)
        tmp[ lbl ] = list(filter(None,pattern.split("|")));
    if "C1" not in tmp:
        tmp["C1"] = [ "----------------" for i in range( 0 , len( tmp[ list(tmp.keys())[0] ] ) )];
    if "HH" not in tmp:
        tmp["HH"] = [ "----------------" for i in range( 0 , len( tmp[ list(tmp.keys())[0] ] ) )];
    if "SD" not in tmp:
        tmp["SD"] = [ "----------------" for i in range( 0 , len( tmp[ list(tmp.keys())[0] ] ) )];
    if "BD" not in tmp:
        tmp["BD"] = [ "----------------" for i in range( 0 , len( tmp[ list(tmp.keys())[0] ] ) )];
    return tmp;

drums = parseTab( drumTabs );
drumFills = parseTab( drumFillTabs );

running = True

bar = 1;
cord = None;
cord = getCord( _RAND);

SIXTEENTH = ( 60 / (BPM*4) );

print("Setting up midi.")

pygame.midi.init()
player = pygame.midi.Output( MIDI_PORT );

noteBD = None;
noteSD = None;
noteHH = None;
noteC1 = None;
noteBass = None;
noteLead = None;

drumPnt = randint(0,len(drums["BD"]) - 1);
drumFillPnt = randint(0,len(drumFills["BD"]) - 1);
sixteenthPnt = 0;

while running:
    try:
        seq = None;
        pnt = 0;
        if bar == 4:
            pnt = drumFillPnt;
            seq = drumFills
        else:
            seq = drums
            pnt = drumPnt
        
        #DB
        if seq["BD"][ pnt ][ sixteenthPnt ] != "-":
            player.note_on( 65 , velocity = 100,channel=0 );
            noteBD = 65;
        elif noteBD:
            player.note_off( 65,channel=0);
            noteBD = None;
        #SD 
        if seq["SD"][ pnt ][ sixteenthPnt ] != "-":
            player.note_on( 65 , velocity = 100,channel=1 );
            noteSD = 65;
        elif noteSD:
            player.note_off( 65,channel=1);
            noteSD = None;
        #HH
        if seq["HH"][ pnt ][ sixteenthPnt ] != "-":
            player.note_on( 65 , velocity = 100,channel=2 );
            noteHH = 65;
        elif noteHH:
            player.note_off( 65,channel=2);
            noteHH = None;
        #C1
        if seq["C1"][ pnt ][ sixteenthPnt ] != "-":
            player.note_on( 65 , velocity = 100,channel=3 );
            noteC1 = 65;
        elif noteC1:
            player.note_off( 65,channel=3);
            noteC1 = None;
        #BASS
        if ( seq["BD"][ pnt ][ sixteenthPnt ] != "-" or
            seq["SD"][ pnt ][ sixteenthPnt ] != "-"):
            if randint(0,_RAND) == 0:
                noteBass = getMidiKey(SCALE, cord, ROOT_BASS );
                player.note_on( noteBass , velocity = 100,channel=4 );
        elif noteBass:
            player.note_off( noteBass , velocity = 100,channel=4 );
        
        
        if sixteenthPnt == 0:
            #LEAD
            if noteLead:
                player.note_off( noteLead, velocity = 100,channel=5 );
            cord = getCord( _RAND );
            noteLead = getMidiKey(SCALE, cord, ROOT_LEAD);
            player.note_on( noteLead , velocity = 100,channel=5 );
            
            #NEW DRUm Pnt
            drumPnt
            if bar == 3:
                drumFillPnt = randint(0,len(drumFills) - 1);
            else:
                drumPnt = randint(0,len(drums) - 1);
        elif sixteenthPnt == 15:
            bar += 1;
            if bar > 4:
                bar = 1;
            
        sixteenthPnt += 1;
        if sixteenthPnt > 15:
            sixteenthPnt = 0;
        
        time.sleep( SIXTEENTH );
    except:
        traceback.print_exc()
        break;


