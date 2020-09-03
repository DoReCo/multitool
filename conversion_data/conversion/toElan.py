from .Transcription import Transcription, Tier

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data

def writeHOpen(file,trans):
    """Support support function to write user-defined metadata in the header."""
    
        # I actually have no idea how to handle this...
        # So for now it will remain empty
        # Eventually the user should be able to choose
    
    for key,value in trans.metadata.transcript:
        file.write("\t\t<PROPERTY NAME=\"{}\">{}</PROPERTY>\n"
                   .format(key,value))
def writeHeader(file,trans):
    """Support function to write the header (and annotation document start)."""
    
        # We deal with the annotation document itself
    version = "3.0"; author = ""; date = ""; n_audio = ""
    if trans.format == "elan" and trans.metadata.transcript.format_version:
        version = trans.metadata.transcript.format_version
    if trans.metadata.recording.name:
        n_audio = trans.metadata.recording.name[0]
    versions = trans.metadata.getversion()
    if versions:
        author = versions[-1][2]; date = versions[-1][1]
    del versions
    file.write("<ANNOTATION_DOCUMENT DATE=\"{}\" AUTHOR=\"{}\" FORMAT=\"{}\" "
               "VERSION=\"{}\" xmlns:xsi=\"http://www.w3.org/2001/"
               "XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\""
               "http://www.mpi.nl/tools/elan/EAFv3.0.xsd\">\n\t<HEADER "
               "MEDIA_FILE=\"{}\" TIME_UNITS=\"milliseconds\">\n"
               .format(date,author,version,version,n_audio))
        # We add the actual header's stuff
    url = ""; type = ""; count = 0; check = False
        # We get back our MEDIA_DESCRIPTORs oh yeah
    while True:
        n_media = "MEDIA_DESCRIPTOR"+str(count)
        n_link = "LINKED_FILE_DESCRIPTOR"+str(count)
        count += 1
        dict = trans.metadata.recording.open
        if not dict:
            break
        med = dict.get(n_media); n_media = "MEDIA_DESCRIPTOR"
        if not med:
            med = dict.get(n_link); n_media = "LINKED_FILE_DESCRIPTOR"
        if not med:
            break
        check = True
        n_media = "\t\t<{}".format(n_media)
        for key,value in med.items():
            n_media = n_media + " {}=\"{}\"".format(key,value)
        file.write(n_media+"/>\n")
    
        # If ELAN failed us, resort to 'omni' metadata
        ## Note: no need to check if '<HEADER>' contains something, it will
    if not check:
        if trans.metadata.recording.url:
            lrl = len(trans.metadata.recording.url)
            lty = len(trans.metadata.recording.type)
            url = ""; type = ""
            for a in range(lrl):
                url = trans.metadata.recording.url[a]
                file.write("\t\t<MEDIA_DESCRIPTOR MEDIA_URL=\"{}\"".format(url))
                if a < lty:
                    type = trans.metadata.recording.type[a]
                    file.write(" MIME_TYPE=\"{}\"".format(type))
                file.write("/>\n")
        # We get... everything else
        ## Note: I'm not a masochist, so only 'corpus' and 'transcript' are in there
        ## Note: We can only handle 'strings' here... for now
    writeHOpen(file,trans)
    file.write("\t</HEADER>")
def writeTime(file,trans):
    """Support function to write the timetable"""
    
    timeorder = {}
        # We apply
    file.write("\n\t<TIME_ORDER>\n")
    for a in range(len(trans.timetable)):
        id = "ts"+str(a+1)
        if trans.timetable[a] < 0.:
            file.write("\t\t<TIME_SLOT TIME_SLOT_ID=\""+id+"\" />\n")
            timeorder[-1.] = "ts"+str(a+1)
        else:
                # /!\ milliseconds!
            file.write("\t\t<TIME_SLOT TIME_SLOT_ID=\""+id+"\" TIME_VALUE="
                       "\""+"{:.3f}"
                       .format(trans.timetable[a]).replace('.','')+"\"/>\n")
            timeorder[trans.timetable[a]] = id
    file.write("\t</TIME_ORDER>\n")
    return timeorder
def writeRefSeg(file,trans,tier):
    """Support support function to write ref-aligned segments."""
    
    id = ""; ref = ""
        # We reconstitute the "prev":
    l_prev = []; o_ref = ""
    for a in range(len(tier)):
        seg = tier.segments[a]
        if not seg.ref == o_ref:
            l_prev.append("")
            o_ref = seg.ref; check = 1
        else:
            l_prev.append(tier.segments[a-1].id)
        # We write
    for a in range(len(tier)):
        seg = tier.segments[a]
        if seg.unit == True:
            content = escape(seg.content)
            id = seg.id; ref = seg.ref; prev = l_prev[a]
            ext = seg.metadata.get('ext_ref')
            file.write("\t\t<ANNOTATION>\n\t\t\t<REF_ANNOTATION "
                       "ANNOTATION_ID=\""+escape(id)+"\" ANNOTATION_REF=\""
                       +escape(ref)+"\"")
            if not prev == "":
                file.write(" PREVIOUS_ANNOTATION=\""+escape(prev)+"\"")
            if ext:
                file.write(" EXT_REF=\""+escape(ext)+"\"")
            file.write(">\n\t\t\t\t<ANNOTATION_VALUE>"+content
                       +"</ANNOTATION_VALUE>\n\t\t\t</REF_ANNOTATION>"
                       "\n\t\t</ANNOTATION>\n")
def writeTimeSeg(file,trans,tier,timeorder):
    """Support support function to write time-aligned segments."""
    
    ts1 = ""; ts2 = ""
    for seg in tier.segments:
        if seg.unit == True:
            id = seg.id; content = escape(seg.content)
            ts1 = timeorder[seg.start]; ts2 = timeorder[seg.end]
            svg = seg.metadata.get('svg_ref')
            ext = seg.metadata.get('ext_ref')
            file.write("\t\t<ANNOTATION>\n\t\t\t<ALIGNABLE_ANNOTATION "
                      "ANNOTATION_ID=\""+escape(id)+"\" TIME_SLOT_REF1=\""+ts1+
                      "\" TIME_SLOT_REF2=\""+ts2+"\"")
            if svg:
                file.write(" SVG_REF=\""+escape(svg)+"\"")
            if ext:
                    file.write(" EXT_REF=\""+escape(ext)+"\"")
            file.write(">\n\t\t\t\t<ANNOTATION_"
                      "VALUE>"+content+"</ANNOTATION_VALUE>\n\t\t\t"
                      "</ALIGNABLE_ANNOTATION>\n\t\t</ANNOTATION>\n")
def writeTier(file,trans,tier,timeorder,l_types):
    """Support function to write each tier."""
    type = ""
        # We get the tier type
    if tier.type:
        type = escape(tier.type)
    elif tier.truetype:
        type = tier.truetype
    else:
        type = "time" # Default to time-alignment
    if not type in l_types:
        l_types.append((type,tier.truetype,tier.parent))
        # We write the tier head
    file.write("\t<TIER TIER_ID=\""+escape(tier.name)+"\" LINGUISTIC_TYPE_REF=\""
               +type+"\"")
    if tier.parent:
        file.write(" PARENT_REF=\""+escape(tier.parent)+"\"")
    lang = tier.metadata.get('language')
    spk = tier.metadata.get('speaker')
    auth = tier.metadata.get('author')
    if lang:
        file.write(" DEFAULT_LOCALE=\"{}\"".format(escape(lang)))
    if spk:
        file.write(" PARTICIPANT=\"{}\"".format(escape(spk)))
    if auth:
        file.write(" ANNOTATOR=\"{}\"".format(escape(auth)))
    if not tier.segments:
        file.write(" />\n"); return
    file.write(">\n")
        # SEGMENTS
            # symbolic-association / symbolic-subdivision
    if tier.truetype == "ref":
        writeRefSeg(file,trans,tier)
        # time-alignement / time-subdivision / included-in
    else:
        writeTimeSeg(file,trans,tier,timeorder)
    file.write("\t</TIER>\n")
def writeFooter(file,trans,l_types):
    """Support function to write the footer.
    This is a mess, but the footer only holds internal tools for Elan,
    not 'actual' metadata. As long as all types are declared, eh."""
    
    check = 0; l_ttypes = []; footer = trans.metadata.footer
    if trans.format == "elan" and trans.metadata.footer:
        check = 1
        p_deb = footer.find("<LINGUISTIC_TYPE"); l_temp = []
        pos = p_deb; p_fin = pos+1; sym = ""; type = ""; lt = len(l_types)
        if p_deb >= 0:
            while True:
                pos = footer.find("LINGUISTIC_TYPE_ID",p_fin)+20
                if pos < 20:
                    break
                sym = footer[pos-1]
                p_fin = footer.find(sym,pos)
                type = footer[pos:p_fin]
                l_temp.append(type)
            for tuple in l_types:
                if tuple[0] not in l_temp:
                    l_ttypes.append(tuple)
            l_temp.clear()
    else:
        l_ttypes = l_types
        # clean types
    d_temp = {}; l_temp = []
    for tuple in l_ttypes:
        if tuple[0] not in d_temp:
            l_temp.append(tuple)
            d_temp[tuple[0]] = True
    l_ttypes = l_temp.copy()
    del d_temp; del l_temp
    for tuple in l_ttypes: # using "truetype" to determine the type of type
        if not tuple[1] == "time":
            footer = ("\t<LINGUISTIC_TYPE LINGUISTIC_TYPE_ID=\"{}\" "
                      "TIME_ALIGNABLE=\"{}\" CONSTRAINTS=\"Symbolic_"
                      "Subdivision\" GRAPHIC_REFERENCES=\"{}"
                      "\"/>\n".format(tuple[0],"false","false")) + footer
        elif tuple[2]:
            footer = ("\t<LINGUISTIC_TYPE LINGUISTIC_TYPE_ID=\"{}\" "
                      "TIME_ALIGNABLE=\"{}\" CONSTRAINTS=\"Time_"
                      "Subdivision\" GRAPHIC_REFERENCES=\"{}"
                      "\"/>\n".format(tuple[0],"true","false")) + footer
        else:
            footer = ("\t<LINGUISTIC_TYPE LINGUISTIC_TYPE_ID=\"{}\" "
                      "TIME_ALIGNABLE=\"{}\" GRAPHIC_REFERENCES=\"{}"
                      "\"/>\n".format(tuple[0],"true","false")) + footer
    if check == 0:
        footer = footer + ("\t<CONSTRAINT STEREOTYPE=\"Time_Subdivision\" DESCRIPTION=\""
             "Time subdivision of parent annotation's time interval, no time "
             "gaps allowed within this interval\"/>\n\t<CONSTRAINT STEREOTYPE="
             "\"Symbolic_Subdivision\" DESCRIPTION=\"Symbolic subdivision of a "
             "parent annotation. Annotations refering to the same parent are "
             "ordered\"/>\n\t<CONSTRAINT STEREOTYPE=\"Symbolic_Association\" "
             "DESCRIPTION=\"1-1 association with a parent annotation\"/>\n\t"
             "<CONSTRAINT STEREOTYPE=\"Included_In\" DESCRIPTION=\"Time alignable "
             "annotations within the parent annotation's time interval, gaps are "
             "allowed\"/>\n")
    file.write(footer)
def toElan(f, trans, **args):
    """Creates an ELAN file from a Transcription object.
    
    Only handles boundaries in milliseconds (ELAN doesn't seem to save in PAL/NTSC)
    Footer is simply copied as is from an 'elan' file, or defaulted."""
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
    setchildtime = args.get('setchildtime',False)
        # We need a list of transcriptions
    if not args.get('multiple',False):
        trans = [trans]; f = [f]
        # We write
    for a in range(len(trans)):
        tran = trans[a]; ff = f[a]
            # Complete information
        tran.settimetable(1); tran.setstructure(setchildtime=setchildtime)
        with open(ff, 'w', encoding=encoding) as file:
            copy = ""
                # XML head
            file.write("<?xml version=\"1.0\" encoding=\"{}\"?>\n"
                       .format(encoding))
                # HEADER
            writeHeader(file,tran)
                # TIME_ORDER
            timeorder = writeTime(file,tran)
                # TIERS
            l_types = []
            for tier in tran.tiers:
                writeTier(file,tran,tier,timeorder,l_types)
            # 'B_morph_type'; 'B_word-txt-wca'
                # FOOTER
            writeFooter(file,tran,l_types)
            file.write("</ANNOTATION_DOCUMENT>")
    return 0