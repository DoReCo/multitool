from .Transcription import Transcription, Tier

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data

    # Fills the ID dictionaries
def getIDs(trans):
    """Fills the dictionaries { name : id }."""
    d_trans = {}; tr_id = "tr"; tr_count = 0
    d_md = {}; md_id = "md"; md_count = 0
    d_spk = {}; spk_id = "spk"; spk_count = 0
    d_tiers = {}; ti_id = "ti"; ti_count = 0
    for tran in trans:
            # Trans / metadata IDs
        d_trans[tran.name] = tr_id+str(tr_count) # 'tr_count' incremented later
        d_md[tran.name] = d_md+str(md_count); md_count += 1
            # Speaker IDs
        for spk in tran.tranSpeakers():
            spk = tr_id+str(tr_count)+"_"+spk
            d_spk[spk] = spk_id+str(spk_count); spk_count += 1
            # Tier IDs
        for tier in tran:
            name = tr_id+str(tr_count)+"_"+tier.name
            d_tiers[name] = ti_id+str(ti_count); ti_count += 1
            # Late trans count increment
        tr_count += 1
    return (d_trans,d_md,d_spk,d_tiers)
    # Writes 'trans.csv'
def writeTrans(dir,trans,d_trans,d_md,encoding):
    """Writes the 'transcriptions.csv'."""
    
        # Variables
    l_trans = ["ID","Metadata_ID","Name"]       # Columns
    f = os.path.join(dir,"Trans.csv")           # Output file
        # We Write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        check = True
        for col in l_trans:
            if check:
                file.write(col); check = False
                continue
            file.write(","+col)
            # Rows
        for tran in trans:
            file.write("\n{},{},{}"
                       .format(d_trans[tran.name]),d_md[tran.name],
                               tran.name)
    return l_trans
    # Writes 'metadata.csv'
def writeMetadata(dir,trans,d_trans,d_md,encoding):
    """Writes the 'metadata.csv'."""
    
        # Variables
    l_md = ["ID","Trans_ID"]                    # Static data columns
    l_dmd = []                                  # Dynamic data columns
    f = os.path.join(dir,"Metadata.csv")        # Output file
        # We add dynamic data columns
        ## ???
        # We Write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        check = True
        for col in l_trans:
            if check:
                file.write(col); check = False
                continue
            file.write(","+col)
            # Rows
        for tran in trans:
                # Static data
            file.write("\n{},{}"
                       .format(d_md[tran.name]),d_trans[tran.name])
                # Dynamic data
                ## ???
    l_md = l_md + l_dmd
    return l_md
    # Writes 'speakers.csv'
def writeSpeakers(dir,trans,d_trans,d_spk,encoding):
    """Writes the 'speakers.csv'."""
    
        # Variables
    l_spk = ["ID","Trans_ID","name","gender",   # Static data columns
             "age","birthdate","birthplace",
             "currentdate","currentplace",
             "familystate","education",
             "occupation","L1","L2","dialects"]
    l_dspk = []                                 # Dynamic data columns
    f = os.path.join(dir,"Speakers.csv")        # Output file
        # We add dynamic data columns
        ## ???
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        check = True
        for col in l_trans:
            if check:
                file.write(col); check = False
                continue
            file.write(","+col)
            # Rows
        for tran in trans:
            tr_id = d_trans[tran.name]
            for name,spk in tran.metadata.speakers.items():
                    # Static data rows
                spk_id = d_spk[tr_id+"_"+name]
                file.write("\n{},{},{},{},{},{},{},{},{},{},"
                           "{},{},{},{},{}"
                           .format(spk_id,tr_id,spk.name,spk.gender,
                                   spk.age,spk.birthDate,spk.birthLoc,
                                   spk.curDate,spk.curloc,spk.familyState,
                                   spk.eduState,spk.jobState,spk.languages[0],
                                   spk.languages[1],spk.languages[2]))
                    # Dynamic data rows
                    ## ???
    l_spk = l_spk + l_dspk
    return l_spk
    # Writes 'tiers.csv'
def writeTiers(dir,trans,d_trans,d_spk,d_tiers,encoding):
    """Writes the 'tiers.csv'."""
    
        # Variables
    l_tiers = ["ID","Trans_ID","Speakers_ID",   # Static data columns
               "name","type","start","end",
               "dependency"]
    l_dtiers = []                               # Dynamic data columns
    f = os.path.join(dir,"Tiers.csv")           # Output file
        # We add dynamic data columns
        ## ???
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        check = True
        for col in l_trans:
            if check:
                file.write(col); check = False
                continue
            file.write(","+col)
            # Rows
        for tran in trans:
            tr_id = d_trans[tran.name]
            for tier in tran:
                    # Fixed data rows
                ti_id = d_tiers[tr_id+"_"+tier.name]
                pti_id = d_tiers[tr_id+"_"+tier.parent] # parent tier
                spk_id = d_spk[tr_id+"_"+tier.metadata['speaker']]
                file.write("\n{},{},{},{},{},{},{},{}"
                           .format(ti_id,tr_id,spk_id,tier.name,tier.type,
                                   tier.start,tier.end,pti_id))
                    # Dynamic data rows
                    ## ???
    l_tiers = l_tiers + l_dtiers
    return l_tiers
    # Writes a given 'tierx.csv'
def writeTier(dir,trans,tier,tr_id,spk_id,ti_id,encoding):
    """Writes a given 'tier.csv'."""
    
        # Variables
    l_tiers = ["ID","Tiers_ID"]                 # Static data columns
    l_dtiers = []                               # Dynamic data columns
    f = os.path.join(dir,(d_tiers[tier.name]+   # Output file
                          ".csv"))
        # We write
    
    l_tiers = l_tiers + l_dtiers
    return l_tiers
    # Writes 'corpus-metadata.json'
def writeJson(dir,d_trans,d_md,d_spk,d_tiers,
              l_trans,l_md,l_spk,l_tiers,ll_tiers,encoding):
    """Writes the 'corpus-metadata.json'."""
    pass
    # Main
def toTables(f, trans, **args):
	"""Creates a W3C Tabular data format from a Transcription object."""
    import os
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
        # We need a list of transcriptions
    if not args.get('multiple',False)
        trans = [trans]; f = [f]
        # We actually need a directory
    dir,fname = os.path.split(f[0])
        # Complete information
    for tran in trans:
        tran.timetable.clear(); tran.setchildtime()
        tran.checkSpeakers()
    
        # Variables
    d_trans,d_md,d_spk,d_tiers = getIDs(trans)        # dict { name : id }
    l_trans = []; l_md = []; l_spk = []; l_tiers = [] # list [ columns ]
    dl_tiers = {}                                     # dict { id : [columns] }
        
        # We write 'transcriptions.csv'
    l_trans = writeTrans(dir,trans,d_trans,d_md,encoding)
        # We write 'metadata.csv'
    l_md = writeMetadata(dir,trans,d_trans,d_md,encoding)
        # We write 'speakers.csv'
    l_spk = writeSpeakers(dir,trans,d_trans,d_spk,encoding)
        # We write 'tiers.csv'
    l_tiers = writeTiers(dir,trans,d_trans,d_spk,d_tiers,encoding)
        # We write each 'tier.csv'
    for tran in trans:
        tr_id = d_trans[tran.name]
        for tier in tran:
            ti_id = d_tiers[tr_id+"_"+tier.name]
            spk_id = d_spk[tr_id+"_"+tier.metadata['speaker']]
            ll_tiers[d_tiers[tier.name]] = writeTier(dir,tran,tier,
                                                     tr_id,spk_id,ti_id
                                                     encoding)
        # We write 'corpus-metadata.json'
    writeJson(dir,d_trans,d_md,d_spk,d_tiers,
              l_trans,l_md,l_spk,l_tiers,ll_tiers,encoding)
    return 0