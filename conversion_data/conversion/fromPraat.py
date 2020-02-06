from .Transcription import Transcription, Tier
import os

def escape(data):
    """Support function to clean the content"""
    
    data = data.replace("\"\"","\"")
    return data
def getFormat(f,trans):
    """Support function to get the transcription's name and format."""
        # Name
    trans.name = os.path.splitext(f)
    trans.metadata.transcript.name = [trans.name]
        # Format
    trans.format = "praat"
    trans.metadata.transcript.format = trans.format

def fromPraat(f, **args):
    """Create a Transcription object representing the TextGrid transcription.
    
    Only handles the 'text file' format. Will have to handle 'short text'
    and 'binary' eventually."""
    
    trans = Transcription()
        # Encoding
    encoding = args.get('encoding')
        # False unit symbol
    sym = args.get('sym',["_"])
    if isinstance(sym,str):
        sym = [sym]
        # We test the encoding (utf-8 or utf-16)
    if not encoding:
        with open(f, 'rb') as file:
            bytes = file.read(3)
            if bytes[2] == 0x6c:
                encoding = "utf-8"
            elif bytes[2] == 0x46:
                encoding = "utf-16-le"
            elif bytes[2] == 0x00:
                encoding = "utf-16-be"
            else:
                print("Not an ooTextFile type.")
                return trans

        # Now we open in text mode
    with open(f, encoding=encoding) as file:
            # We test the type of TextGrid
            ## Currently no test, only 'text file' format handled
        segment = file.readline()
        if segment == '':
            print("Error: empty Praat file.")
            return trans
        file.seek(0)
            # Variables
        start_time = 0.; end_time = 0.
        start_n = 0.; end_n = 0.; count = 0
        content = ""; tier = None
            # We simply read the file line by line and add the information
        while not ((segment == '') or ("item []:" in segment)):
            segment = file.readline()
            if "xmin" in segment:
                trans.start = float(segment.split("= ")[1])
            elif "xmax" in segment:
                trans.end = float(segment.split("= ")[1])
        while segment != '':
            segment = file.readline()
                # New tier
            if "name =" in segment:
                name = segment.split("\"")[1]
                trans.addtier(name, trans.start, trans.end)
                tier = trans.tiers[-1]
                # New segment
            elif "xmin =" in segment:
                start_n = float(segment.split("= ")[1])
            elif "xmax =" in segment:
                end_n = float(segment.split("= ")[1])
            elif "text =" in segment:
                content = escape(segment.split("\"")[1])
                id = "a"+str(count); count += 1
                tier.addsegment(-1,start_n,end_n,content,id)
                for s in sym:
                    if content == s:
                        tier.segments[-1].unit = False; break
        # Transcription name / format
    getFormat(f,trans)
    return trans