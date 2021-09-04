#!/usr/bin/env python3
# coding: utf-8

# # Gerative Midi
# 
# Python code to generate continuious music sequences.

from random import randint
import time
import sys
import traceback
import pygame.midi

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

def getBassNote( n ):
    if not n:
        return "__";
    for k in _BASS_MIDI_KEYS.keys():
        if n == _BASS_MIDI_KEYS[k]:
            return k;
    return "__";

def getLeadNote( n ):
    if not n:
        return "__";
    for k in _LEAD_MIDI_KEYS.keys():
        if n == _LEAD_MIDI_KEYS[k]:
            return k;
    return "__";

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

def getCord( r , progs ):
    if not hasattr(getCord,"pnt"):
        getCord.pnt = 0
    if not hasattr(getCord,"progPnt"):
        getCord.progPnt = 0
    cord = progs[ getCord.progPnt ][ getCord.pnt ];
    if randint(0,r) == 0:
        tries = 0;
        while tries < 10:
            tries += 1;
            newProgPnt = randint(0,len(progs) - 1);
            if progs[ getCord.progPnt ][ getCord.pnt ] in progs[ newProgPnt ]:
                newPnt = 0;
                for ii in range(0, len( progs[ newProgPnt ])):
                    if progs[ getCord.progPnt ][ getCord.pnt ] == progs[ newProgPnt ][ ii ]:
                        newPnt = ii;
                        break;
                getCord.progPnt = newProgPnt;
                newPnt += 1
                if newPnt >= len( progs[ getCord.progPnt ] ):
                    newPnt = 0;
                getCord.pnt = newPnt;
        if tries == 10:
            getCord.pnt +=1;
    else:
        getCord.pnt +=1;
    if getCord.pnt >= len(progs[ getCord.progPnt ]):
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

def task( player ):
    try:
        seq = None;
        pnt = 0;
        if _STATE["BAR"] == 4:
            pnt = _STATE["FILL_PNT"];
            seq = _STATE["FILLS"];
        else:
            seq = _STATE["DRUMS"]
            pnt = _STATE["DRUM_PNT"];
        
        #DB
        if seq["BD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-":
            player.note_on( 65 , velocity = 100,channel=0 );
            _STATE["NOTES"]["BD"] = 65;
        elif _STATE["NOTES"]["BD"]:
            player.note_off( 65,channel=0);
            _STATE["NOTES"]["BD"] = None;
        #SD 
        if seq["SD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-":
            player.note_on( 65 , velocity = 100,channel=1 );
            _STATE["NOTES"]["SD"] = 65;
        elif _STATE["NOTES"]["SD"]:
            player.note_off( 65,channel=1);
            _STATE["NOTES"]["SD"] = None;
        #HH
        if seq["HH"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-":
            player.note_on( 65 , velocity = 100,channel=2 );
            _STATE["NOTES"]["HH"] = 65;
        elif _STATE["NOTES"]["HH"]:
            player.note_off( 65,channel=2);
            _STATE["NOTES"]["HH"] = None;
        #C1
        if seq["C1"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-":
            player.note_on( 65 , velocity = 100,channel=3 );
            _STATE["NOTES"]["C1"] = 65;
        elif _STATE["NOTES"]["C1"]:
            player.note_off( 65,channel=3);
            _STATE["NOTES"]["C1"] = None;
        #BASS
        if ( seq["BD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-" or
            seq["SD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-"):
            if randint(0, _STATE["RAND"] ) == 0:
                _STATE["NOTES"]["BASS"] = getMidiKey( _STATE["SCALE"], _STATE["CORD"], _STATE["ROOT_BASS"] );
                player.note_on( _STATE["NOTES"]["BASS"] , velocity = 100,channel=4 );
        elif _STATE["NOTES"]["BASS"]:
            player.note_off( _STATE["NOTES"]["BASS"] , velocity = 100,channel=4 );
            _STATE["NOTES"]["BASS"] = None;
        
        
        if _STATE["SIXTEENTH_PNT"] == 0:
            #LEAD
            if _STATE["NOTES"]["LEAD"]:
                player.note_off( _STATE["NOTES"]["LEAD"], velocity = 100,channel=5 );
            _STATE["CORD"] = getCord( _STATE["RAND"] , _STATE["PROGRESSIONS"] );
            _STATE["NOTES"]["LEAD"] = getMidiKey( _STATE["SCALE"], _STATE["CORD"], _STATE["ROOT_LEAD"]);
            player.note_on( _STATE["NOTES"]["LEAD"] , velocity = 100,channel=5 );
            
            #NEW DRUm Pnt
            if _STATE["BAR"] == 3:
                _STATE["FILL_PNT"] = randint(0,len( _STATE["FILLS"] ) - 1);
            else:
                _STATE["DRUM_PNT"] = randint(0,len( _STATE["DRUMS"] ) - 1);
        elif _STATE["SIXTEENTH_PNT"] == 15:
            _STATE["BAR"] += 1;
            if _STATE["BAR"] > 4:
                _STATE["BAR"] = 1;
            
        _STATE["SIXTEENTH_PNT"] += 1;
        if _STATE["SIXTEENTH_PNT"] > 15:
            _STATE["SIXTEENTH_PNT"] = 0;
    except:
        traceback.print_exc()

_STATE = {};

def main( args ):
    global _STATE ;

    args["ROOT_BASS"] = _BASS_MIDI_KEYS[ args["ROOT"] ];
    args["ROOT_LEAD"] = _LEAD_MIDI_KEYS[ args["ROOT"] ];
    args["RUNNING"] = True
    args["BAR"] = 1;
    args["CORD"] = getCord( args["RAND"], args["PROGRESSIONS"]);
    args["SIXTEENTH"] = ( 60 / ( args["BPM"] * 4 ) );

    args["SIXTEENTH_PNT"] = 0;
    args["DRUM_PNT"] = randint(0,len( args["DRUMS"]["BD"]) - 1);
    args["FILL_PNT"] = randint(0,len( args["FILLS"]["BD"]) - 1);
    args["NOTES"] = { "BD":None, "SD":None, "HH":None, "C1":None, "BASS": None, "LEAD":None };
    
    _STATE = args;

    print("Setting up midi.")
    
    pygame.midi.init()
    player = pygame.midi.Output( args["PORT"] );

    while _STATE["RUNNING"]:
        task( player );
        print( "\r {:4s} {} {} {} {} {:2s} {:2s}".format(
            _STATE["CORD"] ,
            ( _STATE["DRUMS"]["BD"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["BD"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
            ( _STATE["DRUMS"]["SD"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["SD"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
            ( _STATE["DRUMS"]["HH"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["HH"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
            ( _STATE["DRUMS"]["C1"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["C1"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
             getBassNote( _STATE["NOTES"]["BASS"] ) ,
             getLeadNote( _STATE["NOTES"]["LEAD"] )          
             ), end="" );
        time.sleep( _STATE["SIXTEENTH"] );

def printHelp( name ):
    if not name:
        name = "<program>";
    print("""A program that generates midi drum, bass and lead sequences, in a 4:4 time signature
{0} --scale <scale> --root <root> --BPM <bpm> --RAND <randomization> --PORT <port> --DRUMS <tab file> --FILL <tab file> --PROGRESSIONS <progressions file>
\tscales: {1}
\troot: c,c#,d,d#,e,f,f#,g,g#,a,a#,b
\trandomization: 1-5
\tport: midi port number, (default: 0 )
\ttab file: a file containing drum tabs, with soxteenth divisions, and labels: BD, SD, HH, C1
\tprogressions file: a file containing cord progressions e.g i-vi-iv-v"
""".format( name, list(SCALES.keys()) ));

def parseArgs():
    tmp = {};
    i = 1;
    try:
        while len(sys.argv) - i > 0:
            if sys.argv[i] == "--scale":
                i += 1;
                tmp["SCALE"] = int(sys.argv[i],0);
                i += 1;
            elif sys.argv[i] == "--root":
                i += 1;
                tmp["ROOT"] = int(sys.argv[i]);
                i += 1;
            elif sys.argv[i] == "--BPM":
                i += 1;
                tmp["BPM"] = int(sys.argv[i],0);
                i += 1;
            elif sys.argv[i] == "--RAND":
                i += 1;
                tmp["RAND"] = int(sys.argv[i],0);
                i += 1;
            elif sys.argv[i] == "--PORT":
                i += 1;
                tmp["PORT"] = int(sys.argv[i],0);
                i += 1;
            elif sys.argv[i] == "--PROGRESSIONS":
                i += 1;
                tmp["PROGRESSIONS"] = sys.argv[i];
                try:
                    with open(sys.argv[i]) as f:
                        tmp1 = f.read(f);
                except:
                    traceback.print_exc();
                i += 1;
            elif sys.argv[i] == "--DRUMS":
                i += 1;
                tmp["DRUMS"] = sys.argv[i];
                try:
                    with open(sys.argv[i]) as f:
                        tmp1 = f.read(f);
                except:
                    traceback.print_exc();
                i += 1;
            elif sys.argv[i] == "--FILLS":
                i += 1;
                tmp["FILLS"] = sys.argv[i];
                try:
                    with open(sys.argv[i]) as f:
                        tmp1 = f.read(f);
                except:
                    traceback.print_exc();
                i += 1;
            else:
                i += 1;
                print("Bad arguments "+sys.argv[i]);
                useage();
        #DEFAULTS
        if "SCALE" not in tmp:
            tmp["SCALE"] = 'pentatonicmajor';
        if "ROOT" not in tmp:
            tmp["ROOT"] = "c";
        if "BPM" not in tmp:
            tmp["BPM"] = 86
        if "PORT" not in tmp:
            tmp["PORT"] = 0
        if "RAND" not in tmp:
            tmp["RAND"] = 2;
        if "PROGRESSIONS" not in tmp:
            arr = [
                "i-vi-iv-v",
                "ii-iii-i-i",
                "iv-iii-ii-i",
                "iii-v-i-i",
                "ii-v-i-i",
                "i-iv-ii-v",
                "i-v-vi-iv",
                "i-vi-ii-v",
                "v-iv-i-i"];
            tmp["PROGRESSIONS"] = [ arr[i].split("-") for i in range(0,len(arr)) ];
        if "DRUMS" not in tmp:
            tab = """
C1|----------------|------x---------|--------------x-|--------------x-|
HH|x-x-x-x-x-x-x-x-|x-x-x---x-x-x-x-|x-x-x-x-x-x-x---|x-x-x---x-x-x---|
SD|----o-------o---|----o-------o---|----o-------o---|----o-------o---|
BD|o-----o---o-----|o-----o---o-----|o-----o-o-------|o-----o---o-----|"""
            tmp["DRUMS"] = parseTab( tab );
        if "FILLS" not in tmp:
            tab = """
C1|------------x-x-|------x-------x-|--------x-x-x-x-|------------x-x-|
HH|x-x-x-x-x-x-----|x-x-x---x-x-x---|x-x-x-x---------|x-x-x-x-x-x-----|
SD|----o-------o-o-|----o-------o---|----o-------o-o-|----o-------o-o-|
BD|o-----o---o-----|o-----o-o-o---o-|o-----o-o-------|o---------o-----|"""
            tmp["FILLS"] = parseTab( tab );
    except:
        print("Bad args.")
        traceback.print_exc();
        printHelp( sys.argv[0] );
    return tmp;

if __name__ == '__main__':
    try:
        main(parseArgs());
    except (SystemExit,KeyboardInterrupt):
        printHelp( sys.argv[0] );
    else:
        printHelp( sys.argv[0] );

