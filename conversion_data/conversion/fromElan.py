from .Transcription import Transcription, Tier
import xml.etree.cElementTree as ETree
import os

def escape(data):
    """Support function to replace 'xml>sax>saxutils'.
    Why is that needed here I don't know."""
    
    data = data.replace("&quot;","\"").replace("&apos;","'") \
               .replace("&lt;","<").replace("&gt;",">") \
               .replace("&amp;","&")
    return data
def getFormat(f,trans):
    """Support function to get the transcription's name and format."""
        # Name
    trans.name = os.path.split(f)[1]
    trans.name = os.path.splitext(trans.name)[0]
    trans.metadata.transcript.name = [trans.name]
        # Format
    trans.format = "elan"
    trans.metadata.transcript.format = trans.format

def readTime(trans,elem,timeorder):
    """Support function simply to fill that timeorder.
    Adds transcription's start/end times."""
    
    l_ids = []
    for time in elem:
        l_ids.append(time.get("TIME_SLOT_ID"))
        if "TIME_VALUE" in time.attrib:
            timeorder[l_ids[-1]] = time.get("TIME_VALUE")
        else:
            timeorder[l_ids[-1]] = "-1000"
    start = timeorder[l_ids[0]]; end = timeorder[l_ids[-1]]
    trans.start = float(start[:-3] + '.' + start[-3:])
    trans.end = float(end[:-3] + '.' + end[-3:])
    return timeorder
def setTierMD(tier,attr):
    """Support support function to load tier metadata."""
    
    tier.parent = attr.get('PARENT_REF')
    if not tier.parent:
        tier.parent = ""
    tier.type = attr.get('LINGUISTIC_TYPE_REF')
    if not tier.type:
        tier.type = ""
    spk = attr.get('PARTICIPANT')
    if spk:
        tier.metadata['speaker'] = spk
    auth = attr.get('ANNOTATOR')
    if auth:
        tier.metadata['author'] = auth
    lang = attr.get('DEFAULT_LOCALE')
    if lang:
        tier.metadata['language'] = lang
def setSegMD(tier,attr):
    """Support support function to load segment metadata."""
    seg = tier.segments[-1]
    seg.id = attr.get('ANNOTATION_ID')
    if not seg.id:
        seg.id = ""
    ext = attr.get('EXT_REF')
    if ext:
        seg.metadata['ext_ref'] = ext
    ext = attr.get('SVG_REF')
    if ext:
        seg.metadata['svg_ref'] = ext
def readTier(trans,elem,timeorder):
    """Support function to load a tier into the Transcription object."""
    
    trans.addtier(elem.attrib["TIER_ID"], trans.start, trans.end)
    tier = trans.tiers[-1]; tier.format = "elan"
    setTierMD(tier,elem.attrib)
    start = -1.; end = -1.; status = 0; p = 0; l_segs = []
        # If it's of truetype 'time':
    tier.truetype = "time"
    for anno in elem.iter("ALIGNABLE_ANNOTATION"):
        cont = anno.find("ANNOTATION_VALUE").text
        if cont == None:
            cont = ""
        else:
            cont = escape(cont)
        start = -1.; end = -1.
        s_start = anno.attrib["TIME_SLOT_REF1"]
        s_end = anno.attrib["TIME_SLOT_REF2"]
        if s_start in timeorder:
            s_start = timeorder[s_start]
            start = float(s_start[:-3] + '.' + s_start[-3:])
        if s_end in timeorder:
            s_end = timeorder[s_end]
            end = float(s_end[:-3] + '.' + s_end[-3:])
        tier.addsegment(p, start, end, cont,"","",True,tier,1)
        setSegMD(tier,anno.attrib); p += 1
        if end < 0:
            l_segs.append(tier.segments[-1])
        elif start < 0.:
            l_segs.append(tier.segments[-1])
            if end >= 0.:
                ls = len(l_segs)
                start = l_segs[0].start; end = l_segs[-1].end; dur = end-start
                for a in range(ls):
                    seg = l_segs[a]
                    seg.start = start + dur*(a/ls)
                    seg.end = start + dur*((a+1)/ls)
                l_segs.clear()
    if tier.segments:
        return
        # Otherwise it was 'ref':
    tier.truetype = "ref"
    for anno in elem.iter("REF_ANNOTATION"):
        cont = anno.find("ANNOTATION_VALUE").text
        if cont == None:
            cont = ""
        id = anno.attrib["ANNOTATION_ID"]; ref = anno.attrib["ANNOTATION_REF"]
        tier.addsegment(p, -1.,-1., cont, id, ref, True, tier, 1)
        setSegMD(tier,anno.attrib); p += 1
def readHeader(trans,root,elem):
    """Support function to store 'header' metadata."""
    
        # We extract from 'root' (ANNOTATION_DOCUMENT)
        ## 'version' is sort of reserved, so we store it in 'EAF_VERSION' instead
    vers = -1
    for key,value in root.attrib.items():
        if key == "VERSION":
            trans.metadata.transcript.format_version = value
        elif key == "AUTHOR":
            trans.metadata.addversion("Elan_export","",value,"",0)
        elif key == "DATE":
            trans.metadata.addversion("Elan_export",value,"","",0)
        elif key == "FORMAT":
            continue
        # We extract from the sub-elements
        # Note: extraction from 'elem' attributes done after that.
    l_url = []; l_type = []; o_ch = 0
    for el in elem:
            # We only store 'url' (and its 'type'), the rest is left as ELAN keys.
            ## Media descriptors
        if el.tag == "MEDIA_DESCRIPTOR" or el.tag == "LINKED_FILE_DESCRIPTOR":
                # We store 'url' and 'type' in their lists 'l_url/type'
            for key,value in el.attrib.items():
                if key == "MEDIA_URL":
                    l_url.append(value)
                elif key == "MIME_TYPE":
                    l_type.append(value)
                # every descriptor is however saved fully in 'open'
            name = el.tag+str(o_ch); o_ch += 1
            trans.metadata.addopen(name,el.attrib.copy(),1)
            ## Properties (user-defined metadata)
        else:
                # add to 'trans.metadata.transcript['open']'
            trans.metadata.addopen(el.get('NAME'),el.text,2)
        # We store the lists in the metadata
    trans.metadata.recording.url = l_url.copy()
    trans.metadata.recording.type = l_type.copy()
        # We get the names from the urls
    for url in trans.metadata.recording.url:
        if "\\" in url:
            name = url.rsplit("\\", 1)[1]
        elif "/" in url:
            name = url.rsplit("/", 1)[1]
        else:
            name = url
        trans.metadata.recording.name.append(name)
        # We extract from 'elem'
    for key,value in elem.attrib.items():
        if key == "MEDIA_FILE":
            trans.metadata.recording.name.append(value)
        else:
            trans.metadata.addopen(key,value,1)       
def readFooter(trans,root):
    """Support function to store 'footer' metadata.
    Elan's footer is technical. It contains informations for internal tools,
    not actual metadata. Therefore it is only kept as a block text for Elan export."""
    
    trans.metadata.footer = "\t"
    for elem in root:
        trans.metadata.footer = (trans.metadata.footer + 
                                 ETree.tostring(elem,"utf-8").decode("utf-8"))
    
    #trans.metadata.footer = ETree.tostring(root, "utf-8").decode("utf-8")
def fromElan(f,**args):
    """Creates a Transcription object out of an ".eaf" file.
    Relies on the etree library.
    Footer stored in 'trans.metadata.footer' in block as a string."""
    
        # **args is for "encoding", which isn't used due to the xml library
    
    trans = Transcription()
    setchildtime = args.get('setchildtime',False)
    timeorder = {}
    root = None
    
    b_root = False
    for event, elem in ETree.iterparse(f, events=("start","end")):
            # Find root for operation (cleaning)
        if not b_root:
            root = elem
            b_root = True
        elif event == "end":
                # getTimeorder (/!\ not Timetable)
            if elem.tag == "TIME_ORDER":
                timeorder = readTime(trans,elem,timeorder)
                root.remove(elem)
                # getTiers
            elif elem.tag == "TIER":
                readTier(trans,elem,timeorder)
                root.remove(elem)
                # getHeader&Footer
            elif elem.tag == "HEADER":
                readHeader(trans,root,elem)
                root.remove(elem)
            elif elem.tag == "ANNOTATION_DOCUMENT":
                readFooter(trans,root)
                root.clear()
        # Transcription name and format
    getFormat(f,trans); trans.setstructure(setchildtime=setchildtime)
    return trans