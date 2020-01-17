from .Transcription import Transcription, Tier
import xml.etree.cElementTree as ETree

def escape(data):
    """Support function to replace 'xml>sax>saxutils'.
    Why is that needed here I don't know."""
    
    data = data.replace("&quot;","\"").replace("&apos;","'") \
               .replace("&lt;","<").replace("&gt;",">").replace("&amp;","&")
    return data

def readMeta(elem,trans):
    """Support function to add some metadata to the Transcription object.
    (corpus, recording & transcript)"""
    
    for el in elem:
        if el.tag == "project-name":
            if el.text:
                trans.metadata.corpus.name.append(el.text)
        elif el.tag == "transcription-name":
            if el.text:
                trans.metadata.transcript.name.append(el.text)
                trans.name = el.text
        elif el.tag == "referenced-file":
            url = el.get('url')
            if url:
                trans.metadata.recording.url.append(url)
                if "/" in url:
                    url = url.rsplit("/",1)[1]
                elif "\"" in url:
                    url = url.rsplit("\"",1)[1]
                trans.metadata.recording.name.append(url)
        elif el.tag == "ud-meta-information":
            for e in el:
                if "attribute-name" in e.attrib and e.text:
                    trans.metadata.transcript.open[e.get('attribute-name')] \
                                                   = e.text
            # /!\ If a previous 'comment' metadata was stored, it's overwritten
        elif el.tag == "comment":
            if el.text:
                trans.metadata.transcript.open['comment'] = el.text
        elif el.tag == "transcription-convention":
            if el.text:
                trans.metadata.transcript.open['guidelines'] = el.text
def readSpeakers(elem,trans):
    """Support function to add some metadata to the Transcription object.
    (speakers)"""
    
    id = ""; lang = ""
    for spk in elem:
            # Get the ID (or we can't create the speaker)
        id = spk.get('id')
        if not id:
            id = spk.get('abbreviation')
        if not id:
            continue
        spk = trans.metadata.addspeaker(id)
        for el in spk:
            if el.tag == "abbreviation":
                spk.open['abbreviation'] = el.text
            elif el.tag == "sex":
                if "value" in el.attrib:
                    spk.gender = el.get('value')
                elif el.text:
                    spk.gender = el.text
                # Languages are stored in a list of three lists:
                ## [ [ L1 ], [ L2 ], [ dialect (?!?) ] ]
                ## Default is stored in L1
                ## We don't (but should) check if a language is repeated between
                ##  sublists
            elif el.tag == "languages-used":
                for e in el:
                    lang = e.get('lang')
                    if lang:
                        spk.languages[0].append(e)
            elif el.tag == "l1":
                for e in el:
                    lang = e.get("lang")
                    if lang:
                        spk.languages[1].append(lang)
            elif el.tag == "l2":
                for e in el:
                    lang = e.get("lang")
                    if lang:
                        spk.languages[2].append(lang)
            elif el.tag == "ud-speaker-information":
                for e in el:
                    if "attribute-name" in e.attrib and e.text:
                        spk.open[e.get("attribute-name")] = e.text
                # /!\ If a previous 'comment' metadata was stored, it's overwritten
            elif el.tag == "comment":
                if el.text:
                    spk.open['comment'] = el.text
def readTimeline(elem,timeorder):
    """Support function to fill the 'timeorder' list."""
    
    for tli in elem:
        if "time" in tli.attrib:
            timeorder[tli.get("id")] = float(tli.get("time"))
        else:
            timeorder[tli.get("id")] = -1.
def readTier(elem,trans,timeorder, count):
    """Support function to fill the tiers.
    
    Note: category and type.
    category    :   'v', 'de', 'sup', 'nv' (verbal, german, suprasegmental, non-verbal)
    type        :   't', 'd', 'a' (transcription, non-verbal, annotation)
    There should be only one 't' per speaker."""
    
        # tier
        ## We don't check the speaker, category, type
    trans.addtier(); tier = trans.tiers[-1]
    for key, value in elem.attrib.items():
        if key == "display-name": 
            tier.name = value
        elif key == "category":
            tier.metadata['category'] = value
        elif key == "type":
            tier.type = value
        elif key == "speaker":
            tier.metadata['speaker'] = value
        # segments
    start = -1.; end = -1.
    cont = ""; id = ""; s_meta = {}
    for el in elem:
            # additional tier metadata
        if el.tag == "ud-tier-information":
            for e in el:
                key = e.get('attribute-name')
                if key and e.text:
                    tier.metadata[key] = e.text
        else:
                # segment time boundaries
            start = -1.; end = -1.
            for key, value in el.attrib.items():
                if key == "start":
                    start = timeorder[value]
                elif key == "end":
                    end = timeorder[value]
                # segment metadata
            s_meta.clear()
            for e in el:
                if (e.tag == "ud-information" and "attribute-name" in e.attrib and
                    e.text):
                    key = e.get("attribute-name"); value = e.text
                    s_meta[key] = value; el.remove(e)
                # id and content
            id = "a"+str(count); count += 1
            l_txt = []
            for txt in el.itertext():
                l_txt.append(txt)
            cont = escape("".join(l_txt))
                # creation
            tier.addsegment(-1, start, end, cont, id, "", True, tier, 1)
                # metadata
            tier.segments[-1].metadata = s_meta.copy()
def checkTrans(trans):
    """Support function to finalize the transcription.
    1. Establish a structure using speakers (and types).
    2. Deal with missing time boundaries."""
    
        # Clean the name
    for tier in trans:
        if "category" in tier.metadata:
            c = "["+tier.metadata['category']+"]"; l = len(c)*-1
            if tier.name.endswith(c):
                tier.name = tier.name[:l]
    
        # Get speakers
        ## First we sort the tiers by speakers
    l_spk = []; l_tiers = []; test = False
    for a in range(len(trans)):
        tier = trans.tiers[a]
        if "speaker" in tier.metadata:
            spk = tier.metadata['speaker']; test = False
            for b in range(len(l_spk)):
                if spk == l_spk[b]:
                    l_tiers[b].append((a,tier))
                    test = True; break
            if test == False:
                l_spk.append(spk); l_tiers.append([(a,tier)])
        ## Then we structure (using type too)
    del l_spk
    for list in l_tiers:
            # parent
        test = False
        for a,tier in list:
            if "type" in tier.metadata and tier.metadata['type'] == "t":
                for b,ctier in list:
                    if not a == b:
                        ctier.parent = tier.name
                        ctier.pindex = a
                        ctier.level = 1
                        tier.children.append(b)
                test = True; break
        if test == True:
            continue
        a = -1; tier = None
        for i in range(len(list)):
            b,ctier = list[i]
            if i == 0:
                a = b; tier = ctier; continue
            ctier.parent = tier.name
            ctier.pindex = a
            ctier.level = 1
            tier.children.append(b)
    del l_tiers
        
        # Get subd
        ## In case some time boundaries lacked a value
    l_segs = []
    for tier in trans:
        l_segs.clear()
        for a in range(len(tier)):
            start = tier.segments[a].start; end = tier.segments[a].end
            if end < 0:
                l_segs.append(tier.segments[a])
            elif start < 0.:
                l_segs.append(tier.segments[a])
                if end >= 0.:
                    ls = len(l_segs)
                    start = l_segs[0].start; end = l_segs[-1].end; dur = end-start
                    for a in range(ls):
                        seg = l_segs[a]
                        seg.start = start + dur*(a/ls)
                        seg.end = start + dur*((a+1)/ls)
                    l_segs.clear()
def fromExmaralda(f, **args):
    """Creates a Transcription object from an ".exb" file.
    Relies on the etree library."""

    trans = Transcription()
    timeorder = {}; id = 0
    root = None; head = None; body = None
    
    b_root = False
    for event, elem in ETree.iterparse(f, events=("start","end")):
        if not b_root:
            root = elem
            b_root = True; continue
        elif event == "start":
            if elem.tag == "head":
                head = elem
            elif elem.tag == "basic-body":
                body = elem
        else: # event == "end"
            if elem.tag == "meta-information":
                readMeta(elem,trans)
            elif elem.tag == "speakertable":
                readSpeakers(elem,trans)
                root.remove(head)
            elif elem.tag == "common-timeline":
                readTimeline(elem,timeorder)
                body.remove(elem)
            elif elem.tag == "tier":
                readTier(elem,trans,timeorder,id)
                body.remove(elem)
    del root; del timeorder
        # A series of checks
    checkTrans(trans)
        # We get name and format
    trans.format = "exmaralda"
    trans.metadata.transcript.format = trans.format
    if not trans.name:
        if "\\" in f:
            name = f.rsplit("\\", 1)[1]
        elif "/" in f:
            name = f.rsplit("/", 1)[1]
        else:
            name = f
        trans.name = name.rsplit(".",1)[0]
        trans.metadata.transcript.name = [trans.name]
    return trans