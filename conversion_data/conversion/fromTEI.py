from .Transcription import Transcription, Tier
import xml.etree.cElementTree as ETree
import os

def escape(data):
    """Support function to replace 'xml>sax>saxutils'.
    Why is that needed here I don't know."""
    
    data = data.replace("&quot;","\"").replace("&apos;","'") \
               .replace("&lt;","<").replace("&gt;",">").replace("&amp;","&")
    return data
def getFormat(f,trans):
    """Support function to get the transcription's name and format."""
        # Name
    if trans.metadata.transcript.name:
        trans.name = trans.metadata.transcript.name[0]
    else:
        trans.name = os.path.split(f)[1]
        trans.name = os.path.splitext(trans.name)[0]
        trans.metadata.transcript.name = [trans.name]
        # Format
    trans.format = "tei"
    trans.metadata.transcript.format = trans.format

def readFloat(timestamp,unit):
    """Support support function for 'readTime'.
    Turns 'absolute' attributes (00:00:00.000) in floats."""

    value = 0.
        # We check if it is even necessary to operate
    if not ":" in timestamp:
        if unit == "ms" and (not "." in timestamp):
            timestamp = timestamp[:-3] + '.' + timestamp[-3:]
        return float(timestamp)
    l_time = timestamp.split(":"); lt = len(l_time)-1; stop = 0
        # We check if milliseconds are separated by ":"
        ## Note: in that fringe case, no need to check for unit type
    if lt > 2:
        value = float(l_time[-2] + "." + l_time[-1])
        lt -= 2
    else:
        timestamp = l_time[-1]
        if unit == "ms" and (not "." in timestamp):
            timestamp = timestamp[:-3] + '.' + timestamp[-3:]
        value = float(timestamp)
        lt -= 1
        # We also make sure not to go past hours
    if lt > 1:
        stop = lt-1
        # We multiply
    while lt >= stop:
        time = float(l_time[lt])
        if lt == stop:
            value = value + (time*3600)
        else:
            value = value = (time*60)
        lt -= 1
    return value
def readTime(trans,elem,timeorder):
    """Support function simply to fill that timeorder.
    Adds transcription's start/end times."""
    
    l_ids = []
        # We check the time type
    unit = ""
    if "unit" in elem.attrib:
        unit = elem.attrib['unit']
        # We check how time is stored
    count = -1; id = ""; start = -1.
    for time in elem:
        count += 1
            # First tag, usually absolute
        if count == 0:
            for key, value in time.attrib.items():
                if key.endswith(":id"):
                    id = key
                    l_ids.append(value)
                elif key == "absolute":
                    start = readFloat(value,unit)
                elif key == "interval":
                    start = readFloat(value,unit)
            timeorder[l_ids[-1]] = start
            # Other tags, usually intervals (with "since")
        else:
            l_ids.append(time.get(id))
                # test "absolute"
            value = time.get("absolute")
            if value:
                timeorder[l_ids[-1]] = readFloat(value,unit)
                continue
                # test "interval"
            value = time.get("interval")
            if value:
                tag = time.get("since")
                if tag:
                    timeorder[l_ids[-1]] = timeorder[tag] + readFloat(value,unit)
                else:
                    timeorder[l_ids[-1]] = start + readFloat(value,unit)
    trans.start = start; trans.end = timeorder[l_ids[-1]]
    return timeorder
def readHeader(trans,elem):
    """Support function to store 'header' metadata."""
    
    pass
def fromTei(f, **args):
    """Creates a Transcription object from a TEI file.
    Relies on the etree library."""
    
    trans = Transcription()
    timeorder = {}
    root = None; body = None; ttier = False
    
        ## We need a bazillion variables to make a bazillion checks
        ## to know what bloody structure people chose to use to store the data
        ## if we want to write 'tiers' while reading.
        ## Otherwise we need to wait for the whole document to have been read
        ## to start reading the 'tiers'
    
    b_root = False
    for event, elem in ETree.iterparse(f, events=("start","end")):
            # Find root for operation (cleaning)
        if not b_root:
            root = elem
            b_root = True
        elif event == "start":
            if elem.tag == "body":
                body = True
        elif event == "end":
            if elem.tag == "teiHeader":
                readHeader(trans,elem)
                root.remove(elem)
            elif elem.tag == "timeline":
                timeorder = readTime(trans,elem,timeorder)
                root.remove(elem); ttier = True
            elif ttier:
                break