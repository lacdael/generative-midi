#!/usr/bin/env python3
# coding: utf-8

from random import randint
import time
import sys
import traceback
import mido
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


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

MIXES = [
        {"BD":True,"SD":True,"HH":True,"C1":True,"BASS":True,"LEAD":True,"DITTY":True},    
        {"BD":True,"SD":True,"HH":False,"C1":False,"BASS":True,"LEAD":False,"DITTY":True},    
        {"BD":False,"SD":False,"HH":True,"C1":False,"BASS":True,"LEAD":True,"DITTY":True},    
        {"BD":True,"SD":False,"HH":False,"C1":False,"BASS":True,"LEAD":False,"DITTY":True},    
        ]

def canPlay( what , i ):
    return MIXES[ i ][ what ];


_BASS_MIDI_KEYS = {"c":36,"c#":37,"d":38,"d#":39,"e":40,"f":41,"f#":42,"g":43,"g#":44,"a":45,"a#":46,"b":47};
_LEAD_MIDI_KEYS = {"c":60,"c#":61,"d":62,"d#":63,"e":64,"f":65,"f#":66,"g":67,"g#":68,"a":69,"a#":70,"b":71};

def getBassNote( n ):
    if not n:
        return "";
    for k in _BASS_MIDI_KEYS.keys():
        if n == _BASS_MIDI_KEYS[k]:
            return k;
    return "";

def getLeadNote( n ):
    if not n:
        return "";
    for k in _LEAD_MIDI_KEYS.keys():
        if n == _LEAD_MIDI_KEYS[k]:
            return k;
    return "";

def getOffsetNote(i,scale,root,offset):
    _len = len(SCALES[ scale ])
    if (offset - 1 ) < 0:
        return None;
    if i == "i":
        return root + sum(SCALES[ scale ][ 0: (offset - 1) ]) if _len > (offset - 1) else None;
    elif i == "ii":
        return root  + sum(SCALES[ scale ][ 0:(1 + offset - 1) ]) if _len > (1 + offset - 1) else None;
    elif i == "iii":
        return root +  sum(SCALES[ scale ][ 0:(2 + offset - 1) ]) if _len > (2 + offset - 1) else None;
    elif i == "iv":
        return root +  sum(SCALES[ scale ][ 0:(3 + offset - 1) ]) if _len > (3 + offset - 1) else None;
    elif i == "v":
        return root +  sum(SCALES[ scale ][ 0:(4  + offset - 1) ]) if _len > (4 + offset - 1) else None;
    return None;


def getDitty( scale, root, prog):
    arr = [];
    for i in prog:
        arr.append( getMidiKey( scale, i , root ) );
    #find commond notes
    tmp = {};
    for i in prog:
        if i == 'vi':
            i = 'i';

        n = getMidiKey( scale, i , root );
        
        if n != None: 
            k = str(n)
            if k in tmp:
                tmp[ k ] += 1;
            else:
                tmp[ k ] = 0;
        n3 = getOffsetNote( i , scale , root, 3);
        if n3 != None:
            k = str(n3)
            if k in tmp:
                tmp[ k ] += 1;
            else:
                tmp [ k ] = 0;
        n5 = getOffsetNote( i, scale , root, 5);
        if n5 != None:
            k = str(n5)
            if k in tmp:
                tmp[ k ] += 1;
            else:
                tmp [ k ] = 0;
    for k in tmp.keys():
        if k and tmp[k] > 0:
            arr.append( int( k ) );
    return arr;
            

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
    global _STATE
    if not hasattr(getCord,"pnt"):
        getCord.pnt = 0
    cord = progs[ _STATE["PROGRESSION_PNT"] ][ getCord.pnt ];
    if randint(0,r) == 0:
        tries = 0;
        while tries < 10:
            tries += 1;
            newProgPnt = randint(0,len(progs) - 1);
            if progs[ _STATE["PROGRESSION_PNT"] ][ getCord.pnt ] in progs[ newProgPnt ]:
                newPnt = 0;
                for ii in range(0, len( progs[ newProgPnt ])):
                    if progs[ _STATE["PROGRESSION_PNT"] ][ getCord.pnt ] == progs[ newProgPnt ][ ii ]:
                        newPnt = ii;
                        break;
                _STATE["PROGRESSION_PNT"] = newProgPnt;
                newPnt += 1
                if newPnt >= len( progs[ _STATE["PROGRESSION_PNT"] ] ):
                    newPnt = 0;
                getCord.pnt = newPnt;
        if tries == 10:
            getCord.pnt +=1;
    else:
        getCord.pnt +=1;
    if getCord.pnt >= len(progs[ _STATE["PROGRESSION_PNT"] ]):
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

BD_KEY = 36
SD_KEY = 38
HH_KEY = 42
C1_KEY = 49

def task( ):
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
        if seq["BD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-" and canPlay( "BD", _STATE["MIX"] ):
            _player.send( mido.Message('note_on', note=BD_KEY , velocity = 100,channel=0 ));
            _STATE["NOTES"]["BD"] = BD_KEY
        elif _STATE["NOTES"]["BD"]:
            _player.send( mido.Message('note_off',note=BD_KEY,channel=0));
            _STATE["NOTES"]["BD"] = None;
        #SD 
        if seq["SD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-" and canPlay( "SD", _STATE["MIX"] ):
            _player.send( mido.Message('note_on',note=SD_KEY , velocity = 100,channel=0 ));
            _STATE["NOTES"]["SD"] = SD_KEY;
        elif _STATE["NOTES"]["SD"]:
            _player.send( mido.Message('note_off', note=SD_KEY,channel=0));
            _STATE["NOTES"]["SD"] = None;
        #HH
        if seq["HH"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-" and canPlay( "HH", _STATE["MIX"] ):
            _player.send( mido.Message('note_on', note=HH_KEY , velocity = 100,channel=0 ));
            _STATE["NOTES"]["HH"] = HH_KEY;
        elif _STATE["NOTES"]["HH"]:
            _player.send( mido.Message('note_off',note=HH_KEY,channel=0));
            _STATE["NOTES"]["HH"] = None;
        #C1
        if seq["C1"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-" and canPlay( "C1" , _STATE["MIX"] ):
            _player.send( mido.Message('note_on',note=C1_KEY, velocity = 100,channel=0 ));
            _STATE["NOTES"]["C1"] = C1_KEY;
        elif _STATE["NOTES"]["C1"]:
            _player.send( mido.Message('note_off', note=C1_KEY, channel=0));
            _STATE["NOTES"]["C1"] = None;
        #BASS
        if ( seq["BD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-" or
            seq["SD"][ pnt ][ _STATE["SIXTEENTH_PNT"] ] != "-"):
            if randint(0, _STATE["RAND"] ) == 0 and canPlay( "BASS", _STATE["MIX"] ):
                _STATE["NOTES"]["BASS"] = getMidiKey( _STATE["SCALE"], _STATE["CORD"], _STATE["ROOT_BASS"] );
                _player.send( mido.Message('note_on', note=_STATE["NOTES"]["BASS"] , velocity = 100,channel=4 ));
            if not _STATE["NOTES"]["DITTY_NOTE"] and canPlay( "DITTY", _STATE["MIX"] ) and _STATE["NOTES"]["DITTY"] and randint(0,1) == 0:
                n = _STATE["NOTES"]["DITTY"].pop();
                _player.send( mido.Message('note_on', note=n , velocity = randint(75, 100) ,channel=6 ));
                _STATE["NOTES"]["DITTY_NOTE"] = n;
        else:
            if _STATE["NOTES"]["BASS"]:
                _player.send( mido.Message('note_off', note=_STATE["NOTES"]["BASS"] , velocity = 100,channel=4 ));
                _STATE["NOTES"]["BASS"] = None;
            if _STATE["NOTES"]["DITTY_NOTE"] and randint(0,_STATE["RAND"]) == 0:
                _player.send( mido.Message('note_off', note=_STATE["NOTES"]["DITTY_NOTE"] , velocity = randint(70,100) ,channel=6 ) );
                _STATE["NOTES"]["DITTY_NOTE"] = None;
        
        if _STATE["SIXTEENTH_PNT"] == 0:
            
            #NEW MIX
            _STATE["MIX"] = 0;
            if randint(0,_STATE["RAND"]) == 0:
                _STATE["MIX"] = randint(0, len(MIXES) - 1);
            _STATE["CORD"] = getCord( _STATE["RAND"] , _STATE["PROGRESSIONS"] );
            #LEAD
            if "ARP" not in _STATE:
                if _STATE["NOTES"]["LEAD"]:
                    _player.send( mido.Message( 'note_off', note= _STATE["NOTES"]["LEAD"], velocity = 100, channel=5 ) );
                _STATE["NOTES"]["LEAD"] = getMidiKey( _STATE["SCALE"], _STATE["CORD"], _STATE["ROOT_LEAD"]);
                if canPlay("LEAD", _STATE["MIX"] ):
                    _player.send( mido.Message('note_on', note=_STATE["NOTES"]["LEAD"] , velocity = 100, channel=5 ));
                
            #NEW DRUm Pnt
            if _STATE["BAR"] == 3:
                _STATE["FILL_PNT"] = randint(0,len( _STATE["FILLS"] ) - 1);
            elif _STATE["BAR"] == 1 and randint(0,_STATE["RAND"]) == 0:
                _STATE["NOTES"]["DITTY"] = getDitty( _STATE["SCALE"], _STATE["ROOT_LEAD"], _STATE["PROGRESSIONS"][ _STATE["PROGRESSION_PNT"] ] );
            
            else:
                _STATE["DRUM_PNT"] = randint(0,len( _STATE["DRUMS"] ) - 1);
        
            #TRIGGERS
            _STATE["BAR16_PNT"] += 1;
            if _STATE["BAR16_PNT"] > 15:
                _STATE["BAR16_PNT"] = 0
                if not _STATE["NOTES"]["TRIGGER"]:
                    notes = [51,59,54,56];
                    n = notes[ randint(0, len(notes) - 1 ) ]
                    _player.send( mido.Message('note_on', note=n , velocity = 100, channel=0 ));
                    _STATE["NOTES"]["TRIGGER"] = n  
          
        
        
        elif _STATE["SIXTEENTH_PNT"] == 15:
            _STATE["BAR"] += 1;
            if _STATE["BAR"] > 4:
                _STATE["BAR"] = 1;
        if _STATE["NOTES"]["TRIGGER"]:
            _player.send( mido.Message('note_off', note=_STATE["NOTES"]["TRIGGER"] , velocity = 100, channel=0 ));
            _STATE["NOTES"]["TRIGGER"] = None;

  




        #ARP
        if "ARP" in _STATE:
            if _STATE["NOTES"]["ARP"]:
                _player.send( mido.Message( 'note_off', note= _STATE["NOTES"]["ARP"], velocity = 100, channel=5 ) );
                _STATE["NOTES"]["ARP"] = None;
            if _STATE["APR"][ _STATE["ARP_PNT"] ] in ["1","3","4","5"]:
                n = getOffsetNote( _STATE["CORD"], _STATE["SCALE"], _STATE["ROOT_LEAD"] , int( _STATE["ARP"][ _STATE["ARP_PNT"] ] ) );
                if n:
                    _player.send( mido.Message('note_on', note=n , velocity = 100, channel=5 ));
                    _STATE["NOTES"]["ARP"] = n;
            
        _STATE["SIXTEENTH_PNT"] += 1;
        if _STATE["SIXTEENTH_PNT"] > 15:
            _STATE["SIXTEENTH_PNT"] = 0;
    except:
        traceback.print_exc()

_STATE = {};
_player = None;

def main( args ):
    global _STATE, _player;


    args["ROOT_BASS"] = _BASS_MIDI_KEYS[ args["ROOT"] ];
    args["ROOT_LEAD"] = _LEAD_MIDI_KEYS[ args["ROOT"] ];
    args["RUNNING"] = True
    args["BAR"] = 1;
    args["BAR16_PNT"] = 0;
    args["MIX"] = 0;
    args["SIXTEENTH"] = ( 60 / ( args["BPM"] * 4 ) );

    args["PROGRESSION_PNT"] = 0;
    args["SIXTEENTH_PNT"] = 0;
    args["ARP_PNT"] = 0;
    args["DRUM_PNT"] = randint(0,len( args["DRUMS"]["BD"]) - 1);
    args["FILL_PNT"] = randint(0,len( args["FILLS"]["BD"]) - 1);
    args["NOTES"] = { "BD":None, "SD":None, "HH":None, "C1":None, "BASS": None, "LEAD":None,"DITTY":[],"DITTY_NOTE":None,"ARP":None,"TRIGGER":None};
    
    _STATE = args;
    _STATE["CORD"] = getCord( args["RAND"], args["PROGRESSIONS"]);

    _player = mido.open_output( args["PORT"] );
    #send keys for midi-gate multiplexer
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=36, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=36, velocity = 100, channel=0 ));
        done = input("Have you mapped notes 36 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=38, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=38, velocity = 100, channel=0 ));
        done = input("Have you mapped notes 38 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=42, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=42, velocity = 100, channel=0 ));
        done = input("Have you mapped note 42 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=49, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=49, velocity = 100, channel=0 ));
        done = input("Have you mapped note 49 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=51, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=51, velocity = 100, channel=0 ));
        done = input("Have you mapped note 51 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=59, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=59, velocity = 100, channel=0 ));
        done = input("Have you mapped note 59 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=54, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=54, velocity = 100, channel=0 ));
        done = input("Have you mapped note 54 for channel 0 ? [y]es/[n]o?");
    done ="n";
    while done != "y":
        _player.send( mido.Message( 'note_on', note=56, velocity = 100, channel=0 ) );
        time.sleep(0.2);
        _player.send( mido.Message('note_off', note=56, velocity = 100, channel=0 ));
        done = input("Have you mapped note 56 for channel 0 ? [y]es/[n]o?");


    def job():
        task( );
        print( "{:4s} {} {} {} {} {:2s} {:2s} {:2s} {:2s}".format(
            _STATE["CORD"] ,
            ( _STATE["DRUMS"]["BD"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["BD"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
            ( _STATE["DRUMS"]["SD"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["SD"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
            ( _STATE["DRUMS"]["HH"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["HH"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
            ( _STATE["DRUMS"]["C1"][ _STATE["DRUM_PNT"] ][ _STATE["SIXTEENTH_PNT" ] ]
                if _STATE["BAR"] < 4 else _STATE["FILLS"]["C1"][ _STATE["FILL_PNT"] ][ _STATE["SIXTEENTH_PNT"] ]),
             getBassNote( _STATE["NOTES"]["BASS"] ).upper() ,
             getLeadNote( _STATE["NOTES"]["LEAD"] ),          
             getLeadNote( _STATE["NOTES"]["DITTY_NOTE"] ),        
             _STATE["NOTES"]["TRIGGER"] if _STATE["NOTES"]["TRIGGER"] else ""          
             ));

    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=_STATE["SIXTEENTH"]);
    scheduler.start()

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
            elif sys.argv[i] == "--ARP":
                i += 1;
                tmp["ARP"] = int(sys.argv[i],0);
                i += 1;
            elif sys.argv[i] == "--PROGRESSIONS":
                i += 1;
                try:
                    arr = None;
                    with open(sys.argv[i]) as f:
                        arr = f.read(f);
                    if arr:
                        tmp["PROGRESSIONS"] = [ arr[i].split("-") for i in range(0,len(arr)) ];
                except:
                    traceback.print_exc();
                i += 1;
            elif sys.argv[i] == "--DRUMS":
                i += 1;
                tab = None;
                try:
                    with open(sys.argv[i]) as f:
                        tab = f.read(f);
                    if tab:
                        tmp["DRUMS"] = parseTab( tab );
                except:
                    traceback.print_exc();
                i += 1;
            elif sys.argv[i] == "--FILLS":
                i += 1;
                try:
                    tab = None;
                    with open(sys.argv[i]) as f:
                        tmp["FILLS"] = f.read(f);
                    if tab:
                        tmp["FILLS"] = parseTab( tab );
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
            arr = mido.get_output_names();
            for p in range(0,len(arr)):
                print("[{}] {}".format( p + 1, arr[p]));
            selected = -1;
            while selected < 1 or selected > len(arr):
                selected = int( input("Enter a MIDI device:") );

            tmp["PORT"] = arr[ selected - 1 ];
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

