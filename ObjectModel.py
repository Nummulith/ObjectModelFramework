import xml.etree.ElementTree as ET

import os

from Drawing import Drawing, ItemView

from xml.dom import minidom

IdDv = "|"

#Fields
fType  = 0
fOwner = 1
fLName = 2
fLItem = 3
fId    = 4
fView  = 5
fExt   = 6
fIcon  = 7
fOut   = 8
fIn    = 9

#Draw
dView = 1 #0
dExt  = 2 #1
dIcon = 4 #2
dId   = 8 #3

dAll  = dView + dExt + dIcon + dId
dDef  = dAll - dExt

def prettify(elem):
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def structure_to_xml(data, element = None):
    isroot = element == None
    if isroot:
        element = ET.Element('root')

    if isinstance(data, list):
        for item in data:
            sub_element = ET.SubElement(element, "list_item")
            structure_to_xml(item, sub_element)
    elif isinstance(data, dict):
        for key, value in data.items():
            sub_element = ET.SubElement(element, key)
            structure_to_xml(value, sub_element)
    else:
        element.text = str(data)

    if isroot:
        return ET.ElementTree(element)

    return element

def PlainQuery(tree, path, pref = "/", res = [], parfields = None):
    this, _, next = path.partition("/")
    result = tree.findall(pref + this)

    for item in result:
        fields = {} if parfields == None else parfields.copy()
        
        for child in item:
            fields[child.tag] = child.text

        if next:
            PlainQuery(item, next, "./", res, fields)
        else:
            res.append(fields)
    
    return res


class ObjectModelItem:
    Icon = ""
    Show = True
    Draw = dDef
    Color = "#A9DFBF"

    def __init__(self, model, IdQuery, Index, resp, DoAutoSave=True):
        if IdQuery != None:
            par_id, _, cur_id = IdQuery.rpartition(IdDv)
            if par_id != "":
                setattr(self, "ParentId", par_id)

        if hasattr(self, "Index"):
            setattr(self, "Index", Index)

        fields = type(self).Fields()

        key = self.FieldOfAKind(fId) # process Id first
        if key != None and key in resp:
            setattr(self, key, resp[key])

        for key, value in resp.items():
            if key in fields:
                cfg = fields[key]
            else:
                cfg = type(value)

            fieldtype = cfg[fType] if isinstance(cfg, tuple) else cfg
            
            if type(fieldtype) == list:
                if len(fieldtype) == 0:
                    continue
                if fieldtype[0] == str:
                    continue
                else:
                    model[fieldtype[0]].Fetch(f"{self.GetId()}{IdDv}*", value, DoAutoSave)
            elif fieldtype == list:
                continue
            elif type(fieldtype) == dict:
                tkkey, tkval = next(iter(fieldtype.items()))
                for pair in value:
                    setattr(self, "Tag_" + pair[tkkey], pair[tkval])
                continue
            else:
                setattr(self, key, value)
        
    def FieldsOfAKind(self, kind):
        return (key for key, value in self.Fields().items() if isinstance(value, tuple) and value[1] == kind)
    
    def FieldOfAKind(self, kind):
        return next(self.FieldsOfAKind(kind), None)

    def ValueOfAKind(self, kind):
        field = self.FieldOfAKind(kind)
        return getattr(self, field, None)

    def GetObject(self, model, field):
        if field == None: return None

        id = getattr(self, field, None)
        if id == None: return None

        clss = self.Fields()[field][fType]

        if not id in model[clss].Map : return None
        obj = model[clss].Map[id]
        return obj

    def ObjectOfAKind(self, model, kind):
        field = self.FieldOfAKind(kind)
        return self.GetObject(model, field)

    def GetLink(self, model):
        lister = self.ObjectOfAKind(model, fLItem)
        if lister != None:
            listname = self.ValueOfAKind(fLName)
            return f"{lister.GetId()}-{listname}:{self.GetId()}"

        return self.GetId()

    def GetId(self):
        field = self.FieldOfAKind(fId)
        if field != None and hasattr(self, field): return getattr(self, field)

        return f"{getattr(self, 'ParentId', '?')}{IdDv}{getattr(self, 'Index', '?')}"

    def GetView(self):
        field = self.FieldOfAKind(fView)
        if field != None and hasattr(self, field): return getattr(self, field)

        return f"{getattr(self, 'Tag_Name', self.GetId())}"

    def GetExt(self):
        field = self.FieldOfAKind(fExt)
        if field != None and hasattr(self, field): return getattr(self, field)

        return ""

    def GetIcon(self):
        field = self.FieldOfAKind(fIcon)
        if field != None and hasattr(self, field): return getattr(self, field)

        return ""

    @classmethod
    def GetObjectsByIndex(clss, id, ListField, FilterField):
        sg_id = None; ip_n = None
        if id != None:
            sg_id, _, ip_n = id.rpartition(IdDv)

        pars = clss.GetObjects(sg_id)

        res = []
        for par in pars:
            index = -1
            for permission in par[ListField]:
                index += 1

                if ip_n != None and ip_n != "" and ip_n != "*":
                    if ip_n != (str(index) if FilterField == int else str(permission[FilterField])):
                        continue

                res.append(permission)

        return res

    @classmethod
    def Query(clss, query):
        data_structure = clss.GetObjects()

        xml_tree = structure_to_xml(data_structure)

        with open("Query.xml", "w", encoding="utf-8") as file: file.write(prettify(xml_tree.getroot()))

        reslist = PlainQuery(xml_tree, query)

        resdict = {}
        for idx, d in enumerate(reslist):
            for key, value in d.items():
                if key not in resdict:
                    resdict[key] = [None] * len(reslist)
                resdict[key][idx] = value

        return resdict


    @staticmethod
    def GetObjects(id=None):
        return None

    
    @staticmethod
    def Fields():
        return {}

    @staticmethod
    def CLIAdd(args = None):
        return "<?>"

    @staticmethod
    def CLIDel(args = None):
        return "<?>"

    @classmethod
    def GetClassView(cls):
        return cls.__name__[1:]


class ObjectList:
    def __init__(self, model, clss):
        self.Model = model
        self.Class = clss
        self.Map = {}

    def __getitem__(self, key):
        return self.Map[key]

    def __setitem__(self, key, value):
        self.Map[key] = value

    def Count(self):
        return len(self.Map)

    def View(self):
        return self.Class.GetClassView()
    
    def Release(self, IdQuery = None, DoAutoSave = True):
        if IdQuery != None:
            del self.Map[IdQuery]
        else:
            self.Map.clear()

        if DoAutoSave:
            self.Model.AutoSave()

    def Fetch(self, IdQuery = None, resp = None, DoAutoSave = True):
        if resp == None:
            try:
                resp = self.Class.GetObjects(IdQuery)
            except Exception as e:
                ErrorCode = e.response['Error']['Code']
                print(f"{self.Class.GetClassView()}.GetObjects: {e.args[0]}")
                # if ErrorCode[-9:] == '.NotFound' or ErrorCode == "AccessDenied":
                #     return
                # else:
                #     raise
                return

        sg_id = ""; ip_n = "*"
        if IdQuery != None:
            sg_id, _, ip_n = IdQuery.rpartition(IdDv)
            
        Index = -1
        for el in resp:
            Index += 1
            ip_nn = ip_n
            if ip_nn == "*":
                ip_nn = int(Index)

            obj = self.Class(self.Model, f"{sg_id}{IdDv}{ip_nn}", Index, el, DoAutoSave)
            self.Map[obj.GetId()] = obj

        if DoAutoSave:
            self.Model.AutoSave()


    def Create(self, *args):
        try:
            id = self.Class.Create(*args)
        except Exception as e:
            print(f"{self.View()}.Create: An exception occurred: {type(e).__name__} - {e}")
            return None

        self.Fetch(id)

        return id

    def DeleteInner(self, args):
        try:
            self.Class.Delete(*args)
        except Exception as e:
            print(f"{self.View()}.Delete: An exception occurred: {type(e).__name__} - {e}")
            return

        id = args[0]
        if id in self.Map:
            del self.Map[id]
            self.Model.AutoSave()

    def Delete(self, *args):
        self.DeleteInner(args)

    def DeleteAll(self):
        keys_to_delete = list(self.Map.keys())
        index = len(keys_to_delete) - 1
        while index >= 0:
            id = keys_to_delete[index]
            self.DeleteInner((id,), True)
            index -= 1

    def Print(self):
        if len(self.Map) == 0 : return

        print(f"  {self.View()}: {len(self.Map)}")
        for id, obj in self.Map:
            print(f"{id}: {obj}")

def NodeLabel(obj):
    draw  = type(obj).Draw
    color = type(obj).Color

    res = ""
    if draw & dView: res = res + f'''
        <TR>
            <TD BGCOLOR="{color}" PORT="p0"><B>{obj.GetView()}</B></TD>
        </TR>
    '''
    if draw & dExt : res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p1"><B>{obj.GetExt()}</B></TD>
        </TR>
    '''
    if draw & dIcon: res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p2"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
        </TR>
    '''
    res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p4"><FONT POINT-SIZE="7.0">{obj.GetClassView()}</FONT></TD>
        </TR>
    '''
    if draw & dId  : res = res + f'''
        <TR>
            <TD BGCOLOR="{color}" PORT="p3"><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
        </TR>
    '''
    if res == "":
        res = res + f'''
        <TR>
            <TD BGCOLOR="{color}" PORT="p0"><B>{obj.GetId()}</B></TD>
        </TR>
    '''

    return f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        {res}
        </TABLE>
    >'''

def ClusterLabel(obj):
    draw = obj.Draw

    res0 = ""
    if draw & dIcon: res0 = res0 + f'''
        <TD ROWSPAN="3"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
    '''
        
    if draw & dView: res0 = res0 + f'''
        <TD><B>{obj.GetView()}</B></TD>
    '''
        
    if res0 != "":
        res0 = f'''
    <TR>
        {res0}
    </TR>
    '''

    res1 = ""
    if draw & dExt: res1 = res1 + f'''
    <TR>
        <TD><FONT POINT-SIZE="7.0">{obj.GetExt()}</FONT></TD>
    </TR>
    '''
        
    res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="7.0">{obj.GetClassView()}</FONT></TD>
        </TR>
        '''

    if draw & dId: res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
        </TR>
        '''

    if res0 == "" and res1 == "":
        res0 = res0 + f'''
        <TR>
            <TD PORT="p0"><B>{obj.GetId()}</B></TD>
        </TR>
    '''

    return f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            {res0}
            {res1}
        </TABLE>
    >'''

class ObjectModel:

    # def ClassesList():
    #     # Get all classes defined in the module
    #     classes = [obj for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)]

    #     # Return the list of class names
    #     return [cls.__name__ for cls in classes]

    # # Print the list of classes in the module
    # print("List of classes in the module:", ClassesList())

    def __init__(self, path, DoAutoLoad, DoAutoSave, Const, Classes):
        self.Path = path
        self.DoAutoLoad = DoAutoLoad
        self.DoAutoSave = DoAutoSave

        ObjectModel.Const = Const
        ObjectModel.Classes = Classes

        ObjectModel.Classes["ALL"] = []
        for key, clsss in ObjectModel.Classes.items():
            if key == "ALL": continue
            ObjectModel.Classes["ALL"] += clsss

        for clss in ObjectModel.Classes["ALL"]:
            wrapper = ObjectList(self, clss)
            name = wrapper.View()
            setattr(self, name, wrapper)

        self.AutoLoad()


    def __getitem__(self, clss):
        key = clss.GetClassView()
        return getattr(self, key)

    def __setitem__(self, clss, wrap):
        key = clss.GetClassView()
        setattr(self, key, wrap)

    def DeleteAll(self, clssList = None):
        clsss = self.StringToClasses(clssList)

        for clss in reversed(clsss):
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.DeleteAll()
    
    def Print(self, clssList = None):
        clsss = self.StringToClasses(clssList)

        for clss in clsss:
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.Print()


    def Load(self):
        if not os.path.exists(self.Path + ".xml"): return
             
        with open(self.Path + ".xml", 'r') as file:
            xml_string = file.read()
        root = ET.fromstring(xml_string)

        for element in root:
            wrapper = getattr(self, element.tag)
            for child in element:
                id = child.text
                wrapper.Fetch(id, None, False)

    def AutoLoad(self):
        if self.DoAutoLoad:
            self.Load()

    def Save(self):
        root = ET.Element("root")

        for clss in ObjectModel.Classes["ALL"]:
            name = clss.GetClassView()
            wrapper = getattr(self, name)

            category_element = ET.SubElement(root, name)
            for id, obj in wrapper.Map.items():
                id_element = ET.SubElement(category_element, f"id")
                id_element.text = str(id)


        tree = prettify(root)
        with open(self.Path + ".xml", "w") as file:
            file.write(tree)

    def AutoSave(self):
        if self.DoAutoSave:
            self.Save()

    def StringToClasses(self, clssList = None):
        clsss = clssList

        if clsss == None: clsss = "ALL"

        if hasattr(self, clsss):
            clsss = [getattr(self, clsss).Class]

        if type(clsss) == str:
            clsss = ObjectModel.Classes[clsss]
        
        return clsss

    def Fetch(self, clssList = None):
        clsss = self.StringToClasses(clssList)

        for clss in clsss:
            if getattr(clss, "DontFetch", False): continue
            self[clss].Fetch()

    def Release(self, clssList = None):
        clsss = self.StringToClasses(clssList)

        if type(clsss) == str:
            clsss = ObjectModel.Classes[clsss]

        for clss in clsss:
            self[clss].Release()

    def Draw(self, clssList = None):
        clsss = self.StringToClasses(clssList)
        drawing = Drawing()

        hasowned  = {}; isowned  = {}
        haslisted = {}; islisted = {}
        for clss in clsss:
            wrap = self[clss]

            for id, obj in wrap.Map.items():
                owner = obj.ObjectOfAKind(self, fOwner)
                if owner != None:
                    isowned[obj] = owner
                    hasowned[owner] = True
                
                listitemfield = obj.FieldOfAKind(fLItem)
                if listitemfield != None and hasattr(obj, listitemfield):
                    listitem = getattr(obj, listitemfield)

                    islisted[obj] = listitem

                    listname = getattr(obj, obj.FieldOfAKind(fLName), "List")

                    if not listitem in haslisted: haslisted[listitem] = {}
                    if not listname in haslisted[listitem]: haslisted[listitem][listname] = []

                    haslisted[listitem][listname].append(obj)


        for clss in clsss:
            wrap = self[clss]
            if not clss in clsss: continue

            for id, obj in wrap.Map.items():
                if obj in hasowned or id in haslisted:
                    drawing.AddItem(id,
                        cluster = ItemView(ClusterLabel(obj), style = 'filled', fillcolor = type(obj).Color),
                        point   = ItemView("", shape='point', width='0.1')
                    )
                elif obj in islisted:
                    pass
                else:
                    drawing.AddItem(id, ItemView(NodeLabel(obj), shape='plaintext'))

                par = isowned[obj] if obj in isowned else None
                if par != None:
                    drawing.AddParent(id, par.GetId())

                if id in haslisted:
                    for listname, listitems in haslisted[id].items():
                        # break

                        label = f'<TR><TD BGCOLOR="#A9DFBF"><B>{listname}</B></TD></TR>\n'
                        for listitem in listitems:
                            label += f'<TR><TD BGCOLOR="white" PORT="{listitem.GetId()}"><FONT POINT-SIZE="7.0">{listitem.GetView()}</FONT></TD></TR>\n'

                        label = f'''<
                            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                            {label}
                            </TABLE>
                        >'''

                        drawing.AddItem  (id + "-" + listname, ItemView(label, shape='plaintext'))
                        drawing.AddParent(id + "-" + listname, id)


                idlink = obj.GetLink(self)

                for field in obj.FieldsOfAKind(fOut):
                    # corr = getattr(obj, field, None)
                    # if corr == None: continue
                    # drawing.AddLink(idlink, corr, field)
                    corr = obj.GetObject(self, field)
                    if corr == None: continue
                    drawing.AddLink(idlink, corr.GetLink(self), field)

                for field in obj.FieldsOfAKind(fIn):
                    # corr = getattr(obj, field, None)
                    # if corr == None: continue
                    # drawing.AddLink(corr, idlink, field + "<")
                    corr = obj.GetObject(self, field)
                    if corr == None: continue
                    drawing.AddLink(corr.GetLink(self), idlink, field + "<")


#        drawing.print()
        drawing.Draw(self.Path)
