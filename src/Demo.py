"""
Object Model Framework Demo Module

This module representing a behaivour of Object Model Framework

Classes:
    ParentClass, InheritedClass, Listed, Drawing, GraphViz, Picture

Usage:
    Run the module. See the graph output in Demo.html file.

Author: Pavel ERESKO
"""

from ObjectModelFramework import *

class DemoItem(ObjectModelItem):
    Icon = "Y3A"
    Color = "#e998ed"

    @classmethod
    def get_objects(cls, node = None):
        if node is None:
            return DemoObjectModel.Const[cls.__name__]
        else:
            for obj in ParentClass.get_objects():
                if obj["Id"] == node:
                    return [obj]
            return []

    def get_icon(self):
        icon = super().get_icon()
        return os.path.abspath('./src/Demo/icons').replace("\\", "/") + "/" + icon + ".png"

class GraphViz(DemoItem):
    Icon = "Graphviz"
    Color = "#adcdd9"

    @staticmethod
    def fields():
        return {
                    'Id': (ParentClass, FIELD.ID),
                    'Name': (ParentClass, FIELD.VIEW),
                    'Link': (Drawing, FIELD.LINK),
                }

class ParentClass(DemoItem):
    Icon = "ObjectModel"
    Name = "Object Model"
    Color = '#84def4'

    @staticmethod
    def fields():
        return {
                    'Id': (ParentClass, FIELD.ID),
                    'Name': (ParentClass, FIELD.VIEW),
                    'Owner': (InheritedClass, FIELD.OWNER),
                }

class Drawing(DemoItem):
    Icon = "Drawing"
    Name = "Drawing"
    Color = '#c8b7ea'

    @staticmethod
    def fields():
        return {
                    'Id': (Listed, FIELD.ID),
                    'Name': (Listed, FIELD.VIEW),
                    'Owner': (ParentClass, FIELD.OWNER),
                }

class Picture(DemoItem):
    Icon = "Demo"
    Draw = DRAW.ICON

    @staticmethod
    def fields():
        return {
                    'Id': (Picture, FIELD.ID),
                    'Link': (Drawing, FIELD.LINK_IN),
                }

class InheritedClass(DemoItem):
    Icon = "Obj"
    Color = "#A9DFBF"

    @staticmethod
    def fields():
        return {
                    'Id': (ParentClass, FIELD.ID),
                    'Name': (ParentClass, FIELD.VIEW),
                    'Icon': (ParentClass, FIELD.ICON),
                }

class Listed(DemoItem):
    ListName = "Inherited"
    Color = "#ff9999"

    @staticmethod
    def fields():
        return {
                    'Id': (Listed, FIELD.ID),
                    'Name': (Listed, FIELD.VIEW),
                    # 'ListOwner': (ParentClass, FIELD.OWNER),
                    'ListOwner': (ParentClass, FIELD.LIST_ITEM),
                    'ListName': (str, FIELD.LIST_NAME),
                    "Link": (ParentClass, FIELD.LINK),
                }
    def __init__(self, aws, id_query, index, resp, do_auto_save=True):
        super().__init__(aws, id_query, index, resp, do_auto_save)
        self.ListItem = self.Id
    
class DemoObjectModel(ObjectModel):
    def __init__(self):
        super().__init__(
            "./src/Demo/Demo.xml",
            False,
            False,
            {
                'GraphViz' : [
                    {
                        "Id": "graphviz",
                        "Name" : "graphviz",
                        "Link" : "d-Original",
                    },
                ],
                'ParentClass' : [
                    {
                        "Id": "pc-Original",
                        "Owner" : None,
                    },
                    {
                        "Id": "pc-Y3A",
                        "Owner" : "ic-Y3A",
                    },
                    {
                        "Id": "pc-Demo",
                        "Owner" : "ic-Demo",
                    },
                ],
                'Drawing' : [
                    {
                        "Id": "d-Original",
                        "Owner" : "pc-Original",
                    },
                    {
                        "Id": "d-Y3A",
                        "Owner" : "pc-Y3A",
                    },
                    {
                        "Id": "d-Demo",
                        "Owner" : "pc-Demo",
                    },
                ],
                'Picture' : [
                    {
                        "Id": "Picture",
                        "Link": "d-Demo",
                    },
                ],
                'InheritedClass' : [
                    {
                        "Id": "ic-Y3A",
                        "Name" : "Y3A",
                        # "Icon" : "Y3A",
                    },
                    {
                        "Id": "ic-Demo",
                        "Name" : "Demo",
                    },
                ],
                'Listed' : [
                    {
                        "Id": "l-Y3A",
                        "Name" : "Y3A",
                        "ListOwner" : "pc-Original",
                        "Link" : "pc-Y3A",
                    },
                    {
                        "Id": "l-Demo",
                        "Name" : "Demo",
                        "ListOwner" : "pc-Original",
                        "Link" : "pc-Demo",
                    },
                ],
            },
            {
                'OBJECTMODULE' : [
                    ParentClass, Drawing, 
                ],
                'INHERITED' : [
                    InheritedClass, Listed, 
                ],
                'OTHER' : [
                    GraphViz, Picture
                ],
            }
        )

OM = DemoObjectModel()
OM.fetch()

# source = OM.source()
# with open('./src/Demo/Demo.svg', 'w') as file:
#     file.write(source)

draw = OM.html()
with open('./src/Demo/Demo.html', 'w') as file:
    file.write(draw)
