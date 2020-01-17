"""17/10/2019
Provides a 'Transcription' class as an intermediary step for conversions.

Structure:
    Transcription
        Metadata
        Tier 1
            Segment 1, Segment 2, ... Segment n
        Tier 2
            Segment 1, Segment 2, ... Segment n
        ...
        Tier n
Transcription and Tier classes are iterable.

A transcription in oral linguistics is a transcription (text) time-aligned
 with its recording; that is, text segmented in time segments (segments).
 Since multiple types of texts can exist (translations, speakers, annotations,
 ...), each type has its own set of segments: this is called here a 'tier'."""
        
class Segment:
    """A container class for "annotation units".
    
    Methods are anecdotal."""
    def __init__(self, start=0., end=0., cont="", id="", ref="",
                 unit=True, tier=None):
        self.start = start
        self.end = end
        self.content = cont
        self.tier = tier
        self.unit = unit
            # Pangloss variables
        self.pangloss = {}
        self.notes = [] # list of tuples (pos, tag, attrib, text)
            # Structure variables
        self.id = id
        self.ref = ref
            # Omni
        self.metadata = {}
    
    def copy(self):
        copy = Segment(self.start,self.end,self.content,self.id,self.ref,
                       self.unit,self.tier)
        copy.pangloss = self.pangloss.copy()
        copy.notes = self.notes.copy()
        copy.elan = self.elan.copy()
        copy.metadata = self.metadata.copy()
        return copy
        
    def setseg(self, **args):
        """Helps with 'safely' updating the segment.
        Only updates the given arguments."""
        for name, value in args.items():
            if name == "start":
                self.start = value
            elif name == "end":
                self.end = value
            elif name == "content":
                self.content = value
            elif name == "id":
                self.id = value
            elif name == "ref":
                self.ref = value
            elif name == "unit":
                self.unit = value
            elif name == "tier":
                self.tier = value
    def uptime(self, start, end):
        self.start = start
        self.end = end
    
class Tier:
    """A list of Segment classes corresponding to a tier.
    
    When iterated upon, returns each segment in 'self.segments'.
    'checktime'     : uses the segments timestamps to set the tier's start/end.
    'addsegment'    : should be a safe way to add segments.
    'content'       : returns a list of all segments' content.
    Other methods are anecdotal."""
    
    def __init__(self, name="", start=-1., end=-1., trans=None):
        self.name = name
        self.start = start
        self.end = end
        self.trans = trans
        self.segments = []
            # Pangloss variable
        self.pangloss = ({},{}) # Tuple of two dictionaries (level, FORM/TRANSL)
            # Structure variables
        self.type = ""
        self.truetype = ""      # 'time' or 'ref'
        self.parent = ""        # reference id
        self.pindex = -1        # index of the parent in trans.tiers
        self.level = 0          # depth of parenting (default 0, no parent)
        self.children = []      # list of tier indexes
            # Omni
        self.metadata = {}
            # hash
        self.thash = None        # list of lists of lists of tuple (int,index)
    
    def __len__(self):
        return len(self.segments)
    def __iter__(self):
        self.its = -1
        self.itf = len(self.segments)
        return self
    def __next__(self):
        self.its += 1
        if self.its < self.itf:
            return self.segments[self.its]
        else:
            raise StopIteration
      
    def copy(self):
        copy = Tier(self.name, self.start,self.end,self.trans)
        for seg in self.segments:
            copy.segments.append(seg.copy())
        copy.pangloss = (self.pangloss[0].copy(),self.pangloss[1].copy())
        copy.type = self.type
        copy.truetype = self.truetype; copy.parent = self.parent
        copy.pindex = self.pindex; copy.level = self.level
        copy.children = self.children.copy()
        return copy
      
    def sethash(self):
        """Create a list of lists of indexes to fast-find a segment.
        Only use after checking the tier's time boundaries.
        The depth goes to the tenth of a second."""
        
            # Variables
        max = 0.; p = 0; ls = len(self.segments)
        l_temp = []; self.thash = []
        oseg = 0; ob = 0; o0 = 0; o1 = 0; o2 = 0; l1=0; l2=0
            # We check that the timestamps are ordered
        for seg in self.segments:
            if (seg.end < seg.start) or (seg.start < max):
                self.thash = None
                return
            max = seg.end
            # We find the depth
        while max >= 0.1:
            max /= 10; p += 1
            # We quickly get segment integers to reduce calculus load
        for seg in self.segments:
            list = []; start = int(seg.start*10)
            for a in range(p):
                list.append(start % 10); start //= 10
            l_temp.append(list)
            # We get the indexes
        o0 = 0; o1 = 0; o2 = 0; l1 = 0; l2 = 0; ob = ls; max = 0
        for a in range(p):
            self.thash.append([]); self.thash[a].append([(0,0)])
                # For each segment
            for b in range(ls):
                seg = l_temp[b][p-(a+1)]
                    # Does 'b' get past the upper-list's 'b'?
                if b >= ob:
                    if o2 == l2:                # Next upper-list
                        o1 += 1; o2 = 1; l2 = len(self.thash[o0][o1])-2
                    else:                       # Next tuple
                        o2 += 1
                    self.thash[a][-1].append((10,ob))
                    self.thash[a].append([(0,ob)]); oseg = 0
                    if len(self.thash[a]) > 2:
                        max += len(self.thash[a][-3])-2
                    self.thash[a][-2].append(max)
                    ob = self.thash[o0][o1][o2][1]
                    # Does 'seg' increment?
                if seg > oseg:
                    if (len(self.thash[a]) > 1 and
                        self.thash[a][-1][-1][1] == b):
                        self.thash[a][-1][-1] = (seg,b)
                    else:
                        self.thash[a][-1].append((seg,b))
                    oseg = seg
            ob = self.thash[a][0][1][1]; oseg = 0
            if len(self.thash[a]) > 1:
                max += len(self.thash[a][-2])-2
            self.thash[a][-1].append((10,ls)); self.thash[a][-1].append(max)
            o1 = 0; o2 = 1; o0 = a; max = 0
            l1 = len(self.thash[o0])-1;l2 = len(self.thash[o0][0])-2
        del l_temp
    def hash(self,time=-1.):
        """Finds the segment within which 'time' occurs."""
        if time < 0. or not self.thash:
            return None
            # Variables
        list = []; t = int(time*10); lh = len(self.thash)
        for a in range(lh):
            list.append(t % 10); t //= 10
        pos = 0; tuple = (0,len(self.segments))
            # Search (on self.thash)
        a = 0
        while a < lh:
            s = list[lh-(a+1)]
            #print("check:",a,s, list)
            for b in range(len(self.thash[a][pos])-2):
                if ((s >= self.thash[a][pos][b][0]) and
                    (s < self.thash[a][pos][b+1][0])):
                    if ((a == lh-1) or ((self.thash[a][pos][b+1][1] -
                        self.thash[a][pos][b][1]) < 10)):
                        if self.thash[a][pos][b][1] > 0:
                            tuple = (self.thash[a][pos][b][1]-1,
                                     self.thash[a][pos][b+1][1])
                        else:
                            tuple = (self.thash[a][pos][b][1],
                                     self.thash[a][pos][b+1][1])
                        a = lh; break
                    pos = self.thash[a][pos][-1]+b; break
            a += 1
            # Search (on self.segments)
        for a in range(tuple[0],tuple[1]):
            if ((time >= self.segments[a].start) and
                (time <= self.segments[a].end)):
                return self.segments[a]
      
    def uptime(self, t_d, t_i):
        self.start = t_d
        self.end = t_i
    def checktime(self):
        self.start = self.segments[0].start
        self.end = self.segments[-1].end
    def addsegment(self, p=-1, start=-1., end=-1., cont="", id="", ref="",
                   unit=True, tier=None, mode=0):
        """Inserts a new segment.
        In mode='0', adjusts the boundaries, including creating false
        segments."""
            # Setup
        if (p < 0) or (p > len(self.segments)):
            p = len(self.segments)
        if not tier:
            tier = self
            # Mode '0': edits previous boundary or adds segment
        if (mode == 0) and (self.segments):
            fin = self.segments[p-1].end
            if start < fin:
                self.segments[p-1].setseg(end=start)
            elif start > fin:
                self.segments.insert(p, Segment(self.segments[p-1].end,
                                     start, "", id, "", False, tier)); p += 1
            # Actual insertion
        self.segments.insert(p, Segment(start, end, cont, id, ref, unit, tier))
    def checksegment(self):
        """Simply recreates the whole list of segments in mode 0."""
        l_trans = []
        for seg in self.segments:
            l_trans.append(seg)
        self.segments.clear()
        for seg in l_trans:
            self.addsegment(-1, seg.start, seg.end, seg.content, seg.id, seg.ref,
                            seg.unit, seg.tier, 0)
            self.segments[-1].pangloss = seg.pangloss.copy()
            self.segments[-1].notes = seg.notes.copy()
            self.segments[-1].metadata = seg.metadata.copy()
        l_trans.clear()
    def reclaim(self):
        """Just in case there was a doubt as to who owns those segments."""
        for seg in self.segments:
            seg.tier = self
    def content(self):
        """Sends a list of all segments' content."""
        l_content = []
        for seg in self.segments:
            l_content.append(seg.content)
        return l_content 
    def getAllChildren(self,mode=0):
        """Expands the 'children' list to all sub-children."""
        
            # Mode 0: list of levels, with lists per parent tier, with lists of children
        if mode == 0:
            l_struct = [[self.children]]; test = True
            while test:
                l_struct.append([]); test = False
                for struct in l_struct[-2]:
                    if not struct:
                        l_struct[-1].append([])
                    for a in struct:
                        if self.trans.tiers[a].children:
                            l_struct[-1].append(self.trans.tiers[a].children)
                            test = True
                        else:
                            l_struct[-1].append([])
                # Mode 1: list of parent tiers, with a list of children tiers in order
                ## This is mainly for Pangloss
        else:
            l_struct = []; temp = []
            for i in self.children:
                if not self.trans.tiers[i].children:
                    l_struct.append(i)
                else:
                    temp.append(i)
            Ctier = None; l_child = [temp.copy()]; l_pos = [0]; l_max = [len(l_child[-1])]
            while True:
                while l_pos[-1] >= l_max[-1]:
                    l_child.pop(); l_pos.pop(); l_max.pop()
                    if not l_child:
                        break
                if not l_child:
                    break
                ind = l_child[-1][l_pos[-1]]; l_pos[-1] += 1
                l_struct.append(ind)
                Ctier = self.trans.tiers[ind]
                if Ctier.children:
                    temp.clear()
                    for i in Ctier.children:
                        if not self.trans.tiers[i].children:
                            l_struct.append(i)
                        else:
                            temp.append(i)
                    l_child.append(temp.copy())
                    l_pos.append(0); l_max.append(len(l_child[-1]))
            
        return l_struct

class Corpus:
    """Support container for 'Metadata'.
    Iterates over its 'open' dictionary."""
    def __init__(self):
        self.name = []
        self.type = []
        self.version = [[],[],[],[]]
        self.ownership = []
        self.open = {}
    def __len__(self):
        return len(self.open)
    def __iter__(self):
        self.it = iter(self.open); self.val = None
        return self
    def __next__(self):
        self.val = next(self.it,None)
        if not self.val:
            raise StopIteration
        return (self.val,self.open[self.val])
    def copy(self):
        copy = Corpus()
        copy.name = self.name.copy()
        copy.type = self.type.copy()
        copy.version = []
        for v in self.version:
            copy.version.append(v)
        copy.ownership = self.ownership.copy()
        copy.open = self.open.deepcopy()
        return copy
class Record:
    """Support container for 'Metadata'.
    Iterates over its 'open' dictionary."""
    def __init__(self):
        self.name = []
        self.url = []
        self.type = []
        self.quality = []
        self.version = [[],[],[],[]]
        self.open = {}
    def __len__(self):
        return len(self.open)
    def __iter__(self):
        self.it = iter(self.open); self.val = None
        return self
    def __next__(self):
        self.val = next(self.it,None)
        if not self.val:
            raise StopIteration
        return (self.val,self.open[self.val])
    def copy(self):
        copy = Record()
        copy.name = self.name.copy()
        copy.url = self.url.copy()
        copy.type = self.type.copy()
        copy.quality = self.quality.copy()
        copy.version = []
        for v in self.version:
            copy.version.append(v)
        copy.open = self.open.deepcopy()
        return copy
class Transcript:
    """Support container for 'Metadata'.
    Iterates over its 'open' dictionary."""
    def __init__(self):
        self.name = []
        self.url = []
        self.format = ""
        self.format_version = ""
        self.type = []
        self.version = [[],[],[],[]]
        self.ownership = []
        self.open = {}
    def __len__(self):
        return len(self.open)
    def __iter__(self):
        self.it = iter(self.open); self.val = None
        return self
    def __next__(self):
        self.val = next(self.it,None)
        if not self.val:
            raise StopIteration
        return (self.val,self.open[self.val])
    def copy(self):
        copy = Transcript()
        copy.name = self.name.copy()
        copy.url = self.url.copy()
        copy.format = self.format
        copy.format_version = self.format_version
        copy.type = self.type.copy()
        copy.version = []
        for v in self.version:
            copy.version.append(v)
        copy.ownership = self.ownership.copy()
        copy.open = self.open.deepcopy()
        return copy
class Speaker:
    """Support container for 'Metadata'.
    Iterates over its 'open' dictionary."""
    def __init__(self,name="",gender="",age=-1,birthDate="",birthLoc="",
                 curDate="",curLoc="",familyState="",eduState="",jobState="",
                 languages=[[],[],[]],open={}):
        self.name = name
        self.gender = gender
        self.age = age
        self.birthDate = birthDate
        self.birthLoc = birthLoc
        self.curDate = curDate
        self.curLoc = curLoc
        self.familyState = familyState
        self.eduState = eduState
        self.jobState = jobState
        self.languages = languages
        self.open = open
    def __len__(self):
        return len(self.open)
    def __iter__(self):
        self.it = iter(self.open); self.val = None
        return self
    def __next__(self):
        self.val = next(self.it,None)
        if not self.val:
            raise StopIteration
        return (self.val,self.open[self.val])
    def copy(self):
        copy = Speaker(self.name,self.gender,self.age,self.birhtDate,
                       self.birthLoc,self.curDate,self.curloc,self.familyState,
                       self.eduState,self.jobState,self.languages.deepcopy(),
                       self.open.deepcopy())
        return copy
    def getall(self):
        """Provides a tuple of all variables."""
        
        return (self.name,self.gender,self.age,self.birthDate,self.birthLoc,
                self.curDate,self.curLoc,self.familyState,self.eduState,
                self.jobState,self.languages,self.open)
    def getlanguages(self):
        """Provides a list of languages in tuples (type,lang)."""
        
        check = []; languages = []; lt = -1
        if self.languages:
            lt = len(self.languages)
        if lt >= 1:
            for lang in self.languages[0]:
                if lang not in check:
                    check.append(lang); languages.append(("l1",lang))
        if lt >= 2:
            for lang in self.languages[1]:
                if lang not in check:
                    check.append(lang); languages.append(("l2",lang))
        if lt >= 3:
            for lang in self.languages[2]:
                if lang not in check:
                    check.append(lang); languages.append(("dia",lang))
        return languages
class Metadata:
    """Contains all metadata for the Transcription class.
    
    Metadata can be stored in three ways:
    1.  in 'header', 'speaker' and 'footer' as an unanalyzed block of text.
    2.  in premade fields in 'corpus', 'recording', 'transcript' and
        'speakers'.
    3.  in the 'open' dictionary on any of those 4 subclasses.
    Iterates over all 'open' dictionaries."""
    
    def __init__(self):
            # Blocks of unparsed text
            ## It's too complicated and costly to parse everything each time
        self.header = ""
        self.speaker = ""
        self.footer = ""
            # Parsed data (Omni)
            ## Used to be open dictionaries... but it's too static.
            ## 'open' dictionaries within sub-classes are user-defined metadata
        self.corpus = Corpus()
        self.recording = Record()
        self.transcript = Transcript()
        self.speakers = {}
    
        # Used to iterate over the speaker list
    def __len__(self):
        return (len(self.corpus.open)+len(self.recording.open)
                +len(self.transcript.open))
    def __iter__(self):
        self.ach = [self.corpus.open,self.recording.open,self.transcript.open]
        self.incr = 0; self.l = 3; self.val = None
        self.it = iter(self.ach[self.incr])
        return self
    def __next__(self):
        while True:
            self.val = next(self.it,None)
            if self.val:
                break
            self.incr += 1
            if self.incr >= self.l:
                raise StopIteration
            self.it = iter(self.ach[self.incr])
        return (self.incr,self.val,self.ach[self.incr][self.val])
    def copy(self):
        copy = Metadata()
        copy.header = self.header; copy.speaker = self.speaker
        copy.footer = self.footer
        copy.corpus = self.corpus.copy()
        copy.recording = self.recording.copy()
        copy.transcript = self.transcript.copy()
        copy.speakers = []
        for spk in self.speakers:
            copy.speakers.append(spk.copy())
        return copy  

    def getMD(self,id=-1,mode=0):
        """Getting the type of metadata we want."""
        if mode == 0:
            if id < 0:
                return None
            elif id == 0:
                return self.corpus
            elif id == 1:
                return self.recording
            elif id == 2:
                return self.transcript
            elif id == 3:
                return self.speakers
            else:
                return None
        elif mode == 1:
            if not id:
                return None
            elif id == 'corpus':
                return self.corpus
            elif id == 'recording':
                return self.recording
            elif id == 'transcript':
                return self.transcript
            elif id == 'speakers':
                return self.speakers
            else:
                return None
    def addspeaker(self,name,gender="",age="",birthDate="",birthLoc="",
                   curDate="",curLoc="",familyState="",eduState="",
                   jobState="",languages=[[],[],[]],open={}):
        """Adds a 'Speaker' object to the speaker dictionary."""

        spk = Speaker(name,gender,age,birthDate,birthLoc,curDate,curLoc,
                      familyState,eduState,jobState,languages,open)
        self.speakers[name] = spk
        return self.speakers[name]
        
    def addversion(self,version="",versionDate="",versionAuth="",versionLoc="",
                   index=-1,forMD=2):
        """By convention, we store a metadata's 'version' in four lists.
        Appending to one list should append to all. This makes sure of it.
        Index       :   What version is concerned (0< or >len = adds)
        forMD       :   Which metadata (corpus=0,recording=1,transcript=2)"""
        
            # We check if anything has to be done
        arg_ch = [False,False,False,False]
        n_arg = ["version","versionDate","versionAuth","versionLoc"]
        l_arg = [version,versionDate,versionAuth,versionLoc]
        for a in range(len(l_arg)):
            if l_arg[a]:
                arg_ch[a] = True
        check = False
        for arg in arg_ch:
            if arg == True:
                check = True; break
        if check == False:
            return
            # We get the right dictionary to work with
        l_version = self.getMD(forMD).version
            # We check the length
        l_ld = []; ld = -1
        for list in l_version:
            l_ld.append(len(list))
        for l in l_ld:
            if l > ld:
                ld = l
        if index >= 0 and index < ld:
            ld = index
            # We append
        for a in range(len(l_arg)):
                # Too few entries
            for b in range(l_ld[a],l-1):
                l_version[a].append("")
            if arg_ch[a]:
                if l_ld[a] > ld:
                    l_version[a][ld] = l_arg[a]
                else:
                    l_version[a].append(l_arg[a])
    def getversion(self,forMD=2):
        """Returns a list of versions in tuples (version,date,author,location)."""
        
        l_return = []
            # We get the right dictionary
        l_lists = self.getMD(forMD).version
        l_arg = ['version','versionDate','versionAuth','versionLoc']
            # We check if there is anything
        check = False
        for list in l_lists:
            if list:
                check = True; break
        if check == False:
            return l_return
            # We check the length
        l = -1; l_ld = []
        for list in l_lists:
            l_ld.append(len(list))
            if l_ld[-1] > l:
                l = l_ld[-1]
            # We reorganize
        l_tup = []
        for a in range(0,l):
            for b in range(len(l_lists)):
                if l_ld[b] <= a:
                    l_tup.append("")
                else:
                    l_tup.append(l_lists[b][a])
            l_return.append(l_tup.copy()); l_tup.clear()
        return l_return
    def addopen(self,key,value,forMD=2):
        """Adds an entry to 'open'.
        Note: deprecated function from when all was dictionaries.
        'open' is for user-defined metadata dictionary."""
        
            # Get the right dictionary
        self.getMD(forMD).open[key] = value
    
class Transcription:
    """Class containing the metadata and a list of Tier classes.
    
    When iterated upon, returns each tier in 'self.tiers'.
    'addtier'/'removetier'  : should provide a safe way to manipulate tiers.
    'settimetable'          : an ordered list of timestamps is memory-heavy
                              so it is not created automatically.
    'setchildtime'          : if the structure is in place, this will give
                              proper timestamps to all segments.
    'setstructure'          : sets the tier parents, pindexes and children,
                              and for each segment their ref(erent).
                              /!\ It doesn't use timestamps to guess parents
                                  and refs
    Other methods are anecdotal."""
    def __init__(self, name="", start =-1., end =-1.):
        self.name = name
        self.start = start
        self.end = end
        self.tiers = []
        self.dictionary = None # Elan and Pangloss integrate dictionaries
        self.metadata = Metadata()
            # Complements
        self.notes = [] # Pangloss
        self.timetable = [] # see 'settimetable'
        self.format = "" # where was it imported from
    
    def __len__(self):
        return len(self.tiers)
    def __iter__(self):
        self.its = -1
        self.ite = len(self.tiers)
        return self
    def __next__(self):
        self.its += 1
        if self.its < self.ite:
            return self.tiers[self.its]
        else:
            raise StopIteration
    
    def copy(self):
        copy = Transcription(self.name,self.start,self.end)
        for tier in self.tiers:
            copy.tiers.append(tier.copy())
        copy.metadata = self.metadata.copy()
        copy.notes = self.notes.copy()
        copy.format = self.format
        return copy
    
    def addtier(self, name="", start=-1., end=-1., insert=-1):
        """Creates and adds the tier.
        If 'insert>=0', inserted at index 'insert'; otherwise appended."""
        if insert >= 0 and insert < len(self.tiers):
            self.tiers.insert(insert, Tier(name, start, end, self))
        else:
            self.tiers.append(Tier(name, start, end, self))
    def removetier(self, ind=-1):
        """Removes the tier.
        We check the parent and remove the children index accordingly."""
        if ind < 0 or ind >= len(self.tiers):
            ind = len(self.tiers)-1
            # We check all tiers for all children
            ## It's costly but must be done
        todel = -1
        for atier in self.tiers:
            if atier.children:
                todel = -1
                for b in range(len(atier.children)):
                    if atier.children[b] == ind:
                        todel = b
                    elif atier.children[b] > ind:
                        atier.children[b] = atier.children[b] - 1
                if todel >= 0:
                    ctier = self.tiers[atier.children[todel]]
                    ctier.parent = ""; ctier.pindex = -1
                    ctier.truetype = "time"; ctier.level = 0
                    del ctier
                    atier.children.pop(todel)
        self.tiers.pop(ind)

    def settimetable(self, adjust=0):
        """Creates a list of boundaries ordered (smallest to biggest) and without duplicates
        adjust=1 to also adjust the Tier's boundaries"""
    
        self.timetable.clear()
        for tier in self.tiers:
            #if tier.truetype and (tier.truetype != "time"):
            #    continue
            count = 0
            for segment in tier.segments:
                count += 1
                start = segment.start
                if start not in self.timetable:
                    if (not self.timetable) or (start > self.timetable[-1]):
                        self.timetable.append(segment.start)
                    else:
                        for t in self.timetable:
                            if start < t:
                                self.timetable.insert(self.timetable.index(t), start)
                                break
                end = segment.end
                if end not in self.timetable:
                    if (not self.timetable) or (self.timetable[-1] < end):
                        self.timetable.append(segment.end)
                    else:
                        for t in self.timetable:
                            if end < t:
                                self.timetable.insert(self.timetable.index(t), end)
                                break
        if adjust == 1 and self.timetable:
            for time in self.timetable:
                if time >= 0:
                    self.start = time; break
            self.end = self.timetable[-1]
    def uptime(self, mode=0):
        """If you don't want to create a timetable but still adjust the
        Trans's boundaries.
        mode: '0' to use the segments, '1' to use the tier's start/end
        themselves"""
        if mode == 0:
            for tier in self.tiers:
                for segment in tier.segments:
                    start = segment.start
                    if start >= 0. and (self.start > start or self.start < 0.):
                        self.start = start
                    end = segment.end
                    if self.end < end:
                        self.end = end
        elif mode == 1:
            for tier in self.tiers:
                if tier.start >= 0. and (self.start > tier.start
                                         or self.start < 0.):
                    self.start = tier.start
                if self.end < tier.end:
                    self.end = tier.end
    def checktime(self, mode=0):
        """Adjusts each tier's first and last segment to match Transcriptions' start/end time
        mode: '0' to simply update the segment's boundary; '1' to create new segments"""
        for tier in self.tiers:
            n_start = tier.segments[0].start
            n_end = tier.segments[-1].end
            if mode == 0:
                if n_start > self.start:
                    tier.segments[0].start = self.start
                if n_end < self.end:
                    tier.segments[0].end = self.end
            elif mode == 1:
                if n_start > self.start:
                    tier.addsegment(0, self.start, n_start, "", "", "",
                                    False, tier, 1)
                if n_end < self.end:
                    tier.addsegment(-1, n_end, self.end, "", "", "",
                                    False, tier, 1)
    def checkseg(self):
        """Realigns all tiers segments."""
        
        for tier in self:
            tier.checksegment()
    def sethash(self, l_tiers=[]):
        """Brute-force 'sethash' the tier indexes in l_tiers.
        We try to alter as little of the transcription as necessary."""
        if not l_tiers:
            for a in range(len(self.tiers)):
                l_tiers.append(a)
            setchildtime() # We only 'setchildtime' if all tiers are concerned
        for a in l_tiers:
            tier = self.tiers[a]
            tier.checksegment()
            tier.sethash()
    def setchildtime(self,l_tiers=[]):
        """For ELAN, gives "assoc" and "subd" tiers actual time boundaries."""
        
        self.setstructure()
            # We set up a list 'l_children' containing for each parent
            #  the list of children indexes (in order)
        l_children = []; l_parent = []
        if not l_tiers:
            for tier in self.tiers:
                if tier.pindex < 0:
                    l_parent.append(tier)
                    l_children.append(tier.getAllChildren(1))
        else:
            for a in range(len(l_tiers)):
                tier = self.tiers[a]
                l_parent.append(tier)
                l_children.append(tier.getAllChildren(1))

            # We fill from parent first
        l_count = []; l_segs = []
        for ptier in l_parent:
            l_count.clear(); l_segs.clear(); lc = len(ptier.children)
            for b in ptier.children:
                l_count.append(0)
            for pseg in ptier:
                start = pseg.start; end = pseg.end; dur = end-start
                for b in range(lc):
                    child = self.tiers[ptier.children[b]]
                    if child.truetype == "time":
                        continue # No altering preexisting timestamps
                    for c in range(l_count[b],len(child)):
                        seg = child.segments[c]
                        if seg.ref == pseg.id:
                            l_segs.append(seg)
                        else:
                            l_count[b] = c; break
                    ls = len(l_segs)
                    for a in range(len(l_segs)):
                        seg = l_segs[a]
                        seg.start = start + (dur*(a/ls))
                        seg.end = start + (dur*((a+1)/ls))
                    l_segs.clear()
            ptier.checktime()
        
            # We fill from the children next
        for list in l_children:
            for a in list:
                ptier = self.tiers[a]
                l_count.clear(); l_segs.clear(); lc = len(ptier.children)
                for b in ptier.children:
                    l_count.append(0)
                for pseg in ptier:
                    start = pseg.start; end = pseg.end; dur = end-start
                    for b in range(lc):
                        child = self.tiers[ptier.children[b]]
                        if child.truetype == "time":
                            continue # No altering preexisting timestamps
                        for c in range(l_count[b],len(child)):
                            seg = child.segments[c]
                            if seg.ref == pseg.id:
                                l_segs.append(seg)
                            else:
                                l_count[b] = c; break
                        ls = len(l_segs)
                        for a in range(len(l_segs)):
                            seg = l_segs[a]
                            seg.start = start + (dur*(a/ls))
                            seg.end = start + (dur*((a+1)/ls))
                        l_segs.clear()
                ptier.checktime()
        l_parent.clear(); l_children.clear()
    def setstructure(self,mode=0,l_tiers=[], **args):
        """Attributes parents, children, levels, ids and refs to tiers.
        
        'mode'      : '0' - relies on existing refs and parents.
                      '1' - relies on time boundaries.
        'l_tiers'   : the set of tiers on which to operate.
                      /!\ A limited set can break the transcription.
        'ids'       : a string for ids, coupled with an incremented int.
                      if empty, old ids are used (including empty ids).
        This is to automatically get the structure. To be distinguished from
        a manual structuration."""
        
            # Variables
        ids = "a"
        if "ids" in args:
            ids = args['ids']
            # If no tier is selected, we get all tiers
        if not l_tiers:
            for a in range(len(self.tiers)):
                l_tiers.append(a)
        
            ## Mode = 1: using timestamps
            ## /!\ Unfinished
        if mode == 1:
            l_parent = l_tiers.copy(); l_children = []; l_pos = []
            start = -1.; end = -1.
            while l_parent:
                lp = len(l_parent); l_pos.clear()
                for a in range(lp):
                    l_pos.append(0)
                while True:
                    break
            
                    
                
                    
            return
            
            ## Mode = 0: using preexisting refs
        
        l_parent = []; test = 0
            # We set the children
        for a in l_tiers:
            self.tiers[a].children.clear()
        for a in l_tiers:
            tier = self.tiers[a]
            if tier.parent:
                for b in range(len(self.tiers)):
                    if tier.parent == self.tiers[b].name:
                        self.tiers[b].children.append(a)
                        tier.pindex = b
                        test = 1; break
                if test == 0:
                    tier.parent = ""; tier.pindex = -1
                    tier.truetype = "time"
                    l_parent.append(a); test = 0
            else:
                tier.pindex = -1; tier.truetype = "time"
                l_parent.append(a)
            # We set the ids and refs
        l_count = []; l_temp = []; count = 0; level = 0
        while l_parent:
            for a in l_parent:
                ptier = self.tiers[a]; ptier.level = level
                l_count.clear()
                for b in ptier.children:
                    l_count.append(0)
                    l_temp.append(b)
                for pseg in ptier:
                    if not ids:
                        id = pseg.id
                    else:
                        id = ids+str(count); count += 1
                    for b in range(len(ptier.children)):
                        child = self.tiers[ptier.children[b]]; test = 0
                        for c in range(l_count[b],len(child)):
                            seg = child.segments[c]
                            if seg.ref == pseg.id:
                                seg.ref = id
                                if test == 0:
                                    test = 1
                            elif test == 1:
                                l_count[b] = c; break
                    pseg.id = id
            l_parent = l_temp.copy(); l_temp.clear();level += 1
        l_tiers.clear()
    def getparents(self):
        """Provides a list of parent tiers and their children."""
        
        l_parents = []; l_struct = []
        for a in range(len(self.tiers)):
            tier = self.tiers[a]
            if tier.pindex < 0:
                l_parents.append(a)
                l_struct.append(tier.getAllChildren(1))
        return (l_parents, l_struct)
    def iterseg(self,l_tiers=[]):
        """Creates a generator to provide the segments in time order.
        By default, does that for all parent tiers.
        Returns a tuple (list index, tier index, segment index, segment)."""
        
            # Setup
            ## l_tiers
        if not l_tiers:
            l_tiers = self.getparents()[0]
            ## lists (aligned on 'l_tiers')
        l_pos = []; l_max = []; l_segs = []
        tier = None
        for a in l_tiers:
            tier = self.tiers[a]
            if not tier.segments:
                continue
            l_pos.append(0); l_max.append(len(tier))
            l_segs.append(tier.segments[0])
            ## floats and int (for the loop)
        start = -1.; s_start = -1.; cur = -1
        
            # Iteration
        while True:
                # We compare the segments
            start = -1.; cur = -1
            for a in range(len(l_segs)):
                    # If tier is over
                if l_segs[a] == None:
                    continue
                    # Else
                s_start = l_segs[a].start
                if start < 0:
                    start = s_start; cur = a
                elif start > s_start:
                    start = s_start; cur = a
                # If no tier is left
            if cur < 0:
                break
                # We yield the segment
                ## Tuple (index, tier index, segment index, segment)
            yield (cur,l_tiers[cur],l_pos[cur],l_segs[cur])
                # We update the segment
            l_pos[cur] += 1
                ## Tier is over
            if l_pos[cur] >= l_max[cur]:
                l_segs[cur] = None
            else:
                    ## Next segment
                try:
                    l_segs[cur] = self.tiers[l_tiers[cur]].segments[l_pos[cur]]
                    ## Can't find another segment here, tier is over
                except IndexError:
                    l_max[cur] = 0; l_segs[cur] = None
    def find(self,pattern,mode=0,index=0):
        if mode == 0:
            try:
                import re
            except:
                mode = 2
        if mode == 0:
            for a in range(index,len(self.tiers)):
                if re.search(pattern,self.tiers[a].name):
                    return (a,self.tiers[a])
        elif mode == 1:
            for a in range(index,len(self.tiers)):
                if self.tiers[a].name.startswith(pattern):
                    return (a,self.tiers[a])
        elif mode == 2:
            for a in range(index,len(self.tiers)):
                if pattern in self.tiers[a].name:
                    return (a,self.tiers[a])
        elif mode == 3:
            for a in range(index,len(self.tiers)):
                if self.tiers[a].name.endswith(pattern):
                    return (a,self.tiers[a])
        elif mode == 4:
            for a in range(index,len(self.tiers)):
                if self.tiers[a].name == pattern:
                    return (a,self.tiers[a])
        return (-1,None)
    def tierSpeakers(self):
        """Checks tier.metadata for 'speaker', then provides the list.
        Returns a list of tuples (speaker_name, list_of_tier_indexes)."""
        
        l_speakers = []; check = False
        spk = []; tiers = []; other = []
        for a in range(len(self)):
            tier = self.tiers[a]
            if not 'speaker' in tier.metadata:
                other.append(a); continue
            s = tier.metadata['speaker']; check = False
            for b in range(len(spk)):
                if s == spk[b]:
                    tiers[b].append(a); check = True; break
            if check == False:
                spk.append(s); tiers.append([a])
        for a in range(len(spk)):
            l_speakers.append((spk[a],tiers[a].copy()))
        if other:
            count = 0; s = "spk0"
            while s in spk:
                count += 1; s = "spk"+str(count)
            l_speakers.append((s,other.copy()))
            for a in range(len(self)):
                if a in other:
                    self.tiers[a].metadata['speaker'] = "spk"+str(count)
        return l_speakers
    def transSpeakers(self):
        """Checks the transcription metadata for speakers, then provides the list.
        Returns a list of strings."""
        
        l_spk = []
        for key in self.metadata.speakers.keys():
            l_spk.append(key)
        return l_spk
    def clear(self,mode=0):
        if mode == 0:
            self.timetable.clear()
        else:
            self.name = ""; self.start = 0.; self.end = 0.
            del self.metadata
            self.tiers.clear()
            self.dictionary.clear()
            self.notes.clear()
            self.timetable.clear()
            self.format = ""

