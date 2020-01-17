from .Transcription import Transcription

def getCSV(trans,cf,l_tiers,l_except,encoding="utf-8",t_re=False):
    """Support function to create the CSVs.
    
    This is meant to be automated but can be used manually.
    'cf'        :   path of the file to create
    'l_tiers'   :   list of tier indexes to process (int)
    'l_except'  :   list of exceptions to remove (string)
    'encoding'  :   encoding used for the output file.
    't_re'      :   if 'l_except' contains regular expressions
                    means the 're' library has alread been imported.
    Creates the ".csv", returns 0."""
    
    with open(cf,'w',encoding=encoding) as fi:
        for a in l_tiers:
            tier = trans.tiers[a]
            for seg in tier:
                if seg.unit == False:           # We ignore pauses
                    continue
                content = seg.content
                for ex in l_except:             # We parse the exceptions
                    if t_re:
                        content = re.sub(ex,"",content)
                    else:
                        content = content.replace(ex)
                while content.endswith(" "):    # We try and be safe by removing end spaces
                    content = content[:-1]
                if content:
                    file.write("{:.3f}{}{:.3f}{}{}\n".format(seg.start,sep,seg.end,sep,content))

def toMAUS(l_trans,fout="",**args):
    """Exports transcription tiers into ".csv" files, parsed.
    
    Three parameters are necessary:
    'l_trans'   :   A list of transcription objects
    'fout'      :   The folder where the ".csv" should go (default 'fin' + "toMaus")
    
    Other arguments are useful to make relevant ".csv" for MAUS:
    'encoding'  :   the encoding of files to create (default "utf-8")
    'sep'       :   the separator symbol for the ".csv" (default ",")
                    MAUS might require ",".
    'ttiers'    :   The path to the 'ttiers' file.
    'tiers'     :   a list of tier indexes (relevant tiers)
                    overrules 'ttiers' (default all tiers)
    't_encode'  :   the encoding for 'ttiers' file
    'except'    :   The path to the 'exceptions' file.
    'e_encode'  :   the encoding for 'except' file
    'g2p'       :   the path to the 'grapheme-to-phoneme' file.
    Each segment of each selected tier is parsed with 're' for exceptions."""
    
        # Test 'os and 're'
    import os
    t_re = True
    try:
        import re
    except ImportError:
        t_re = False
    
        # Variables
        ## miscellaneous
    encoding = "utf-8"; sep = ","; l_tiers = []; l_ex = []
    if "encoding" in args:
        encoding = args['encoding']
    if "sep" in args:
        sep = args['sep']
    if "g2p" in args:
        g2p = args['g2p']
        if not g2p.endswith(".txt"):
            g2p = g2p + ".txt"
        ## l_tiers
    if "tiers" in args:
        l_tiers = args['tiers']
    elif "ttiers" in args:
        t_encode = encoding; l_temp = []
        if "t_encode" in args:
            t_encode = args['t_encode']
        f = args['ttiers']
        if not f.endswith(".txt"):
            f = f + ".txt"
        with open(f,encoding=t_encode) as fi:
            for line in fi:
                n,t = line.split(";",1)
                if n == name:
                    l_temp.append(t)
        for a in range(len(trans)):
            if trans.tiers[a].name in l_temp:
                l_tiers.append(a)
    else:
        for a in range(len(trans)):
            l_tiers.append(a)
        ## exceptions
    if "except" in args:
        e_encode = encoding
        if "e_encode" in args:
            e_encode = args['e_encode']
        f = args['except']
        if not f.endswith(".txt"):
            f = f + ".txt"
        with open(f,encoding=e_encode) as fi:
            for line in fi:
                line = line[:-1]
                if t_re:
                    l_except.append(re.compile(line))
                else:
                    l_except.append(line)
        
        # We process the transcriptions
    if not fout.exists:
        os.mkdir(fout)
    for a in range(len(l_trans)):
        name = ""; trans = l_trans[a]
        if trans.name:
            name = trans.name+".csv"
        elif "name" in trans.metadata.transcript:
            name = trans.metadata.transcript['name']+".csv"
        else:
            name = "trans"+str(a)+".csv"
        cf = os.path(fout,name)
        getCSV(trans,name,l_tiers,l_except,encoding,t_re)
        # We copy the 'g2p' (ignoring shutil)
    with open(g2p,'rb') as fi:
        with open(os.path.join(fout,os.path.basename(g2p)),'wb') as cp:
            byte = fi.read(1)
            while byte:
                cp.write(byte)
                byte = fi.read(1)