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

from graphclass import Drawing, cluster_label, node_label, list_label

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
    VIEW  =  1 #1
    EXT   =  2 #2
    ICON  =  4 #3
    ID    =  8 #4
    CLASS = 16 #5

    ALL  = VIEW + EXT + ICON + ID + CLASS # Full
    DEF  = ALL - EXT # Default

class USAGE:
    VALUE = "VALUE"
    LIST  = "LIST"

class COLOR:
    ORANGE    = "#FFC18A"
    RED_DARK  = "#E76E6F"
    RED       = "#F29F9B"
    RED_LIGHT = "#FDD0C7"
    LILA      = "#f2c4f4"
    BLUE_LIGHT= "#f0f9ff"
    BLUE      = "#d7c1ff"
    BLUE_DARK = "#c19fff"
    CRIMSON   = "#F2B3BC"
    GREEN     = "#a9dfbf"


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
                model[fieldtype[0]].fetch(f"{self.get_id()}{ID_DV}*", value, do_auto_save)

            elif isinstance(fieldtype, tuple) and len(fieldtype) != 0 and issubclass(fieldtype[0], ObjectModelItem):
                setattr(self, key, (value,) if type(value) == str else tuple(value))

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
        return [(key, value[1]) for key, value in self.fields().items()
                 if isinstance(value, tuple)
                    and (
                        value[1] in kind if type(kind) is tuple
                            else value[1] == kind
                    )
               ]

    @classmethod
    def field_of_a_kind(self, kind):
        ''' Getting the first field of a kind '''

        fields = self.fields_of_a_kind(kind)

        if len(fields) == 0:
            return None
        
        return fields[0][0]

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

        if type(clss) is tuple:
            clss = clss[0]

            if type(node_id) is tuple or type(node_id) is list:
                return tuple([self.get_class_object(model, clss, cur_node_id) for cur_node_id in node_id])
            else:
                return (self.get_class_object(model, clss, node_id),)

        else:
            return self.get_class_object(model, clss, node_id)
    
    def get_class_object(self, model, clss, node_id):
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
            import uuid
            # print(f"{cls.get_class_view()}.call_form_id: {e}")
            id = "id-" + str(uuid.uuid4())

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
        ''' Saves model to xml file '''
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

        ''' Saves model to yaml file '''
        root = self.data()
        with open(self.path +'.yaml', 'w') as file:
            yaml.dump(root, file, default_flow_style=False)

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

    def data(self):
        root = {}
        for clss in ObjectModel.Classes["ALL"]:
            class_attrs = dir(clss)
            name = clss.get_class_view()
            wrapper = getattr(self, name)

            if len(wrapper.map) == 0:
                continue

            clss_props = {attr: getattr(clss, attr) for attr in class_attrs \
                if not callable(getattr(clss, attr)) and not attr.startswith('__') \
                    and attr != "model"
            }

            fields = {}
            for field_id, field in clss.fields().items():
                field_type, field_role = field
                if type(field_type) == tuple:
                    field_type = field_type[0]
                field_type = field_type.get_class_view() if field_type != str else "str"
                fields[field_id] = {
                    # "Id"  : field_id,
                    "Type": field_type,
                    "Role": field_role,
                }
            clss_props["Fields"] = fields

            objs = {}
            for node_id, obj in wrapper.map.items():
                object_attrs = dir(obj)
                props = {attr: getattr(obj, attr) for attr in object_attrs \
                            if attr not in class_attrs and not callable(getattr(obj, attr)) and not attr.startswith('__') \
                                and attr != "model"
                        }
                objs[node_id] = props
            clss_props["Nodes"] = objs

            root[name] = clss_props

        return root

    def _field_of_a_kind(self, datas, class_attrs, node_attrs, role):
        field_id, field = next(((field_id, field) for field_id, field in class_attrs["Fields"].items() if field['Role'] == role), (None, None))
        if field_id == None:
            return (None, None)
        
        if not field_id in node_attrs:
            return (field["Type"], None)

        return (field["Type"], node_attrs[field_id])

    def draw(self, clss_list = None):
        ''' Drawing the model '''

        datas = self.data()

        clsss = self.string_to_classes(clss_list)
        drawing = Drawing()

        hasowned  = {}
        isowned   = {}
        haslisted = {}
        islisted  = {}

        _isowned = {}
        _hasowned = {}

        for clss in clsss:
            wrap = self[clss]
            class_attrs = datas[clss.get_class_view()]
            nodes = class_attrs["Nodes"]
            node_clss = clss.__name__

            # for _, obj in wrap.map.items():
            for node_id, node_attrs in nodes.items():
                obj = wrap.map[node_id]

                node_draw = f"{node_clss}_{node_id}"

                owner_class, owner_id = self._field_of_a_kind(datas, class_attrs, node_attrs, FIELD.OWNER)
                owner_draw = f"{owner_class}_{owner_id}"
                owner = obj.object_of_a_kind(self, FIELD.OWNER)
                # if owner is not None:
                if owner_id is not None:
                    isowned [obj] = owner
                    hasowned[owner] = True

                    _isowned [node_draw ] = owner_draw
                    _hasowned[owner_draw] = True

                listitemfield = obj.field_of_a_kind(FIELD.LIST_ITEM)
                list_class, list_id = self._field_of_a_kind(datas, class_attrs, node_attrs, FIELD.LIST_ITEM)
                list_draw = f"{list_class}_{list_id}"

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
            # for node_id, node_attrs in nodes.items():
            #     obj = wrap.map[node_id]

                obj_view = obj.get_draw_id(self)
                links = obj.fields_of_a_kind((FIELD.LINK, FIELD.LINK_IN))
                
                # if obj in hasowned or obj_view in haslisted or len(links) > 0:
                #     drawing.add_item(obj_view,
                #         cluster = drawing.item_view(cluster_label(obj, DRAW), style = 'filled', fillcolor = type(obj).Color),
                #         point   = drawing.item_view("", shape='point', width='0.1')
                #     )
                # elif obj in islisted:
                #     pass
                # else:
                #     drawing.add_item(obj_view, drawing.item_view(node_label(obj, DRAW), shape='plaintext'))

                if obj in islisted:
                    pass
                else:
                    drawing.add_item(obj_view,
                        node    = drawing.add_item(obj_view, drawing.item_view(node_label(obj, DRAW))),
                        cluster = drawing.item_view(cluster_label(obj, DRAW), style = 'filled', fillcolor = type(obj).Color),
                        point   = drawing.item_view("", shape='point', width='0.1'),
                    )


                par = isowned[obj] if obj in isowned else None
                if par is not None:
                    drawing.add_parent(obj_view, par.get_draw_id(self))

                if obj_view in haslisted:
                    for list_name, listitems in haslisted[obj_view].items():
                        self.draw_table(drawing, obj_view, list_name, listitems)

                idlink = obj.get_draw_link(self)

                # for field in obj.fields_of_a_kind(FIELD.LINK):
                #     corr = obj.get_field_object(self, field)
                #     if corr is None:
                #         continue
                #     drawing.add_link(idlink, corr.get_draw_link(self), field)

                # for field in obj.fields_of_a_kind(FIELD.LINK_IN):
                #     corr = obj.get_field_object(self, field)
                #     if corr is None:
                #         continue
                #     drawing.add_link(corr.get_draw_link(self), idlink, field + "<")

                for field, link in links:
                    corr = obj.get_field_object(self, field)

                    if corr is None:
                        continue

                    elif type(corr) is tuple:
                        self.draw_table(drawing, obj_view, field, corr)

                        for list_item in corr:
                            if list_item is None:
                                continue
                            if link == FIELD.LINK:
                                drawing.add_link(idlink + "-" + field + ":" + list_item.get_draw_id(self), list_item.get_draw_link(self), "" )
                            else:
                                drawing.add_link(list_item.get_draw_link(self), idlink + "-" + field + ":" + list_item.get_draw_id(self), "<")

                    else:
                        if link == FIELD.LINK:
                            drawing.add_link(idlink, corr.get_draw_link(self), field      )
                        else:
                            drawing.add_link(corr.get_draw_link(self), idlink, field + "<")

        return drawing
    


    def draw_table(self, drawing, obj_view, list_name, list_objs):

        listitems = []
        for list_obj in list_objs:
            if list_obj is None:
                continue

            listitems.append({
                "id"  : list_obj.get_draw_id(self),
                "view": list_obj.get_view(),
                "href": list_obj.get_href(),
            })

        label = list_label(list_name, listitems)
        drawing.add_item  (obj_view + "-" + list_name, drawing.item_view(label))

        drawing.add_parent(obj_view + "-" + list_name, obj_view)


    def source(self, clss_list = None, name = "OMF"):
        return self.draw(clss_list).source(name)

    def print(self, clss_list = None):
        return self.draw(clss_list).print()

    def html(self, clss_list = None, name = "OMF", engine = "dot", reload_time = 0, html_wrap=True):
        return self.draw(clss_list).html(name, engine=engine, reload_time=reload_time, html_wrap=html_wrap)

    def svg(self, clss_list=None, name="OMF", engine="dot"):
        return self.draw(clss_list).svg(name, engine)


# SchemaViz

class SchemaVizItem(ObjectModelItem):
    # Icon = "Icon"
    Color = COLOR.GREEN

    @classmethod
    def get_objects(cls, node = None):
        if node is None:
            return SchemaVizObjectModel.DATA[cls.__name__]
        else:
            for obj in SchemaVizItem.get_objects():
                if obj["Id"] == node:
                    return [obj]
            return []

    # def get_icon(self):
    #     icon = super().get_icon()
    #     return os.path.abspath(ROOTPATH + 'icons').replace("\\", "/") + "/" + icon + ".png"

class SchemaVizObjectModel(ObjectModel):
    def addSections(self, merged_data, data, clss=None, ids=None):
        for section in data:
            for key, values in section.items():
                if clss != None and key != clss:
                    continue
                for val in values:
                    if ids != None and val["Id"] not in ids:
                        continue
                    if key in merged_data:
                        merged_data[key].append(val)
                    else:
                        merged_data[key] = [val]
    
    def make_static_fields(self, fields):
        @staticmethod
        def static_fields():
            return fields
        return static_fields

    def __init__(self, metadata, data):
        classes = {}
        for name, clscfg in metadata.items():
            attrs = {}
            methods = {}

            for parname, par in clscfg.items():
                if parname == "Color":
                    attrs[parname] = getattr(COLOR, par.upper())
                elif parname == "Draw":
                    attrs[parname] = sum(getattr(DRAW, field.upper()) for field in par)
                elif isinstance(par, dict):
                    if "Value" in par:
                        attrs[parname] = par["Value"]
                else:
                    attrs[parname] = par

            clss = type(name, (SchemaVizItem,), {**attrs, **methods})
            classes[name] = clss

        for name, clscfg in metadata.items(): # fields
            fields = {}
            for parname, par in clscfg.items():
                if isinstance(par, dict):
                    fieldtype = str
                    fieldrole = FIELD.VIEW
                    fieldusg  = USAGE.VALUE
                    for fname, fval in par.items():
                        if   fname == "Type":
                            fieldtype = fval
                            if fieldtype in classes:
                                fieldtype = classes[fieldtype]
                            else:
                                type_map = {
                                    "str": str,
                                    "int": int,
                                    "bool": bool,
                                    "float": float,
                                }
                                fieldtype = type_map.get(fieldtype.lower())
                        elif fname == "Role":
                            fieldrole = getattr(FIELD, fval.upper())
                        elif fname == "Usage":
                            fieldusg = getattr(USAGE, fval.upper())
                        if fieldusg == USAGE.LIST:
                            fieldtype = (fieldtype,)
                            
                    fields[parname] = (fieldtype, fieldrole)

            classes[name].fields = self.make_static_fields(fields)
        
        super().__init__(
            None,
            False,
            False,
            None,
            {
                'SCHEMAVIZ' : 
                    [clss for name, clss in classes.items()]
                ,
            }
        )

        merged_data = {}
        self.addSections(merged_data, data)
        SchemaVizObjectModel.DATA = merged_data
