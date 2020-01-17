from .Transcription import Transcription, Tier

def escape(data):
    """Support function to replace xml>sax>saxutils."""
    
    data = data.replace("\"","\"\"").replace("&quot;","\"") \
               .replace("&apos;","'").replace("&lt;","<") \
               .replace("&gt;",">").replace("&amp;","&")
    return data

def toPraat(f, trans, **args):
    """Creates a Praat file (.TextGrid) from a Transcription object.
    
    Doesn't handle short file nor binary."""
        # Quick assurance that the boundaries will be right
    trans.checktime(1)
    trans.uptime(1)
    for tier in trans:
        tier.checksegment()
        # Encoding
    encoding = args.get('encoding')
    if not encoding:
        encoding = "utf-8"
        # Sym   (used to fill 'False' segments)
    sym = args.get('sym')
    if not sym:
        sym = "_"
        # We write
    with open(f, 'w', encoding=encoding) as file:
        file.write("File type = \"ooTextFile\"\nObject class = \"TextGrid\"\n\n"
                   "xmin = {:.3f}\nxmax = {:.3f}\ntiers? "
                   "<exists>\nsize = {}\nitem []:\n"
                   .format(trans.start,trans.end,len(trans.tiers)))
        for a in range(len(trans.tiers)):
            tier = trans.tiers[a]
            file.write("\titem [{}]:\n\t\tclass = \"IntervalTier\"\n\t\tname"
                    " = \"{}\"\n\t\txmin = {:.3f}\n\t\txmax"
                    " = {:.3f}\n\t\tintervals: size = {}\n"
                    .format(a+1,tier.name,tier.start,tier.end,len(tier.segments)))
            for b in range(len(tier.segments)):
                seg = tier.segments[b]
                if seg.unit == False:
                    seg.content = sym
                file.write("\t\tintervals [{}]:\n\t\t\txmin = {:.3f}\n\t\t\txmax = "
                           "{:.3f}\n\t\t\ttext = \"{}\"\n"
                           .format(b+1,seg.start,seg.end,escape(seg.content)))