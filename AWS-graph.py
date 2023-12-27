from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

import boto3

from graphviz import Digraph

fType  = 0
fId    = 1
fOwner = 2
fIn    = 3
fOut   = 4

class cParent:
    Icon = "AWS"
    Show = True
    Draw = (True, False, True, True)
    Color = "#A9DFBF"

    def __init__(self, Data, parent, index, resp):
        if parent != None:
            setattr(self, "_Parent", parent)
            setattr(self, "_Index" , index )

        fields = type(self).Fields()
        for key, cfg in fields.items():
            if not key in resp:
                continue
            value = resp[key]
            field = fields[key][fType]
            if type(field) == list:
                if len(field) == 0:
                    #setattr(self, key, value)
                    continue
                if field[0] == str:
                    continue
                else:
                    field[0].LoadObjects(Data, field[0], self, value)
            elif field == list:
                continue
            #elif field == str or field == cEC2 or field == cReservation:
            elif type(field) == dict:
                tkkey, tkval = next(iter(field.items()))
                for pair in value:
                    setattr(self, "Tag_" + pair[tkkey], pair[tkval])
                continue
            else:
                #print(f"{key} = {value}")
                setattr(self, key, value)
        
        self.items = []

    def FieldsOfAKind(self, kind):
        return (key for key, value in self.Fields().items() if value[kind])

    def GetId(self):
        field = next(self.FieldsOfAKind(fId), None)
        return getattr(self, field)

    def GetOwner(self, Data):
#       field = next(((key, value[0]) for key, value in self.Fields().items() if value[fOwner]), (None, None))
        field = next(self.FieldsOfAKind(fOwner), None)
        if field == None: return None
        
        id = getattr(self, field, None)
        if id == None: return None

        clss = self.Fields()[field][fType]

        if not id in Data[clss] : return None

        owner = Data[clss][id]
        return owner

    def GetView(self):
        return f"{getattr(self, 'Tag_Name', type(self).__name__[1:])}"

    @staticmethod
    def LoadObjects(Data, Class, parent = None, lst = None):
#        self.Objects = [self.Class(obj) for obj in self.GetObjects(parent)]
        if not Class in Data:
            Data[Class] = {}

        els = Class.GetObjects(parent, lst)
        for index, el in enumerate(els):
            obj = Class(Data, parent, index, el)
            Data[Class][obj.GetId()] = obj

class cRoot(cParent):
    def __init__(self, Data):
        super().__init__(Data, None, 0, {"Id": "root-" + 17*"0"})

    @staticmethod
    def Fields():
        return {"Id" : (cRoot,True,False,False,False)}
        
class cReservation(cParent): 
    Icon = "EC2"
    Show = False

    @staticmethod
    def Fields():
        return {
                    "ReservationId" : (cReservation,True,False,False,False),
                    "OwnerId"       : (str,False,False,False,False),
                    "Groups"        : ([str],False,False,False,False), # !!!
                    "Instances"     : ([cEC2],False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_instances()['Reservations']
    
class cEC2(cParent): 
    Draw = (True, True, True, True)
    Icon = "EC2"
    Color = "#FFC18A"

    @staticmethod
    def Fields():
        return {
                    "InstanceId" : (cEC2,True,False,False,False),
                    "InstanceType" : (str,False,False,False,False),
                    "PublicIpAddress" : (str,False,False,False,False),
                    "PrivateIpAddress" : (str,False,False,False,False),
                    "SubnetId" : (cSubnet,False,True,False,False),
                    'PlatformDetails' : (str,False,False,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                    'VpcId': (cVpc,False,False,False,False) 
                }
    
# 'AmiLaunchIndex': 0
# 'ImageId': 'ami-0669b163befffbdfc'
# 'KeyName': 'key-antony'
# 'LaunchTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'Monitoring': {'State': 'disabled'}
# 'Placement': {'AvailabilityZone': 'eu-central-1b', 'GroupName': '', 'Tenancy': 'default'}
# 'PrivateDnsName': 'ip-10-222-2-11.eu-central-1.compute.internal'
# 'ProductCodes': []
# 'PublicDnsName': ''
# 'State': {'Code': 16, 'Name': 'running'}
# 'StateTransitionReason': ''
# 'Architecture': 'x86_64'
# 'BlockDeviceMappings': [{'DeviceName': '/dev/xvda', 'Ebs': {...}}]
# 'ClientToken': '5db5facc-d068-410c-a526-29dba78f8184'
# 'EbsOptimized': False
# 'EnaSupport': True
# 'Hypervisor': 'xen'
# 'NetworkInterfaces': [{'Attachment': {...}, 'Description': '', 'Groups': [...], 'Ipv6Addresses': [...], 'MacAddress': '06:02:cb:61:9c:7b', 'NetworkInterfaceId': 'eni-06ef5645d896ee146', 'OwnerId': '047989593255', 'PrivateIpAddress': '10.222.2.11', 'PrivateIpAddresses': [...], ...}]
# 'RootDeviceName': '/dev/xvda'
# 'RootDeviceType': 'ebs'
# 'SecurityGroups': [{'GroupName': 'secgrup-antony', 'GroupId': 'sg-0e050b1cd54e6fcc8'}]
# 'SourceDestCheck': True
# 'VirtualizationType': 'hvm'
# 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}
# 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}
# 'HibernationOptions': {'Configured': False}
# 'MetadataOptions': {'State': 'applied', 'HttpTokens': 'required', 'HttpPutResponseHopLimit': 2, 'HttpEndpoint': 'enabled', 'HttpProtocolIpv6': 'disabled', 'InstanceMetadataTags': 'disabled'}
# 'EnclaveOptions': {'Enabled': False}
# 'BootMode': 'uefi-preferred'
# 'UsageOperation': 'RunInstances'
# 'UsageOperationUpdateTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'PrivateDnsNameOptions': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}
# 'MaintenanceOptions': {'AutoRecovery': 'default'}
# 'CurrentInstanceBootMode': 'legacy-bios'

    
    @staticmethod
    def GetObjects(parent, lst):
        return lst

    def GetAdd(self):
        return f"{getattr(self, "PlatformDetails")}"


class cInternetGateway(cParent): 
    Icon = "Gateway"
    Color = "#F9BBD9"

    @staticmethod
    def Fields():
        return {
                    "InternetGatewayId" : (cInternetGateway,True,False,False,False),
                    'OwnerId' : (str,False,False,False,False),
                    'Attachments' : ([cInternetGatewayAttachment],False,False,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_internet_gateways()['InternetGateways']

class cInternetGatewayAttachment(cParent): 
    Icon = "Gateway"
    Draw = (True, False, False, False)
    Color = "#F488BB"

    @staticmethod
    def Fields():
        return {
                    "VpcId" : (cVpc,False,False,False,True),
                    'State' : (str,False,False,False,False),
                }
    
    def GetView(self):
        return f"Attach[{self._Index}]"

    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
    def GetId(self):
        return f"{self._Parent.GetId()}-{self._Index}"

    def GetOwner(self, Data):
        return self._Parent

class cNATGateway(cParent): 
    Icon = "NATGateway"
    Draw = (True, False, True, True)

    @staticmethod
    def Fields():
        return {
                    "NatGatewayId" : (cNATGateway, True ,False,False,False),
                    "SubnetId"     : (cSubnet    , False,True ,False,False),
                    "State"        : (str        , False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_nat_gateways()['NatGateways']
    
    def GetView(self):
        return f"NAT"

class cSecurityGroup(cParent): 
    @staticmethod
    def Fields():
        return {
                    "GroupName" : (str ,False,False,False,False),
                    "GroupId"   : (str ,True,False,False,False),
                    "VpcId"     : (cVpc,False,True,False,False),
#                    IpPermissions\IpRanges\
                        # for permission in group['IpPermissions']:
                        #     print(f"- From Port: {permission.get('FromPort', 'N/A')}")
                        #     print(f"  To Port: {permission.get('ToPort', 'N/A')}")
                        #     print(f"  Protocol: {permission.get('IpProtocol', 'N/A')}")
                        #     print("  IP Ranges:")
                        #     for ip_range in permission.get('IpRanges', []):
                        #         print(f"  - {ip_range.get('CidrIp', 'N/A')}")
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_security_groups()['SecurityGroups']
    
class cSubnet(cParent): 
    Draw = (True, True, True, True)
    Color = '#D4E6F1'

    @staticmethod
    def Fields():
        return {
                    "SubnetId" : (cSubnet,True,False,False,False),
                    "CidrBlock" : (str,False,False,False,False),
                    "VpcId" : (cVpc,False,True,False,False),
                    "AvailabilityZone" : (str,False,False,False,False), ##!!!!!!!!!!!!!!!
                    'AvailabilityZoneId' : (str,False,False,False,False), ##!!!!!!!!!!!!!!!
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
    
# 'AvailableIpAddressCount': 251
# 'DefaultForAz': False
# 'MapPublicIpOnLaunch': False
# 'MapCustomerOwnedIpOnLaunch': False
# 'State': 'available'
# 'OwnerId': '047989593255'
# 'AssignIpv6AddressOnCreation': False
# 'Ipv6CidrBlockAssociationSet': []
# 'SubnetArn': 'arn:aws:ec2:eu-central-1:047989593255:subnet/subnet-06678d33e23eba72f'
# 'EnableDns64': False
# 'Ipv6Native': False
# 'PrivateDnsNameOptionsOnLaunch': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}


    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_subnets()['Subnets']
    
    def GetAdd(self):
        return f"{getattr(self, "CidrBlock", "")}"


class cNetworkAcl(cParent): 
    Icon = "NetworkAccessControlList"

    @staticmethod
    def Fields():
        return {
                    "NetworkAclId" : (cNetworkAcl,True,False,False,False),
                    'IsDefault': (bool,False,False,False,False),
                    'VpcId': (cVpc,False,True,False,False),
                    'OwnerId': (str,False,True,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
                    # 'Associations': [{'NetworkAclAssociationId': 'aclassoc-0c867a11b811c5be1', 'NetworkAclId': 'acl-0334606b00fe7551c', 'SubnetId': 'subnet-06678d33e23eba72f'}]
                    # 'Entries': [{'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}]
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_network_acls()['NetworkAcls']
    

class cRouteTable(cParent): 
    Draw = (True, False, True, True)
    Icon = "RouteTable"
    Color = "#A9DFBF"

    @staticmethod
    def Fields():
        return {
                    "RouteTableId" : (cRouteTable,True,False,False,False),
                    "VpcId" : (cVpc,False,True,False,False),
                    "Routes" : ([cRoute],False,False,False,False),
                    "Associations" : ([cRouteTableAssociation],False,False,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
# 'Associations': [{'Main': True, 'RouteTableAssociationId': 'rtbassoc-0fcb79c6b321c4521', 'RouteTableId': 'rtb-0c7697e0d2c9ba149', 'AssociationState': {...}}]
# 'PropagatingVgws': []
# 'OwnerId': '047989593255'
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_route_tables()['RouteTables']
    
class cRouteTableAssociation(cParent):
    Color = "#7CCF9C"

    @staticmethod
    def Fields():
        return {
                    'RouteTableAssociationId': (cRouteTableAssociation,True,False,False,False),
                    'RouteTableId': (cRouteTable,False,True,False,False),
                    'SubnetId': (cSubnet,False,False,True,False),
                    'AssociationState': (str,False,False,False,False), #!!!
                    'Main': (bool,False,False,False,False),
                } # +

    @staticmethod
    def GetObjects(parent, lst):
        return lst

    def GetView(self):
        return f"Assoc[{self._Index}]"



class cRoute(cParent): 
    Draw = (True, True, True, False)
    Icon = "Route"
    Color = "#7CCF9C"

    @staticmethod
    def Fields():
        return {
                    "DestinationCidrBlock" : (str,False,False,False,False),
                    "GatewayId" : (cInternetGateway,False,False,True,False),
                    "InstanceId" : (cEC2,False,False,True,False),
                    "NatGatewayId" : (cNATGateway,False,False,True,False),
                    "NetworkInterfaceId" : (cNetworkInterface,False,False,True,False),
                    'Origin': (str,False,False,False,False),
                    'State': (str,False,False,False,False),

                    "GatewayId_local" : (cVpc,False,False,True,False),
                } # +

    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
    def GetId(self):
        return f"{self._Parent.GetId()}-{self._Index}"

    def GetOwner(self, Data):
        return self._Parent

    def GetView(self):
        return f"Route[{self._Index}]"

    def GetAdd(self):
        return f"{self.DestinationCidrBlock}"

    def __init__(self, Data, parent, index, resp):

        super().__init__(Data, parent, index, resp)

        if hasattr(self, "GatewayId") and self.GatewayId == "local":
            self.GatewayId = None
            setattr(self, "GatewayId_local", self._Parent.VpcId)


class cVpc(cParent): 
    Draw = (True, True, True, True)
    Icon = "VPC"
    Color = '#E3D5FF'

    @staticmethod
    def Fields():
        return {
                    "VpcId"           : (cVpc,True,False,False,False),
                    "NetworkAclId"    : (cNetworkAcl,False,False,False,False),
                    'CidrBlock'       : (str,False,False,False,False),
                    'DhcpOptionsId'   : (str,False,False,False,False), #'dopt-0de83e37b426fcfda'
                    'State'           : (str,False,False,False,False),
                    'OwnerId'         : (str,False,False,False,False), #'047989593255'
                    'InstanceTenancy' : (str,False,False,False,False),
#                    'CidrBlockAssociationSet' : [{'AssociationId': 'vpc-cidr-assoc-070bb...bcc9c9695b', 'CidrBlock': '10.222.0.0/16', 'CidrBlockState': {...}}],
                    'IsDefault'       : (bool,False,False,False,False),
                    'Tags'            : ({"Key" : "Value"},False,False,False,False)
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_vpcs()['Vpcs']
    
    def GetAdd(self):
        return f"{self.CidrBlock}"
    
class cVpcEntry(cParent): 
    Icon = "VPC"

    @staticmethod
    def Fields():
        return {
                    "RuleNumber" : (int,False,False,False,False),
                    "Protocol"   : (str,False,False,False,False),
                    "PortRange"  : (str,False,False,False,False),
                    "RuleAction" : (str,False,False,False,False),
                    "CidrBlock"  : (str,False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
class cNetworkInterface(cParent): 
#    Icon = "network.VPCElasticNetworkInterface"

    @staticmethod
    def Fields():
        return {
                    "NetworkInterfaceId" : (cNetworkInterface,True,False,False,False),
                    "Status"             : (str,False,False,False,False),
                    "Attachment"         : (str,False,False,False,False), #    print("Attachment ID:", network_interface['Attachment']['AttachmentId'])
                    "VpcId"              : (cVpc,False,False,False,False),
                    "SubnetId"           : (cSubnet,False,False,False,False),
                    "PrivateIpAddresses" : (str,False,False,False,False), # print("Private IP Addresses:", [private_ip['PrivateIpAddress'] for private_ip in network_interface['PrivateIpAddresses']])
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_network_interfaces()['NetworkInterfaces']
    
class cS3(cParent): 
    Icon = "S3"

    @staticmethod
    def Fields():
        return {
                    "Name" : (cS3,True,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('s3').list_buckets()['Buckets']


class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('AWS-graph.ui', self)

        self.Graph.setScene(QGraphicsScene(self))

        self.bDraw.clicked.connect(self.Draw)

        self.Draw()

    def NodeLabel(self, obj):
        draw  = type(obj).Draw
        color = type(obj).Color

        res = ""
        if draw[0]: res = res + f'''
                <TR>
                    <TD BGCOLOR="{color}" PORT="p0"><B>{obj.GetView()}</B></TD>
                </TR>
        '''
        if draw[1]: res = res + f'''
                 <TR>
                     <TD BGCOLOR="white" PORT="p1"><B>{obj.GetAdd()}</B></TD>
                 </TR>
        '''
        if draw[2]: res = res + f'''
                <TR>
                    <TD BGCOLOR="white" PORT="p2"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
                </TR>
        '''
        if draw[3]: res = res + f'''
                <TR>
                    <TD BGCOLOR="{color}" PORT="p3"><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
                </TR>
        '''
        
        return f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
            {res}
            </TABLE>
        >'''

    def ClusterLabel(self, obj):
        draw = obj.Draw

        res0 = ""
        if draw[2]: res0 = res0 + f'''
                    <TD ROWSPAN="3"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
        '''
        if draw[0]: res0 = res0 + f'''
                    <TD><B>{obj.GetView()}</B></TD>
        '''
        res0 = f'''
                <TR>
                    {res0}
                </TR>
        '''

        res1 = ""
        if draw[1]: res1 = res1 + f'''
                <TR>
                    <TD><FONT POINT-SIZE="7.0">{obj.GetAdd()}</FONT></TD>
                </TR>
        '''
        if draw[3]: res1 = res1 + f'''
                <TR>
                    <TD><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
                </TR>
        '''

        return f'''<
            <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
                {res0}
                {res1}
            </TABLE>
        >'''

    def DrawRec(self, par):
        for clss, list in self.Data.items():
            if not clss.Show: continue

            for id, obj in list.items():
                if par == None:
                    if hasattr(obj, "_Owner") : continue
                else:
                    if (not hasattr(obj, "_Owner") or obj._Owner != par) \
                    : continue
                        #and obj != par \

                if not hasattr(par, "_Digraph"):
                    name = "cluster_" + obj.GetId()[-17:]
                    par._Context = par._Owner._Digraph.subgraph(name=name)
                    par._Digraph = par._Context.__enter__()
#                    par._Digraph.attr(label='cluster\n' + par.GetId()) # + par.GetId()
                    par._Digraph.attr(label=self.ClusterLabel(par)) # + par.GetId()
                    par._Digraph.attr(style = 'filled', fillcolor = type(par).Color)

                    par._Digraph.node(name=par.GetId(), shape='point', width='0.1')
                
                
                if len(obj.items) == 0:
                    par._Digraph.node(name=obj.GetId(), shape='plaintext', label=self.NodeLabel(obj))
                else:
                    self.DrawRec(obj)

                #print(f"{par}.{par.GetId()} -> {obj}.{obj.GetId()} ")
        
        if hasattr(par, "_Context"):
            par._Context.__exit__(None, None, None)
            par._Context = None

        if hasattr(par, "_Digraph"):
            par._Digraph = None


    def Draw(self):
        
        self.Data = {}

        root = cRoot(self.Data)
        cParent.LoadObjects(self.Data, cInternetGateway)
        cParent.LoadObjects(self.Data, cVpc        )
        cParent.LoadObjects(self.Data, cSubnet     )
        cParent.LoadObjects(self.Data, cReservation)
        cParent.LoadObjects(self.Data, cNATGateway )
        cParent.LoadObjects(self.Data, cNetworkAcl )
        cParent.LoadObjects(self.Data, cRouteTable )

        for clss, lst in self.Data.items():
            for id, obj in lst.items():
                owner = obj.GetOwner(self.Data)
                if owner == None:
                    owner = root

                # if obj.ParentField != None:
                #     parcl = clss.Fields()[obj.ParentField][fType]
                #     if hasattr(obj, obj.ParentField):
                #         if obj.ParentField == "_Parent":
                #             owner = obj._Parent
                #         else:
                #             parid = getattr(obj, obj.ParentField)
                #             owner = self.Data[parcl][parid]

                obj._Owner = owner
                owner.items.append(obj)

        dot = Digraph('AWS_Structure', format='png')

        root._Digraph = dot

        self.DrawRec(root)


        for clss, lst in self.Data.items():
            for id, obj in lst.items():
                objid = obj.GetId()

                for field in obj.FieldsOfAKind(fIn):
                    corr = getattr(obj, field, None)
                    if corr == None: continue
                    dot.edge(objid, corr, label = field)

                for field in obj.FieldsOfAKind(fOut):
                    corr = getattr(obj, field, None)
                    if corr == None: continue
                    dot.edge(corr, objid, label = field + "<")


        # Сохраняем диаграмму в файл
        dot.render('AWS-graph', format='png', cleanup=True)

        #pixmap = QPixmap("AWS-graph.png")
        #pixmap_item = QGraphicsPixmapItem(pixmap)
        #self.Graph.scene().addItem(pixmap_item)

        #self.Graph.fitInView(self.Graph.scene().sceneRect()) # Autoscaling

#        self.close()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
#    widget.show()
#    app.exec_()
