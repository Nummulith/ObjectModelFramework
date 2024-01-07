import boto3

fType  = 0
fId    = 1
fOwner = 2
fIn    = 3
fOut   = 4

def region():
    return "eu-central-1"
    return "eu-west-1"

def botoec2():
    return boto3.client('ec2', region_name = region())

def botos3():
    return boto3.client('s3' , region_name = region())

def addTag(resource_id, name, value):
    botoec2().create_tags(
        Resources=[resource_id],
        Tags=[
            {
                'Key': name,
                'Value': value
            },
        ]
    )

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

        if field == None:
            return f"{self._Parent.GetId()}-{self._Index}"
        
        return getattr(self, field)

    def GetOwner(self, Data):
#       field = next(((key, value[0]) for key, value in self.Fields().items() if value[fOwner]), (None, None))
        field = next(self.FieldsOfAKind(fOwner), None)
        if field != None:
            id = getattr(self, field, None)
            if id == None: return None

            clss = self.Fields()[field][fType]

            if not id in Data[clss] : return None

            owner = Data[clss][id]
            return owner

        if hasattr(self, "_Parent"):
            return self._Parent

        return None

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

    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
    @staticmethod
    def Fields():
        return {}

    @staticmethod
    def CLIAdd(args = None):
        return "<?>"

    @staticmethod
    def CLIDel(args = None):
        return "<?>"


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
        return botoec2().describe_instances()['Reservations']


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

    def GetExt(self):
        return f"{getattr(self, 'PlatformDetails', '-')}"


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
                } # +
    
    @staticmethod
    def GetObjects(parent, lst):
        return botoec2().describe_internet_gateways()['InternetGateways']


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
        return botoec2().describe_nat_gateways()['NatGateways']
    
    def GetView(self):
        return f"NAT"


class cSecurityGroup(cParent): 
    @staticmethod
    def Fields():
        return {
                    "GroupId"    : (str ,True,False,False,False),
                    "GroupName"  : (str ,False,False,False,False),
                    'Description': (str ,False,False,False,False),
                    "VpcId"      : (cVpc,False,True,False,False),
                    'OwnerId'    : (str ,False,False,False,False),
                    "IpPermissions" : ([cIpPermission],False,False,False,False),
#'IpPermissionsEgress': [{'IpProtocol': '-1', 'IpRanges': [...], 'Ipv6Ranges': [...], 'PrefixListIds': [...], 'UserIdGroupPairs': [...]}]
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return botoec2().describe_security_groups()['SecurityGroups']

    def GetView(self):
        return f"{self.GroupName}"


class cIpPermission(cParent): 
    @staticmethod
    def Fields():
        return {
            'FromPort': (int,False,False,False,False),
            'IpProtocol': (str,False,False,False,False),
#            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
#            'Ipv6Ranges': []
#            'PrefixListIds': []
            'ToPort': (int,False,False,False,False),
#            'UserIdGroupPairs': []
        }
    
    def GetView(self):
        res = ""
        res = f"{res}{getattr(self, 'IpProtocol', '')}"
        if hasattr(self, "FromPort"):
            ips = f"{self.FromPort}"
            if self.FromPort != self.ToPort:
                ips = f"{ips} - {self.ToPort}"
            res = f"{res}({ips})"
            
        return res


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
        return botoec2().describe_subnets()['Subnets']
    
    def GetExt(self):
        return f"{getattr(self, 'CidrBlock', '-')}"


class cNetworkAcl(cParent): 
    Icon = "NetworkAccessControlList"

    @staticmethod
    def Fields():
        return {
                    "NetworkAclId" : (cNetworkAcl,True,False,False,False),
                    'IsDefault': (bool,False,False,False,False),
                    'VpcId': (cVpc,False,True,False,False),
                    'OwnerId': (str,False,True,False,False),
                    'Entries': ([cNetworkAclEntry],False,True,False,False),  #),[{'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}]
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
                    # 'Associations': [{'NetworkAclAssociationId': 'aclassoc-0c867a11b811c5be1', 'NetworkAclId': 'acl-0334606b00fe7551c', 'SubnetId': 'subnet-06678d33e23eba72f'}]
    
    @staticmethod
    def GetObjects(parent, lst):
        return botoec2().describe_network_acls()['NetworkAcls']


class cNetworkAclEntry(cParent): 
    Draw = (True, True, False, False)
    Icon = "NetworkAccessControlList"

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
    
    def GetView(self):
        return f"{self.RuleNumber}:{self.Protocol} {getattr(self, 'PortRange', '')}"

    def GetExt(self):
        return f"{self.RuleAction} - {getattr(self, 'CidrBlock', '*')}"


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
                    'OwnerId': (str,False,True,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                    # 'PropagatingVgws': []
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return botoec2().describe_route_tables()['RouteTables']


class cRouteTableAssociation(cParent):
    Color = "#7CCF9C"

    @staticmethod
    def Fields():
        return {
                    'RouteTableAssociationId': (cRouteTableAssociation,True,False,False,False),
                    'RouteTableId': (cRouteTable,False,True,False,False),
                    'SubnetId': (cSubnet,False,False,False,True),
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

    def GetExt(self):
        return f"{getattr(self, 'DestinationCidrBlock', '-')}"

    def __init__(self, Data, parent, index, resp):

        super().__init__(Data, parent, index, resp)

        if hasattr(self, "GatewayId") and self.GatewayId == "local":
            self.GatewayId = None
            setattr(self, "GatewayId_local", self._Parent.VpcId)


class cVpc(cParent): 
    Draw = (True, True, True, True)
    Icon = "VPC"
    Color = '#E3D5FF'
    Prefix = "vpc"

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
        return botoec2().describe_vpcs()['Vpcs']
    
    def GetExt(self):
        return f"{getattr(self, 'CidrBlock', '-')}"
    
    @staticmethod
    def Add(Name, CidrBlock):
        return "vpc_id"
    
        response = botoec2().create_vpc(CidrBlock=CidrBlock)
        vpc_id = response['Vpc']['VpcId']

        addTag(vpc_id, "Name", f"{cVpc.Prefix}-{Name}")

        return vpc_id
    
    @staticmethod
    def Del(VpcId):
        return None
        botoec2().delete_vpc(VpcId = VpcId)


class cNetworkInterface(cParent): 
#    Icon = "network.VPCElasticNetworkInterface"

    @staticmethod
    def Fields():
        return {
                    "NetworkInterfaceId" : (cNetworkInterface,True,False,False,False),
                    "Status"             : (str,False,False,False,False),
                    "Attachment"         : (str,False,False,False,False), #    print("Attachment ID:", network_interface['Attachment']['AttachmentId'])
                    "VpcId"              : (cVpc,False,False,False,False),
                    "SubnetId"           : (cSubnet,False,True,False,False),
                    "PrivateIpAddresses" : (str,False,False,False,False), # print("Private IP Addresses:", [private_ip['PrivateIpAddress'] for private_ip in network_interface['PrivateIpAddresses']])
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return botoec2().describe_network_interfaces()['NetworkInterfaces']


class cS3(cParent): 
    Icon = "S3"

    @staticmethod
    def Fields():
        return {
                    "Name" : (cS3,True,False,False,False),
#                    'CreationDate': datetime.datetime(2023, 9, 29, 12, 28, 16, tzinfo=tzutc())
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return botos3().list_buckets()['Buckets']


class cElasticIP(cParent): pass


class cKeyPair(cParent):
    def Add(Name):
        response = botoec2().create_key_pair(KeyName = Name)
        private_key = response['KeyMaterial']
            
        with open(f'{Name}.pem', 'w') as key_file:
            key_file.write(private_key)
        return Name

    def Del(Name):
        botoec2().delete_key_pair(KeyName = Name)

    @staticmethod
    def CLIAdd(Name):
        return f"aws ec2 create-key-pair --key-name {Name} --query 'KeyMaterial' --output text > {Name}.pem"

    @staticmethod
    def CLIDel(Name):
        return f"aws ec2 delete-key-pair --key-name {Name}"
