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

class MyWidget(QWidget):
    """ GUI Window """

    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('Y3A/Y3A.ui', self)

        self.bExample    .clicked.connect(self.example)
        self.bFetch      .clicked.connect(self.fetch)
        self.bRelease    .clicked.connect(self.release)
        self.bDraw       .clicked.connect(self.draw)
        self.bDelete     .clicked.connect(self.delete)

        self.leProfile.setText("TS")
        self.leFile   .setText("Y3A")
        self.leClasses.setText("All")
        self.leExample.setText("Test")

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

    def example(self):
        """ 'Example' button click """

        auto = self.cbLoad.isChecked()
        aws = self.get_aws(auto, auto) if self.cbAWS.isChecked() else None
#        aws.CallClasses = self.leClasses.text()

        module_and_function_name = self.leExample.text()

        try:
            module = importlib.import_module("Examples." + module_and_function_name)
            importlib.reload(module)

            func = getattr(module, module_and_function_name)
            func(aws)

        except Exception as e:
            print(f"Example: An exception occurred: {type(e).__name__} - {e}")

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

        aws.draw(self.leClasses.text())

    def delete(self):
        """ 'delete' button click """
        aws = self.get_aws()
        aws.save() #
        aws.delete_all()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()

def Test():
    app = QApplication([])
    wgt = MyWidget()
    wgt.draw()
