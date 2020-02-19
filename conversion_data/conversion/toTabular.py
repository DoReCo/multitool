from .Transcription import Transcription, Tier
import os

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data

    # Support functions
def getIDs(trans):
    """Fills the dictionaries { name : id }."""
    d_trans = {}; tr_id = "tr"; tr_count = 0
    d_spk = {}; spk_id = "spk"; spk_count = 0
    d_tiers = {}; ti_id = "ti"; ti_count = 0
    d_seg = {}; sg_id = "seg"; sg_count = 0
    for tran in trans:
            # Trans / metadata IDs
        d_trans[tran.name] = tr_id+str(tr_count) # 'tr_count' incremented later
            # Speaker IDs
        for spk in tran.transSpeakers():
            spk = tr_id+str(tr_count)+"_"+spk
            d_spk[spk] = spk_id+str(spk_count); spk_count += 1
            # Tier IDs
        for tier in tran:
            t_name = tr_id+str(tr_count)+"_"+tier.name
            d_tiers[t_name] = ti_id+str(ti_count); # 'ti_count' incr' later
            for seg in tier:
                if seg.unit == False:
                    continue
                s_name = ti_id+str(ti_count)+"_"+seg.id
                d_seg[s_name] = sg_id+ str(sg_count); sg_count += 1
            ti_count += 1
            # Late trans count increment
        tr_count += 1
    return (d_trans,d_spk,d_tiers,d_seg)
def fillCol(file,l_col):
    """Support function for 'writeX' functions: writes the columns header."""
        # Static data columns
    check = True
    for col in l_col:
        if check:
            file.write(col); check = False
            continue
        file.write(","+col)

    # Writes 'trans.csv'
def writeTrans(dir,trans,d_trans,encoding,sep):
    """Writes the 'transcriptions.csv'."""
    
        # Variables
    l_trans = ["ID","Name",                     # Columns
               "md_key","md_value"]
    f = os.path.join(dir,"trans.csv")           # Output file
        # We Write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,l_trans)
            # Rows
        keys = []; values = []
        for tran in trans:
            d_md = tran.metadata.getall()
            file.write("\n{},{}"
                       .format(d_trans[tran.name],tran.name))
            keys = []; values = []
            for key, value in d_md.items():
                keys.append(key); values.append(str(value))
            keys = sep.join(keys); values = sep.join(values)
            file.write(",{},{}".format(keys,values))
    return l_trans
    # Writes 'speakers.csv'
def writeSpeakers(dir,trans,d_trans,d_spk,encoding,sep):
    """Writes the 'speakers.csv'."""
    
        # Variables
    l_spk = ["ID","Trans_ID","name","gender",   # Static data columns
             "age","birthdate","birthplace",
             "currentdate","currentplace",
             "familystate","education",
             "occupation","L1","L2","dialects",
             "md_key","md_value"]
    f = os.path.join(dir,"speakers.csv")        # Output file
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,l_spk)
            # Rows
        for tran in trans:
            tr_id = d_trans[tran.name]
            for name,spk in tran.metadata.speakers.items():
                spk_id = d_spk[tr_id+"_"+name]
                l1 = sep.join(spk.languages[0])
                l2 = sep.join(spk.languages[1])
                dia = sep.join(spk.languages[2])
                file.write("\n{},{},{},{},{},{},{},{},{},{},"
                           "{},{},{},{},{}"
                           .format(spk_id,tr_id,spk.name,spk.gender,
                                   spk.age,spk.birthDate,spk.birthLoc,
                                   spk.curDate,spk.curLoc,spk.familyState,
                                   spk.eduState,spk.jobState,l1,l2,dia))
                keys = []; values = []
                for key, value in spk.open.items():
                    keys.append(key); values.append(value)
                keys = sep.join(keys); values = sep.join(values)
                file.write(",{},{}".format(keys,values))
    return l_spk
    # Writes 'tiers.csv'
def writeTiers(dir,trans,d_trans,d_spk,d_tiers,encoding,sep):
    """Writes the 'tiers.csv'."""
    
        # Variables
    l_tiers = ["ID","Trans_ID","Speakers_ID",   # Static data columns
               "name","type","start","end",
               "dependency","md_key","md_value"]
    f = os.path.join(dir,"tiers.csv")           # Output file
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,l_tiers)
            # Rows
        for tran in trans:
            tr_id = d_trans[tran.name]
            for tier in tran:
                ti_id = d_tiers[tr_id+"_"+tier.name]; pti_id = ""
                if tier.parent:
                    pti_id = d_tiers[tr_id+"_"+tier.parent] # parent tier
                spk_id = d_spk[tr_id+"_"+tier.metadata['speaker']]
                file.write("\n{},{},{},{},{},{},{},{}"
                           .format(ti_id,tr_id,spk_id,tier.name,tier.type,
                                   tier.start,tier.end,pti_id))
                keys = []; values = []
                for key, value in tier.metadata.items():
                    keys.append(key); values.append(value)
                keys = sep.join(keys); values = sep.join(values)
                file.write(",{},{}".format(keys,values))
    return l_tiers
    # Writes a given 'tierx.csv'
def writeTier(dir,trans,tier,tr_id,d_spk,d_tiers,d_seg,encoding,sep):
    """Writes a given 'tier.csv'."""
    
        # Variables
    sg_id = "seg"; count = 0
    ti_id = d_tiers[tr_id+"_"+tier.name]
    spk_id = d_spk[tr_id+"_"+tier.metadata['speaker']]
    pti_id = d_spk.get(tr_id+"_"+tier.parent,"")
    l_tiers = ["ID","Trans_ID","Tiers_ID",      # Static data columns
               "start","end","content",
               "dependency","notes",
               "md_key","md_value"]
    l_dtiers = []                               # Dynamic data columns
    f = os.path.join(dir,(ti_id+".csv"))        # Output file
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,l_tiers)
            #Rows
        for seg in tier:
            if seg.unit == False:
                continue
            id = d_seg[ti_id+"_"+seg.id]
            ref = d_seg.get(pti_id+"_"+seg.ref,"")
            file.write("\n{},{},{},{:.3f},{:.3f},{},{}"
                       .format(id,tr_id,ti_id,seg.start,seg.end,
                               seg.content,ref))
                    # Notes
            file.write(","+sep.join(seg.notes))
                    # Metadata
            keys = []; values = []
            for key, value in seg.metadata.items():
                keys.append(key); values.append(value)
            keys = sep.join(keys); values = sep.join(values)
            file.write(",{},{}".format(keys,values))
    l_tiers = l_tiers + l_dtiers
    return l_tiers
    # Writes 'corpus-metadata.json'
def fillJCol(file,l_col,tab,sep,spk=False):
    """Support function for 'writeJson': writes the static table part."""
        # 'header'
    file.write("\t\t{\n\t\t\t\"tableSchema\": {\n\t\t\t\t\"columns\": [\n")
        # Columns
    ln = len(l_col)-1; l_ids = [] # 'l_ids' will collect for foreign keys
    for a in range(ln+1):
        col = l_col[a]
            # Foreign keys
        if col == "Trans_ID":
            l_ids.append(("Trans_ID","trans.csv"))
        elif col == "Metadata_ID":
            l_ids.append(("Metadata_ID","metadata.csv"))
        elif col == "Speakers_ID":
            l_ids.append(("Speakers_ID","speakers.csv"))
        elif col == "Tiers_ID":
            l_ids.append(("Tiers_ID","tiers.csv"))
        file.write("{}\t{{\n{}\t\t\"datatype\": \"string\",\n"
                   "{}\t\t\"name\": \"{}\",\n"
                   .format(tab,tab,tab,col))
        if col == "ID":
            file.write("{}\t\t\"required\": true,\n".format(tab))
        if col == "notes" or col == "md_key" or col == "md_value":
            file.write("{}\t\t\"separator\": \"{}\",\n"
                       .format(tab,sep))
        elif spk and (col == "L1" or col == "L2" or col == "dialects"):
            file.write("{}\t\t\"separator\": \"{}\",\n"
                       .format(tab,sep))
        file.write("{}\t}}".format(tab))
        if a < ln:
            file.write(",")
        file.write("\n")
    file.write("\t\t\t\t],\n")
        # Foreign keys
    ln = len(l_ids)-1
    if ln >= 0:
        file.write("\t\t\t\t\"foreignKeys\": [\n")
        for a in range(ln+1):
            tuple = l_ids[a]
            file.write("{}{{\n{}\t\"columnReference\": [\n{}\t\t"
                       "\"{}\"\n{}\t],\n{}\t\"reference\": {{\n"
                       "{}\t\t\"resource\": \"{}\",\n{}\t\t"
                       "\"columnReference\": [\n{}\t\t\t\"ID\"\n"
                       "{}\t\t]\n{}\t}}\n{}}}"
                       .format(tab,tab,tab,tuple[0],tab,tab,tab,
                               tuple[1],tab,tab,tab,tab,tab))
            if a < ln:
                file.write(",")
            file.write("\n")
        file.write("\t\t\t\t],\n")
        # Primary key
    file.write("\t\t\t\t\"primaryKey\": [\n{}\"ID\"\n\t\t\t\t]\n"
               "\t\t\t}},\n"
               .format(tab))
def writeJson(dir,l_trans,l_md,l_spk,l_tiers,dl_tiers,encoding,sep):
    """Writes the 'corpus-metadata.json'."""
    
        # Variables
    f = os.path.join(dir,"corpus-metadata.json")
    tab = "\t\t\t\t\t"
        # We write
    with open(f,'w',encoding=encoding) as file:
            # context
        file.write("{\n\t\"@context\": [\n\t\t\"http://www.w3.org/ns/csvw\","
                   "\n\t\t{\n\t\t\t\"@langage\": \"en\"\n\t\t}\n\t],\n\t"
                   "\"tables\": [\n")
            # Metadata
            ## ??? (see dublin-core ?)
            # Trans table
        fillJCol(file,l_trans,tab,sep)
        file.write("\t\t\t\"url\": \"trans.csv\"\n\t\t},\n")
            # Speakers table
        fillJCol(file,l_spk,tab,sep,True)
        file.write("\t\t\t\"url\": \"speakers.csv\"\n\t\t},\n")
            # Tiers table
        fillJCol(file,l_tiers,tab,sep)
        file.write("\t\t\t\"url\": \"tiers.csv\"\n\t\t},\n")
            # Tierx tables
        count = len(dl_tiers)-1; incr = 0
        for ti_id, l_tier in dl_tiers.items():
            fillJCol(file,l_tier,tab,sep)
            file.write("\t\t\t\"url\": \"{}.csv\"\n\t\t}}"
                       .format(ti_id))
            if incr < count:
                file.write(",")
            file.write("\n"); incr += 1
        file.write("\t]\n}")
    # Main
def toTabular(f, trans, **args):
    """Creates a W3C Tabular data format from a Transcription object."""
    import os
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
    sep = args.get('sep',"\\\\t")
        # We need a list of transcriptions
    if not args.get('multiple',False):
        trans = [trans]; f = [f]
        # We actually need a directory
        ## This is a breach of convention but... well...
    dir = f[0]
    if not os.path.isdir(dir):
        dir,fname = os.path.split(dir)
        fname = os.path.splitext(fname)[0]; dir = os.path.join(dir,fname)
        if not os.path.isdir(dir):
            os.mkdir(dir)
        # Complete information
    for tran in trans:
        tran.timetable.clear(); tran.setchildtime()
        tran.checkSpeakers()
    
        # Variables
    d_trans,d_spk,d_tiers,d_seg = getIDs(trans)         # dict { name : id }
    l_trans = []; l_md = []; l_spk = []; l_tiers = []   # list [ columns ]
    dl_tiers = {}                                       # dict { id : [columns] }
    
        # We write 'transcriptions.csv'
    l_trans = writeTrans(dir,trans,d_trans,encoding,sep)
        # We write 'speakers.csv'
    l_spk = writeSpeakers(dir,trans,d_trans,d_spk,encoding,sep)
        # We write 'tiers.csv'
    l_tiers = writeTiers(dir,trans,d_trans,d_spk,d_tiers,encoding,sep)
        # We write each 'tier.csv'
    for tran in trans:
        tr_id = d_trans[tran.name]
        for tier in tran:
            key = d_tiers[tr_id+"_"+tier.name]
            dl_tiers[key] = writeTier(dir,tran,tier,tr_id,d_spk,d_tiers,
                                      d_seg,encoding,sep)
        # We write 'corpus-metadata.json'
    writeJson(dir,l_trans,l_md,l_spk,l_tiers,dl_tiers,encoding,sep)
    return 0