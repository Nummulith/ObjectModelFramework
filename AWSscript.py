from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi

from awsDraw import Draw
from awsClasses import AWS, Const, Classes, awsClassesNW, awsClassesSN, awsClassesObj

FilePath = "AWSScript.xml"

def Clear():
    aws = AWS(FilePath)
    aws.Save()
    aws.Clear()

def Print():
    aws = AWS(FilePath)
    aws.Print()

def DrawScript():
    aws = AWS(FilePath, False, False)
    aws.Load()
    aws.Save()
    Draw(aws)

def Test():
    NYTask()
    DrawScript()
    Clear()

def DrawAll():
    aws = AWS("awsFull.xml", False, False)
    aws.Fetch()
    aws.Save()
    Draw(aws)

def NYTask():
    aws = AWS(FilePath)

    Name = "Pavel-Eresko"

    key = aws.KeyPair.Create(Name)

    vpc = aws.Vpc.Create(Name, '10.3.0.0/16')
    
    sg  = aws.SecurityGroup.Create(Name, f"Security group for {Name}", vpc)
    aws.SecurityGroupRule.Create(sg, 'tcp', 22, '0.0.0.0/0') # SSH (22)
    aws.SecurityGroupRule.Create(sg, 'tcp', 80, '0.0.0.0/0') # HTTP (80)

    igw = aws.InternetGateway.Create(Name)
    aws.InternetGatewayAttachment.Create(igw, vpc)


    # Private subnet
    Name0 = Name + "-Private"
    snPublic = aws.Subnet.Create(Name0, vpc, '10.3.0.0/24')

    rtbPublic  = aws.RouteTable.Create(Name0, vpc)
    aws.RouteTableAssociation.Create(rtbPublic, snPublic)
    aws.Route.Create(rtbPublic, "0.0.0.0/0", igw)

    ec20 = aws.EC2.Create(
        Name0,
        Const["EC2.ImageId.Linux"], Const["EC2.InstanceType.t2.micro"],
        key, snPublic, [sg],
        "10.3.0.10",
        Const["EC2.UserData.Apache"],
    )


    # Public subnet
    Name1 = Name + "-Public"
    snPrivate = aws.Subnet.Create(Name1, vpc, '10.3.1.0/24')

    eip = aws.ElasticIP.Create(Name1)
    nat = aws.NATGateway.Create(Name1, snPrivate, eip)

    rtbPrivate  = aws.RouteTable.Create(Name1, vpc)
    aws.RouteTableAssociation.Create(rtbPrivate, snPrivate)
    aws.Route.Create(rtbPrivate, "0.0.0.0/0", None, nat)

    ec21 = aws.EC2.Create(
        Name1,
        Const["EC2.ImageId.Linux"], Const["EC2.InstanceType.t2.micro"],
        key, snPrivate, [sg],
        "10.3.1.10",
        Const["EC2.UserData.Apache"],
    )


class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('awsScript.ui', self)

        # <widget class="QGraphicsView" name="Graph">
        # self.Graph.setScene(QGraphicsScene(self))

        self.bClear  .clicked.connect(Clear  )
        self.bNYTask .clicked.connect(NYTask )
        self.bDrawAll.clicked.connect(DrawAll)
        self.bDraw   .clicked.connect(DrawScript)
        self.bTest   .clicked.connect(Test   )

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
