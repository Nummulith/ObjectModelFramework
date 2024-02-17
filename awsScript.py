from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi

from awsClasses import AWS

import importlib

class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('awsScript.ui', self)

        self.bExample    .clicked.connect(self.Example)
        self.bFetch      .clicked.connect(self.Fetch)
        self.bRelease    .clicked.connect(self.Release)
        self.bDraw       .clicked.connect(self.Draw)
        self.bDelete     .clicked.connect(self.Delete)

        self.leProfile.setText("TS") # TS, DCI
        self.leFile   .setText("awsScript")
        self.leClasses.setText("RouteTable")
        self.leExample.setText("RDS")

    def GetAWS(self, DoAutoLoad = True, DoAutoSave = True):
        return AWS(
            self.leProfile.text(),
            self.leFile   .text(),
            DoAutoLoad,
            DoAutoSave
        )

    def ExampleScript(self, aws):
        module_and_function_name = self.leExample.text()
        module = importlib.import_module("Examples." + module_and_function_name)
        func = getattr(module, module_and_function_name)
        func(aws)

    def Example(self):
        aws = self.GetAWS()
        self.ExampleScript(aws)

    def Fetch(self):
        aws = self.GetAWS(True, False)
        aws.Fetch(self.leClasses.text())
        aws.Save()

    def Release(self):
        aws = self.GetAWS(True, False)
        aws.Release(self.leClasses.text())
        aws.Save()

    def Draw(self):
        aws = self.GetAWS(False, False)
        aws.Load()
        aws.Save()
        aws.Draw()

    def Delete(self):
        aws = self.GetAWS()
        aws.Save() #
        aws.DeleteAll()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
