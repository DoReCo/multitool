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
    # Support functions
def getFormat(f,trans):
    """Support function to get the transcription's name and format."""
        # Name
    trans.name = os.path.split(f)[1]
    trans.name = os.path.splitext(trans.name)[0]
    trans.metadata.transcript.name = [trans.name]
        # Format
    trans.format = "elan"
    trans.metadata.transcript.format = trans.format

def setRef(string):
    """Support support function ('getStruct') for a list of refs."""
    
        # Character segmentation is discarded
    if "[" in string:
        string = string.split("[",1)[0]
        # Because children
    l_refs = []
    if " " in string:
        l_refs = string.split(" ")
    else:
        l_refs = [string]
    return l_refs
def getStruct(elem,sep,child):
    """Support function to turn an <igt> xml element
    into a tuple (d_ids,l_segs):
    - a list of segments 'l_segs'
    - a dict 'd_ids' to access those segments by ids
    Note:
    - 'children' references are divided into as many 'segments'.
    - 'alignment' references are attributed to separate 'tiers'."""
    
        # Variables
    d_ids = {}
    l_segs = []; ln = 0; ch_align = False; ch_child = False
    i_item = 0; i_ref = 0; i_ttype = 0; i_sid = 0; d_type = {} # increments
    s_old = ""; t_type = ""

        #### For each <tier> ####
    for tier in elem.iter("tier"):
            # tier type
        t_save = tier.get("type",None)
        if not t_save:
            t_save = "tier"+str(i_ttype); i_ttype += 1
            #### For each <item> in that <tier> ###
        i_item = 0; s_old = ""; t_type = ""; d_type.clear()
        for item in tier.iter("item"):
                # attributes
                ## content
            s_save = ""
            for text in item.itertext():
                s_save = s_save + text
                ## id / type
            s_type = item.get("type"); s_id = item.get("id",None)
            if not s_id:
                s_id = "s"+str(i_sid); i_sid += 1
            while s_id in d_ids.keys():
                s_id = "s"+str(i_sid); i_sid += 1
                ## reference
            s_ref = item.get("segmentation",[])
            ch_align = False; ch_child = False
            if not s_ref:
                s_ref = item.get("alignment",[])
                if not s_ref:
                    s_ref = item.get("children",[])
                    if s_ref:
                        ch_child = True
                else:
                    ch_align = True
            if s_ref:
                s_ref = setRef(s_ref)   # We want a list of refs
            elif i_item == 0:
                s_ref = [s_id]; s_old = s_id    # default 'self'
            else:
                s_ref = [s_old]                 # 'muffin' case
                # We add
            i_ref = 0; lref = len(s_ref); s_content = ""
            for ref in s_ref:
                    # We get the right 't_type'
                if ch_align:
                    nb = d_type.get(ref,-1)
                    if nb < 0:
                        t_type = t_save
                        d_type[ref] = 0
                    else:
                        t_type = t_save+sep+str(nb)
                        d_type[ref] += 1
                elif ch_child:
                    t_type = t_save+child
                else:
                    t_type = t_save
                    # We get the right content
                if ch_child and lref > 1:
                    s_content = (s_save+sep+str(i_item)+sep+str(i_ref))
                else:
                    s_content = s_save
                    # to 'l_segs'
                l_segs.append((s_id,ref,t_type,
                               s_type,s_content))
                    # to 'd_ids'
                d_ids[s_id] = ln; ln += 1; i_ref += 1
            i_item += 1
    return (d_ids,l_segs)
def getTiers(trans,d_tiers,struct,g_id,i_id):
    """Support function to add tiers / segments to 'trans'.
    
    After unpacking 'struct', we have a list of segments 'l_segs'.
    We also have dicts to explore that list by 'id', 'ref' or 'type'.
    The game is to attribute all segments to tiers:
    - if the tier doesn't exist ('l_segs[a][2]'), we creat it
    - the parent segment must exist ('l_segs[a][1]')
      or be itself ('== l_segs[a][0]').
    - if it doesn't, we put that segment on 'l_temp' and wait.
    Notes:
    - segments whose 'ref' is invalid (no 'id' for it) are discared.
    - no recursion is used due to Python's default depth and modes."""
    
        # Unpacking 'struct'
    d_ids,l_segs = struct
    d_ids,l_segs = struct
        # Variables
    l_loop = []; l_temp = []
    for a in range(len(l_segs)):
        l_loop.append(a)
    d_gids = {}     # ids to the actual segments
        
        # We loop
    while l_loop:
            # For each remaining index of 'l_segs'
        for a in l_loop:
                # We check the 'ref'
                ## (and discard if no match)
            if l_segs[a][1] not in d_ids.keys():
                continue
                # Unpacking
            id,ref,t_name,s_type,content = l_segs[a]
                # We check the parent
            t_pind,ptier,pind,pseg = d_gids.get(ref,(-1,None,-1,None))
                ## If it exists, we add the segment
            if pseg:
                    # We check the tier
                t_ind,tier = d_tiers.get(t_name,(-1,None))
                if not tier:
                    t_ind,tier = trans.addtier(t_name)
                    d_tiers[t_name] = (t_ind,tier)
                    tier.truetype = "ref"
                    tier.parent = ptier.name; tier.pindex = t_pind
                    ptier.addchild(t_ind)
                    # id
                s_id = g_id+str(i_id); i_id += 1
                tier.addsegment(-1,-1,-1,content,s_id,pseg.id,
                                True,tier,1)
                if s_type:
                    tier.segments[-1].metadata["type"] = s_type
                d_gids[id] = (t_ind,tier,
                              len(tier)-1,tier.segments[-1])
                ## If it is itself, we add the segment
            elif ref == id:
                    # We check the tier
                t_ind,tier = d_tiers.get(t_name,(-1,None))
                if not tier:
                    t_ind,tier = trans.addtier(t_name)
                    d_tiers[t_name] = (t_ind,tier)
                    tier.truetype = "time"
                    tier.start = 0.; tier.end = 0.
                    # id
                s_id = g_id+str(i_id); i_id += 1
                tier.addsegment(-1,tier.end,tier.end+1.,content,
                                s_id,"",True,tier,1)
                tier.end += 1.
                d_gids[id] = (t_ind,tier,
                              len(tier)-1,tier.segments[-1])
                ## Otherwise we need to wait.
            else:
                l_temp.append(a)
        l_loop = l_temp.copy(); l_temp.clear()
        return i_id
    # Main function
def fromXIGT(f,**args):
    """Creates a Transcription object out of an ".xml" file.
    Relies on the etree library.
    
    While this import tries to cover 'all' possible cases, a few
    mishaps can happen:
    - 'alignment' references don't take <item> type into account.
    - characters in 'segmentation' are discarded,
      meaning not used to reorder.
    Namely while the <tier> elements can be in disorder, the <item> ones
    should not."""
    
    trans = Transcription()
    d_tiers = {}                # keeps track of tiers
    g_id = args.get("id","a")   # for id increment (see 'getTiers')
    i_id = 0
    sep = args.get("sep","_")   # for type increment (see 'getStruct')
    child = args.get("child"    # to append to a 'children' tier
                     ,"_child") #  (see 'getStruct')
    
    root = None; b_root = False
        # Main loop
    for event, elem in ETree.iterparse(f, events=("start","end")):
        if not b_root:
            root = elem; b_root = True
        elif event == "end" and elem.tag == "igt":
            struct = getStruct(elem,sep,child)      # get the structure
            root.remove(elem)
            i_id = getTiers(trans,d_tiers,struct,   # use it on 'trans'
                            g_id,i_id)
    getFormat(f,trans)
    return trans
