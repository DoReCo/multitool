from ..conversion.Transcription import Transcription

def timeStructure(trans,tiers,mode=1,**args):
    """Parenting a list of tier pairs including segment ids/refs.
    
    PARAMETERS:
    -   'trans' :   a 'Transcription.py' transcription object.
    -   'tiers' :   a list of tuples ('tier_index','tier_child_index',type)
                    or dict {'tier_index' : (['tier_child_indexes'],type)}
    -   'mode'  :   whether 'tiers' is a list (0) or a dict (1).
    Note: 'type' is either 'time' or 'ref'
          to set the child tier accordingly.
          
    RETURNS:
    - '0' on success. 'trans' is directly edited."""
    
        # Variables
    sym = args.get('sym',"a"); count = 0
    setstruct = args.get('setstructure',True)
        # User input can be list or dictionary (mode)
    l_tiers = []; l_temp = []; l_ids = {}
    if not tiers:
        return 1 # No idea what to do by default
    elif mode == 0:
        l_tiers = tiers.copy()
            # get all tiers
        for pind,cind,type in l_tiers:
            if pind not in l_temp:
                l_temp.append(pind)
            if cind not in l_temp:
                l_temp.append(cind)
    elif mode == 1:
        for key,value in tiers.items():
            if key not in l_temp:
                l_temp.append(ind)
            for ind,type in value:
                l_tiers.append((key,ind,type))
                if ind not in l_temp:
                    l_temp.append(ind)
    else:
        return 1 # eh
    del tiers
    
        # We want dictionaries for all relevant tiers
    dd_tiers = {}; d_tiers = {}
    for ind in l_temp:
        tier = trans.tiers[ind]
        d_tiers.clear()
        for a in range(len(tier)):
            seg = tier.segments[a]
            if seg.start in d_tiers:
                d_tiers[seg.start].append(a)
            else:
                d_tiers[seg.start] = [a]
            if seg.end in d_tiers:
                d_tiers[seg.end].append(a)
            else:
                d_tiers[seg.end] = [a]
        dd_tiers[ind] = d_tiers.copy()
            # We also want to keep track of ids
        l_ids[ind] = False
    del l_temp
        
        # We're now working with pairs of (parent,child) tier indexes
    for pind,cind,type in l_tiers:
        ptier = trans.tiers[pind]; ctier = trans.tiers[cind]
        pid = l_ids[pind]
            # Parenting
        ctier.parent = ptier.name; ctier.pindex = pind
        ptier.addchild(cind)
        if type == 'ref':
            ctier.truetype = 'ref'
        else:
            ctier.truetype = 'time'
            # IDs
            ## Recover the dictionary
        d_segs = dd_tiers[pind]
            ## Make sure the parent tier segments have IDs
        if not pid:
            for seg in ptier:
                if not seg.id:
                    seg.id = sym+str(count); count += 1
            ## Same for child tier, plus REFs
        for seg in ctier:
                # ids
            if not seg.id:
                seg.id = sym+str(count); count += 1
                # refs
                ## We get the parent segment index
            l_start = d_segs.get(seg.start,[])
            l_end = d_segs.get(seg.end,[])
            ind = -1
            for a in l_start:
                for b in l_end:
                    if b == a:
                        ind = a; break
            if ind == -1:
                continue # Somehow this method has failed
                ## We refer
            seg.ref = ptier.segments[ind].id
    if setstruct:
        trans.setstructure()
    return 0