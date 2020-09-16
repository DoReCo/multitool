from .Transcription import Transcription, Tier

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("&quot;","\"").replace("&apos;","'") \
               .replace("&lt;","<").replace("&gt;",">") \
               .replace("&amp;","&").replace("\"","\"\"")
    return data

def toPraat(f, trans, **args):
    """Creates a Praat file (.TextGrid) from a Transcription object.
    
    Doesn't handle short file nor binary."""
    
        # Encoding
    encoding = args.get('encoding',"utf-8")
    check = args.get('check',True)
        # Sym   (used to fill 'False' segments)
    sym = args.get('sym',"_")
        # We need a list of transcriptions
    if not args.get("multiple",False):
        trans = [trans]; f = [f]
        # We write
    for a in range(len(trans)):
        tran = trans[a]; ff = f[a]
            # Complete information
        if check:
            tran.setchildtime(); tran.checktime(1); tran.uptime(1)
            # Actual writing
        with open(ff, 'w', encoding=encoding) as file:
                # Header
            file.write("File type = \"ooTextFile\"\nObject class ="
                       " \"TextGrid\"\n\nxmin = {:.3f}\nxmax = {:.3f}"
                       "\ntiers? <exists>\nsize = {}\nitem []:\n"
                       .format(tran.start,tran.end,len(tran.tiers)))
                # Tier
            for a in range(len(tran.tiers)):
                tier = tran.tiers[a].copy(); tier.checksegment()
                file.write("\titem [{}]:\n\t\tclass = \"IntervalTier\"\n\t\tname"
                        " = \"{}\"\n\t\txmin = {:.3f}\n\t\txmax"
                        " = {:.3f}\n\t\tintervals: size = {}\n"
                        .format(a+1,tier.name,tier.start,tier.end,
                                len(tier.segments)))
                    # Segment
                for b in range(len(tier.segments)):
                    seg = tier.segments[b]
                    if seg.unit == False:
                        seg.content = sym
                    file.write("\t\tintervals [{}]:\n\t\t\txmin = {:.3f}"
                               "\n\t\t\txmax = {:.3f}\n\t\t\ttext = \"{}\"\n"
                               .format(b+1,seg.start,seg.end,escape(seg.content)))
    return 0