from ..conversion.Transcription import Transcription

def createTabular(f,trans,ref_tier,l_tiers=[],**args):
    """Writes a single table for analysis purposes."""
    
        # Checks
    if (not trans) or ((ref_tier < 0) or ref_tier >= len(trans)):
        return 1
    l_copy = []; lt = len(trans)
    if not l_tiers:
        for a in range(len(trans)):
            if not a == ref_tier:
                l_copy.append(a)
    else:
        for ind in l_tiers:
            if ind < 0 or ind >= lt:
                continue
            l_copy.append(ind)
    l_tiers = l_copy.copy(); del l_copy
        # Variables
    encoding = args.get('encoding',"utf-8"); unit = args.get('unit',False)
    sep = args.get('sep',"\\\\t"); id = args.get('id',"R")
    rtier = trans.tiers[ref_tier]
    l_segs = rtier.getsegtree(ref_tier); l_pos = []; ld_segs = []
    
        # We fill 'l_pos' and 'ld_segs'
        ## For each segment
    for a in range(len(rtier)):
        if not rtier.segments[a].unit:
            ld_segs.append(None); continue
            # segment structure
        l_refs = l_segs[a]; l_pos.append(-1); ld_segs.append({})
            # Get the information
        for b in range(len(l_refs)):
                # segment pos
            if l_refs[b][0] == ref_tier:
                l_pos[-1] = b
                # dictionary
            elif l_refs[b][0] in l_tiers:
                ld_segs[-1][l_refs[b][0]] = l_refs[b]
    del l_segs
                
        # We write
    count = 0; text = ""
    with open(f,'w',encoding=encoding) as file:
            # columns
        file.write("ID,{},".format(rtier.name))
        for ind in l_tiers:
            file.write("{},".format(trans.tiers[ind].name))
        file.write("\n")
            # rows
            # For each segment
        for a in range(len(rtier)):
            seg = rtier.segments[a]
            if (not unit) and (not seg.unit):
                continue
            d_seg = ld_segs[a]
                # id
            file.write("{},".format(id+str(count))); count += 1
                # ref_tier
            file.write("{},".format(seg.content))
                # other tiers
            for ind in l_tiers:
                tuple = d_seg.get(ind,None)
                if not tuple:
                    file.write(","); continue
                l_seg = tuple[2]
                ctier = trans.tiers[tuple[0]]
                if not l_seg:
                    file.write(",")
                else:
                    text = ctier.segments[l_seg[0]].content
                    for b in range(1,len(l_seg)):
                        text = text + ("{}{}"
                               .format(sep,ctier.segments[l_seg[b]].content))
                    file.write(text+",")
            file.write("\n")