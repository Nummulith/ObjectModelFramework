"""
Object Model Module

This module facilitates the management and manipulation of a set of classes representing
  an object model. It takes a parameter, a set of classes, and provides several features
  to interact with and analyze the object model.

Features:
- Fetching Structure: Retrieve the hierarchical structure of objects
    and their relationships within the model.
- Object Properties: Obtain detailed information about the properties
    and attributes of individual objects in the model.
- Object Creation and Deletion: Perform operations to create and delete
    objects within the model.
- Drawing Object Structure: Visualize the object model's structure
    using the Graphviz engine, generating graphical representations.
- Querying Objects: Execute queries on objects to generate tabular data,
    allowing users to analyze and understand the object properties.

Usage:
    from ObjectModel import ObjectModel
    object_model = ObjectModel(
        path,
        do_auto_load,
        do_auto_save,
        Const,
        Classes=[ClassA, ClassB, ClassC]
    )

Author: Pavel ERESKO
"""

import xml.etree.ElementTree as ET

import os

from xml.dom import minidom

from graphclass import Drawing

import yaml

ID_DV = "|"

class FIELD:
    ''' Identyfiers for the fields purposes '''
    TYPE      =  0
    FIELD     =  1
    OWNER     =  2
    LIST_NAME =  3
    LIST_ITEM =  4
    ID        =  5
    VIEW      =  6
    EXT       =  7
    ICON      =  8
    LINK      =  9
    LINK_IN   = 10

class DRAW:
    ''' Elements to draw '''
    VIEW = 1 #0
    EXT  = 2 #1
    ICON = 4 #2
    ID   = 8 #3
    ALL  = VIEW + EXT + ICON + ID # Full
    DEF  = ALL - EXT # Default

def prettify(elem):
    ''' Prettyfying the xml document '''
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def structure_to_xml(data, element = None):
    ''' Getting XML from structure '''
    isroot = element is None
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

def plain_query(tree, path, pref = "/", res = [], parfields = None):
    ''' Getting tabular data from XML '''
    ths, _, nxt = path.partition("/")
    result = tree.findall(pref + ths)

    for item in result:
        query_fields = {} if parfields is None else parfields.copy()

        for child in item:
            query_fields[child.tag] = child.text

        if nxt:
            plain_query(item, nxt, "./", res, query_fields)
        else:
            res.append(query_fields)

    return res


class ObjectModelItem:
    ''' Class to inherit for some Model Item '''
    Icon = ""
    Show = True
    Draw = DRAW.DEF
    Color = "#A9DFBF"
    UseIndex = False

    def __init__(self, model, id_query, index, resp, do_auto_save = True):
        self.model = model

        if id_query is not None:
            par_id, _, _ = id_query.rpartition(ID_DV)
            if par_id != "":
                setattr(self, "_parent", par_id)
                resp["_parent"] = par_id

        if getattr(self, "UseIndex", False):
            # setattr(self, "_index", index)
            resp["_index"] = index

        # key = self.field_of_a_kind(FIELD.ID) # process Id first
        # if key is not None and key in resp:
        #     setattr(self, key, resp[key])
        self.call_form_id(resp, self)

        fields = type(self).fields()
        for key, value in resp.items():
            cfg = fields.get(key, type(value))
            fieldtype = cfg[FIELD.TYPE] if isinstance(cfg, tuple) else cfg

            if isinstance(fieldtype, list) and len(fieldtype) != 0 and issubclass(fieldtype[0], ObjectModelItem):
                # if len(fieldtype) == 0:
                #     continue

                # if fieldtype[0] == str:
                #     continue

                model[fieldtype[0]].fetch(f"{self.get_id()}{ID_DV}*", value, do_auto_save)

            # elif fieldtype == list:
            #     continue

            elif isinstance(fieldtype, dict):
                tkkey, tkval = next(iter(fieldtype.items()))
                for pair in value:
                    setattr(self, "Tag_" + pair[tkkey], pair[tkval])
                # continue

            else:
                setattr(self, key, value)

    def __getitem__(self, name):
        value = getattr(self, name, None)
        if value == None:
            return None

        fields = self.fields()
        if name not in fields:
            return value

        field = fields[name]
        if isinstance(field, tuple):
            cls, role = field
        else:
            cls = field
            role = FIELD.FIELD

        if issubclass(cls, ObjectModelItem) and role != FIELD.ID:
            value = self.model[cls][value]

        return value

    @classmethod
    def fields_of_a_kind(self, kind):
        ''' Getting all the fields of a kind '''
        return (key for key, value in self.fields().items()
                 if isinstance(value, tuple) and value[1] == kind
               )

    @classmethod
    def field_of_a_kind(self, kind):
        ''' Getting the first field of a kind '''
        return next(self.fields_of_a_kind(kind), None)

    def value_of_a_kind(self, kind):
        ''' Getting the value of the first field of a kind '''
        field = self.field_of_a_kind(kind)
        return getattr(self, field, None)

    def get_actual_field_type(self, field):
        return self.fields()[field][FIELD.TYPE]

    def get_field_object(self, model, field):
        ''' Getting the object of the field '''
        if field is None:
            return None

        node_id = getattr(self, field, None)
        if node_id is None:
            return None

        clss = self.get_actual_field_type(field)

        if clss == None or not node_id in model[clss].map:
            return None
        
        obj = model[clss].map[node_id]
        return obj

    def object_of_a_kind(self, model, kind):
        '''Getting the object of the field of a kind'''
        field = self.field_of_a_kind(kind)
        return self.get_field_object(model, field)

    def get_draw_link(self, model):
        '''Getting the link, modyfying id if node is in the list'''
        lister = self.object_of_a_kind(model, FIELD.LIST_ITEM)
        if lister is not None:
            list_name = self.value_of_a_kind(FIELD.LIST_NAME)
            return f"{lister.get_draw_id(model)}-{list_name}:{self.get_draw_id(model)}"

        return self.get_draw_id(model)

    def get_draw_id(self, model):
        return self.__class__.get_class_view() + "_" + self.get_id()

    def get_id(self):
        '''Getting Id of object'''
        field = self.field_of_a_kind(FIELD.ID)
        if field == None:
            field = "_id"
        if field is not None and hasattr(self, field):
            return getattr(self, field)

        return f"{getattr(self, '_parent', '?')}{ID_DV}{getattr(self, '_index', '?')}"

    def get_view(self):
        '''Getting view of object'''
        field = self.field_of_a_kind(FIELD.VIEW)
        if field is not None and hasattr(self, field):
            return getattr(self, field)

        return self.get_id()
    
    def get_href(self):
        return ""

    def get_ext(self):
        '''Getting extended view of object'''
        field = self.field_of_a_kind(FIELD.EXT)
        if field is not None and hasattr(self, field):
            return getattr(self, field)

        return ""

    def get_icon(self):
        '''Getting icon of object'''

        field = self.field_of_a_kind(FIELD.ICON)
        if field is None:
            field = "Icon"

        if field is not None and hasattr(self, field):
            return getattr(self, field)

        return ""

    @staticmethod
    def form_id(resp, id_field):
        '''Function to form id from response'''
        return resp[id_field]

    @classmethod
    def call_form_id(cls, resp, obj = None):
        '''Function to call form id from response'''
        
        id_field = cls.field_of_a_kind(FIELD.ID)
        if id_field == None:
            id_field = "_id"

        try:
            id = cls.form_id(resp, id_field)
        except Exception as e:
            print(f"{cls.get_class_view()}.call_form_id: {e}")
            id = "-"

        if obj != None:
            setattr(obj, id_field, id)

        return id

    @classmethod
    def get_objects_by_index(cls, query, list_field, filter_field):
        '''Getting children object by id'''
        par_query = None
        kind_query = None
        if query is not None:
            par_query, _, kind_query = query.rpartition(ID_DV)

        pars = cls.get_objects(par_query)
        result = []
        for par in pars:
            par_id = cls.call_form_id(par)

            if type(list_field) is str:
                kinder = par[list_field]
            else:
                try:
                    kinder = list_field.get_objects_of_parent(par_id, kind_query)
                except Exception as e:
                    ErrorCode = e.response['Error']['Code'] if hasattr(e, "response") else ""
                    if ErrorCode[-9:] == '.NotFound' or ErrorCode == "AccessDenied":
                        kinder = []
                    else:
                        print(f"{cls.get_class_view()}.get_objects: {e.args[0]}")
                        raise

            index = -1
            for kind in kinder:
                index += 1

                kind["_parent"] = par_id
                if type(list_field) is str:
                    pass # kind["_id"] = f"{par_id}{ID_DV}{???}"
                else:
                    kind["_id"] = list_field.call_form_id(kind)

                if kind_query is not None and kind_query != "" and kind_query != "*":
                    if kind_query != (str(index) if filter_field == int else str(kind[filter_field])):
                        continue

                result.append(kind)

        return result

    @classmethod
    def query(cls, query):
        '''Runs the query to have tabular view of objects' properties '''
        data_structure = cls.get_objects()

        xml_tree = structure_to_xml(data_structure)

        # with open("query.xml", "w", encoding="utf-8") as file:
        #     file.write(prettify(xml_tree.getroot()))

        reslist = plain_query(xml_tree, query)

        resdict = {}
        for idx, d in enumerate(reslist):
            for key, value in d.items():
                if key not in resdict:
                    resdict[key] = [None] * len(reslist)
                resdict[key][idx] = value

        return resdict


    @staticmethod
    def get_objects(node_id=None):
        '''Function to return list of objects of the class'''
        return None

    @staticmethod
    def fields():
        '''Function to return list of fields of the class objects'''
        return {}

    @staticmethod
    def cli_add(args = None):
        '''Function to add the object via CLI'''
        return "<?>"

    @staticmethod
    def cli_del(args = None):
        '''Function to delete the object via CLI'''
        return "<?>"

    @classmethod
    def get_class_view(cls):
        ''' Get class view '''
        return cls.__name__


class ObjectList:
    ''' Class for object list '''

    def __init__(self, model, clss):
        self.model = model
        self.Class = clss
        self.map = {}

    def __getitem__(self, key):
        if key in self.map:
            return self.map[key]
        
        objs = self.fetch(key)
        return objs[0]

    def __setitem__(self, key, value):
        self.map[key] = value

    def objects(self):
        return list(self.map.values())

    def count(self):
        ''' Getting the count of the objects in a list '''
        return len(self.map)

    def view(self):
        ''' Getting the class view '''
        return self.Class.get_class_view()

    def release(self, id_query = None, do_auto_save = True):
        ''' Releasing all the objects from the list '''
        if id_query is not None:
            del self.map[id_query]
        else:
            self.map.clear()

        if do_auto_save:
            self.model.auto_save()

    def fetch(self, filter = None, resp = None, do_auto_save = True, create_par = None, refetch = False):
        ''' Fetching all the objects to the list '''

        if isinstance(filter, str) and filter in self.map and not refetch:
            return [self.map[filter]]

        res = []

        if resp is None:
            try:
                resp = self.Class.get_objects(filter)
            except Exception as e:
                # ErrorCode = e.response['Error']['Code'] if hasattr(e, "response") else ""
                print(f"{self.Class.get_class_view()}.get_objects: {e}")
                # if ErrorCode[-9:] == '.NotFound' or ErrorCode == "AccessDenied":
                #     return
                # else:
                #     raise
                return res

        if len(resp) == 0 and create_par is not None:
            new_id = self.Class.create(**create_par)
            resp = self.Class.get_objects(new_id)

        par_id = ""
        ip_n = "*"
        if isinstance(filter, str):
            par_id, _, ip_n = filter.rpartition(ID_DV)

        index = -1
        for el in resp:
            index += 1
            ip_nn = ip_n
            if ip_nn == "*":
                ip_nn = int(index)

            obj = self.Class(self.model, f"{par_id}{ID_DV}{ip_nn}", index, el, do_auto_save)

            obj_id = obj.get_id()
            self.map[obj_id] = obj

            res.append(obj)

        if do_auto_save:
            self.model.auto_save()

        return res

    def create(self, *args):
        ''' Creates object in the list '''
        try:
            node_id = self.Class.create(*args)
        except Exception as e:
            print(f"{self.view()}.create: An exception occurred: {type(e).__name__} - {e}")
            return None

        self.fetch(node_id)

        return node_id

    def delete_inner(self, args):
        ''' Inner method for delete object in the list '''
        try:
            self.Class.delete(*args)
        except Exception as e:
            print(f"{self.view()}.delete: An exception occurred: {type(e).__name__} - {e}")
            return

        node_id = args[0]
        if node_id in self.map:
            del self.map[node_id]
            self.model.auto_save()

    def delete(self, *args):
        ''' Deleting object in the list '''
        self.delete_inner(args)

    def delete_all(self):
        ''' Deleting all the objects in the list '''
        keys_to_delete = list(self.map.keys())
        index = len(keys_to_delete) - 1
        while index >= 0:
            node_id = keys_to_delete[index]
            self.delete_inner((node_id,))
            index -= 1

    def print(self):
        ''' Printing all the objects in the list '''
        res = ""

        if len(self.map) == 0:
            return res

        print(f"  {self.view()}: {len(self.map)}")
        for node_id, obj in self.map.items():
            print(f"{node_id}: {obj}")

            res += f"##### {self.view()}: {node_id}\n\n{yaml.dump(obj.__dict__)}\n\n\n"

        return res

def node_label(obj):
    ''' html code for node '''
    draw  = type(obj).Draw
    color = type(obj).Color

    res = ""
    if draw & DRAW.VIEW:
        res = res + f'''
            <TR>
                <TD {obj.get_href()} BGCOLOR="{color}" PORT="p0"><B>{obj.get_view()}</B></TD>
            </TR>
        '''
    if draw & DRAW.EXT:
        res = res + f'''
            <TR>
                <TD BGCOLOR="white" PORT="p1"><B>{obj.get_ext()}</B></TD>
            </TR>
        '''
    if draw & DRAW.ICON:
        res = res + f'''
            <TR>
                <TD BGCOLOR="white" PORT="p2"><IMG SRC="{obj.get_icon()}"/></TD>
            </TR>
        '''
    res = res + f'''
        <TR>
            <TD BGCOLOR="white" PORT="p4"><FONT POINT-SIZE="9.0">{obj.get_class_view()}</FONT></TD>
        </TR>
    '''
    if draw & DRAW.ID:
        res = res + f'''
            <TR>
                <TD BGCOLOR="{color}" PORT="p3"><FONT POINT-SIZE="9.0">{obj.get_id()}</FONT></TD>
            </TR>
        '''
    if res == "":
        res = res + f'''
            <TR>
                <TD BGCOLOR="{color}" PORT="p0"><B>{obj.get_id()}</B></TD>
            </TR>
        '''

    return f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        {res}
        </TABLE>
    >'''

def cluster_label(obj):
    ''' html code for cluster header '''
    draw = obj.Draw

    res0 = ""
    if draw & DRAW.ICON:
        res0 = res0 + f'''
            <TD ROWSPAN="3"><IMG SRC="{obj.get_icon()}"/></TD>
        '''

    if draw & DRAW.VIEW:
        res0 = res0 + f'''
            <TD {obj.get_href()}><B>{obj.get_view()}</B></TD>
        '''

    if res0 != "":
        res0 = f'''
        <TR>
            {res0}
        </TR>
        '''

    res1 = ""
    if draw & DRAW.EXT:
        res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="9.0">{obj.get_ext()}</FONT></TD>
        </TR>
        '''

    res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="9.0">{obj.get_class_view()}</FONT></TD>
        </TR>
        '''

    if draw & DRAW.ID:
        res1 = res1 + f'''
        <TR>
            <TD><FONT POINT-SIZE="9.0">{obj.get_id()}</FONT></TD>
        </TR>
        '''

    if res0 == "" and res1 == "":
        res0 = res0 + f'''
        <TR>
            <TD PORT="p0"><B>{obj.get_id()}</B></TD>
        </TR>
    '''

    return f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            {res0}
            {res1}
        </TABLE>
    >'''

class ObjectModel:
    ''' Object model class'''

# def ClassesList():
#     # Get all classes defined in the module
#     classes = [obj for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)]

#     # Return the list of class names
#     return [cls.__name__ for cls in classes]

# # Print the list of classes in the module
# print("List of classes in the module:", ClassesList())

    def __init__(self, path, do_auto_load, do_auto_save, Const, Classes):
        self.path = path
        self.do_auto_load = do_auto_load
        self.do_auto_save = do_auto_save

        ObjectModel.Const = Const
        ObjectModel.Classes = Classes

        ObjectModel.Classes["ALL"] = []
        for key, clsss in ObjectModel.Classes.items():
            if key == "ALL": continue
            ObjectModel.Classes["ALL"] += clsss

        for clss in ObjectModel.Classes["ALL"]:
            wrapper = ObjectList(self, clss)
            name = wrapper.view()
            setattr(self, name, wrapper)

        self.auto_load()


    def __getitem__(self, clss):
        ''' Getting the wrapper as a property with the name of a class '''
        key = clss.get_class_view()
        return getattr(self, key)

    def __setitem__(self, clss, wrap):
        ''' Setting the wrapper as a property with the name of a class '''
        key = clss.get_class_view()
        setattr(self, key, wrap)

    def delete_all(self, clss_list = None):
        ''' Deleting all objects from model '''
        clsss = self.string_to_classes(clss_list)

        for clss in reversed(clsss):
            name = clss.get_class_view()
            wrapper = getattr(self, name)
            wrapper.delete_all()

    def print(self, clss_list = None):
        ''' Prints model '''
        clsss = self.string_to_classes(clss_list)

        res = ""
        for clss in clsss:
            name = clss.get_class_view()
            wrapper = getattr(self, name)
            res += wrapper.print()

        return res

    def load(self):
        ''' Loads model from file '''
        if not os.path.exists(self.path): return

        with open(self.path, 'r') as file:
            xml_string = file.read()
        root = ET.fromstring(xml_string)

        for element in root:
            wrapper = getattr(self, element.tag, None)
            if wrapper == None:
                continue
            for child in element:
                node_id = child.text
                wrapper.fetch(node_id, None, False)

    def auto_load(self):
        ''' Autoloads model from file '''
        if self.do_auto_load:
            self.load()

    def save(self):
        ''' Saves model to file '''
        root = ET.Element("root")

        for clss in ObjectModel.Classes["ALL"]:
            name = clss.get_class_view()
            wrapper = getattr(self, name)

            if len(wrapper.map) == 0:
                continue

            category_element = ET.SubElement(root, name)
            for node_id, obj in wrapper.map.items():
                id_element = ET.SubElement(category_element, f"id")
                id_element.text = str(node_id)


        tree = prettify(root)
        with open(self.path, "w") as file:
            file.write(tree)

    def auto_save(self):
        ''' Autosaves model to file '''
        if self.do_auto_save:
            self.save()

    def string_to_classes(self, clss_list = None):
        ''' Interpretes string as a class list '''
        clsss = clss_list

        if clsss is None:
            return self.string_to_classes("ALL")

        elif isinstance(clsss, str) and clsss.find(",") >= 0:
            res = clsss
            res = res.replace(" ", "")
            res = res.split(",")
            return self.string_to_classes(res)

        elif isinstance(clsss, list):
            res = []
            for i in clsss:
                res += self.string_to_classes(i)
            return res

        elif isinstance(clsss, str):
        
            if hasattr(self, clsss):
                return [getattr(self, clsss).Class]

            elif clsss in self.Classes:
                return self.Classes[clsss]
            
            elif clsss in self.Const:
                return self.string_to_classes(self.Const[clsss])

            else:
                print("ObjectModel.string_to_classes: wrong Class string key: " + clsss)
                return []

        elif issubclass(clsss, ObjectModelItem):
            return [clsss]

        else:
            print("ObjectModel.string_to_classes: wrong Class: " + clsss)
            return []


    def fetch(self, clss_list = None):
        ''' Fetching the object '''
        clsss = self.string_to_classes(clss_list)

        for clss in clsss:
            if getattr(clss, "DoNotFetch", False):
                continue
            self[clss].fetch()

    def release(self, clss_list = None):
        ''' Releasing the object '''
        clsss = self.string_to_classes(clss_list)

        if isinstance(clsss, str):
            clsss = ObjectModel.Classes[clsss]

        for clss in clsss:
            self[clss].release()

    def draw(self, clss_list = None):
        ''' Drawing the model '''
        clsss = self.string_to_classes(clss_list)
        drawing = Drawing()

        hasowned  = {}
        isowned   = {}
        haslisted = {}
        islisted  = {}
        for clss in clsss:
            wrap = self[clss]

            for _, obj in wrap.map.items():
                owner = obj.object_of_a_kind(self, FIELD.OWNER)
                if owner is not None:
                    isowned[obj] = owner
                    hasowned[owner] = True

                listitemfield = obj.field_of_a_kind(FIELD.LIST_ITEM)
                if listitemfield is not None and hasattr(obj, listitemfield):
                    list_item_obj = obj.get_field_object(self, listitemfield)

                    if list_item_obj == None:
                        continue

                    list_item = list_item_obj.get_draw_id(self)

                    islisted[obj] = list_item

                    list_name = getattr(obj, obj.field_of_a_kind(FIELD.LIST_NAME), "List")

                    if not list_item in haslisted:
                        haslisted[list_item] = {}
                    if not list_name in haslisted[list_item]:
                        haslisted[list_item][list_name] = []

                    haslisted[list_item][list_name].append(obj)


        for clss in clsss:
            wrap = self[clss]

            for node_id, obj in wrap.map.items():
                obj_view = obj.get_draw_id(self)
                
                if obj in hasowned or obj_view in haslisted:
                    drawing.add_item(obj_view,
                        cluster = drawing.item_view(cluster_label(obj), style = 'filled', fillcolor = type(obj).Color),
                        point   = drawing.item_view("", shape='point', width='0.1')
                    )
                elif obj in islisted:
                    pass
                else:
                    drawing.add_item(obj_view, drawing.item_view(node_label(obj), shape='plaintext'))

                par = isowned[obj] if obj in isowned else None
                if par is not None:
                    drawing.add_parent(obj_view, par.get_draw_id(self))

                if obj_view in haslisted:
                    for list_name, listitems in haslisted[obj_view].items():
                        # break

                        label = f'<TR><TD BGCOLOR="#A9DFBF"><B><FONT POINT-SIZE="9.0">{list_name}</FONT></B></TD></TR>\n'
                        for list_item in listitems:
                            label += f'<TR><TD {list_item.get_href()} BGCOLOR="white" PORT="{list_item.get_draw_id(self)}"><FONT POINT-SIZE="9.0">{list_item.get_view()}</FONT></TD></TR>\n'

                        label = f'''<
                            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                            {label}
                            </TABLE>
                        >'''

                        drawing.add_item  (obj_view + "-" + list_name, drawing.item_view(label, shape='plaintext'))
                        drawing.add_parent(obj_view + "-" + list_name, obj_view)


                idlink = obj.get_draw_link(self)

                for field in obj.fields_of_a_kind(FIELD.LINK):
                    corr = obj.get_field_object(self, field)
                    if corr is None:
                        continue
                    drawing.add_link(idlink, corr.get_draw_link(self), field)

                for field in obj.fields_of_a_kind(FIELD.LINK_IN):
                    corr = obj.get_field_object(self, field)
                    if corr is None:
                        continue
                    drawing.add_link(corr.get_draw_link(self), idlink, field + "<")

        return drawing


    def html(self, clss_list = None):
        return self.draw(clss_list).html("OMF")

    def svg(self, clss_list = None):
        return self.draw(clss_list).svg("OMF")
    
    def source(self, clss_list = None):
        return self.draw(clss_list).source("OMF")
