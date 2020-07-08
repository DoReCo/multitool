from .Transcription import Transcription, Tier

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data
   
def writeMeta(file,trans):
    """Support function to write the header's metadata.
    /!\ Only stores "transcript" metadata in user-defined metadata."""
    
    c_name = trans.metadata.corpus.name
    if not c_name:
        c_name = [""]
    c_name = c_name[0]
    t_name = trans.metadata.transcript.name
    if not t_name:
        t_name = [""]
    t_name = t_name[0]
    url = trans.metadata.recording.url
    if not url:
        url = [""]
    comment = ""; convention = ""; other = {}
    for key, value in trans.metadata.transcript.open.items():
        if key == "comment":
            comment = escape(value)
        elif key == "guidelines":
            convention = escape(value)
        else:
            other[key] = escape(value)
    file.write("<basic-transcription>\n\t<head>\n\t\t<meta-information>"
               "\n\t\t\t<project-name>{}</project-name>"
               "\n\t\t\t<transcription-name>{}</transcription-name>"
               .format(c_name,t_name))
    for u in url:
        file.write("\n\t\t\t<referenced-file url=\"{}\"/>".format(u))
    file.write("\n\t\t\t<ud-meta-information>")
    for key, value in other.items():
        file.write("\n\t\t\t\t<ud-information attribute-name=\"{}\">{}</ud-information>"
                   .format(key,value))
    if other:
        file.write("\n\t\t\t")
    file.write("</ud-meta-information>"
               "\n\t\t\t<comment>{}</comment>"
               "\n\t\t\t<transcription-convention>{}</transcription-convention>"
               "\n\t\t</meta-information>"
               "\n\t\t<speakertable>"
               .format(comment,convention))
def writeSpeakers(file,trans):
    """Support function to write the header's speakers."""

        # Variables
    name = ""; abr = ""; sex = ""; lang = []; l1 = []; l2 = []
    other = {}; comment = ""
        # For each speaker
    for key,spk in trans.metadata.speakers.items():
            # We fill the info
        name = key; abr = ""; sex = spk.gender; comment = ""
        l1 = spk.languages[0].copy(); l2 = spk.languages[1].copy()
        lang = l1 + l2; other.clear()
        for k,value in spk.open.items():
            if k == "abbreviation":
                abr = value
            elif k == "comment":
                comment = escape(value)
            else:
                other[key] = escape(value)
            # We write
            # Name / abbreviation / gender
        if not abr:
            abr = name
        file.write("\n\t\t\t<speaker id=\"{}\">"
                   "\n\t\t\t\t<abbreviation>{}</abbreviation>"
                   "\n\t\t\t\t<sex value=\"{}\"/>"
                   "\n\t\t\t\t<languages-used>"
                   .format(name,abr,sex))
            # Languages
        if lang:
            for l in lang:
                file.write("\n\t\t\t\t\t<language lang=\"{}\"/>".format(l))
            file.write("\n\t\t\t\t</languages-used>")
        else:
            file.write("</languages-used>\n\t\t\t\t<l1></l1>\n\t\t\t\t<l2></l2>")
        if l1:
            file.write("\n\t\t\t\t<l1>")
            for l in l1:
                file.write("\n\t\t\t\t\t<language lang=\"{}\"/>".format(l))
            file.write("\n\t\t\t\t</l1>")
        if l2:
            file.write("\n\t\t\t\t<l2>")
            for l in l2:
                file.write("\n\t\t\t\t\t<language lang=\"{}\"/>".format(l))
            file.write("\n\t\t\t\t</l2>")
        file.write("\n\t\t\t\t<ud-speaker-information>")
        for key,value in other.items():
            file.write("\n\t\t\t\t\t<ud-information attribute-name=\"{}\">{}"
                       "</ud-information>".format(key,value))
        if other:
            file.write("\n\t\t\t\t")
        file.write("</ud-speaker-information>"
                   "\n\t\t\t\t<comment>{}</comment>"
                   "\n\t\t\t</speaker>".format(comment))
    if trans.metadata.speakers:
        file.write("\n\t\t")
    file.write("</speakertable>\n\t</head>\n\t<basic-body>\n\t\t<common-timeline>")
def writeTime(file,trans):
    """Support function to write the timetable."""
    
    timeorder = {}
    count = 0; id = ""
    for time in trans.timetable:
        id = "T"+str(count); count += 1
        file.write("\n\t\t\t<tli id=\"{}\" time=\"{:.3f}\"/>"
                   .format(id,time))
        timeorder[time] = id
    file.write("\n\t\t</common-timeline>")
    return timeorder
def writeTier(file,trans,a,tier,timeorder):
    """Support function to write a given tier."""
    
        # tier attributes
    text = "\n\t\t<tier id=\"{}\"".format("TIE"+str(a))
    spk = ""; category = "v"; type = "t"; other = {}
    for key, value in tier.metadata.items():
        if key == "speaker":
            spk = value
        elif key == "category":
            category = value
        elif key == "type":
            type = value
        else:
            other[key] = escape(value)
    if type == "t" and tier.pindex >= 0:
        type = "a"
    if spk:
        text = text + " speaker=\"{}\"".format(tier.metadata['speaker'])
    file.write(text + (" category=\"{}\" type=\"{}\" display-name=\"{}\">"
                       .format(category,type,tier.name)))
    if other:
        file.write("\n\t\t\t<ud-tier-information>")
        for key, value in other.items():
            file.write("\n\t\t\t\t<ud-information attribute-name=\"{}\">{}</ud-information>"
                       .format(key,value))
        file.write("\n\t\t\t</ud-tier-information>")
        # segments
    for seg in tier:
        if seg.unit == False:
            continue
        start = timeorder[seg.start]; end = timeorder[seg.end]
        file.write("\n\t\t\t<event start=\"{}\" end=\"{}\">".format(start,end))
        for key,value in seg.metadata:
            file.write("<ud-information attribute-name=\"{}\">{}</ud-information>"
                       .format(key,escape(value)))
        file.write("{}</event>".format(escape(seg.content)))
    file.write("\n\t\t</tier>")
def toExmaralda(f, trans, **args):
    """Creates an '.exb' file from a Transcription object.
    Relies on the "saxutils" library to escape xml characters."""
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
        # We need a list of transcriptions
    if not args.get('multiple',False):
        trans = [trans]; f = [f]
    
        # We write
    for a in range(len(trans)):
        tran = trans[a]; ff = f[a]
            # Complete information
        tran.setchildtime(); tran.checkSpeakers()
        tran.settimetable(1,truetype=False)
            # Actual writing
        with open(ff, 'w', encoding=encoding) as file:
                #XML header
            file.write("<?xml version=\"1.0\" encoding=\"{}\"?>\n"
                       .format(encoding)+
                       "<!-- (c) http://www.rrz.uni-hamburg.de/exmaralda -->\n")
                # Metadata
            writeMeta(file,tran)
                # Speakers
            writeSpeakers(file,tran)
                # Timetable
            timeorder = writeTime(file,tran)
                # Tiers
            for a in range(len(tran)):
                tier = tran.tiers[a]
                writeTier(file,tran,a,tier,timeorder)
            file.write("\n\t</basic-body>\n</basic-transcription>")
    return 0