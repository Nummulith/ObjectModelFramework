from xml.dom import minidom
import xml.etree.ElementTree as ET

from AWSclasses import *

class AWSClassWrapper:
    def __init__(self, aws, clss):
        self.aws = aws
        self.Class = clss
        self.List = []

    def __getitem__(self, key):
        return self.List[key]

    def __setitem__(self, key, value):
        self.List[key] = value

    def Count(self):
        return len(self.List)

    def View(self):
        return self.Class.GetClassView()
    
    def Create(self, *args):
        try:
            id = self.Class.Create(*args)
        except Exception as e:
            print(f"{self.View()}.Create: An exception occurred: {type(e).__name__} - {e}")
            return None

        if id != None:
            self.List.append(id)
            self.aws.Save()

        return id

    def Delete(self, id):
        if hasattr(self.Class, "SkipDeletionOnClear") and self.Class.SkipDeletionOnClear:
            pass
        else:
            try:
                self.Class.Delete(id)
            except Exception as e:
                print(f"{self.View()}.Delete: An exception occurred: {type(e).__name__} - {e}")
                return

        if id in self.List:
            self.List.remove(id)
            self.aws.Save()
    
    def Clear(self):
#       for id in self.List:
#           self.Delete(id)
#       self.List.clear()

        index = len(self.List) - 1
        while index >= 0:
            id = self.List[index]
            self.Delete(id)
            index -= 1


    def Print(self):
        if len(self.List) == 0 : return

        print(f"  {self.View()}: {len(self.List)}")
        for id in self.List:
            print(id)

class AWS:
    def __init__(self, path):
        self.Path = path

        for clss in awsClasses:
            wrapper = AWSClassWrapper(self, clss)
            name = wrapper.View()
            setattr(self, name, wrapper)

        self.Load()

    def Clear(self):
        for clss in awsClasses:
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.Clear()

    def Print(self):
        for clss in awsClasses:
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.Print()

    def prettify(self, elem):
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")


    def Save(self):
        root = ET.Element("AWS")

        for clss in awsClasses:
            name = clss.GetClassView()
            wrapper = getattr(self, name)

            category_element = ET.SubElement(root, name)
            for identifier in wrapper.List:
                id_element = ET.SubElement(category_element, f"id")
                id_element.text = identifier


        tree = self.prettify(root)
        with open(self.Path, "w") as file:
            file.write(tree)

    def Load(self):
        with open(self.Path, 'r') as file:
            xml_string = file.read()
        root = ET.fromstring(xml_string)

        for element in root:
            wrapper = getattr(self, element.tag)
            wrapper.List = [child.text for child in element]
