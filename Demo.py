"""
Object Model Framework Demo Module

This module representing a behaivour of Object Model Framework

Classes:
    ParentClass, InheritedClass, Listed, Drawing, GraphViz, Picture

Usage:
    Run the module. See the graph output in Demo.png file.

Author: Pavel ERESKO
"""

from ObjectModel import *

class DemoItem(ObjectModelItem):
    Icon = "Demo\\Y3A-Icon"
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

class GraphViz(DemoItem):
    Icon = "Demo\\GraphvizIcon"
    Color = "#adcdd9"

    @staticmethod
    def fields():
        return {
                    'Id': (ParentClass, FIELD.ID),
                    'Name': (ParentClass, FIELD.VIEW),
                    'Link': (Drawing, FIELD.LINK),
                }

class ParentClass(DemoItem):
    Icon = "Demo\\ObjectModel-Icon"
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
    Icon = "Demo\\Drawing-Icon"
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
    Icon = "Demo\\Demo"
    Draw = DRAW.ICON

    @staticmethod
    def fields():
        return {
                    'Id': (Picture, FIELD.ID),
                    'Link': (Drawing, FIELD.LINK_IN),
                }

class InheritedClass(DemoItem):
    Icon = "Demo\\Obj-Icon"
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
            "Demo",
            True,
            True,
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
                        "Icon" : "yet-another-aws-analyse-icon",
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
OM.draw()
