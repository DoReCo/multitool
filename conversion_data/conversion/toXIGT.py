from .Transcription import Transcription, Tier
import re

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data

    # getStruct()
def getStruct(trans,levels,sep,child):
    """Support function to structure the tiers."""
    
        # Variables
    l_struct = []; d_tiers = {}
    l_parents = []; type = ""; r_sep = None
    if sep:
        r_sep = re.compile('{}\d+$'.format(sep))
        # Fill 'l_tiers'
    if levels:
        for t_ind,n_name in levels:
            d_tiers[t_ind] = (t_ind,trans.tiers[t_ind],n_name)
    else:
        for a in range(len(trans)):
            tier = trans.tiers[a]
            d_tiers[a] = (a,tier,tier.name)
        # We get the parents
    for t_ind,tier,t_name in d_tiers.values():
        if not tier.parent:
            l_parents.append((t_ind,tier,t_name))
        # We use 'l_parents' for the final structure
        ## We also want to know the type of tier it is
    for t_ind,tier,name in l_parents:
        l_struct.append([])
            # We add the parent
        l_struct[-1].append((t_ind,tier,"none",name))
        l_child = tier.getallchildren(1)
            # For each child tier
        for a in range(1,len(l_child)):
            c_ind,c_tier,c_name = d_tiers.get(l_child[a][0],(-1,""))
            if c_ind < 0:
                continue
                # We need to test the type
            type = ""
                ## 'child'
            if child and c_tier.name.endswith(child):
                type = "child"
                ## 'muffin' (part of the same Xigt <tier>)
            elif r_sep and r_sep.search(c_tier.name):
                type = "muffin"
                ## 'segmentation' / 'alignment'
            else:
                o_ref = ""
                for seg in c_tier:
                    if not o_ref:
                        o_ref = seg.ref; continue
                    elif o_ref == seg.ref:
                        type = "segm"; break
                    o_ref = seg.ref
                if not type:
                    type = "align"
                # We add the child
            l_struct[-1].append((c_ind,c_tier,type,c_name))
    del d_tiers; del l_parents
    return l_struct
    # Support functions for 'writeTiers()'
def getId(d_tnames,d_tids,name):
    """Support support function ('writeTiers()') to get an id."""
    t_id = d_tnames.get(name,"")
    if not t_id:
        char = name[0:1]
        while True:
            t_id = t_id + char
            if t_id not in d_tids:
                d_tids[t_id] = name; break
        d_tnames[name] = t_id
    return t_id
def addItems(trans,l_igtems,t_id,tier,type,d_srefs,
             t_ind,pt_ind,l_csegs,l_sind,sep,r_ssep):
    """Sup-support function ('writeTiers()') to add <items>."""
    
        # Variables
    incr = len(l_igtems)+1; ptier = None
    if not t_ind == pt_ind:
        ptier = trans.tiers[pt_ind]
    l_segs = []; ls = 0; d_sep = {}; itype = ""
    
        # 1. We want a clearer list of segments
        ## For each segment
    for a in range(len(l_csegs)):
        s_ind = l_csegs[a]; ps_ind = l_sind[a]
        seg = tier.segments[s_ind]; pseg = None; s_ref = ""
            # Segment ref
        if ptier and (not ptier == tier):
            pseg = ptier.segments[ps_ind]
            s_ref = d_srefs.get(pseg.id,"")
            # Segment type
        s_type = seg.metadata.get('type',"")
        if s_type:
            s_type = " type=\"{}\"".format(s_type)
            # Segment id / content
            ## We have to deal with non-continuous segments
        content = seg.content
        if r_ssep:
            match = r_ssep.search(content)
            if match:
                content,s_item,s_count = content.rsplit(sep,2)
                l_pack = d_sep.get(s_item,[])
                if l_pack:
                    d_sep[s_item].append(s_ref); continue
                else:
                    d_sep[s_item] = [ls]
        s_id = t_id+str(incr); incr += 1
        d_srefs[seg.id] = s_id
            # We add to 'l_segs'
        l_segs.append((s_id,s_type,content,s_ref)); ls += 1
        # A little rework on 'd_sep'
    d_regroup = {}
    for l_ids in d_sep.values():
        d_regroup[l_ids[0]] = l_ids[1:]
    del d_sep
    
        # 2. We use that to write <items>
    for a in range(len(l_segs)):
        s_id,s_type,content,s_ref = l_segs[a]
            # if no type or "muffin"
        if not type or type == "muffin":
            l_igtems.append("<item id=\"{}\"{}>{}</item>\n"
                            .format(s_id,s_type,content))
            continue
            # we regroupe if needed
        l_ids = d_regroup.get(s_id,[])
        for id in l_ids:
            s_ref = s_ref + " " + id
            # type
        itype = ""
        if type == "align":
            itype = "alignment"
        elif type == "segm":
            itype = "segmentation"
        elif type == "child":
            itype = "children"
        else:
            l_igtems.append("\t\t\t<item id=\"{}\"{}>{}</item>\n"
                            .format(s_id,s_type,content)); continue
            # append
        l_igtems.append("\t\t\t<item id=\"{}\"{} {}=\"{}\""
                        ">{}</item>\n"
                        .format(s_id,s_type,itype,s_ref,content))
    del d_regroup; del l_segs
    return l_igtems
def writeTier(file,t_id,name,o_id,type,ch_child):
    """Sup-support function ('writeTiers()') to write the <tier> tag."""
    file.write("\t\t<tier id=\"{}\" type=\"{}\"".format(t_id,name))
    if type == "align":
        file.write(" alignement=\"{}\"".format(o_id))
    elif type == "segm":
        file.write(" segmentation=\"{}\"".format(o_id))
    if ch_child:
        file.write(" children=\"{}\"".format(t_id))
    file.write(">\n")
    # writeTiers()
def writeTiers(file,trans,levels,sep):
    """Support function to write the <igt> elements.
    'levels' is a list of lists of tuples:
    (tier_index,tier,type,name)."""
        # Variables
    d_tiers = {}; r_tsep = None; r_ssep = None
    if sep:
        r_ssep = re.compile("{}\d+{}\d+$".format(sep,sep))
    l_igtems = []; i_igt = 1; ch_child = False
    d_tids = {}; d_tnames = {}; o_id = ""; o_type = ""; o_name = ""
    d_srefs = {}; v_id = ""
        # <xigt> opening
    file.write("<xigt-corpus>\n")
        # For each grouping (see 'getStruct()')
    for l_tiers in levels:
            # We will need to find tiers a lot
        d_tiers.clear()
        for tuple in l_tiers:
            d_tiers[tuple[0]] = tuple
            # We resort to 'getsegtree()'
        ptier = l_tiers[0][1]
        ll_segs = ptier.getsegtree(l_tiers[0][0])
            # And finally we can write '<igt>' items
            ## For each segment in ptier
        l_igtems.clear(); o_id = ""; o_type = ""; o_name = ""; v_id = ""
        ch_child = False
        for l_segs in ll_segs:
                # opening
            file.write("\t<igt id=\"IGT"+str(i_igt)+"\">\n"); i_igt += 1
                # For each child segment (including the parent
            for t_ind,pt_ind,l_csegs,l_sind in l_segs:
                t_ind,tier,type,name = d_tiers.get(t_ind,(-1,None,"",""))
                    # We need a <tier> id
                t_id = getId(d_tnames,d_tids,name)
                    # We test if there is a <tier> to write
                if (((not type == "muffin") and (not type == "child"))
                    and l_igtems):
                        # We write the <tier>
                    writeTier(file,o_id,o_name,v_id,o_type,ch_child)
                    for igtem in l_igtems:
                        file.write(igtem)
                    file.write("\t\t</tier>\n")
                        # We clear
                    l_igtems.clear(); v_id = o_id
                l_igtems = addItems(trans,l_igtems,t_id,tier,type,d_srefs,
                                    t_ind,pt_ind,l_csegs,l_sind,sep,r_ssep)
                o_id = t_id; o_type = type; o_name = name
               # last pass
            if l_igtems:
                    # We write the <tier>
                writeTier(file,t_id,name,o_id,type,ch_child)
                for igtem in l_igtems:
                        file.write(igtem)
                file.write("\t\t</tier>\n")
                # closure
            file.write("\t</igt>\n")
        # <xigt> end
    file.write("</xigt-corpus>\n")
    # Main function
def toXIGT(f, trans, **args):
    """Creates an Xigt file from a Transcription object.
    
    PARAMETERS:
    - 'levels'  :   User-picked tiers
                    must be a list of tuples (tier_index,new_name)
    - 'sep'     :   The separator for 'segm/align/muffin' tiers.
    - 'child'   :   The identifier for 'children' type tiers.
    - 'multiple':   Whether there is more than one transcription.
    Note: all 'levels' really does is restrain the tiers processed
    and renaming them with 'new_name' in the final file.
    Note: if multiple transcriptions, all are put in one file."""
    
        # Kwargs
    encoding = args.get('encoding',"utf-8")    # encoding
    levels = args.get('levels',None)           # structure
    sep = args.get('sep',"_")                  # separator
    child = args.get('child',"")               # children tiers
    multiple = args.get('multiple',False)      # multiple trans'
    if not multiple:
        trans = [trans]; f = [f]; levels = [levels]
        # File opening
    if not f:
        return
    f = f[0]
    file = open(f, 'w', encoding=encoding)
        # We write
    for a in range(len(trans)):
        tran = trans[a]; lev = levels[a]
        lev = getStruct(tran,lev,sep,child)     # get the structure
        writeTiers(file,tran,lev,sep)           # write the tiers
        # File closure
    file.close()
        