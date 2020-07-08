from .Transcription import Transcription, Tier
import os

    # Shared support functions
def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&","&amp;").replace("\"","&quot;") \
               .replace("'","&apos;").replace("<","&lt;").replace(">","&gt;")
    return data
def dq(data):
    """Support function to wrap the value in double-quotes."""
    
    data = '"'+data.replace('"','""')+'"'
    return data

#### createTabular ####
#######################

    # Support functions
def transipa(mode=0):
    """Support 'function' that simply returns a hard-coded IPA-SAMPA table."""
    
    d_IPA = {"i":"i","ɪ":"I","ɨ":"1","e":"e","ɛ":"E","æ":"{","y":"y","ø":"2",
             "œ":"9","ə":"@","ɐ":"6","ɜ":"3","a":"a","ʉ":"}","ɵ":"8","ɶ":"&",
             "ɯ":"M","ɤ":"7","ʌ":"V","ɑ":"A","u":"u","ʊ":"U","o":"o","ɔ":"O",
             "ɒ":"Q","ʏ":"Y","p":"p","b":"b","t":"t","d":"d","ts":"ts",
             "tɕ":"ts\\","ɕ":"s\\","ʑ":"z\\","dz":"dz","tʃ":"tS","dʒ":"dZ",
             "pf":"pf","kx":"kx","c":"c","k":"k","ɡ":"g","q":"q","β":"B",
             "f":"f","v":"v","θ":"T","ð":"D","s":"s","z":"z","ʃ":"S","ʒ":"Z",
             "ç":"C","x":"x","ɣ":"G","h":"h","m":"m","ɱ":"F","n":"n","ɲ":"J",
             "ŋ":"N","ɴ":"N\\","l":"l","ʎ":"L","ɫ":"5","ɾ":"4","r":"r",
             "ʀ":"R","ʋ":"P","w":"w","ɥ":"H","j":"j","ʔ":"?","ʍ":"W",
             "ɟ":"J\\","ɸ":"p\\","ʝ":"j\\","ɰ":"M\\","ħ":"X\\","χ":"X",
             "ɧ":"x\\","ʕ":"?\\","ɦ":"h\\","ɹ":"r\\","ɑː":"A:","ɑː":"AA",
             "ɑɑː":"AA:","ḁ":"a_0","aː":"a:","eː":"e:","eː":"ee","eeː":"ee:",
             "e̊":"e_0","e̯":"e_X","ɛː":"E:","iː":"i:","iː":"ii","iiː":"ii:",
             "i̥":"i_0","ɪː":"I:","uː":"u:","u̥":"u_0","oː":"o:","oː":"oo",
             "ooː":"oo:","o̥":"o_0","o̯":"o_X","ɔː":"O:","ɯː":"M:","ɒː":"Q:",
             "uː":"uu","uuː":"uu:","ʊː":"U:","yː":"yy","yyː":"yy:","yː":"y:",
             "ʏː":"Y:","æː":"{{","æː":"{:","ææː":"{{:","ʉː":"}:","əː":"@@",
             "əː":"@:","əəː":"@@:","ɨː":"1:","øː":"2:","øː":"22","øøː":"22:",
             "ɜː":"3:","ɐː":"6:","ɤː":"77","ɤː":"7:","ɤɤː":"77:","œː":"9:",
             "aʊ":"aU","aɪ":"aI","ae":"ae","ai":"ai","aːi":"a:i","ɑe":"Ae",
             "ɑu":"Au","ɑʊ":"AU","ɑi":"Ai","ɑɪ":"AI","ɑiː":"Ai:","ɑoː":"Ao:",
             "ɑuː":"Au:","ɑeː":"Ae:","ɑʉ":"A}","eɪ":"eI","eə":"e@","ei":"ei",
             "eːi":"e:i","eiː":"ei:","eːu":"e:u","eʊ":"eU","ɛə":"E@",
             "ɛɪ":"EI","ɛi":"Ei","ɪə":"I@","ɪiː":"Ii:","iːə":"i:@",
             "iːa":"i:a","ia":"ia","iə":"i@","io":"io","iu":"iu","ja":"ja",
             "jo":"jo","ju":"ju","oɪ":"oI","oe":"oe","ɔe":"Oe","ɔʏ":"OY",
             "ɔy":"Oy","oi":"oi","oːi":"o:i","oʊ":"oU","ɔʊ":"OU","oɛ":"oE",
             "ɔɛ":"OE","ɔɪ":"OI","ɔi":"Oi","ɔə":"O@","oə":"o@","ɯːa":"M:a",
             "ɯa":"Ma","ɯːə":"M:@","ɯə":"M@","ɒɪ":"QI","ue":"ue","ui":"ui",
             "ʊə":"U@","uə":"u@","uːa":"u:a","ua":"ua","uːə":"u:@","wa":"wa",
             "we":"we","wi":"wi","wɔ":"wO","yu":"yu","yə":"y@","ʊʉ":"U}",
             "ʌʉ":"V}","ʌə":"V@","ʌʊ":"VU","ʌi":"Vi","æo":"{o","æɪ":"{I",
             "æːɪ":"{:I","æi":"{i","æu":"{u","æːu":"{:u","æːʊ":"{:U",
             "æɔ":"{O","ʉi":"}i","əʊ":"@U","əʉ":"@}","ɨːa":"1:a","ɨa":"1a",
             "ɨːə":"1:@","ɨə":"1@","øi":"2i","øiː":"2i:","øy":"2y","ɜɪ":"3I",
             "ɐʊ":"6U","ɐɪ":"6I","ɤoː":"7o:","ɤuː":"7u:","ɤu":"7u","œy":"9y",
             "ɑ̃":"A~","ĩ":"i~","ẽ":"e~","ə͂":"@~","ã":"a~","õ":"o~","ɶ̃":"9~",
             "ɛ̃":"E~","ɔ̃":"O~","ũ":"u~","ɑ̃ː":"A:~","ãː":"a:~","ɛ̃ː":"E:~",
             "õː":"o:~","ɔ̃ː":"O:~","ts̺":"ts_a","s̺":"s_a","z̺":"z_a",
             "l̪":"l_d","n̪":"n_d","t̪":"t_d","d̪":"d_d","l̪":"l_d",
             "tʃʲ":"tS'","tsʲ":"ts'","dzʲ":"dz'","pʃʲ":"pS_j","rʲ":"r'",
             "ʃʲ":"S'","sʲ":"s'","sʲs":"s's","sʲːs":"s':s","zʲ":"z'",
             "mʲ":"m'","mːʲ":"m'm'","nʲ":"n'","nʲn":"n'n","nʲːn":"n':n",
             "lʲ":"l'","lʲl":"l'l","lʲːl":"l':l","tʲ":"t'","tʲt":"t't",
             "tʲːt":"t':t","dʲ":"d'","dːʲ":"d'd'","ɾʲ":"4_j","ɾːʲ":"4_j4_j",
             "dːʲ":"dd'","ɡʲ":"g'","ɡːʲ":"g'g'","xʲ":"x'","kʲ":"k'",
             "kːʲ":"k'k'","fʲ":"f'","vʲ":"v'","bʲ":"b'","bːʲ":"b'b'",
             "pʲ":"p'","pːʲ":"p'p'","ɸʲ":"p\\_j","ɸːʲ":"p\\_jp\\_j",
             "ɸː":"p\\\\p","xːʲ":"xx'","tːʲ":"tt'","tːʲ":"t't'","cʰ":"c_h",
             "pʰ":"p_h","tʰ":"t_h","kʰ":"k_h","tɕʰ":"ts\\_h","ts̻":"ts_m",
             "s̻":"s_m","z̻":"z_m","β̞":"B_o","ᵖm":"m_p","ᵗn":"n_p",
             "ᵏŋ":"N_p","ᶜɲ":"J_p","ᵗ̪n̪":"n_d_p","ʈɳ":"n`_p","gʷ":"g_w",
             "kʷ":"k_w","c'":"c_>","k'":"k_>","p'":"p_>","q'":"q_>",
             "t'":"t_>","ts'":"ts_>","tʃ'":"tS_>","ɖ":"d`","dʐ":"dz`",
             "ɝ":"3`","ɭ":"l`","ɳ":"n`","ɻ":"r\\`","ɽ":"r`","ʂ":"s`",
             "ʈ":"t`","tʂ":"ts`","ʐ":"z`","ʈ":"t`","ɳ":"n`","ɽ":"r`",
             "ɭ":"l`","ɖ":"d`","ŋ̩":"N=","n̩":"n=","m̩":"m=","l̩":"l=",
             "ɳ̍":"n=`","d̥":"d_0","cː":"cc","cː":"c:","çː":"CC","ðː":"D:",
             "tː":"tt","tː":"t:","tːt":"t:t","pː":"pp","pː":"p:","pːp":"p:p",
             "kː":"kk","kː":"k:","kːk":"k:k","dː":"dd","ɾː":"44","ɡː":"gg",
             "ɡː":"g:","bː":"bb","bː":"b:","dː":"d:","tːʃ":"ttS","tːs":"tts",
             "dːʒ":"ddZ","dːz":"ddz","vː":"vv","vː":"v:","vːv":"v:v",
             "sː":"ss","sː":"s:","sːs":"s:s","zː":"zz","ʃː":"SS","ʃː":"S:",
             "ʃːʃ":"S:S","ʒː":"ZZ","xː":"xx","rː":"rr","rː":"r:","rːr":"r:r",
             "ʀʀ":"RR","nː":"nn","nː":"n:","nːn":"n:n","ŋː":"NN","ŋː":"N:",
             "ŋʲ":"N'","ɴ":"N\\N\\","wː":"ww","mː":"mm","mː":"m:","mːm":"m:m",
             "ɱː":"FF","ʎː":"LL","lː":"ll","lː":"l:","lːl":"l:l","ɲː":"JJ",
             "jː":"jj","jː":"j:","jːj":"j:j","fː":"ff","fː":"f:","fːf":"f:f",
             "hː":"hh","hː":"h:","hːh":"h:h","ʔː":"??","ʈː":"t`t`","ʈː":"t:`",
             "t̪ː":"t_dt_d","t̪ː":"t:_d","θː":"T:","tːʃ_cl":"ttS_cl",
             "tːʃ_rl":"ttS_rl","tːs_cl":"tts_cl","tːs_rl":"tts_rl",
             "dːʒ_cl":"ddZ_cl","dːʒ_rl":"ddZ_rl","dːz_cl":"ddz_cl",
             "dːz_rl":"ddz_rl","tʃ_cl":"tS_cl","tʃ_rl":"tS_rl",
             "ts_cl":"ts_cl","ts_rl":"ts_rl","dʒ_cl":"dZ_cl","dʒ_rl":"dZ_rl",
             "dz_cl":"dz_cl","dz_rl":"dz_rl","tː_rl":"tt_rl","tː_cl":"tt_cl",
             "pː_cl":"pp_cl","pː_rl":"pp_rl","kː_cl":"kk_cl","kː_rl":"kk_rl",
             "dː_cl":"dd_cl","dː_rl":"dd_rl","ɡː_cl":"gg_cl","ɡː_rl":"gg_rl",
             "bː_cl":"bb_cl","bː_rl":"bb_rl","t_cl":"t_cl","t_rl":"t_rl",
             "p_cl":"p_cl","p_rl":"p_rl","k_cl":"k_cl","k_rl":"k_rl",
             "ɡ_cl":"g_cl","ɡ_rl":"g_rl","d_cl":"d_cl","d_rl":"d_rl",
             "b_cl":"b_cl","b_rl":"b_rl","(...)":"<","(...)":">","(...)":"\#",
             "(.)":"<nib>","(...)":"<p:>","(...)":"<p>","(..)":"<usb>",}
    if mode == 0:
        return d_IPA
    else:
        d_SAMPA = {}
        for key,value in d_IPA.items():
            d_SAMPA[value] = key
        if mode == 1:
            return d_SAMPA
        elif mode == 2:
            return d_IPA,d_SAMPA
def chargs(l_args):
    """Support function to check 'l_args'.
    Returns a list of booleans/integers."""
    
        # additional columns
    ch_nam = False          # tier name
    ch_tim = False          # start/end
    ch_dur = False          # duration
    ch_spk = False          # speakers
    ch_con = False          # preceding/following units
    ch_ipa = 0              # IPA-SAMPA translation
    ch_ids = False          # ids
    d_IPA = {}; d_SAMPA = {}# dicts for 'ch_ipa'
    
        # List of checks
    for s in l_args:
        if s == "name":
            ch_nam = True
        elif s == "time":
            ch_tim = True
        elif s == "duration":
            ch_dur = True
        elif s == "speaker":
            ch_spk = True
        elif s == "context":
            ch_con = True
        elif s == "IPA":
            ch_ipa = 1; d_IPA = transipa(0)
        elif s == "SAMPA":
            ch_ipa = 2; d_SAMPA = transipa(1)
        elif s == "IPA-SAMPA":
            ch_ipa = 3; d_IPA,d_SAMPA = transipa(2)
        elif s == "ids":
            ch_ids = True
    return (ch_nam,ch_tim,ch_dur,ch_spk,ch_con,ch_ipa),ch_ids,d_IPA,d_SAMPA
def wcolargs(file,ch_tuple,sep):
    """Support function to write columns following 'l_args'."""
    
    if ch_tuple[0]:         # ch_nam
        file.write(sep+"Trans"+sep+"Tier")
    if ch_tuple[1]:         # ch_tim
        file.write(sep+"Start"+sep+"End")
    if ch_tuple[2]:         # ch_dur
        file.write(sep+"Duration")
    if ch_tuple[3]:         # ch_spk
        file.write(sep+"Speaker")
    if ch_tuple[4]:         # ch_con
        file.write(sep+"Prev. unit"+sep+"Next unit")
        # ch_ipa
    if ch_tuple[5] == 1:
        file.write(sep+"IPA")
    elif ch_tuple[5] == 2:
        file.write(sep+"SAMPA")
    elif ch_tuple[5] == 3:
        file.write(sep+"IPA"+sep+"SAMPA")
def wrowargs(file,lr,tran,rtier,s_ind,seg,ch_ids,tr_id,ti_id,spk_id,ch_tuple,
             d_IPA,d_SAMPA,sep):
    """Support function to write rows following 'l_args'."""
    
    if ch_tuple[0]:         # ch_nam
        if ch_ids:
            file.write(sep+tr_id+sep+ti_id)
        else:
            file.write(sep+tran.name+sep+rtier.name)
    if ch_tuple[1]:         # ch_tim
        file.write("{0}{1:.3f}{0}{2:.3f}".format(sep,seg.start,seg.end))
    if ch_tuple[2]:         # ch_dur
        file.write(sep+"{:.3f}".format(seg.end-seg.start))
    if ch_tuple[3]:         # ch_spk
        if ch_ids:
            file.write(sep+spk_id)
        else:
            file.write(sep+rtier.metadata['speaker'])
        #file.write(sep+rtier.metadata.get("speaker",""))
    if ch_tuple[4]:         # ch_con
        prev = s_ind-1; next = s_ind+1
        if prev >= 0:
            file.write(sep+dq(rtier.segments[prev].content))
        else:
            file.write(sep)
        if next < lr:
            file.write(sep+dq(rtier.segments[next].content))
        else:
            file.write(sep)
        # ch_ipa
        ## I have no 'lookup_table' at hand...
    if ch_tuple[5] == 1:
        text = ""
        for char in seg.content:
            text = text + d_IPA.get(char,char)
        file.write(sep+dq(text))
    elif ch_tuple[5] == 2:
        text = ""
        for char in seg.content:
            text = text + d_SAMPA.get(char,char)
        file.write(sep+dq(text))
    elif ch_tuple[5] == 3:
        text1 = ""; text2 = ""
        for char in seg.content:
            text1 = text1 + d_IPA.get(char,char)
            text2 = text2 + d_SAMPA.get(char,char)
        file.write(sep+dq(text1)+sep+dq(text2))
    # createTabular
def createTabular(f,trans,ref_tier,l_tiers=[],l_args=[],**args):
    """Writes a single table for analysis purposes.
    
    Taken and adapted from 'createTabular' in 'conversion_data.tools'.
    ARGUMENTS:
    - f         :   the file path
    - trans     :   (list of) Transcription object(s)
    - ref_tier  :   (string) reference tier name
    - l_tiers   :   (list<string>, default empty) list of other tier names
    - l_args    :   (list<string>, default empty) list of keywords
    RETURNS:
    - writes the file 'f' with a cross-table.
    Note: contrary to 'createTabular' in 'conversion_data.tools', this
          function relies on tier names, not tier indexes. This is because
          it works on multiple transcriptions, without any insurance that
          they would share the same indexes...
    Note: an extra kwarg 'toTab' contains the id dictionaries in a tuple.
          'encoding', 'sep' and 'm_sep' would also use toTabular's."""
    
        ## Check transcription(s)
        # 1. Fill 'l_refs'
    if not trans:
        return 1
    if not args.get('multiple',False):
        trans = [trans]; f = [f]
    l_refs = []; d_ctiers = {}; l_trans = []
    for tran in trans:
        l_rtiers = tran.findAll(ref_tier)
        for t_ind,tier in l_rtiers:
            l_refs.append((tran,t_ind,tier))
        if l_rtiers and tran not in l_trans:
            l_trans.append(tran)
    if not l_refs:
        return 1
        # 2. Fill 'd_ctiers'
    for tran in l_trans:
        d_ctiers[tran] = {}
        for tier_name in l_tiers:
            d_ctiers[tran][tier_name] = []
            l_ctiers = tran.findAll(tier_name)
            for t_ind,tier in l_ctiers:
                d_ctiers[tran][tier_name].append((t_ind,tier))
    del l_trans

        # Variables
        ## l_args
    ch_tuple,ch_ids,d_IPA,d_SAMPA = chargs(l_args)
    del l_args
        ## kwargs
    encoding = args.get('encoding',"utf-8")     # encoding
    unit = args.get('unit',False)               # include non-unit segs
    sep = args.get('sep',",")                   # column separator
    m_sep = args.get('m_sep',"\\\\t")           # in-column separator
    rid = args.get('id',"R")                    # generate IDs
    toTab = args.get('toTab',({},{},{},{}))     # ids dictionaries
        ## others
    count = 0; text = ""
    
        # We write
    with open(f,'w',encoding=encoding) as file:
            ## columns
        file.write("\"ID\""+sep+ref_tier)
        wcolargs(file,ch_tuple,sep)
            # Additional columns
        for tier_name in l_tiers:
            if ch_ids:
                l_cols = []
                file.write(sep); l_cols = []; count = 0
                for tran,d_cols in d_ctiers.items():
                    tr_id = toTab[0].get(tran.name)
                    l_temp = d_cols[tier_name]
                    for t_cind,ctier in l_temp:
                        if count > 0:
                            file.write(m_sep)
                        file.write(toTab[2][tr_id+"_"+ctier.name])
                        count += 1
            file.write(sep+tier_name)
        file.write("\n"); count = 0
            ## rows
            # For each tier
        for tran,tr_ind,rtier in l_refs:
            lr = len(rtier); tr_id = toTab[0].get(tran.name)
            spk_id = toTab[1].get(rtier.metadata['speaker'])
            ti_id = toTab[2].get(tr_id+"_"+rtier.name)
                # For each segment
            for a in range(lr):
                seg = rtier.segments[a]
                if (not unit) and (not seg.unit):
                    continue
                    # id/ref_tier
                if ch_ids:
                    id = toTab[3].get(ti_id+"_"+seg.id)
                    if not id:
                        id = rid+str(count); count += 1
                else:
                    id = rid+str(count); count += 1
                    # writing
                file.write(id+sep+dq(seg.content))
                    # l_args
                wrowargs(file,lr,tran,rtier,a,seg,ch_ids,tr_id,ti_id,spk_id,
                         ch_tuple,d_IPA,d_SAMPA,sep)
                    ## For each other tier
                d_segs = seg.getfulltree(tr_ind,a,dict=True)
                d_cols = d_ctiers[tran]
                for tier_name,l_ctiers in d_cols.items():
                    t_cind = -1; ctier = None
                    for i,ti in l_ctiers:
                        if i in d_segs:
                            t_cind = i; ctier = ti; break
                    l_segs = d_segs.get(t_cind,[])
                    if not l_segs:   
                        if ch_ids:
                            file.write(sep+sep)
                        else:
                            file.write(sep)
                        continue
                    tc_id = toTab[2].get(tr_id+"_"+ctier.name)
                        # content/id
                    cseg = ctier.segments[l_segs[0]]
                    text = cseg.content; id = toTab[3].get(tc_id+"_"+cseg.id)
                    for b in range(1,len(l_segs)):
                        cseg = ctier.segments[l_segs[b]]
                        text = text+m_sep+cseg.content
                        id = id+m_sep+toTab[3].get(tc_id+"_"+cseg.id)
                        # writing
                    if ch_ids:
                        file.write(sep)
                        if ti_id:
                            file.write(id)
                    file.write(sep+dq(text))
                file.write("\n")

#### toTabular ####
###################

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
            if spk not in d_spk:
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
def fillCol(file,sep,l_col):
    """Support function for 'writeX' functions: writes the columns header."""
        # Static data columns
    check = True
    for col in l_col:
        if check:
            file.write(col); check = False
            continue
        file.write(sep+col)

    # Writes 'trans.csv'
def writeTrans(dir,trans,d_trans,encoding,sep,m_sep):
    """Writes the 'transcriptions.csv'."""
    
        # Variables
    l_trans = ["\"ID\"","Name",                 # Columns
               "md_key","md_value"]
    f = os.path.join(dir,"trans.csv")           # Output file
        # We Write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,sep,l_trans)
            # Rows
        keys = []; values = []
        for tran in trans:
            d_md = tran.metadata.getall()
            file.write("\n{}{}{}"
                       .format(d_trans[tran.name],sep,dq(tran.name)))
            keys = []; values = []
            for key, value in d_md.items():
                keys.append(key); values.append(str(value))
            keys = m_sep.join(keys); values = m_sep.join(values)
            file.write("{0}{1}{0}{2}".format(sep,dq(keys),dq(values)))
    return l_trans
    # Writes 'speakers.csv'
def writeSpeakers(dir,trans,d_trans,d_spk,encoding,sep,m_sep):
    """Writes the 'speakers.csv'."""
    
        # Variables
    l_spk = ["\"ID\"","Trans_ID","name","gender",# Static data columns
             "age","birthdate","birthplace",
             "currentdate","currentplace",
             "familystate","education",
             "occupation","L1","L2","dialects",
             "md_key","md_value"]
    f = os.path.join(dir,"speakers.csv")         # Output file
        # We need another dict
    d_tspk = {}
    for name,spk in d_spk.items():
        d_tspk[name] = []
    for tran in trans:
        for name,spk in tran.metadata.speakers.items():
            d_tspk[name].append((tran,spk))
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,sep,l_spk)
            # Rows
        for name,l_tspk in d_tspk.items():
            spk = None; s_tran = ""; count = 0
            for tran,speakr in l_tspk:
                if count > 0:
                    s_tran = s_tran + m_sep + d_trans[tran.name]
                else:
                    spk = speakr # We take the first speaker...
                    s_tran = d_trans[tran.name]
                count += 1
            spk_id = d_spk[name]
            l1 = m_sep.join(spk.languages[0])
            l2 = m_sep.join(spk.languages[1])
            dia = m_sep.join(spk.languages[2])
            file.write("\n{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}"
                       "{8}{0}{9}{0}{10}{0}{11}{0}{12}{0}{13}{0}{14}"
                       "{0}{15}"
                       .format(sep,spk_id,s_tran,spk.name,spk.gender,
                               spk.age,spk.birthDate,spk.birthLoc,
                               spk.curDate,spk.curLoc,spk.familyState,
                               spk.eduState,spk.jobState,l1,l2,dia))
            keys = []; values = []
            for key, value in spk.open.items():
                keys.append(key); values.append(value)
            keys = m_sep.join(keys); values = m_sep.join(values)
            file.write("{0}{1}{0}{2}".format(sep,dq(keys),dq(values)))
    return l_spk
    # Writes 'tiers.csv'
def writeTiers(dir,trans,d_trans,d_spk,d_tiers,encoding,sep,m_sep):
    """Writes the 'tiers.csv'."""
    
        # Variables
    l_tiers = ["\"ID\"","Trans_ID","Speakers_ID",# Static data columns
               "name","type","start","end",
               "dependency","md_key","md_value"]
    f = os.path.join(dir,"tiers.csv")            # Output file
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,sep,l_tiers)
            # Rows
        for tran in trans:
            tr_id = d_trans[tran.name]
            for tier in tran:
                ti_id = d_tiers[tr_id+"_"+tier.name]; pti_id = ""
                if tier.parent:
                    pti_id = d_tiers[tr_id+"_"+tier.parent] # parent tier
                spk_id = d_spk[tier.metadata['speaker']]
                file.write("\n{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}"
                           .format(sep,ti_id,tr_id,spk_id,tier.name,
                                   tier.type,tier.start,tier.end,pti_id))
                keys = []; values = []
                for key, value in tier.metadata.items():
                    keys.append(key); values.append(value)
                keys = m_sep.join(keys); values = m_sep.join(values)
                file.write("{0}{1}{0}{2}".format(sep,dq(keys),dq(values)))
    return l_tiers
    # Writes a given 'transx.csv'
def writeTran(dir,trans,tr_id,d_spk,d_tiers,d_seg,encoding,sep,m_sep):
    """Writes a given 'tier.csv'."""
    
        # Variables
    sg_id = "seg"; count = 0
    l_tiers = ["\"ID\"","Tiers_ID",             # Static data columns
               "start","end","content",
               "dependency","notes",
               "md_key","md_value"]
    l_dtiers = []                               # Dynamic data columns
    f = os.path.join(dir,(tr_id+".csv"))        # Output file
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,sep,l_tiers)
            #Rows
        for tier in trans:
            ti_id = d_tiers[tr_id+"_"+tier.name]
            pti_id = d_tiers.get(tr_id+"_"+tier.parent,"")
            for seg in tier:
                if seg.unit == False:
                    continue
                id = d_seg[ti_id+"_"+seg.id]
                ref = d_seg.get(pti_id+"_"+seg.ref,"")
                file.write("\n{1}{0}{2}{0}{3:.3f}{0}{4:.3f}{0}{5}{0}{6}"
                           .format(sep,id,ti_id,seg.start,seg.end,
                                   dq(seg.content),ref))
                        # Notes
                file.write(sep+m_sep.join(seg.notes))
                        # Metadata
                keys = []; values = []
                for key, value in seg.metadata.items():
                    keys.append(key); values.append(value)
                keys = m_sep.join(keys); values = m_sep.join(values)
                file.write("{0}{1}{0}{2}".format(sep,dq(keys),dq(values)))
    l_tiers = l_tiers + l_dtiers
    return l_tiers
    # Writes a given 'tierx.csv'
    ## /!\ Not in use anymore. Replaced by 'writeTran'.
def writeTier(dir,trans,tier,tr_id,d_spk,d_tiers,d_seg,encoding,sep,m_sep):
    """Writes a given 'tier.csv'."""
    
        # Variables
    sg_id = "seg"; count = 0
    ti_id = d_tiers[tr_id+"_"+tier.name]
    spk_id = d_spk[tier.metadata['speaker']]
    pti_id = d_tiers.get(tr_id+"_"+tier.parent,"")
    l_tiers = ["\"ID\"","Trans_ID","Tiers_ID",  # Static data columns
               "start","end","content",
               "dependency","notes",
               "md_key","md_value"]
    l_dtiers = []                               # Dynamic data columns
    f = os.path.join(dir,(ti_id+".csv"))        # Output file
        # We write
    with open(f,'w',encoding=encoding) as file:
            # Column headers
        fillCol(file,sep,l_tiers)
            #Rows
        for seg in tier:
            if seg.unit == False:
                continue
            id = d_seg[ti_id+"_"+seg.id]
            ref = d_seg.get(pti_id+"_"+seg.ref,"")
            file.write("\n{1}{0}{2}{0}{3}{0}{4:.3f}{0}{5:.3f}{0}{6}{0}{7}"
                       .format(sep,id,tr_id,ti_id,seg.start,seg.end,
                               dq(seg.content),ref))
                    # Notes
            file.write(sep+m_sep.join(seg.notes))
                    # Metadata
            keys = []; values = []
            for key, value in seg.metadata.items():
                keys.append(key); values.append(value)
            keys = m_sep.join(keys); values = m_sep.join(values)
            file.write("{0}{1}{0}{2}".format(sep,dq(keys),dq(values)))
    l_tiers = l_tiers + l_dtiers
    return l_tiers
    # Writes 'corpus-metadata.json'
def fillJCol(file,l_col,tab,m_sep,spk=False):
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
                       .format(tab,m_sep))
        elif spk and (col == "L1" or col == "L2" or col == "dialects"):
            file.write("{}\t\t\"separator\": \"{}\",\n"
                       .format(tab,m_sep))
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
def writeJson(dir,l_trans,l_md,l_spk,l_tiers,dl_tiers,encoding,m_sep):
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
        fillJCol(file,l_trans,tab,m_sep)
        file.write("\t\t\t\"url\": \"trans.csv\"\n\t\t},\n")
            # Speakers table
        fillJCol(file,l_spk,tab,m_sep,True)
        file.write("\t\t\t\"url\": \"speakers.csv\"\n\t\t},\n")
            # Tiers table
        fillJCol(file,l_tiers,tab,m_sep)
        file.write("\t\t\t\"url\": \"tiers.csv\"\n\t\t},\n")
            # Transx tables
            # Tierx tables
        count = len(dl_tiers)-1; incr = 0
        for ti_id, l_tier in dl_tiers.items():
            fillJCol(file,l_tier,tab,m_sep)
            file.write("\t\t\t\"url\": \"{}.csv\"\n\t\t}}"
                       .format(ti_id))
            if incr < count:
                file.write(",")
            file.write("\n"); incr += 1
        file.write("\t]\n}")
    # Main
def toTabular(f, trans, **args):
    """Creates a W3C Tabular data format from a Transcription object.
    ARGUMENTS:
    - f         :   the file path
    - trans     :   the (list of) transcription(s)
    - sep       :   (kwarg,string,default ',') column separator
    - m_sep     :   (kwarg,string,default '\\\t') in-column separator
    - d_custom  :   (kwarg,dict,default empty) arguments for cross-table(s)
    RETURNS:
    - exports in directory 'f' CSV tables and a '.json' structure file.
    Note: if 'f' is not a directory, it will be turned into one.
    Note: the 'sep' arg replaces the comma symbol of '.csv's, but metadata
          won't reflect that change. To respect W3C standards, do not change.
    Note: 'd_custom' is a dictionary whose keys are file names and values 
          are arguments for 'createTabular': 'ref_tier,l_ind,l_args'. See
          'createTabular' for details."""
    import os
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
    sep = args.get('sep',",")
    m_sep = args.get('m_sep',"\\\\t")
    d_custom = args.get('custom',{})
        # We need a list of transcriptions
        ## Also a directory for output... which is a breach of convention...
    dir = f
    if not args.get('multiple',False):
        trans = [trans]; f = [f]; dir = f[0]
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
    d_trans,d_spk,d_tiers,d_seg = getIDs(trans)       # dict { name : id }
    l_trans = []; l_md = []; l_spk = []; l_tiers = [] # list [ columns ]
    #dl_tiers = {}                                     # dict { id : [columns] }
    dl_trans = {}                                     # dict { id : [columns] }
    
        # We write 'transcriptions.csv'
    l_trans = writeTrans(dir,trans,d_trans,encoding,sep,m_sep)
        # We write 'speakers.csv'
    l_spk = writeSpeakers(dir,trans,d_trans,d_spk,encoding,sep,m_sep)
        # We write 'tiers.csv'
    l_tiers = writeTiers(dir,trans,d_trans,d_spk,d_tiers,encoding,sep,m_sep)
        # We write each 'tier.csv'
    for tran in trans:
        tr_id = d_trans[tran.name]
        dl_trans[tr_id] = writeTran(dir,tran,tr_id,d_spk,d_tiers,d_seg,
                                    encoding,sep,m_sep)
        """for tier in tran:
            key = d_tiers[tr_id+"_"+tier.name]
            dl_tiers[key] = writeTier(dir,tran,tier,tr_id,d_spk,d_tiers,
                                      d_seg,encoding,m_sep)"""
        # We write 'corpus-metadata.json'
    writeJson(dir,l_trans,l_md,l_spk,l_tiers,dl_trans,encoding,m_sep)
        # We write the cross-table
    if not d_custom:
        return 0
    for name,tuple in d_custom.items():
        cf = os.path.join(dir,name+".csv")
        ref_tier,l_ind,l_args = tuple
        createTabular(cf,trans,ref_tier,l_ind,l_args,sep=sep,m_sep=m_sep,
                      toTab=(d_trans,d_spk,d_tiers,d_seg),multiple=True)
    return 0