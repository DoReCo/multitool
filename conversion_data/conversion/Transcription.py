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
    """A container class for "annotation units"."""
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
        self.ppoint = None
            # Omni
        self.metadata = {}
            # For overloaded methods
        self.d_setparent = {(None):self._spn,('Segment'):self._spo,
                            ('int'):self._spi,('str'):self._sps}
    
    def copy(self):
        copy = Segment(self.start,self.end,self.content,self.id,self.ref,
                       self.unit,self.tier)
        copy.ppoint = None
        copy.pangloss = self.pangloss.copy()
        copy.notes = self.notes.copy()
        copy.metadata = self.metadata.copy()
        return copy
        
        # 'setparent'
    def _checkptier(self):
        """Support function to obtain the tier's parent."""
        if not self.tier:
            return None
        ptier = self.tier.ppoint
        if not ptier:
            self.tier.checkparenting; ptier = self.tier.ppoint
        return ptier
    def setparent(self,*args):
        if not args:
            f = self.d_setparent.get((None))
        else:
            f = self.d_setparent.get(tuple(arg.__class__ for arg in args))
        if f is None:
            raise TypeError("Check 'd_setparent' in 'Segment'.")
        return f(self,*args)
    def _spn(self):
        """Sets a segment's parent segment.
        Won't work if tier has no parent."""
        self.ref = ""; self.ppoint = None
    def _spo(self,seg):
        self.ppoint = seg; self.ref = seg.id
    def _spi(self,ind):
        ptier = self._checkptier()
        if not ptier or (ind <= 0 or ind >= len(ptier)):
            return setparent()
        self.ppoint = ptier.segments[ind]; self.ref = self.ppoint.id
    def _sps(self,ref):
        ptier = self._checkptier()
        if not ptier or not ref:
            return setparent()
        for seg in ptier:
            if seg.id == ref:
                self.ppoint = seg; self.ref = ref; break
        # 'getindexes'
    def getindexes(self,t_ind=-1,s_ind=-1):
        """Retrieves the tier and segment indexes."""
        
            # We need the tier...
        if not self.tier:
            return (-1,-1)
            # ... and the tier's trans
        trans = self.tier.trans
        if not trans:
            t_ind = -1
            # Whose index we must check
        elif ((t_ind < 0 or t_ind > len(trans)) or (not
            trans.tiers[t_ind] == self.tier)):
            t_ind = -1
            for a in range(len(trans)):
                if trans.tiers[a] == self.tier:
                    t_ind = a; break
            # We want the segment index anyway
        if ((s_ind < 0 or s_ind >= len(self.tier)) or (not
            self.tier.segments[s_ind] == self)):
            s_ind = -1
            for a in range(len(self.tier)):
                if self.tier.segments[a] == self:
                    s_ind = a; break
        return (t_ind,s_ind)
        # 'gettree' and 'getfulltree'
    def _getparents(self,trans,t_ind,s_ind,l_master):
        """Support function for 'gettree' and 'getfulltree'.
        Note: list is not reversed yet for 'getfulltree'."""
        o_ind = t_ind; index = self.tier.pindex
        ptier = self.tier; self.tier.checkparenting(index)
        ss_ind = s_ind; ref = self.ref
        while ptier.pindex >= 0 and ref:
            ptier = trans.tiers[index]; ptier.checkparenting(index)
                # We find the segment
            for a in range(len(ptier)):
                if ptier.segments[a].id == ref:
                    l_master.append((index,o_ind,[a],ss_ind))
                    ref = ptier.segments[a].ref; ss_ind = a; break
            o_ind = index; index = ptier.pindex
        return l_master
    def _getchildren(self,trans,t_ind,s_ind,l_master):
        """Support function for 'gettree' and 'getfulltree'."""
        l_struct = self.tier.getallchildren(1)
        if not l_struct:
            return l_master
        l_ids = [(t_ind,t_ind,[s_ind])]; l_temp = []; l_cur = l_ids[0]
        for a in range(1,len(l_struct)):
            c_ind = l_struct[a][0]; ctier = trans.tiers[c_ind]
            ctier.checkparenting(c_ind)
                # We are lazy (and also needlessly thorough)
            d_segs = {}
            for a in range(len(ctier)):
                ref = ctier.segments[a].ref
                if ref in d_segs:
                    d_segs[ref].append(a)
                else:
                    d_segs[ref] = [a]
                # We need the correct parent tier
            if not ctier.pindex == l_cur[0]:
                check = False
                for b in range(len(l_ids)-1,-1,-1):
                    if ctier.pindex == l_ids[b][0]:
                        check = True; l_cur = l_ids[b]; break
                    if check:
                        break
                if not check: # wut
                    continue
                # We find the segments
            for ss_ind in l_cur[2]:
                id = trans.tiers[l_cur[0]].segments[ss_ind].id
                if id in d_segs:
                    l_temp = l_temp + d_segs[id]
                # We update the reference segments
            l_master.append((c_ind,ctier.pindex,l_temp.copy(),ss_ind))
            l_ids.append((c_ind,ctier.pindex,l_temp.copy()))
            l_temp.clear()
        return l_master
    def gettree(self,t_ind=-1,s_ind=-1):
        """Get all parent and children segments for that segment.
        ARGUMENT:
        - 't_ind'   :   the tier index
        - 's_ind'   :   the segment index
        RETURNS:
        - a list of tuples (tier_index,p/ctier_index,
                            list_segindex,p/cseg_index)
        The list is organized around this segment's tier. All above will give
        a child tier index, all under a parent tier index. Likewise for the 
        'reference segment index'. This segment's tier is included, with the
        index repeated for the tier and segment.
        Note: all in linear order.
        Note: relies on IDs."""
        
            # Variables
        l_master = []
            # Checks
            ## If 'trans', 'tier' exist and the indexes
        t_ind,s_ind = self.getindexes(t_ind,s_ind)
        if t_ind < 0 or s_ind < 0:
            return l_master
        trans = self.tier.trans
        
            # We fill the list
            ## We get the parents
        l_master = self._getparents(trans,t_ind,s_ind,l_master)
            ## We add this segment
        l_master.reverse(); l_master.append((t_ind,t_ind,[s_ind],s_ind))
            ## We get the children
        l_master = self._getchildren(trans,t_ind,s_ind,l_master)
        return l_master  
    def getfulltree(self,t_ind=-1,s_ind=-1,dict=False):
        """Same as 'gettree' but including indirect children for that segment.
        ARGUMENT:
        - 't_ind'   :   the tier index
        - 's_ind'   :   the segment index
        - 'dict'    :   turns the list into a dictionary (tier_ind: list_segs)
        RETURNS:
        - a list of tuples (tier_index,p/ctier_index,
                            list_segindex,p/cseg_index)
        Note: see 'gettree' for the list organization.
        Note: all in linear order.
        Note: relies on IDs and 'gettree'."""
        
            # Variables
        l_master = []
            # Checks
            ## If 'trans', 'tier exist and the indexes
        t_ind,s_ind = self.getindexes(t_ind,s_ind)
        if t_ind < 0 or s_ind < 0:
            return l_master
        trans = self.tier.trans
        
            ## We get the tree with 'gettree'
        l_temp = self.gettree(t_ind,s_ind); d_check = {}
        d_check = {}; check = False
        for tuple in l_temp:
            d_check[tuple[0]] = True
            ## We refill 'l_master' by including the parents' children
        for a in range(len(l_temp)):
            l_master.append(l_temp[a])
            if check == True: # children
                continue
            ti = l_temp[a][0]; tier = trans.tiers[ti]
            if ti == t_ind: # end of parents
                check = True; continue
            si = l_temp[a][2][0]; seg = tier.segments[si]
            l_seg = seg.gettree(ti,si)
            for tuple in l_seg: # parents' children
                if tuple[0] in d_check:
                    continue
                else:
                    l_master.append(tuple)
        del d_check; del l_temp
        if dict:
            d_master = {}
            for tuple in l_master:
                d_master[tuple[0]] = tuple[2]
            del l_master; return d_master
        return l_master
        
class Tier:
    """A list of Segment classes corresponding to a tier.
    
    When iterated upon, returns each segment in 'self.segments'."""
    
    def __init__(self, name="", start=-1., end=-1., trans=None):
        self.name = name
        self.start = start
        self.end = end
        self.trans = trans
        self.segments = []
            # Pangloss variable
        self.pangloss = ({},{}) # Tuple of two dictionaries
                                # (level, FORM/TRANSL)
            # Structure variables
        self.type = ""
        self.truetype = ""      # 'time' or 'ref'
        self.parent = ""        # reference id
        self.pindex = -1        # index of the parent in trans.tiers
        self.level = 0          # depth of parenting (default 0, no parent)
        self.children = []      # list of tier indexes
            # extra structure
        self.ppoint = None      # pointer to parent tier
        self.cpoints = []       # pointers to children tiers
        self.ch_ref = False     # whether segments have valid references
        self.ch_time = False    # whether segments have valid time codes
            # Omni
        self.metadata = {}
            # hash
        self.thash = None        # list of lists of lists of tuple (int,index)
            # For overloaded methods
        self.d_setparent = {():self._spn,(type(None),):self._spo,
                            ('Segment',):self._spo,(type(int),):self._spi,
                            (type(str),):self._sps}
            ## Quick check
        self.checkparenting()
        
    
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
        copy.ppoint = None; copy.cpoints = []
        return copy
    
        # Experiment for quick segment access through timestamps
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
        # Basic functions
    def uptime(self, t_d, t_i):
        self.start = t_d
        self.end = t_i
    def checktime(self):
        if self.segments:
            self.start = self.segments[0].start
            self.end = self.segments[-1].end
        # Functions to deal with segments
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
                self.segments[p-1].end = start
            elif start > fin:
                self.segments.insert(p, Segment(self.segments[p-1].end,
                                     start, "", id, "", False, tier)); p += 1
            # Actual insertion
        self.segments.insert(p, Segment(start, end, cont, id, ref, unit, tier))
        # Functions to edit the structure
    def _cleanp(self,mode,ind):
        """Support function for 'setparent'."""
        if mode == 0 and self.ppoint:
            if self in self.ppoint.cpoints:
                self.ppoint.cpoints.remove(self)
            if ind in self.ppoint.children:
                self.ppoint.children.remove(ind)
        elif mode == 1 and self.ppoint:
            if self not in self.ppoint.cpoints:
                self.ppoint.cpoints.append(self)
            if self not in self.ppoint.children:
                self.ppoint.children.remove(ind)
    def setparent(self,*args):
        f = self.d_setparent.get(tuple(arg.__class__ for arg in args))
        if f is None:
            raise TypeError("Check 'self.d_setparent' in 'Tier'.")
        return f(*args)
    def _spn(self):
        """Sets the tier's parent.
        Won't work if tier has no 'trans'."""
        if self.trans:
            if self.pindex >= 0 and self.pindex < len(self.trans.tiers):
                self.setparent(self.pindex)
            elif self.parent:
                self.setparent(self.parent)
            else:
                self.setparent(None)
    def _spo(self,tier):
        t_ind = self._gettierindex(); self._cleanp(0,t_ind)
        if tier == None:
            self.pindex = -1; self.parent = ""; self.ppoint = None
            return
        if self.trans and tier in self.trans.tiers:
            self.pindex = self.trans.index(tier)
        else:
            self.pindex = -1
        self.parent = tier.name; self.ppoint = tier
        self._cleanp(1,t_ind)
    def _spi(self,ind):
        if (not self.trans) or (ind <= 0 or ind >= len(self.trans)):
            return self.setparent(None)
        t_ind = self._gettierindex(); self._cleanp(0,t_ind)
        self.pindex = ind; self.ppoint = self.trans.tiers[ind]
        self.parent = self.ppoint.name
        self._cleanp(1,t_ind)
    def _sps(self,name):
        if not self.trans:
            return self.setparent(None)
        ind,tier = self.trans.find(name,4)
        if not tier:
            return self.setparent(None)
        t_ind = self._gettierindex(); self._cleanp(0,t_ind)
        self.pindex = ind; self.ppoint = tier; self.parent = tier.name
        self._cleanp(1,t_ind)
    def addchild(self,index):
        """Inserts a child tier index in 'children'.
        RETURNS: '0/1' if success/failure."""
        
            # Index needs to be valid
        if index < 0 or index >= len(self.trans.tiers):
            return 1
        tier = self.trans.tiers[index]
        if tier not in self.cpoints:
            self.cpoints.append(tier)
        if index in self.children:
            return 0
            # Inserting
            ## If no other value
        if not self.children or index > self.children[-1]:
            self.children.append(index); return 0
            ## Else
        for a in range(len(self.children)):
            if index < self.children[a]:
                self.children.insert(a,index); return 0
    def clearp(self,mode=1):
        """Safety function: cleans all pointers.
        ARGUMENT:
        - 'mode'        :   '0' for tier only,
                            '1' for tier and segments
                            '2' for segments only"""
        if mode <= 1:
            self._cleanp(0)
            self.ppoint = None; self.cpoints.clear()
        if mode >= 1:
            for seg in self.segments:
                seg.ppoint = None
        # Function to get information
    def _gettierindex(self,index=-1):
        """Tier index is not stored, as it can easily change.
        This is to retrieve it 'quickly'."""
        
        if not self.trans:
            return -1
        lt = len(self.trans.tiers)
        if ((index < 0 or index >= lt) or (not
            self.trans.tiers[index] == self)):
            for a in range(lt):
                if self.trans.tiers[a] == self:
                    return a
            return -1
        return index
    def getsegtree(self,t_ind=-1,l_ind=[]):
        """Gets all the parent and children segments for those segments.
        ARGUMENTS:
        - 't_ind'   :   this tier's index
        - 'l_ind'   :   the list of segments (default all)
        RETURNS:
        - a list of tuples
          (tier_index,p/ctier_index,list_segindex,p/cseg_index)
        See the Segment equivalent for more."""
        
            # Variables
        l_master = []; t_ind = self._gettierindex(t_ind)
        ls = len(self.segments)
        if t_ind < 0:
            return []
        if not l_ind:
            for a in range(ls):
                l_ind.append(a)
        
            # Tier variables
            ## We get the parents
        ptier = self; self.checkparenting(t_ind)
        l_parent = []; ld_parent = []; o_ind = t_ind; index = self.pindex
        while ptier.pindex >= 0:
            ptier = self.trans.tiers[index]; ptier.checkparenting(index)
                # dictionary
            ld_parent.append({})
            for a in range(len(ptier)):
                ld_parent[-1][ptier.segments[a].id] = a
                # tier
            l_parent.append((index,o_ind))
            o_ind = index; index = ptier.pindex
            ## We get the children
        l_struct = self.getallchildren(1); l_child = []; ld_child = []
        if l_struct:
            for tuple in l_struct:
                c_ind = tuple[0]; ctier = self.trans.tiers[c_ind]
                ctier.checkparenting(c_ind)
                    # dictionary
                ld_child.append({})
                for a in range(len(ctier)):
                    ref = ctier.segments[a].ref
                    if ref in ld_child[-1]:
                        ld_child[-1][ref].append(a)
                    else:
                        ld_child[-1][ref] = [a]
                    # tier
                l_child.append((c_ind,ctier.pindex))
            # We fill the segments
        for s_ind in l_ind:
            if s_ind < 0 or s_ind >= ls:
                continue
            l_master.append([]); seg = self.segments[s_ind]
            ref = seg.ref; o_ind = s_ind
                # Parents
            for a in range(len(l_parent)):
                ps_ind = ld_parent[a].get(ref,-1)
                if ps_ind < 0:
                    break
                l_master[-1].append((l_parent[a][0],l_parent[a][1],
                                     [ps_ind],[o_ind]))
                ref = self.trans.tiers[l_parent[a][0]] \
                                .segments[ps_ind].ref
                o_ind = ps_ind
            l_master[-1].reverse()
                # Main tier
            l_master[-1].append((t_ind,t_ind,[s_ind],[s_ind]))
                # Children
            if not l_child:
                continue
            l_ids = [(t_ind,t_ind,[s_ind])]
            l_temp = []; l_cur = l_ids[0]; l_inds = []
            for a in range(1,len(l_child)):
                c_ind = l_child[a][0]; ctier = self.trans.tiers[c_ind]
                    # We need the correct parent tier
                if not ctier.pindex == l_cur[0]:
                    check = False
                    for b in range(len(l_ids)-1,-1,-1):
                        if ctier.pindex == l_ids[b][0]:
                            check = True; l_cur = l_ids[b]; break
                        if check:
                            break
                    if not check: # wut
                        continue
                    # We find the segments
                for ss_ind in l_cur[2]:
                    id = self.trans.tiers[l_cur[0]] \
                                   .segments[ss_ind].id
                    l_tmp = ld_child[a].get(id,[])
                    for b in range(len(l_tmp)):
                        l_temp.append(l_tmp[b])
                        l_inds.append(ss_ind)
                    # We update the reference segments
                l_master[-1].append((c_ind,ctier.pindex,
                                     l_temp.copy(),l_inds.copy()))
                l_ids.append((c_ind,ctier.pindex,l_temp.copy()))
                l_cur = l_ids[-1]; l_temp.clear(); l_inds.clear()
            # Clearing lists
        l_ind.clear(); l_parent.clear(); l_child.clear()
        ld_parent.clear(); ld_child.clear()
        return l_master
    def getallchildren(self,mode=1,index=-1):
        """Expands the 'children' list to all sub-children.
        ARGUMENTS:
        - 'mode'    :   '0' for level order
                        '1' for linear order
        - 'index'   :   this tier's index
        RETURNS:
        - A list of tuples (tier_index, parenttier_index, list_childtierindex)
        Each tuple has the tier index 't_ind', parent tier index and 
        the list of child tier indexes.
        /!\ The list contains the tier itself!"""
        
            # Variables
        if index < 0:
            index = self._gettierindex(index)
            # Mode 0: level order
        if mode == 0:
                # Variables
            l_struct = [(index,self.pindex,[self.children])]
            l_children = self.children; l_temp = []
                # We cycle through the children
            while l_children:
                for a in l_children:
                    ctier = self.trans.tiers[a]; ctier.checkparenting(index)
                    if ctier.pindex < 0:
                        continue
                    l_struct.append((a,ctier.pindex,[ctier.children]))
                    l_temp = l_temp + ctier.children
                l_children = l_temp.copy(); l_temp.clear()
            # Mode 2: linear order
        elif mode == 1:
            l_struct = [(index,self.pindex,[self.children])]
            for ind in self.children:
                ctier = self.trans.tiers[ind]
                if not ctier.children:
                    l_struct.append((ind,index,[]))
                else:
                    l_struct = l_struct + ctier.getallchildren(1,ind)
        return l_struct
        # Function to kind of check the tier
    def checksegment(self,mode=0):
        """Simply recreates the whole list of segments in mode 0."""
        l_trans = []
        for seg in self.segments:
            l_trans.append(seg)
        self.segments.clear()
        if mode == 0:
            for seg in l_trans:
                self.addsegment(-1, seg.start, seg.end, seg.content,
                                seg.id, seg.ref,seg.unit, seg.tier, 0)
                self.segments[-1].pangloss = seg.pangloss.copy()
                self.segments[-1].notes = seg.notes.copy()
                self.segments[-1].metadata = seg.metadata.copy()
        elif mode == 1:
            for seg in l_trans:
                if not seg.unit:
                    continue
                self.addsegment(-1, seg.start, seg.end, seg.content,
                                seg.id, seg.ref,seg.unit, seg.tier)
                self.segments[-1].pangloss = seg.pangloss.copy()
                self.segments[-1].notes = seg.notes.copy()
                self.segments[-1].metadata = seg.metadata.copy()
        l_trans.clear()
        # Functions to check the tier
    def checkparenting(self,index=-1):
        """Checks the tier's parent/pindex and that parent tier's child.
        ARGUMENT:
        - 'index'   :   tier index
        RETURNS: '-1' if not a valid index
                 '0' if no parent
                 '1' otherwise.
        Note: /!\ It expects this tier and its parent to be part of the 
              same 'Transcription' instance! If not, it will de-parent."""
            # Get the tier index
        index = self._gettierindex(index)
        if index < 0:
            self.setparent(); return -1
            
            # Checks parent/pindex/ppoint
        check = False; lt = len(self.trans.tiers)
            # By name
        if self.parent:
            for a in range(len(self.trans.tiers)):
                if self.trans.tiers[a].name == self.parent:
                    self.pindex = a; check = True; break
            # By index
        if not check:
            if self.pindex >= 0 and self.pindex < lt:
                self.parent = self.trans.tiers[self.pindex].name
                check = True
            # By children
            else:
                for a in range(lt):
                    ptier = self.trans.tiers[a]
                    if index in ptier.children:
                        tier.pindex = a; tier.parent = ptier.name
                        check = True; break
            # By ppoint
        if not check:
            if self.ppoint and self.ppoint in self.trans.tiers:
                self.pindex = self.trans.tiers.index(self.ppoint)
                self.parent = self.ppoint.name; check = True
            else:
                    # By cpoints
                for a in range(lt):
                    ptier = self.trans.tiers[a]
                    if self in ptier.cpoints:
                        tier.pindex = a; tier.parent = ptier.name
                        check = True; break
                        
            # We deal with the result 
        self._cleanp(0,index)
        if not check:
            self.ppoint = None; self.parent = ""; self.pindex = -1
            return 0
        self.ppoint = self.trans.tiers[self.pindex]
            # We check the parent tier's children/cpoints
        for a in range(lt):
            if a == self.pindex:
                self.trans.tiers[a].addchild(index)
            else:
                if index in self.trans.tiers[a].children:
                    self.trans.tiers[a].children.remove(index)
                if self in self.trans.tiers[a].cpoints:
                    self.trans.tiers[a].cpoints.remove(self)
        return 0
    def checkids(self,**args):
        """Checks all the ids against that of the parent tier"""
        
        l_refs = []
            # Parenting must be checked
        if args.get('checkparenting',False):
            self.checkparenting()
        clean = args.get('clean',False)
            # Other checks
        if (not self.trans) or (not self.parent):
            if clean:
                for seg in self.segments:
                    seg.ref = ""; seg.ppoint = None
            return (False,l_refs)
        elif not self.segments:
            return (True,l_refs)
            # We get the parent
        ptier = self.trans.tiers[self.pindex]
        if not ptier.segments:
            if clean:
                for seg in self.segments:
                    seg.ref = ""; seg.ppoint = None
            return (False,l_refs)
        d_ref = {}
        for seg in ptier:
            d_ref[seg.id] = seg
            # We check
        check = True
        for a in range(len(self.segments)):
            seg = self.segments[a]
            if seg.unit == False:
                continue
            if (not seg.ref) or (seg.ref not in d_ref):
                l_refs.append(a); seg.ppoint = None
            else:
                seg.ppoint = d_ref[seg.ref]
        if l_refs:
            if clean:
                for seg in self.segments:
                    seg.ref = ""; self.ppoint = None
            return (False,l_refs)
        return (True,l_refs)
    def setids(self):
        """Sets segment pointers according to 'ref'.
        RETURNS     :   a list of segment indexes where 'ref' failed.
                        a segment index '-1' if no 'ppoint' was found.
        Note: requires a tier 'ppoint'.
        Note: includes False units.
        Note: will keep the segment 'ref' intact no matter what."""
        
        l_negs = []
        if not self.ppoint:
            self.setparent()
            if not self.ppoint:
                return [-1]
        d_refs = {}
        for seg in self.ppoint:
            d_refs[seg.id] = seg
        for a in range(len(self.segments)):
            seg = self.segments[a]
            pseg = d_refs.get(seg.ref)
            if pseg:
                seg.ppoint = pseg
            else:
                l_negs.append(a); seg.ppoint = None
        del d_refs; return l_negs
    def checktimestamps(self,**args):
        """Checks all the timestamps for positive linear values.
        RETURNS: a tuple (check_time,list,list)
        Each list has segment indexes: the first is for negative boundaries,
        the second for 'overlapping' boundaries."""
        
            # We check
        end = -1.; l_neg = []; l_faults = []
        for a in range(len(self.segments)):
            seg = self.segments[a]
            if seg.start < 0. or seg.end < 0.:
                l_neg.append(a)
            elif seg.start < end or seg.end < end:
                l_faults.append(a)
            if seg.end > end:
                end = seg.end
            # We clean
            ## I have yet to define what cleaning would mean
        check = True
        if l_neg or l_faults:
            check = False
        return (check,l_neg,l_faults)
    def settimestamps(self):
        """Sets segment pointers according to time codes.
        RETURNS     :   a list of segment indexes where it failed.
                        a segment index '-1' if no 'ppoint' was found.
        Note: requires a tier 'ppoint' and relies on 'Tier.hash()'
        Note: include False units.
        Note: matches if 'seg' is inside or equivalent  of 'pseg'.
        Note: will keep the time codes intact no matter what."""
        
        l_negs = []
        if not self.ppoint:
            self.setparent()
            if not self.ppoint:
                return [-1]
        ptier.sethash()
        for a in range(len(self.segments)):
            seg = self.segments[a]
            pseg = ptier.hash(seg.start)
            if pseg and seg.end <= pseg.end:
                seg.ppoint = pseg
            else:
                l_negs.append(a); seg.ppoint = None
        ptier.thash = None; return l_negs
        # Accessory functions
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
    
def getit(dict,list,keyname):
    """Support function for 'getall' methods."""
        # Nothing to add
    if not list:
        return dict
        # Only one element
    if len(list) == 1:
        dict[keyname] = list[0]
        # More than one element
    else:
        count = 0
        for val in list:
            dict[keyname+str(count)] = val; count += 1
    return dict
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
    def getall(self,open=True):
        """Returns a dictionary of all corpus metadata.
        Prefixes every key with 'c_'."""
        
            # Variables
        d_md = {}; count = 0
            # names / types / ownerships
        getit(d_md,self.name,'c_name')
        getit(d_md,self.type,'c_type')
        getit(d_md,self.ownership,'c_ownership')
            # versions
        for a in range(len(self.version)):
            l_vers = self.version[a]
            if a == 0:
                getit(d_md,l_vers,'c_vers')
            elif a == 1:
                getit(d_md,l_vers,'c_versDate')
            elif a == 2:
                getit(d_md,l_vers,'c_versAuth')
            elif a == 3:
                getit(d_md,l_vers,'c_versLoc')
            # Open
        if open:
            for key,value in self.open.items():
                d_md['c_'+key] = value
        return d_md
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
    def getall(self,open=True):
        """Returns a dictionary of all corpus metadata.
        Prefixes every key with 'c_'."""
        
            # Variables
        d_md = {}; count = 0
            # names / types / ownerships
        getit(d_md,self.name,'r_name')
        getit(d_md,self.url,'r_url')
        getit(d_md,self.type,'r_type')
        getit(d_md,self.quality,'r_quality')
            # versions
        for a in range(len(self.version)):
            l_vers = self.version[a]
            if a == 0:
                getit(d_md,l_vers,'r_vers')
            elif a == 1:
                getit(d_md,l_vers,'r_versDate')
            elif a == 2:
                getit(d_md,l_vers,'r_versAuth')
            elif a == 3:
                getit(d_md,l_vers,'r_versLoc')
            # Open
        if open:
            for key,value in self.open.items():
                d_md['r_'+key] = value
        return d_md
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
    def getall(self,open=True):
        """Returns a dictionary of all corpus metadata.
        Prefixes every key with 'c_'."""
        
            # Variables
        d_md = {}; count = 0
            # names / types / ownerships
        getit(d_md,self.name,'t_name')
        getit(d_md,self.url,'t_url')
        getit(d_md,self.type,'t_type')
        getit(d_md,self.ownership,'t_ownership')
            # versions
        for a in range(len(self.version)):
            l_vers = self.version[a]
            if a == 0:
                getit(d_md,l_vers,'t_vers')
            elif a == 1:
                getit(d_md,l_vers,'t_versDate')
            elif a == 2:
                getit(d_md,l_vers,'t_versAuth')
            elif a == 3:
                getit(d_md,l_vers,'t_versLoc')
            #Format
        if self.format:
            d_md['t_format'] = self.format
        if self.format_version:
            d_md['t_formatVers'] = self.format_version
            # Open
        if open:
            for key,value in self.open.items():
                d_md['t_'+key] = value
        return d_md
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
    def getall(self):
        """Returns a dictionary of all metadata (minus speakers).
        Prefixes keys with 'c_','r_' and 't_'
        for Corpus, Recording, Transcript."""
        d_md = {}
        d_md.update(self.corpus.getall())
        d_md.update(self.recording.getall())
        d_md.update(self.transcript.getall())
        return d_md
   
class Transcription:
    """Class containing the metadata and a list of Tier classes.
    
    When iterated upon, returns each tier in 'self.tiers'."""
    def __init__(self, name="", start =-1., end =-1.):
        self.name = name
        self.start = start
        self.end = end
        self.tiers = []             # list of Tier objects
        self.dictionary = None      # Elan and Pangloss integrate dictionaries
        self.metadata = Metadata()  # Metadata object
            # Complements
        self.notes = []             # Pangloss notes
        self.timetable = []         # see 'settimetable'
        self.format = ""            # where it was imported from
    
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
    
        # Add content
    def addtiers(self, mode=0, l_info=[], insert=-1, **args):
        """Creates tiers.
        ARGUMENTS:
        - mode    : '0' from nothing
                    '1' from a list of segments
                    '2' from copying an existing tier
                    '3' from tokenizing an existing tier
        - l_info  : a list of tuples, segments, tiers or strings.
        - insert  : an index for inserting the new tier(s).
        - types   : **arg, list of 'truetype' (string, one per tier)
        RETURNS:
        - A list of tuples (index,tier)
        Note : 'l_info' varies according to the mode.
               '0' requires tuples (name,start,end,parent).
               '1' requires segment objects; '2' tiers objects.
               '3' requires separators (either a string or a list).
        Note : for '3', 'insert' is a list of tier indexes to tokenize."""
        
            # Variables
        l_tiers = []; lt = len(self.tiers)
        l_types = args.get("types",[])
            ## From nothing
        if mode == 0:
                # No info on tiers
            if not l_info:
                l_tiers.append(self.addtier("",-1.,-1.,insert))
                # Tuples with info on tiers
            else:
                name = ""; start = -1.; end = -1.; parent = ""
                lt = len(tuple)
                for a in range(len(l_info)):
                    tuple = l_info[a]
                    if lt > 3:
                        parent = tuple[3]
                    if lt > 2:
                        end = tuple[2]
                    if lt > 1:
                        start = tuple[1]
                    name = tuple[0]
                    ind,tier = self.addtier(name,start,end,insert)
                    l_tiers.append((ind,tier))
                    if parent:
                        for b in range(len(self.tiers)):
                            ptier = self.tiers[b]
                            if not ptier.name == parent:
                                continue
                            tier.parent = parent; tier.pindex = b
                            ptier.addchild(ind); break
                    if l_types:
                        tier.truetype = l_types[a]
                    insert += 1
            ## From a list of segments
        elif mode == 1:
            ind,tier = self.addtier("",-1.,-1.,insert)
            for seg in l_info:
                tier.segments.append(seg.copy())
            l_tiers.append((ind,tier))
            ## From copying a tier
        elif mode == 2:
                # add the tiers
            for tier in l_info:
                self.tiers.insert(insert, tier.copy())
                l_tiers.append((insert,self.tiers[insert]))
                insert += 1
                # fix indexes
            li = len(l_info)
            for tier in self:
                if tier.pindex >= insert:
                    tier.pindex += li
                for b in range(len(tier.children)):
                    if tier.children[b] >= insert:
                        tier.children[b] += li
            ## From tokenizing
        elif mode == 3:
                # We get the tokens
            d_tok = {}; li = len(insert); l_cont = []; count = 0
            for el in l_info:
                d_tok[el] = True
            for a in range(li):
                    # We get the index
                ind = insert[a]
                if ind < 0 or ind >= lt:
                    continue
                    # We get the tiers
                tier = self.tiers[ind]; name = tier.name+"[tok]"
                cind,ctier = self.addtier(name,tier.start,tier.end,ind+1)
                l_tiers.append((cind,ctier))
                    # We fix other indexes
                for b in range(a+1,li):
                    if insert[b] > ind:
                        insert[b] += 1
                    # We parent the new tier
                ctier.parent = tier.name; ctier.pindex = ind
                tier.addchild(cind)
                if l_types:
                    tier.truetype = l_types[a]
                    # We tokenize
                for seg in tier:
                    if seg.unit == False or not seg.content:
                        continue
                    l_cont.clear(); cont = ""
                    start = seg.start; end = seg.end; dur = end-start
                        # We get the sub-segments
                    for char in seg.content:
                        if char in d_tok:
                            if cont:
                                l_cont.append(cont)
                            cont = ""
                        else:
                            cont = cont + char
                        # We create the new segments
                    lc = len(l_cont)
                    for b in range(lc):
                        cont = l_cont[b]; id = "s"+str(count); count += 1
                        c_start = start+(dur*(b/lc))
                        c_end = start+(dur*((b+1)/lc))
                        ctier.addsegment(-1,c_start,c_end,cont,id,
                                         seg.id,True,ctier,1)
        return l_tiers
    def addtier(self, name="", start=-1., end=-1., insert=-1):
        """Creates and adds the tier.
        If 'insert>=0', inserted at index 'insert'; otherwise appended."""
        if insert >= 0 and insert < len(self.tiers):
            self.tiers.insert(insert, Tier(name, start, end, self))
                # We check the indexes
            for tier in self:
                if tier.pindex >= insert:
                    tier.pindex += 1
                for b in range(len(tier.children)):
                    if tier.children[b] >= insert:
                        tier.children[b] += 1
            return (insert,self.tiers[insert])
        else:
            self.tiers.append(Tier(name, start, end, self))
            return (len(self.tiers)-1,self.tiers[-1])
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
        # Basic functions
    def uptime(self, mode=0):
        """If you don't want to create a timetable but still adjust the
        Trans's boundaries.
        mode: '0' to use the segments, '1' to use the tier's start/end
        themselves"""
        if mode == 0:
            for tier in self.tiers:
                for seg in tier.segments:
                    start = seg.start
                    if start >= 0. and (self.start > start or self.start < 0.):
                        self.start = start
                    end = seg.end
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
            tier.start = self.start; tier.end = self.end
            if tier.segments:
                n_start = tier.segments[0].start
                n_end = tier.segments[-1].end
                if mode == 0:
                    tier.segments[0].start = self.start
                    tier.segments[0].end = self.end
                elif mode == 1:
                    if n_start > self.start:
                        tier.addsegment(0, self.start, n_start, "", "", "",
                                        False, tier, 1)
                    elif n_start < self.start:
                        tier.segments[0].start = self.start
                    if n_end < self.end:
                        tier.addsegment(-1, n_end, self.end, "", "", "",
                                        False, tier, 1)
                    elif n_end > self.end:
                        tier.segments[-1].end = self.end
    def checkseg(self):
        """Realigns all tiers segments."""
        
        for tier in self:
            tier.checksegment()
        # See tiers' 'hash' functions
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
        # Tiers structure
    def settimetable(self, adjust=0,**args):
        """Creates a list of boundaries ordered (smallest to biggest)
        and without duplicates.
        adjust=1 to also adjust the Tier's boundaries"""
    
        check = args.get('truetype',True)
        self.timetable.clear()
        for tier in self.tiers:
            if check and tier.truetype and not tier.truetype == "time":
                continue
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
                                self.timetable.insert(self.timetable.index(t), 
                                                      start)
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
    def setchildtime(self,l_tiers=[],**args):
        """For ELAN, gives "assoc" and "subd" tiers actual time boundaries."""
        
        if args.get('setstructure',True):
            self.setstructure(setchildtime=False)
            # We set up a list 'l_children' containing for each parent
            #  the list of children indexes (in order)
        l_children = []; l_parent = []
        if not l_tiers:
            for tier in self.tiers:
                if tier.pindex < 0:
                    l_parent.append(tier)
                    l_children.append(tier.getallchildren(1))
        else:
            for a in range(len(l_tiers)):
                tier = self.tiers[a]
                l_parent.append(tier)
                l_children.append(tier.getallchildren(1))

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
            for tuple in list:
                ptier = self.tiers[tuple[0]]
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
    def checkstructure(self,l_tiers=[],**args):
        """Checks the tiers' structure.
        1. Ensures 'parent'-'pindex'-'children'-'ppoint' are synched
        2. Returns False if a single ID or timestamp is missing
        
        ARGUMENTS:
        - l_tiers   :     list of tiers to check
        - clean     :     clean invalid IDs/timestamps
        Note: invalid timestamps are kept if no valid IDs are available
        Note: checks parents/children beyond the set of tiers
        
        RETURNS:
        - a tuple (tuple,list)
        - 'tuple' contains (type,ref_check,time_check) in string, bool, bool
        - 'l_return' contains a list of tuples
          (type,ref_check,time_check,l_neg,l_faults)
        The 'tuple' checks the whole list; 'l_return' checks each tier.
        'l_neg' is indexes of segments with negative boundaries.
        'l_faults' is indexes of segments with 'overlapping' boundaries.
        Note: 'type' is the tier's truetype, updated by this function.
        Note: 'type' for 'tuple' can have the value "mixed"."""
        
            # Variables
        tuple = ("",False,False); l_return = []
        setchildtime = args.get('setchildtime',True)
        clean = args.get('clean',False)
            # If no tier is selected, we get all tiers
        if not l_tiers:
            for a in range(len(self.tiers)):
                l_tiers.append(a)
            # Separate check for parent/pindex/children
        l_parent = []
        for ind in l_tiers:
            self.tiers[ind].checkparenting(ind)
        if setchildtime:
            self.setchildtime(l_tiers,setstructure=False)
            # Checks the ids and timestamps
        for ind in l_tiers:
            tier = self.tiers[ind]
                # IDS
            ref_check,l_refs = tier.checkids(clean=clean)
                # TIMESTAMPS
            time_check,l_neg,l_faults = tier.checktimestamps()
                # cleaning
                ## Note: We don't clean timestamps if there are no ids
            if clean and ref_check and not time_check:
                for seg in tier:
                    seg.start = -1.; seg.end = -1.
                # TYPE
                ## Again, default to time even if flawed
            if tier.truetype == "ref" and not ref_check:
                tier.truetype = "time"
            elif tier.truetype == "time" and not time_check:
                if ref_check:
                    tier.truetype = "ref"
                # List of checks
            l_return.append((tier.truetype,ref_check,l_refs,time_check,
                             l_neg,l_faults))
            # Final return value
        ref_check = True; time_check = True; type = ""
        for tuple in l_return:
                # TYPE
            if not type:
                type = tuple[0]
            elif not type == tuple[0]:
                type = "mixed"
                # IDS
            if ref_check and not tuple[1]:
                ref_check = False
                # TIMESTAMPS
            if time_check and not tuple[2]:
                time_check = False
        tuple = (type,ref_check,time_check)
        return (tuple,l_return)
    def setstructure(self,mode=0,l_tiers=[], **args):
        """Attributes parents, children, levels, ids and refs to tiers.
        
        ARGUMENTS:
        'mode'      : '0' - relies purely on the preexisting structure.
                      '1' - relies also on timestamps.
        'l_tiers'   : the list of tiers on which to operate.
        'ids'       : a string for ids, coupled with an incremented int.
        'clean'     : boolean, whether to clean the previous structure
        
        RETURNS:
        - 0/1 for success/failure
        This is to automatically get the structure. To be distinguished from
        a manual structuration."""
        
            # Variables
        ids = args.get('ids',"a")
        setchildtime = args.get('setchildtime',True)
        clean = args.get('clean',False)
            # If no tier is selected, we get all tiers
        if not l_tiers:
            for a in range(len(self.tiers)):
                l_tiers.append(a)
            # We get checking values
            ## 'setchildtime' adds timestamps where possible
        g_check, gl_check = self.checkstructure(l_tiers,clean=clean,
                                                setchildtime=setchildtime)
            # If clean, we clean all structure
        if clean:
            for a in l_tiers:
                self.tiers[a].parent = ""; self.tiers[a].pindex = -1

            # Mode = 1: we add to the structure using timestamps
        if mode == 1:
            l_struct = []; l_ti = []
            l_segs = []; l_pos = []; l_max = []; l_acc = []
                # We only keep 'time' tiers
            for a in range(len(l_tiers)):
                if gl_check[a][2] and self.tiers[a].segments:
                    l_ti.append(self.tiers[l_tiers[a]])
                    l_struct.append([]); l_acc.append(0)
                    l_segs.append(l_ti[-1].segments[0])
                    l_pos.append(0); l_max.append(len(l_ti[-1]))
                # l_struct is actually a matrix
                ## list of lists of integers
            for struct in l_struct:
                for a in l_ti:
                    struct.append(0)
            pl = len(l_ti)
                # We compare segs
            while True:
                    # Step 1: we get the earliest segment
                seg = None; ind = -1; start = -1.
                for a in range(1,len(l_segs)):
                    sseg = l_segs[a]
                    if sseg == None:
                        continue
                    if start < 0 or sseg.start < start:
                        seg = sseg; start = sseg.start; ind = a
                    # Break the 'while' loop if no segment is left
                if seg == None:
                    break
                    # Step 2: we compare that segment with every other
                struct = l_struct[ind]
                for a in range(len(l_segs)):
                        # If the structure already failed, why bother
                    if (struct[a] < 0 or l_segs[a] == None or a == ind):
                        continue
                    rseg = l_segs[a]
                        # Discrepancy, no structure between them
                    if (seg.start < rseg.start or seg.end > rseg.end):
                        struct[a] = -1; continue
                        # End of unit for that comparison
                    elif seg.end == rseg.end:
                        if l_acc[a] > struct[a]:
                            struct[a] = l_acc[a]
                        l_acc[a] = 0
                        # Another matching unit
                    else:
                        l_acc[a] += 1
                    # Step 3: we increment that tier's segment
                l_pos[ind] += 1
                if l_pos[ind] >= l_max[ind]:
                    l_segs[ind] = None
                else:
                    l_segs[ind] = l_ti[ind].segments[l_pos[ind]]
            del l_acc; del l_segs; del l_pos; del l_max
                # We now have filled a matrix 'l_struct'
                ## Time to get the best result for each tier
                ## We'll also take that occasion to give them ids
            count = 0; pos = 0
            for a in range(1,len(l_struct)):
                    # Get the smallest positive result
                    ## This is the trick to seek the closest parent
                s = -1; ind = -1
                for b in range(len(l_struct[a])):
                    if s < 0 or l_struct[a][b] < s:
                        s = l_struct[a][b]; ind = b
                    # That's our parent
                if ind >= 0:
                    tier = l_ti[a]; rtier = l_ti[ind]
                    tier.parent = rtier.name; tier.pindex = ind
                    rtier.addchild(a); pos = 0; pl = len(tier)
                        # We add ids because we can
                    for seg in rtier:
                        seg.id = ids+str(count); count += 1
                        for b in range(pos,pl):
                            cseg = tier.segments[b]; cseg.ref = seg.id
                            cseg.id = ids+str(count); count += 1
                            if cseg.end == seg.end:
                                pos = b+1; break
            del l_struct; del l_ti
        
            # Timestamps or not, we renew the ids
            ## This also sets the tier levels
            ## We get the parents
        l_parent = []; test = 0
        for a in l_tiers:
            if not self.tiers[a].parent:
                l_parent.append(a)
            ## We set the ids and refs
        l_count = []; l_temp = []; count = 0; level = 0
        while l_parent:
            for a in l_parent:
                ptier = self.tiers[a]; ptier.level = level
                l_count.clear(); lc = len(ptier.children)
                for b in ptier.children:
                    l_count.append(0)
                    l_temp.append(b)
                for pseg in ptier:
                    id = ids+str(count); count += 1
                    for b in range(lc):
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
            l_parent = l_temp.copy(); l_temp.clear(); level += 1
        l_tiers.clear()
        return 0
    def clearp(self,mode=1):
        """Safety function: clears all pointers.
        ARGUMENT:
        - 'mode'        :   '0' for tier only,
                            '1' for tier and segments
                            '2' for segments only"""
        for tier in self.tiers:
            tier.clearp(mode)
        # Get information
    def getparents(self):
        """Provides a list of parent tiers and their children."""
        
        l_parents = []; l_struct = []
        for a in range(len(self.tiers)):
            tier = self.tiers[a]
            if tier.pindex < 0:
                l_parents.append(a)
                l_struct.append(tier.getallchildren(1))
        return (l_parents, l_struct)
    def getsegtree(self,l_segs=[]):
        """Get all the parent and children ids of a given segment.
        ARGUMENTS:
        - 'l_segs'      :   list of tuples (tier_index,list_segindex).
        RETURNS:
        - A list of lists of lists [ tier [ segment [ (tuple) ] ] ].
        Where each tuple contains (tier_index,p/ctier_index,
                                   list_segindex,p/cseg_index).
        See the Segment equivalent method for details."""
        
            # Variables
        l_master = []
            # We simply call the Tier method
        for tuple in l_segs:
            t_ind = tuple[0]
            if t_ind < 0 or t_ind > len(self.tiers):
                continue
            tier = self.tiers[t_ind]; lt = len(tier)
                # Quick check
            l_copy = []
            for ind in tuple[1]:
                if ind >= 0 and ind < lt:
                    l_copy.append(ind)
            l_master.append(tier.getsegtree(t_ind,l_copy)); l_copy.clear()
        return l_master  
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
    def find(self,pattern,mode=0,index=0,lt=-1):
        """Find a tier by name.
        ARGUMENTS:
        - 'pattern'     :   the name to be found
        - 'mode'        :   '0' re, '1-4' starts-in-ends-equals
        - 'index'       :   starting index in the tier list.
        RETURNS:
        - a tuple (tier_index,tier)."""
        
        if lt < 0:
            lt = len(self.tiers)
        if mode == 0:
            try:
                import re
            except:
                mode = 2
        if mode == 0:
            for a in range(index,lt):
                if self.tiers[a].name == pattern:
                    return (a,self.tiers[a])
            for a in range(index,lt):
                if re.search(pattern,self.tiers[a].name):
                    return (a,self.tiers[a])
        elif mode == 1:
            for a in range(index,lt):
                if self.tiers[a].name.startswith(pattern):
                    return (a,self.tiers[a])
        elif mode == 2:
            for a in range(index,lt):
                if pattern in self.tiers[a].name:
                    return (a,self.tiers[a])
        elif mode == 3:
            for a in range(index,lt):
                if self.tiers[a].name.endswith(pattern):
                    return (a,self.tiers[a])
        elif mode == 4:
            for a in range(index,lt):
                if self.tiers[a].name == pattern:
                    return (a,self.tiers[a])
        return (-1,None)
    def findAll(self,pattern,mode=0):
        """Find multiple tiers by name. Relies on 'self.find()'."""
        pos = 0; lt = len(self.tiers); l_tiers = []
        while True:
            pos,tier = self.find(pattern,mode,pos,lt)
            if pos < 0:
                break
            l_tiers.append((pos,tier)); pos += 1
        return l_tiers
        # Speakers
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
    def checkSpeakers(self):
        """Makes sure each tier has a speaker."""
        tier_spk = self.tierSpeakers()
        tran_spk = self.transSpeakers()
        for tuple in tier_spk:
            if tuple[0] not in tran_spk:
                self.metadata.addspeaker(tuple[0])
        if not self.metadata.speakers:
            l_spk = []
            for tier in self.tiers:
                if tier.pindex < 0:
                    l_spk.append(tier)
            for tier in l_spk:
                self.metadata.addspeaker(tier.name)
                tier.metadata['speaker'] = tier.name
                l_child = tier.getallchildren(1)
                for cind in l_child:
                    self.tiers[cind].metadata['speaker'] = tier.name
                    self.tiers[cind].type = "a"  
        # Deprecated
    def clear(self,mode=0):
        if mode == 0:
            self.timetable.clear()
        else:
            self.name = ""; self.start = 0.; self.end = 0.
            self.metadata = Metadata()
            self.tiers.clear()
            self.dictionary.clear()
            self.notes.clear()
            self.timetable.clear()
            self.format = ""

