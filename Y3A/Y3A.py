"""
AWS GUI Module

This module creates a graphical user interface (GUI) to showcase the capabilities
  of the ObjectModel Module with AWS set. It leverages the utility classes to offer
  a user-friendly interface for interacting with AWS services.

Features:
- Fetching information about objects structure in AWS cloud
- Getting AWS objects properties
- Drawing the diagram of dependencies between objects into png or svg file.

Usage:
Run the application

Author: Pavel ERESKO
"""

import importlib

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi

from awsClasses import AWS

from jinja2 import Template

class MyWidget(QWidget):
    """ GUI Window """

    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('Y3A/Y3A.ui', self)

        self.bExample .clicked.connect(lambda: self.example(func = None    ))
        self.bExUpdate.clicked.connect(lambda: self.example(func = "update"))
        self.bExClean .clicked.connect(lambda: self.example(func = "clean" ))

        self.bFetch   .clicked.connect(self.fetch)
        self.bRelease .clicked.connect(self.release)
        self.bDraw    .clicked.connect(self.draw)
        self.bDelete  .clicked.connect(self.delete)
        self.bShow    .clicked.connect(self.show_object)

        self.leProfile.setText("PE" )
        self.leFile   .setText("Y3A")
        self.leClasses.setText("All")
        self.leExample.setText("API")

        self.cbAWS .setChecked(True)
        self.cbLoad.setChecked(True)

        self.AWS = None

    def get_aws(self, do_auto_load = True, do_auto_save = True):
        """ Creating the AWS object """
        
        if self.AWS == None:
            self.AWS = AWS(
                self.leProfile.text(),
                self.leFile   .text(),
                do_auto_load, do_auto_save
            )

        return self.AWS

    def example(self, func = None):
        """ 'Example' button click """

        auto = self.cbLoad.isChecked()
        aws = self.get_aws(auto, auto) if self.cbAWS.isChecked() else None
#        aws.CallClasses = self.leClasses.text()

        module_name = self.leExample.text()
        function_name = module_name if func == None else func

        try:
            module = importlib.import_module(f"Examples." + module_name + "." + module_name)
            importlib.reload(module)

            func = getattr(module, function_name)
            func(aws)

        except Exception as e:
            print(f"Example: An exception occurred: {type(e).__name__} - {e}")

        if aws != None and auto:
            aws.save()

    def fetch(self):
        """ 'Fetch' button click """
        aws = self.get_aws(True, False)
        aws.fetch(self.leClasses.text())
        aws.save()

    def release(self):
        """ 'Release' button click """
        aws = self.get_aws(True, False)
        aws.release(self.leClasses.text())
        aws.save()

    def draw(self):
        """ 'Draw' button click """
        aws = self.get_aws(False, False)
        aws.load()
        aws.save()

        drawstr = aws.draw(self.leClasses.text())

        with open('Y3A\\render\\Y3A.svg', 'w') as file:
            file.write(drawstr)

        with open('Y3A\\Y3A.j2', 'r') as file: template_str = file.read()
        template = Template(template_str)
        output = template.render(content=drawstr)
        with open('Y3A\\render\\Y3A.html', 'w') as f: f.write(output)

    def delete(self):
        """ 'delete' button click """
        aws = self.get_aws()
        aws.save() #
        aws.delete_all()

    def show_object(self):
        """ 'show' button click """
        aws = self.get_aws()

        res_type = self.leType.text()
        res_id   = self.leId.text()

        # res_type = "CloudFormation_Stack"
        # res_id = "ECS-Console-V2-Service-wind-service-wind-0a454f7f"

        print("=========")
        print(f"{res_type}::{res_id}")

        try:
            wrap = getattr(aws, res_type)
            obj = wrap.fetch(res_id)[0]

        except Exception as e:
            print(f"show: An exception occurred: {type(e).__name__} - {e}")
            return

        for field in [attr for attr in dir(obj)]:
            if field.startswith('__') and field.endswith('__'):
                continue
            
            value = getattr(obj, field)

            if callable(value):
                continue

            print(f"{field}: {value}")

        print("")

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()

def Test():
    app = QApplication([])
    wgt = MyWidget()
    wgt.draw()
