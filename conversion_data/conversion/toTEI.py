from .Transcription import Transcription, Tier

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data

def writeHeader(file,trans):
    """Support function to write the TEI header."""
    
    """ Parts of the TEI header aren't read, since unpredictable
        So we try and recover those blocks
        Note: for now we simply write"""
    header = ""
    if trans.format == 'TEI' and trans.metadata.header:
        file.write(trans.metadata.header)
        return
    
        # We write the header
        """ We take infos' from Omni
            We add what's in 'header'...
            Note: for now the header block is processed separately"""
    file.write("\n\t<teiHeader>\n\t\t<encodingDesc>")
        # encodingDesc
    name = trans.metadata.corpus.name
    if name:
        name = name[0]
        file.write("\n\t\t\t<projectDesc>{}</projectDesc>".format(escape(name)))
    file.write("\n\t\t\t<appInfo>"
               "\n\t\t\t\t<application ident=\"multitool\"/>"
               "\n\t\t\t</appInfo>\n\t\t</encodingDesc>\n\t\t<fileDesc>")
               
        # fileDesc
        ## transcription name/ownership
    name = trans.name
    if not name:
        name = trans.metadata.transcript.name
        if name:
            name = name[0]
    ownership = trans.metadata.transcript.ownership
    if name or ownership:
        file.write("\n\t\t\t<titleStmt>")
        if name:
            file.write("\n\t\t\t\t<title>{}</title>".format(escape(name)))
        for own in ownership:
            file.write("\n\t\t\t\t<principal>{}</principal>".format(escape(own)))
        file.write("\n\t\t\t</titleStmt>")
        ## Recording metadata
    if trans.metadata.recording.url or trans.metadata.recording.name:
        file.write("\n\t\t\t<sourceDesc>\n\t\t\t\t<recordingStmt>"
                   "\n\t\t\t\t\t<recording>")
        lut = len(trans.metadata.recording.url)
        lnt = len(trans.metadata.recording.name)
        ltt = len(trans.metadata.recording.type)
        lt = -1; url=""; rtype=""
        if lut > 0:
            lt = lut
        else:
            lt = lnt
        for a in range(lt):
            url = ""; rtype = ""
            if a < lut:
                url = trans.metadata.recording.url[a]
            elif a < lnt:
                url = trans.metadata.recording.name[a]
            if url:
                file.write("\n\t\t\t\t\t\t<media")
                if a < ltt:
                    rtype = trans.metadata.recording.type[a]
                if rtype:
                    file.write(" mimeType=\"{}\"".format(rtype))
                file.write(" url=\"{}\" />".format(url))
        file.write("\n\t\t\t\t\t</recording>\n\t\t\t\t</recordingStmt>"
                   "\n\t\t\t</sourceDesc>")
    file.write("\n\t\t</fileDesc>")
        
        # profileDesc
        ## We get the list of speakers
    file.write("\n\t\t<profileDesc>")
    l_tierSpk = trans.tierSpeakers()
    l_tranSpk = trans.transSpeakers()
    for spk,list in l_tierSpk:
        if spk not in l_tranSpk:
            trans.metadata.addspeaker(spk)
            l_tranSpk.append(spk)
    del l_tierSpk
        ## particDesc
    if l_tranSpk:
        file.write("\n\t\t\t<particDesc>")
        for spk in l_tranSpk:
            speaker = trans.metadata.speakers.get(spk)
            file.write("\n\t\t\t\t<person xml:id=\"{}\" n=\"{}\">"
                       .format(spk,spk))
            if not speaker:
                file.write("\n\t\t\t\t\t<persName>\n\t\t\t\t\t\t<abbr>"
                           "{}</abbr>\n\t\t\t\t\t</persName>\n\t\t\t\t</person>"
                           .format(spk))
            else:
                tuple = spk.getall()
                    # name
                if tuple[0]:
                    file.write("\n\t\t\t\t\t<persName>\n\t\t\t\t\t\t<abbr>"
                               "{}</abbr>\n\t\t\t\t\t</persName>"
                               .format(tuple[0]))
                    # gender
                if tuple[1]:
                    file.write("\n\t\t\t\t\t<sex>{}</age>"
                               .format(tuple[1]))
                    # age
                if tuple[2]:
                    file.write("\n\t\t\t\t\t<age>{}</age>"
                               .format(tuple[2]))
                    # birth
                if tuple[3]:
                    file.write("\n\t\t\t\t\t<birth when=\"{}\""
                               .format(tuple[3]))
                    if tuple[4]:
                        file.write(">\n\t\t\t\t\t\t<placeName>{}</placeName>"
                                   "\n\t\t\t\t\t</birth>"
                                   .format(tuple[4]))
                    else:
                        file.write(" />")
                elif tuple[4]:
                    file.write("\n\t\t\t\t\t<birth>"
                               "\n\t\t\t\t\t\t<placeName>{}</placeName>"
                               "\n\t\t\t\t\t</birth>"
                               .format(tuple[4]))
                    # residence
                if tuple[5]:
                    file.write("\n\t\t\t\t\t<residence when=\"{}\""
                               .format(tuple[5]))
                    if tuple[6]:
                        file.write(">\n\t\t\t\t\t\t<placeName>{}</placeName>"
                                   "\n\t\t\t\t\t</residence>"
                                   .format(tuple[6]))
                    else:
                        file.write(" />")
                elif tuple[6]:
                    file.write("\n\t\t\t\t\t<residence>"
                               "\n\t\t\t\t\t\t<placeName>{}</placeName>"
                               "\n\t\t\t\t\t</residence>"
                               .format(tuple[6]))
                    # familyState
                if tuple[7]:
                    file.write("\n\t\t\t\t\t<state type=\"familyState\">"
                               "{}</state>".format(tuple[7]))
                    # sosecStatus
                if tuple[8]:
                    file.write("\n\t\t\t\t\t<sosecStatus>"
                               "{}</sosecStatus>".format(tuple[8]))
                    # occupation
                if tuple[9]:
                    file.write("\n\t\t\t\t\t<occupation>"
                               "{}</occupation>".format(tuple[9]))
                    # langKnowledge
                languages = speaker.getlanguages()
                if languages:
                    file.write("\n\t\t\t\t\t<langKnowledge>")
                    for type,lang in languages:
                        file.write("\n\t\t\t\t\t\t<langKnown type=\"\">"
                                   "{}</langKnown>".format(type,lang))
                    file.write("\n\t\t\t\t\t</langKnowledge>")
                file.write("\n\t\t\t\t</person>")
        file.write("\n\t\t\t</particDesc>")
    file.write("\n\t\t</profileDesc>")
        # revisionDesc
    versions = trans.metadata.getversion(); vid = 0
    if versions:
        file.write("\n\t\t<revisionDesc>")
        for version in versions:
            vid += 1
            file.write("\n\t\t\t<change xml:id=\"{}\"".format("ch"+str(vid)))
            if version[2]:
                file.write(" who=\"{}\"".format(version[2]))
            if version[1]:
                file.write(" when=\"{}\"".format(version[1]))
            if version[0]:
                file.write(">{}</change>".format(version[0]))
            else:
                file.write(" />")
        file.write("\n\t\t</revisionDesc>")
        # End of header
    file.write("\n\t</teiHeader>")
    
def writeTime(file,trans):
    """Support function to write the timetable."""
    
    timeorder = {0.:"T0"}
    file.write("\n\t\t<timeline unit=\"s\">\n\t\t\t"
               "<when absolute=\"00:00:00.0\" xml:id=\"T0\" />")
    trans.settimetable(1,truetype=False)
    count = 1; id = ""
    for time in trans.timetable:
        if time == 0: # We already have "0"
            continue
        id = "T"+str(count); count += 1
        file.write("\n\t\t\t<when xml:id=\"{}\" interval=\"{:.3f}\""
                   " since=\"T0\" />".format(id,time))
        timeorder[time] = id
    file.write("\n\t\t</timeline>")
    return timeorder
def writeInterp(file,trans):
    """Support function to write 'interp'."""
    
        # Variables
    tierorder = {}; count = 0; id = ""
        # We fill 'tierorder' and write
    file.write("\n\t\t<interpGrp type=\"tiers\">")
    for tier in trans:
        id = "tier"+str(count); count += 1
        tierorder[tier.name] = id
        file.write("\n\t\t\t<interp xml:id=\"{}\" type=\"tier\">"
                   .format(id))
            # We fill in the metadata
            ## Static metadata
        name = tier.name; type = tier.type; parent = tier.parent
        speaker = tier.metadata.get('speaker')
        lang = tier.metadata.get('language')
        start = ""; end = ""
        if tier.start >= 0:
            start = "{:.3f}".format(tier.start)
        if tier.end >= 0:
            end = "{:.3f}".format(tier.end)
        if start or end or name or type or speaker or lang or parent:
            file.write("\n\t\t\t\t<fs xml:id=\"{}m1\" type=\"st_metadata\">"
                       .format(id))
            if name:
                file.write("\n\t\t\t\t\t<f name=\"name\">{}</f>"
                           .format(name))
            if type:
                file.write("\n\t\t\t\t\t<f name=\"type\">{}</f>"
                           .format(type))
            if start:
                file.write("\n\t\t\t\t\t<f name=\"start\">{}</f>"
                           .format(start))
            if end:
                file.write("\n\t\t\t\t\t<f name=\"end\">{}</f>"
                           .format(end))
            if parent:
                file.write("\n\t\t\t\t\t<f name=\"dependency\">{}</f>"
                           .format(parent))
            if speaker:
                file.write("\n\t\t\t\t\t<f name=\"speaker\">{}</f>"
                           .format(speaker))
            if lang:
                file.write("\n\t\t\t\t\t<f name=\"language\">{}</f>"
                           .format(lang))
            file.write("\n\t\t\t\t</fs>")
            ## Dynamic metadata (user-defined)
        check = False
        for key in tier.metadata:
            if key == 'speaker' or key == 'language':
                continue
            check = True; break
        if check:
            file.write("\n\t\t\t\t<fs xml:id=\"{}m2\" type=\"ud_metadata\">"
                       .format(id))
            for key,value in tier.metadata.items():
                if key == 'speaker' or key == 'language':
                    continue
                file.write("\n\t\t\t\t\t<f name=\"{}\">{}</f>"
                           .format(key,value))
            file.write("\n\t\t\t\t</fs>")
        file.write("\n\t\t\t</interp>")
    file.write("\n\t\t</interpGrp>")
    return tierorder
def writeTiers(file,trans,timeorder,tierorder):
    """Support function to write the 'tiers'..."""
    
        # Variables
    s_start = ""; s_end = ""; old = -1.
    c_start = ""; c_end = ""
    l_cpos = []; uid = 1; sid = 1; pid = 1; gid = 1
    spk = ""
        # We get the list of parents (and their children)
    l_parents,l_struct = trans.getparents()
        # We setup 'l_cpos' (segment position in the child)
    for struct in l_struct:
        l_cpos.append([])
        for a in struct:
            l_cpos[-1].append(0)
        # We iterate each segment of the parent tiers in time order
    for p, pi,psi,pseg in trans.iterseg(l_parents):
            # false units are ignored
        if pseg.unit == False:
            continue
        ptier = trans.tiers[pi]
            # Timeorder and Pauses
        s_start = timeorder[pseg.start]
        if s_end and old < pseg.start:
            file.write("\n\t\t\t<pause xml:id=\"{}\" start=\"{}\" end=\"{}\" />"
                       .format("p"+str(pid),s_end,s_start))
            pid += 1
        s_end = timeorder[pseg.end]; old = pseg.end
            # tier attributes
        attrib = (" xml:id=\"{}\" ana=\"{}\""
                 .format("aB"+str(uid),tierorder[ptier.name]))
        spk = ptier.metadata['speaker']
        if spk:
            attrib = attrib + " who=\"{}\"".format(escape(spk))
        attrib = attrib + (" start=\"{}\" end=\"{}\""
                 .format(s_start,s_end))
            # We write <u>
        file.write("\n\t\t\t<annotationBlock {}>"
                   "\n\t\t\t\t<u xml:id=\"{}\""
                   .format(attrib,"u"+str(uid)))
        if pseg.content:
            file.write(">{}</u>".format(escape(pseg.content)))
        else:
            file.write(" />")
        uid += 1
            # We deal with the children
        for a in range(len(l_struct[p])):
                # Child tier variables
            csi = l_struct[p][a][0] # child tier index
            cpos = l_cpos[p][a]  # child segment index
            ctier = trans.tiers[csi]; lct = len(ctier)
                # We write <spanGrp>
            file.write("\n\t\t\t\t<spanGrp xml:id=\"{}\" ana=\"{}\">"
                       .format("sG"+str(gid),tierorder[ctier.name]))
            gid += 1
                # We write <span>
            for b in range(cpos,lct):
                cseg = ctier.segments[b]
                if cseg.start >= pseg.end:
                    l_cpos[p][a] = b; break
                c_start = timeorder[cseg.start]; c_end = timeorder[cseg.end]
                file.write("\n\t\t\t\t\t<span xml:id=\"{}\" "
                           "from=\"{}\" to=\"{}\""
                           .format("s"+str(sid),c_start,c_end))
                if cseg.content:
                    file.write(">{}</span>".format(escape(cseg.content)))
                else:
                    file.write(" />")
                sid += 1
            file.write("\n\t\t\t\t</spanGrp>")
            # End of segment
        file.write("\n\t\t\t</annotationBlock>")
def toTEI(f, trans, **args):
    """Creates a TEI file from a Transcription object."""
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
        # We need a list of transcriptions
    if not args.get('multiple',False):
        trans = [trans]; f = [f]
    
        # We write
    for a in range(len(trans)):
        tran = trans[a]; ff = f[a]
            # Complete information
        tran.setchildtime()
        for tier in tran:
            tier.checktime()
        with open(ff, 'w', encoding=encoding) as file:
                #XML header
            file.write("<?xml version=\"1.0\" encoding=\"{}\"?>\n"
                       "<TEI xmlns=\"http://www.tei-c.org/ns/1.0\">"
                       .format(encoding))
                # Metadata
            writeHeader(file,tran)
                # TEXT tag
            lang = tran.metadata.transcript.open.get('lang')
            if not lang:
                file.write("\n\t<text>")
            else:
                file.write("\n\t<text xml:lang=\"{}\">".format(lang))
                # Timetable
            timeorder = writeTime(file,tran)
                # Interp
            tierorder = writeInterp(file,tran)
                # Tiers
            file.write("\n\t\t<body>")
            writeTiers(file,tran,timeorder,tierorder)
                # End of file
            file.write("\n\t\t</body>\n\t</text>\n</TEI>")
    return 0