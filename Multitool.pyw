"""Graphical interface for the 'multitool' package.

Non-graphical functions should be externalized for console use.
Relevant data is kept  and shared through the 'Data' class."""

    # Basic support functions       
def mul_strDict(string):
    """Support function to turn a string into a Dictionary.
    Keys and values are always strings."""
    
        # We check
    l_dict = {}
    if not string:
        return l_dict
        # We parse
    state = 0; sym = ""; key = ""; value = ""
    for char in string:
        if state == 0 or state == 3:
            if char == "\"" or char == "'":
                sym = char; state += 1
        elif state == 2:
            if char == ":":
                state += 1
        elif state == 5:
            l_dict[key] = value; key = ""; value = ""
        elif state == 6:
            if char == ",":
                state = 0
        else:
            if char != sym:
                if state == 1:
                    key = key + char
                elif state == 4:
                    value = value + char
            elif not key:
                state = 0
            else:
                state += 1
    return l_dict
def mul_strList(string):
    """Support function to turn a string into a List.
    Values are always strings."""
    
        # We check
    l_list = []
    if not string:
        return l_list
        # We parse
    state = 0; sym = ""; value = ""
    for char in string:
        if state == 0:
            if char == "\"" or char == "'":
                sym = char; state += 1
        elif state == 1:
            if char != sym:
                value = value + char
            else:
                if value:
                    l_list.append(value); value = ""
                state += 1
        elif state == 2:
            if char == ",":
                state = 0
    return l_list
def mul_strType(string):
    """To check what a string is meant to contain."""
    import re
    if not string:
        return ""
    elif string[0] == "[" and string[-1] == "]":
        return mul_strList(string)
    elif string[0] == "{" and string[-1] == "}":
        return mul_strDict(string)
    elif string == "True":
        return True
    elif string == "False":
        return False
    elif re.match("\d",string[0]):
        if "." in string:
            return float(string)
        else:
            return int(string)
    else:
        return string
    # Main support functions
def mul_load(data=None,f="",**args):
    """Loads a properties file.
    Currently deprecated..."""
    import os
        
        # Checks
    if not data:
        return data
    prod,prop = os.path.split(f)
    if not os.path.isfile(f):
        return data
    
        # encoding
    encoding = args.get('encoding',"utf-8")
        # Default properties file
    default = False
    if prop == "default.txt":
        default = True; data.dflt = f
        # We open and read
    with open(f,encoding=encoding) as file:
        for line in file:
                # Not the right properties file.
                ## We try and avoid recursivity here
            if default and "cur_prop" in line:
                line = getArg(line)
                if (line and (not line == data.dflt) and
                    (os.path.isfile(line))):
                    return load(line,encoding=encoding)
                # Package path
            elif "package" in line:
                line = getArg(line)
                if os.path.isdir(line):
                    data.setPack(data.pack,prod)
                # List of 'tools' folders
            elif "tools_dir" in line:
                line = strList(getArg(line))
                for item in line:
                    if ((line not in data.tool) and
                        (os.path.isdir(line))):
                        data.tool.append(item)
                # if tools are activated
            elif "ch_tools" in line:
                data.ch_tool = getArg(line)
                # the current operation
            elif "ch_ope" in line:
                data.ope = int(getArg(line))
                # the list of tools to import
            elif "tools" in line:
                line = strList(getArg(line))
                for item in line:
                        # Complete path
                    if os.path.isfile(item):
                        data.tools.append(item)
                        continue
                        # Only the file name
                    for dir in data.tool:
                        if os.path.isdir(dir):
                            for file in os.listdir(dir):
                                if file == item:
                                    data.tools.append(os.path.join(dir,item))
    return data
def mul_save(data=None,f="",**args):
    """Saves the current properties file."""
    import os
    
        # Checks
    if not data:
        return 1
    prod,prop = os.path.split(f)
    if not os.path.isdir(prod):
        return 1
    if not f:
        f = data.prop
    
        # encoding
    encoding = args.get('encoding',"utf-8")
        # We check
    default = False
    if prop == "default.txt":
        default = True; data.dflt = f
        # We edit the default property file if needed
    if (os.path.isfile(data.dflt) and (data.dflt != f)):
        f_cop = []
            # First pass to copy the default file
        with open(data.dflt,encoding=encoding) as file:
            for line in file:
                f_cop.append(line)
        check = False
            # Second pass to rewrite it with the one line edited
        with open(data.dflt,'w',encoding=encoding) as file:
            for line in f_cop:
                if "cur_prop" in line:
                    line = ("ncur_prop=\"{}\"\n".format(f))
                file.write(line)
        # We write the save file
    with open(f,'w',encoding=encoding) as file:
        if default:
            file.write("\t# Different from default\ncur_prop=\"\"\n")
        file.write("\t# General variables\n\t## Tools\n"
                   "tools_dir={}\nch_tools={}\n\t# Operation\n"
                   "ch_ope={}\n\t# Collection save\nfolders={}\n"
                   "files={}"
                   .format(data.tool,data.ch_tool,data.ope,"[]","[]"))
    if f != data.prop:
        data.prop = f
    return 0
def mul_imPackage(data=None,f=""):
    """Imports the 'conversion_data' package.
    > Checks whether it is already in sys.modules
    > Checks if it can be imported as is (tries to add to 'sys.path' otherwise)
    > Checks if it can be imported with the new path
    Relies on the 'importlib' library (Python >3.4) or 'pkgutil' (Python 2).
    ARGUMENTS:
        - 'data'    :   a 'Data' object
        - 'f'       :   a directory path
    RETURNS:
        - 0/1 (success-failure)"""
    import sys,os
        
        # Check
        ## the 'data' object overrides 'f'
    if data:
        f = data.p_pack
    elif not f:
        return 1
    if data and data.pack:
        return 0
        # Variables
    pad,pack = os.path.split(f)
        # Last check
    if pack in sys.modules:
        if data:
            data.pack = sys.modules[pack]; data.pname = pack
        return 0
        # For Python 2
    if sys.version_info < (3,4):
        import pkgutil
            # Raw import
        if pkgutil.find_loader(pack):
            module = __import__(pack)
            if data:
                data.pack = module; data.pname = pack
            return 0
            # Again but with adding to 'sys.path'
        if (os.path.isdir(f) and os.access(f,os.R_OK)):
            sys.path.append(pad)
            if pkgutil.find_loader(pack):
                module = __import__(pack)
                if data:
                    data.pack = module; data.pname = pack
                return 0
        return 1
        # For Python >=3.4
    import importlib.util
        # Raw import
    if importlib.util.find_spec(pack):
        module = __import__(pack)
        if data:
            data.pack = module; data.pname = pack
        return 0
        # Again but with adding to 'sys.path'
    if (os.path.isdir(data.pack) and os.access(data.pack,os.R_OK)):
        sys.path.append(pad)
        if importlib.util.find_spec(pack):
            module = __import__(pack)
            if data:
                data.pname = module; data.pname = pack
            return 0
        # All failed
    return 1
def mul_tryImp(data=None,o="",pack=""):
    """Imports a module in the 'conversion_data' package.
    Returns the loaded module (or None if already there)."""

        # Because reasons, we need to detail the pack
    path = pack + "." + o
        # We check with the modules already loaded
        ## If data
    if data:
        if pack.endswith("conversion"): # conversions
            for name in data.conversion:
                if name == o:
                    return None
        elif pack.endswith("interface"): # interface
            for name in data.interface:
                if name == o:
                    return None
        else:
            for name in data.tools: # tools
                if name == o:
                    return None
        ## Else we resort to 'sys'
    else:
        import sys
        for module in sys.modules:
            if module == path:
                return None
    import sys
    return __import__(path,fromlist=[o])
    # Temporary function while waiting for a... cleaner way...
def mul_convert(data=None,in_module=None,out_module=None,
                infiles=[],outfiles=[],**args):
    """To do pure conversions.
    ARGUMENTS:
        input       :   the relevant input module
        output      :   the relevant output module
        infiles     :   the set of files (paths) to process
        outfiles    :   the set of files (paths) to write
    **args is for options but currently, we'll ignore those.
    'data' is simply added for attribute consistency between 'mul' functions."""
    
        # Quick test...
        ## Each 'infile' should have a corresponding 'outfile'
    if not len(infiles) == len(outfiles):
        return
        # Encoding
    inCode = args.get('inCode',"utf-8")
    inSym = mul_strType(args.get('inSym',"['_']"))
    outCode = args.get('outCode',"utf-8")
    outSym = mul_strType(args.get('outSym',"_"))
        # Reloading the modules
        ## It costs nothing and allows us to dynamically edit them
    if sys.version_info < (3,0):
        reload(in_module[1]); reload(out_module[1])
    elif sys.version_info <= (3,3):
        import imp
        imp.reload(in_module[1]); imp.reload(out_module[1])
    else:
        import importlib
        importlib.reload(in_module[1]); importlib.reload(out_module[1])
        # Set the input function
    in_function = getattr(in_module[1],in_module[0])
    out_function = getattr(out_module[1],out_module[0])
    
        # We convert
    for a in range(len(infiles)):
        trans = in_function(infiles[a],encoding=inCode,sym=inSym)
        out_function(outfiles[a],trans,encoding=outCode,sym=outSym)

    # Support class (contains all information)
class Data:
    """Container class to contain all the necessary data."""
    import os
    
    def __init__(self):
            # Process
            ## Current operation
        self.fil = 0                    # current collection
        self.ope = 0                    # current operation
        self.files = {}                 # shared list of files {file : path}
            ## Collections
        o_coll = []                     # list of 'Collection' objects
        c_oper = []                     # list of 'Operation' objects
        
            # Properties
            ## Paths
        self.home = os.getcwd()
            ### Package
        self.p_pack = os.path.join(self.home,"conversion_data")
        self.p_tool = os.path.join(self.p_pack,"tools")
            ### Property file (save)
        self.p_dflt = os.path.join(self.p_pack,             # default
                                   "interface","collection",
                                   "default.txt")
        self.p_prop = self.p_dflt                             # current
            ## Checks
        self.ch_tool = False            # tools status...
            ## Package
        self.pack = None                # package module
        self.pname = ""                 # Eventual name of the package
        self.ptran = None               # 'Transcription' module
        self.conversion = {}            # List of imported modules {name:module}
        self.interface = {}             # List of imported modules {ibidem}
        self.tools = {}                 # List of imported modules {ibidem}


    #### GUI ####
    #############

import sys,os,re
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *

    # Menu
class Menutitool(Menu):
    """Support overloaded class for the menu bar."""
    
    def __init__(self,parent=None):
        Menu.__init__(self)
        self.parent = parent
        menu1 = Menu(self, tearoff=0)
        menu1.add_command(label="Load",
                          command=self.parent.load)
        menu1.add_command(label="Save",
                          command=lambda: self.parent.save(self.parent.data.prop))
        menu1.add_command(label="Save as...",
                          command=self.parent.save)
        menu1.add_separator()
        #menu1.add_command(label="Files collection",
        #                  command=lambda: self.parent.loadPage(1))
        menu1.add_command(label="Properties",
                          command=lambda: self.parent.loadPage(0))
        menu1.add_separator()
        menu1.add_command(label="Quit",command=parent.quit)
        menu2 = Menu(self, tearoff=0)
        menu2.add_separator()
        menu2.add_command(label="New collection")
        menu3 = Menu(self, tearoff=0)
        menu3.add_command(label="Conversion",
                          command=lambda: self.parent.loadPage(2))
        menu3.add_separator()
        menu4 = Menu(self, tearoff=0)
        menu4.add_command(label="About")
        self.add_cascade(label="File", menu=menu1)
        self.add_cascade(label="File manager",menu=menu2)
        self.add_cascade(label="Operations", menu=menu3)
        self.add_cascade(label="Help", menu=menu4)
    
    
    # Support class shared by 'operation' and 'collection'
class FileField(Frame):
    """Manages the files used to operate.
    For now, 'bastardized' to not rely on the 'Collection' class."""
    
    def __init__(self,parent=None,main=None):
        Frame.__init__(self,parent)
        self.main = main
        self.parent = parent
        
            # Variables (from args)
        bg_color = self.main.bg_color
        fr_color = self.main.fr_color
        
            # Setup
        self.config(background=fr_color)
        
            # Elements
            ## Button
        button1 = Button(self,text="Add",command=self.addFiles)
        button1.grid(row=0,column=0,sticky=N+S+W+E,padx=2,pady=2)
        button2 = Button(self,text="Remove",command=self.removeFiles)
        button2.grid(row=0,column=1,columnspan=2,sticky=N+S+W+E,
                     padx=2,pady=2)
            ## List
        self.l_files = Listbox(self,selectmode='extended',
                               activestyle='none')
        self.l_files.grid(row=1,column=0,columnspan=2,sticky=N+S+W+E,pady=2)
        bar = Scrollbar(self); bar.config(command = self.l_files.yview)
        bar.grid(row=1,column=2,sticky=N+S+W+E,pady=2)
        self.l_files.config(yscrollcommand = bar.set)
        
            # Grid
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=2)
        
        self.getFiles()
    
    def testExt(self,ext=""):
        """Dummy function by lack of 'Collection' class."""
        if ext == ".TextGrid":
            return True
        elif ext == ".trs":
            return True
        elif ext == ".exb":
            return True
        elif ext == ".xml":
            return True
        elif ext == ".eaf":
            return True
        elif ext == ".tei":
            return True
        return False
    def addFiles(self):
        """Adds files to the list."""
        l_paths = askopenfilenames(title="Add files:")
            # Because tkinter is...
        for f_path in l_paths:
            if not os.path.isfile(f_path):
                continue
            file = os.path.basename(f_path)
            if self.testExt(os.path.splitext(file)[1]):
                self.main.data.files[file] = f_path
        """ # If the user chooses a directory
        if os.path.isdir(path):
            for file in os.path.listdir(path):
                if self.testExt(os.path.splitext(file)[1]):
                    self.main.data.files[file] = os.path.join(path,file)
            # Else it's a single file
        elif os.path.isfile(path):
            if self.testExt(os.path.splitext(file)[1]):
                self.main.data.files[file] = os.path.join(path,file)"""
            # We update the list
        self.getFiles()
    def removeFiles(self):
        """Removes files from the list."""
        l_files = []
        for index in self.l_files.curselection():
            l_files.append(self.l_files.get(index))
        if not l_files:
            return
        for file in l_files:
            self.main.data.files.pop(file)
        self.getFiles()
    def getFiles(self):
        """Simply copies the 'files' list from 'Data'."""
        self.l_files.delete(0, 'end')
        for file in self.main.data.files:
            self.l_files.insert('end',file)

    # Support classes for the 'properties' page
class ProField(Frame):
    """Support support class for 'Propertitool'."""
    
    def __init__(self,parent=None,main=None):
        Frame.__init__(self,parent)
        self.main = main
        self.parent = parent
            # Variables (Entry fields)
        prod,prop = os.path.split(self.main.data.p_prop)
        pad,pack = os.path.split(self.main.data.p_pack)
        self.prop = StringVar(); self.prop.set(prop)
        self.prod = StringVar(); self.prod.set(prod)
        self.pack = StringVar(); self.pack.set(pack)
        self.pad = StringVar(); self.pad.set(pad)
            # Variables (from args)
        bg_color = self.main.bg_color
        fr_color = self.main.fr_color
        
            # Setup
        self.config(background=fr_color)
        
            # Elements
            ## Technicals
        tech = Frame(self)
        tech.grid(row=0,sticky=W+E,padx=2,pady=2)
            ### Label
        label00 = Label(tech,text="Technicals",anchor=W)
        label00.config(background=fr_color)
        label00.grid(row=0,column=0,columnspan=4,sticky=W+E)
            ### 'Property file'
        label1 = Label(tech,text="Property file:",anchor=W)
        label1.grid(row=1,column=0,sticky=W+E,pady=2)
        button1 = Button(tech,text="...",command=self.main.load)
        button1.config(width=2)
        button1.grid(row=1,column=1,pady=2)
        entry1 = Entry(tech,textvariable=self.prod,state="readonly")
        entry1.grid(row=1,column=2,sticky=W+E,padx=2,pady=2)
        entry10 = Entry(tech,textvariable=self.prop,state="readonly")
        entry10.grid(row=1,column=3,sticky=W+E,padx=2,pady=2)
            ### 'Package folder'
        label2 = Label(tech,text="Package folder:",anchor=W)
        label2.grid(row=2,column=0,sticky=W+E,pady=2)
        button2 = Button(tech,text="...",command=self.loadPack)
        button2.config(width=2)
        button2.grid(row=2,column=1,pady=2)
        if self.main.data.pack:
            button2.config(state=DISABLED)
        entry2 = Entry(tech,textvariable=self.pad,state="readonly")
        entry2.grid(row=2,column=2,sticky=W+E,padx=2,pady=2)
        entry20 = Entry(tech,textvariable=self.pack,state="readonly")
        entry20.grid(row=2,column=3,sticky=W+E,padx=2,pady=2)
            ## Interface
        ui = Frame(self)
        ui.grid(row=1,sticky=W+E,padx=2,pady=2)
            ### Label
        label01 = Label(ui,text="Interface",anchor=W)
        label01.config(background=fr_color)
        label01.grid(row=0,column=0,columnspan=3,sticky=W+E)
        
            # Grid
            ## Main
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(2,weight=1)
            ## tech
        tech.grid_columnconfigure(2,weight=5)
        tech.grid_columnconfigure(3,weight=1)
            ## ui
        ui.grid_columnconfigure(2,weight=1)

    def loadPack(self):
        """Loads a new package folder."""
        
            # Variables
        f = ""; pad,pack = os.path.split(self.main.data.pack)
        if not os.path.isdir(pad):
            pad = self.main.data.home; pack = "conversion_data"
            # Filedialog
        while not os.path.isdir(f):
            f = ""
            f = askdirectory(initialdir=pad,initialfile=pack,
                             title="Select the package folder:")
            # We check our property file
        prop = os.path.join(self.prod.get(),self.prop.get())
        if os.path.isfile(prop):
            prop = self.prod.get()
        else:
            prop = ""
            # We load
        self.main.loadPack(f,prop)
class SavField(Frame):
    """Support support class for 'Propertitool'."""
    
    def __init__(self,parent=None,main=None):
        Frame.__init__(self,parent)
        self.main = main
        self.parent = parent
            # Variables (from args)
        bg_color = self.main.bg_color
        fr_color = self.main.fr_color
        
            # Setup
        self.config(background=fr_color)
        
            # Elements
        load = Button(self,text='Load',command=self.main.load)
        load.grid(row=0,column=1,sticky=N+S+W+E,padx=2,pady=2)
        save = Button(self,text='Save',
                      command=lambda: self.main.save(self.main.data.prop))
        save.grid(row=0,column=2,sticky=N+S+W+E,padx=2,pady=2)
        svas = Button(self,text='Save as...',command=self.main.save)
        svas.grid(row=0,column=3,sticky=N+S+W+E,padx=2,pady=2)
        file = Button(self,text='Files'); file.config(state='disabled')
                      #command=lambda: self.main.loadPage(1))
        file.grid(row=0,column=4,sticky=N+S+W+E,padx=2,pady=2)
        oper = Button(self,text='Task',
                      command=lambda: self.main.loadPage(2))
        oper.grid(row=0,column=5,sticky=N+S+W+E,padx=2,pady=2)
        quit = Button(self,text='QUIT',command=self.main.quit)
        quit.grid(row=0,column=6,sticky=N+S+W+E,padx=2,pady=2)
        
            # Grid
        tuple = self.grid_size()
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
    # 'Properties' page
class Propertitool(Frame):
    """Support overloaded class for the 'properties' page."""
    
    def __init__(self,parent=None,**args):
        Frame.__init__(self,parent)
        self.parent = parent
            # Variables (from args)
        bg_color = self.parent.bg_color
        fr_color = self.parent.fr_color
        
            # Setup
        self.config(background=bg_color)
        
            # Elements
            ## Label
        label = Label(self,text="Properties")
        label.grid(row=0,sticky=N+S+W+E)
        if not self.parent.data.pack:
            label.text = "Properties\n/!\ No package path!"
            ## property fields
        self.proField = ProField(self,self.parent)
        self.proField.grid(row=1,sticky=N+S+W+E,padx=2,pady=2)
            ## save field
        self.saveField = SavField(self,self.parent)
        self.saveField.grid(row=2,sticky=N+S+W+E,padx=2,pady=2)
        
            # Grid
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=98)
        self.grid_rowconfigure(2,weight=1)
    
    # Support classes for the 'operation' page
class SpecField(Canvas):
    """Support support class for 'Operitool'."""
    
    def __init__(self,parent=None,main=None):
        Canvas.__init__(self,parent)
        self.main = main
        self.parent = parent
        
            # Variables
        bg_color = self.main.bg_color
        fr_color = self.main.fr_color
            # Variables (lists of formats)
        input,output = self.getFormats()
        
            # Setup
        self.config(background=fr_color)
        
            # Elements
        """Note: if tabs are implemented (ttk.Notebook), this will become
        a tab. For now, only 'conversion' is available so..."""
            ## Label
        label = Label(self,text="Conversion",anchor=W)
        label.grid(row=0,column=0,columnspan=3,sticky=N+S+W+E,padx=2,pady=2)
            ## Main conversion options
            ### Input format
        self.input = ttk.Combobox(self,values=input); #self.input.current(0)
        self.input.grid(row=2,column=0,sticky=N+S+W+E,padx=4,pady=4)
        self.input.config(state="readonly")
        if self.input['values']:
            self.input.current(0)
            ### Output format
        self.output = ttk.Combobox(self,values=output)
        self.output.grid(row=2,column=1,columnspan=2,
                         sticky=N+S+W+E,padx=4,pady=4)
        self.output.config(state="readonly"); #self.output.current(0)
        if self.output['values']:
            self.output.current(0)
            ## Input options
        inframe = Frame(self)
        inframe.grid(row=3,column=0,sticky=N+S+W+E,padx=2,pady=2)
            ## Output options
        outframe = Frame(self)
        outframe.grid(row=3,column=1,columnspan=2,sticky=N+S+W+E,padx=2,pady=2)
            ## Writing
        writeframe = Frame(self)
        writeframe.grid(row=4,column=0,columnspan=3,
                        sticky=N+S+W+E,padx=2,pady=2)
            ## 'Console'
        self.console = Text(self)
        self.console.grid(row=5,column=0,columnspan=2,
                          sticky=N+S+W+E,padx=4,pady=4)
        text = ("Converts the selected files from one of the input formats "+
                "to one of the output formats. Output names and folder "+
                "are options.")
        self.console.insert('end',text)
        bar = Scrollbar(self); bar.config(command = self.console.yview)
        bar.grid(row=5,column=2,sticky=N+S+W+E,padx=2,pady=2)
        self.console.config(yscrollcommand = bar.set)
        
            # Inframe elements
            ## Label
        inlabel = Label(inframe,text="Input options")
        inlabel.grid(row=0,column=0,columnspan=2,sticky=N+S+W+E,padx=2,pady=2)
            ## Encoding field
        inlabel1 = Label(inframe,text="Encoding:",anchor=W)
        inlabel1.grid(row=1,column=0,sticky=N+S+W+E,padx=2,pady=2)
        self.inCode = StringVar(); self.inCode.set("utf-8")
        inCode = Entry(inframe,textvariable=self.inCode)
        inCode.grid(row=1,column=1,sticky=W+E,padx=2,pady=2)
            ### Symbol field
        inlabel2 = Label(inframe,text="Empty segment:",anchor=W)
        inlabel2.grid(row=2,column=0,sticky=N+S+W+E,padx=2,pady=2)
        self.inSym = StringVar(); self.inSym.set("['_']")
        inSym = Entry(inframe,textvariable=self.inSym)
        inSym.grid(row=2,column=1,sticky=W+E,padx=2,pady=2)
            # Outframe elements
            ## Label
        outlabel = Label(outframe,text="Output options")
        outlabel.grid(row=0,column=0,columnspan=2,sticky=N+S+W+E,padx=2,pady=2)
            ## Encoding field
        outlabel1 = Label(outframe,text="Encoding:",anchor=W)
        outlabel1.grid(row=1,column=0,sticky=N+S+W+E,padx=2,pady=2)
        self.outCode = StringVar(); self.outCode.set("utf-8")
        outCode = Entry(outframe,textvariable=self.outCode)
        outCode.grid(row=1,column=1,sticky=W+E,padx=2,pady=2)
            ### Symbol field
        outlabel2 = Label(outframe,text="Empty segment:",anchor=W)
        outlabel2.grid(row=2,column=0,sticky=N+S+W+E,padx=2,pady=2)
        self.outSym = StringVar(); self.outSym.set("_")
        outSym = Entry(outframe,textvariable=self.outSym)
        outSym.grid(row=2,column=1,sticky=W+E,padx=2,pady=2)
            # Writeframe elements
            ## Label
        wrlabel = Label(writeframe,text="Writing options")
        wrlabel.grid(row=0,column=0,columnspan=5,sticky=N+S+W+E,padx=2,pady=2)
            ## File name
        wrlabel1 = Label(writeframe,text="File name:",anchor=W)
        wrlabel1.grid(row=1,column=0,columnspan=2,
                      sticky=N+S+W+E,padx=2,pady=2)
        self.preName = Entry(writeframe)
        self.preName.grid(row=1,column=2,sticky=N+S+W+E,padx=2,pady=2)
        wr1 = StringVar(); wr1.set("Name")
        wrentry1 = Entry(writeframe,textvariable=wr1,state="readonly")
        wrentry1.grid(row=1,column=3,sticky=N+S+W+E,padx=2,pady=2)
        self.suName = Entry(writeframe)
        self.suName.grid(row=1,column=4,sticky=N+S+W+E,padx=2,pady=2)
            ## Folder
        wrlabel2 = Label(writeframe,text="Output folder:",anchor=W)
        wrlabel2.grid(row=2,column=0,sticky=N+S+W+E,padx=2,pady=2)
        wrbutton1 = Button(writeframe,text="...",command=self.getFolder)
        wrbutton1.grid(row=2,column=1,pady=2); wrbutton1.config(width=2)
        self.folder = StringVar(); self.folder.set(self.main.data.home)
        fentry = Entry(writeframe,textvariable=self.folder,state="readonly")
        fentry.grid(row=2,column=2,columnspan=3,sticky=W+E,padx=2,pady=2)
            ## Execution
        apply = Button(writeframe,text="Conversion",command=self.convert)
        apply.grid(row=3,column=0,columnspan=5,sticky=W+E,padx=2,pady=2)
        
            # Grid
            ## Self
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=3)
        self.grid_rowconfigure(5,weight=1)
            ## Inframe
        inframe.grid_columnconfigure(1,weight=1)
            ## Outframe
        outframe.grid_columnconfigure(1,weight=1)
            ## Writeframe
        writeframe.grid_columnconfigure(2,weight=1)
        writeframe.grid_columnconfigure(4,weight=1)
        
    def getFormats(self):
        """Retrieves the conversion formats from 'Data'.
        Returns two lists 'from' and 'to'."""
        
        l_from = []; l_to = []
        for op in self.main.data.conversion:
            if op.startswith("from"):
                l_from.append(op)
            elif op.startswith("to"):
                l_to.append(op)
        return (l_from,l_to)
    def getFolder(self):
        """Chooses the folder for the converted files."""
        
        folder = askdirectory(title="Output folder:")
        if os.path.isdir(folder):
            self.folder.set(folder)
    def getExt(self,func=""):
        """Dummy function while waiting for better days..."""
        if not func:
            return ""
        elif func == "toElan":
            return ".eaf"
        elif func == "toPangloss":
            return ".xml"
        elif func == "toTEI":
            return ".tei"
        elif func == "toPraat":
            return ".TextGrid"
        elif func == "toExmaralda":
            return ".exb"
        else:
            return ""
    def convert(self):
        """Calls the conversion scripts for the user.
        Eventually, a 'tab' will only send the info, 
        and 'SpecField', 'Operitool' or 'Screentitool' will operate."""
        
        # We get the modules
        out = self.output.get()
        input = (self.input.get(), self.main.data.conversion[self.input.get()])
        output = (self.output.get(),
                  self.main.data.conversion[out])
            # We get the files (input)
        infiles = []; temp = []
        for index in self.parent.fField.l_files.curselection():
            temp.append(self.parent.fField.l_files.get(index))
        if not temp:
            temp = self.main.data.files
        for file in temp:
            infiles.append(self.main.data.files[file])
            # We get the folder
            ## We actually want a list of output files
        outfiles = []; folder = self.folder.get()
        preName = self.preName.get(); suName = self.suName.get()
        ext = self.getExt(out)
        if not folder:
            folder = self.main.data.home
        for file in temp:
            file = os.path.splitext(file)[0]
            file = preName + file + suName + ext
            outfiles.append(os.path.join(folder,file))
            # We get aaaall the options
        args = {}
        inCode = self.inCode.get()
        if inCode:
            args['inCode'] = inCode
        inSym = mul_strType(self.inSym.get())
        if inSym:
            args['inSym'] = inSym
        outCode = self.outCode.get()
        if outCode:
            args['outCode'] = outCode
        outSym = mul_strType(self.outSym.get())
        if outSym:
            args['outSym'] = outSym
            # We convert
            ## The interface only gathers information
            ## The actual operation is externalized
        mul_convert(self.main.data,input,output,infiles,outfiles,**args)
        
    # 'Operation' page
class Operitool(Frame):
    """Support overloaded class for the 'operation' page."""
    
    def __init__(self,parent=None):
        Frame.__init__(self,parent)
        self.parent = parent
            # Variables (from args)
        bg_color = self.parent.bg_color
        fr_color = self.parent.fr_color
    
            # Setup
        self.config(background=bg_color)
            
            # Elements
            ## Label
        label = Label(self,text="Operations")
        label.grid(row=0,column=0,columnspan=2,sticky=N+S+W+E)
            ## Files field
        self.fField = FileField(self,self.parent)
        self.fField.grid(row=1,column=0,sticky=N+S+W+E,padx=2,pady=2)
            ## Specifics field
        self.sField = SpecField(self,self.parent)
        self.sField.grid(row=1,column=1,rowspan=2,sticky=N+S+W+E,
                         padx=2,pady=2)
        
            # Grid
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
    
    #### MainWindow ####
    ####################
class Screentitool(Tk):
    """Overloaded class to build the main window."""
    
    def __init__(self):
        Tk.__init__(self)
        self.title("Multitool")
        self.minsize(240,0)
            # Variables
            ## Interface
        self.page = None                # page displayed
        self.type = -1                  # type of page displayed
            ## Data
        self.data = Data()              # Contains all data (package, files, etc)
            ## Theme
        self.bg_color = "#ffffff"
        self.fr_color = "#dddddd"
        
            # Set the menu bar
        self.config(menu=Menutitool(self))
            # Check the package
            ## Load the scripts if possible
        if self.loadPack(self.data.p_pack) == 0:
            self.loadOper("conversion")
            self.loadOper("interface")
        self.loadPage(self.type)

    def loadOper(self,o=""):
        """Seeks to load a new operation."""
        
            # From files
            ## If for conversion
        if o == "conversion":
            if self.data.conversion: # It should only be done once
                self.data.ope = 0; return
            folder = os.path.join(self.data.p_pack,"conversion")
            pack = self.data.pname+".conversion"
            for file in os.listdir(folder):
                if not file.endswith(".py"):
                    continue
                file = file.rsplit(".",1)[0]
                if (file.startswith("from") or file.startswith("to")):
                    module = mul_tryImp(self.data,file,pack) # import
                    self.data.conversion[file] = module
                elif file == "Transcription":
                    self.data.ptran = mul_tryImp(self.data,file,pack)
            self.data.ope = 0; return
        if o == "interface":
            pack = self.data.pname+".interface"
            for file in dir(pack):
                continue # For now we ignore the interface
            return
            ## Else for tools
        l_ch = self.data.tools.keys()
        if o not in l_ch: # Loading 'tools' script
            module = mul_tryImp(self.data,o,self.data.pname+".tools") # import
            self.data.tools.append(module); self.data.ope = len(self.data.tools)
        else: # Operation selection
            self.data.ope = l_ch.index(o)
    def loadPack(self,f=""):
        """Loads the package.
        'f' is the package path. Mostly used to check the path's validity.
        Returns 0/1 (success-failure)."""
        
        self.data.p_pack = f
            # We need a path
        if not f or not os.path.isdir(f):
            self.type = 0; self.loadPage(self.type); return 1
            # We import
        check = mul_imPackage(self.data)
        if check == 0:
            if self.type < 0:
                self.type = 2
        else:
            self.type = 0
        return 0
    def load(self,f="",**args):
        """Loads a property file (save)."""
        
            # encoding
        encoding = args.get('encoding',"utf-8")
            # We need a valid properties file
        prod,prop = os.path.split(self.data.p_prop)
        if not os.path.isdir(prod):
            prod = self.data.home
        while not os.path.isfile(f):
            f = ""
            f = askopenfilename(initialdir=prod,initialfile=prop,
                                title="Load property file:",
                                filetypes=(("text files","*.txt"),
                                           ("all files","*.*")))
            if not f:
                return 1
            # We load
            # We might not have a package file
        mul_load(self.data,f,encoding=encoding)
        if self.type < 0:
            self.type = 0
        loadPage(self.type)

        return 0
    def save(self,f="",**args):
        """Saves the current properties file."""
        
            # encoding
        encoding = args.get('encoding',"utf-8")
            # Saveas?
        if not f:
            fd=""; prod,prop = os.path.split(self.data.prop)
            if not os.path.isdir(prod):
                prod = self.data.home
            while not os.path.isdir(fd):
                f = ""
                f = asksaveasfilename(initialdir=prod,initialfile=prop,
                                      title="Choose a file name:",
                                      defaultextension=".txt",
                                      filetypes=(("text files",".txt"),
                                                 ("all files",".")))
                if not f:
                    return 1
                fd = os.path.dirname(f)
        save(self.data,f,encoding=encoding)
        if self.page and self.page.type == 0:
            prod,prop = os.path.split(self.prop)
            self.page.proField.prop.set(prop)
            self.page.proField.prod.set(prod)
        return 0
    def loadPage(self,type=2):
        """Deletes the previous page and loads a new one."""
            # Tries hard to delete the old page
        if self.page:
            self.page.pack_forget()
            self.page.destroy()
            # Loads the new page on demand
        if type == 0:
            self.page = Propertitool(self)
        #elif type == 1:
        #    self.page = Collectitool(self)
        elif type == 2:
            self.page = Operitool(self)
        self.page.pack(fill='both',expand=True)


if __name__ == "__main__":
    """Creates the interface."""
    import sys,os,re
    
        # We will need to deal with packages...
    if sys.version_info >= (3,0):
        if sys.version_info < (3,4):
            import imp, pkgutil
        else:
            import importlib,importlib.util
            importlib.invalidate_caches()
    else:
        import pkgutil
    
    mainWindow = Screentitool()
    mainWindow.mainloop()
