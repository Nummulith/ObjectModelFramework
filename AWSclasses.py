import boto3

from xml.dom import minidom
import xml.etree.ElementTree as ET

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

def idpar(field, id):
    params = {}

    if id is not None:
        params[field] = [id]
    
    return params

class cParent:
    Icon = "AWS"
    Show = True
    Draw = (True, False, True, True)
    Color = "#A9DFBF"
    Prefix = ""

    def __init__(self, aws, parent, index, resp):
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
                    #field[0].LoadObjects(aws, field[0], self, value)
                    aws[field[0]].Append(None, self, value)
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

    def GetOwner(self, aws):
#       field = next(((key, value[0]) for key, value in self.Fields().items() if value[fOwner]), (None, None))
        field = next(self.FieldsOfAKind(fOwner), None)
        if field != None:
            id = getattr(self, field, None)
            if id == None: return None

            clss = self.Fields()[field][fType]

            if not id in aws[clss].Map : return None

            owner = aws[clss].Map[id]
            return owner

        if hasattr(self, "_Parent"):
            return self._Parent

        return None

    def GetView(self):
        return f"{getattr(self, 'Tag_Name', type(self).__name__[1:])}"


    @staticmethod
    def GetObjects(id):
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

    @classmethod
    def GetClassView(cls):
        return cls.__name__[1:]

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
    def GetObjects(id):
        resp = botoec2().describe_instances(**idpar('ReservationIds', id))
        return resp['Reservations']


class cEC2(cParent): 
    Prefix = "i"
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
    def GetObjects(id):
        resp = botoec2().describe_instances(**idpar('InstanceIds', id))
        return resp['Reservations'][0]["Instances"]


    def GetExt(self):
        return f"{getattr(self, 'PlatformDetails', '-')}"

    @staticmethod
    def Create(Name, ImageId, InstanceType, KeyName, SubnetId, Groups=[], PrivateIpAddress=None, UserData=""):
        id = botoec2().run_instances(
            ImageId = ImageId,
            InstanceType = InstanceType,
#           SubnetId = SubnetId,
            KeyName  = KeyName,
            NetworkInterfaces=[
                {
                    'SubnetId': SubnetId,
                    'DeviceIndex': 0,
                    'AssociatePublicIpAddress': True if PrivateIpAddress != None else False,
                    'PrivateIpAddress': PrivateIpAddress,
                    'Groups': Groups,
                }
            ],
            UserData = UserData,
            MinCount = 1,
            MaxCount = 1
        )['Instances'][0]['InstanceId']

        cTag.Create(id, "Name", f"{cEC2.Prefix}-{Name}")

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().terminate_instances(
            InstanceIds=[id]
        )
    


class cInternetGateway(cParent): 
    Prefix = "igw"
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
    def GetObjects(id):
        return botoec2().describe_internet_gateways(**idpar('InternetGatewayIds', id))['InternetGateways']


    @staticmethod
    def Create(Name):
        id = botoec2().create_internet_gateway()['InternetGateway']['InternetGatewayId']
        cTag.Create(id, "Name", f"{cInternetGateway.Prefix}-{Name}")
        return id

    @staticmethod
    def Delete(id):
        botoec2().delete_internet_gateway(InternetGatewayId = id)


class cInternetGatewayAttachment(cParent): 
    Prefix = "igw-attach"
    SkipDeletionOnClear = True
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
    def GetObjects(id):
        return lst
    
    def GetId(self):
        return f"{self._Parent.GetId()}-{self._Index}"

    def GetOwner(self, aws):
        return self._Parent

    @staticmethod
    def Create(InternetGatewayId, VpcId):
        resp = botoec2().attach_internet_gateway(InternetGatewayId=InternetGatewayId, VpcId=VpcId)
        return None

    @staticmethod
    def Delete(InternetGatewayId, VpcId):
        botoec2().detach_internet_gateway(InternetGatewayId=InternetGatewayId, VpcId=VpcId)


class cNATGateway(cParent): 
    Prefix = "nat"
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
    def GetObjects(id):
        return botoec2().describe_nat_gateways()['NatGateways']
    
    def GetView(self):
        return f"NAT"

    @staticmethod
    def Create(Name, SubnetId, AllocationId):
        id = botoec2().create_nat_gateway(SubnetId = SubnetId, AllocationId = AllocationId)['NatGateway']['NatGatewayId']

        cTag.Create(id, "Name", f"{cNATGateway.Prefix}-{Name}")

        waiter = botoec2().get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[id])
    
        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_nat_gateway(NatGatewayId = id)


class cSecurityGroup(cParent):
    Prefix = "sg"

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
    def GetObjects(id):
        return botoec2().describe_security_groups()['SecurityGroups']

    def GetView(self):
        return f"{self.GroupName}"

    @staticmethod
    def Create(Name, Description, Vpc):
        sgName = f"{cSecurityGroup.Prefix}-{Name}"

        id = botoec2().create_security_group(
            GroupName = Name,
            Description = Description,
            VpcId = Vpc
        )['GroupId']

        cTag.Create(id, "Name", sgName)


        # SRId = botoec2().authorize_security_group_ingress( # SSH (22)
        #     GroupId=id,
        #     IpPermissions=[
        #         {
        #             'IpProtocol': 'tcp',
        #             'FromPort': 22,
        #             'ToPort': 22,
        #             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        #         }
        #     ]
        # )["SecurityGroupRules"][0]["SecurityGroupRuleId"]

        # SRId = botoec2().authorize_security_group_ingress( # HTTP (80)
        #     GroupId=id,
        #     IpPermissions=[
        #         {
        #             'IpProtocol': 'tcp',
        #             'FromPort': 80,
        #             'ToPort': 80,
        #             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        #         }
        #     ]
        # )["SecurityGroupRules"][0]["SecurityGroupRuleId"]

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_security_group(
            GroupId=id
        )

class cSecurityGroupRule(cParent):
    Prefix = "sgr"
    SkipDeletionOnClear = True

    @staticmethod
    def Create(GroupId, IpProtocol, FromToPort, CidrIp):
        id = botoec2().authorize_security_group_ingress(
            GroupId=GroupId,
            IpPermissions=[
                {
                    'IpProtocol': IpProtocol,
                    'FromPort': FromToPort,
                    'ToPort': FromToPort,
                    'IpRanges': [{'CidrIp': CidrIp}]
                }
            ]
        )["SecurityGroupRules"][0]["SecurityGroupRuleId"]

        return id

    @staticmethod
    def Delete(security_group_id, id):
        botoec2().revoke_security_group_rule(security_group_id, id)(
            GroupId=id
        )

class cIpPermission(cParent): 
    Prefix = "ipp"

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
    Prefix = "subnet"
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
    def GetObjects(id):
        return botoec2().describe_subnets()['Subnets']
    
    def GetExt(self):
        return f"{getattr(self, 'CidrBlock', '-')}"

    @staticmethod
    def Create(Name, Vpc, CidrBlock):
        id = botoec2().create_subnet(
            VpcId = Vpc,
            CidrBlock = CidrBlock,
#           AvailabilityZone='us-east-1a'
        )["Subnet"]["SubnetId"]

        cTag.Create(id, "Name", f"{cSubnet.Prefix}-{Name}")

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_subnet(
            SubnetId = id
        )

    

class cNetworkAcl(cParent): 
    Prefix = "nacl"
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
    def GetObjects(id):
        return botoec2().describe_network_acls()['NetworkAcls']


class cNetworkAclEntry(cParent): 
    Prefix = "nacle"
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
    def GetObjects(id):
        return lst
    
    def GetView(self):
        return f"{self.RuleNumber}:{self.Protocol} {getattr(self, 'PortRange', '')}"

    def GetExt(self):
        return f"{self.RuleAction} - {getattr(self, 'CidrBlock', '*')}"


class cRouteTable(cParent): 
    Prefix = "rtb"
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
    def GetObjects(id):
        return botoec2().describe_route_tables()['RouteTables']

    @staticmethod
    def Create(Name, VpcId):
        id = botoec2().create_route_table(VpcId = VpcId)['RouteTable']['RouteTableId']
        cTag.Create(id, "Name", f"{cRouteTable.Prefix}-{Name}")
        return id

    @staticmethod
    def Delete(id):
        botoec2().delete_route_table(RouteTableId = id)                
    

class cRouteTableAssociation(cParent):
    Prefix = "rtba"
    SkipDeletionOnClear = True
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
    def GetObjects(id):
        return lst

    def GetView(self):
        return f"Assoc[{self._Index}]"

    @staticmethod
    def Create(SubnetId, RouteTableId):
        resp = botoec2().associate_route_table(SubnetId = SubnetId, RouteTableId = RouteTableId)
        return None

    @staticmethod
    def Delete(SubnetId, RouteTableId):
        
        response = botoec2().describe_route_tables(
            RouteTableIds=[RouteTableId]
        )
        associations = response['RouteTables'][0].get('Associations', [])

        association_id = ""
        for assoc in associations:
            if 'SubnetId' in assoc and assoc['SubnetId'] == SubnetId:
                association_id = assoc['RouteTableAssociationId']
                break

        response = botoec2().disassociate_route_table(
            AssociationId=association_id
        )

    

class cRoute(cParent): 
    SkipDeletionOnClear = True
    Prefix = "route"
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
    def GetObjects(id):
        return lst
    
    def GetId(self):
        return f"{self._Parent.GetId()}-{self._Index}"

    def GetOwner(self, aws):
        return self._Parent

    def GetView(self):
        return f"Route[{self._Index}]"

    def GetExt(self):
        return f"{getattr(self, 'DestinationCidrBlock', '-')}"

    def __init__(self, aws, parent, index, resp):

        super().__init__(aws, parent, index, resp)

        if hasattr(self, "GatewayId") and self.GatewayId == "local":
            self.GatewayId = None
            setattr(self, "GatewayId_local", self._Parent.VpcId)

    @staticmethod
    def Create(RouteTableId, DestinationCidrBlock, GatewayId = None, NatGatewayId = None):
        args = {
            "RouteTableId": RouteTableId,
            "DestinationCidrBlock": DestinationCidrBlock,
        }

        if GatewayId != None:
            args["GatewayId"] = GatewayId
        
        if NatGatewayId != None:
            args["NatGatewayId"] = NatGatewayId

        resp = botoec2().create_route(**args)
        return None
    
    @staticmethod
    def Delete(RouteTableId, DestinationCidrBlock):
        resp = botoec2().delete_route(
            RouteTableId = RouteTableId,
            DestinationCidrBlock = DestinationCidrBlock
        )


class cVpc(cParent): 
    Prefix = "vpc"
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
    def GetObjects(id):
        return botoec2().describe_vpcs()['Vpcs']
    
    def GetExt(self):
        return f"{getattr(self, 'CidrBlock', '-')}"
    
    @staticmethod
    def Create(Name, CidrBlock):
        id = botoec2().create_vpc(CidrBlock=CidrBlock)['Vpc']['VpcId']
        cTag.Create(id, "Name", f"{cVpc.Prefix}-{Name}")
        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_vpc(VpcId = id)
    
    @staticmethod
    def CLIAdd(Name, CidrBlock):
        return f"id000000001"

class cNetworkInterface(cParent): 
    Prefix = "ni"
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
    def GetObjects(id):
        return botoec2().describe_network_interfaces()['NetworkInterfaces']

    @staticmethod
    def CLIAdd(Name, CidrBlock, fdrgtd):
        return f"id000000002"


class cS3(cParent): 
    Prefix = "s3"
    Icon = "S3"

    @staticmethod
    def Fields():
        return {
                    "Name" : (cS3,True,False,False,False),
#                    'CreationDate': datetime.datetime(2023, 9, 29, 12, 28, 16, tzinfo=tzutc())
                }
    
    @staticmethod
    def GetObjects(id):
        return botos3().list_buckets()['Buckets']


class cElasticIP(cParent):
    Prefix = "eipassoc"

    @staticmethod
    def Create(Name):
        id = botoec2().allocate_address(Domain='vpc')['AllocationId']
        cTag.Create(id, "Name", f"{cElasticIP.Prefix}-{Name}")
        return id
    
    @staticmethod
    def Delete(id):
        botoec2().release_address(AllocationId=id)


class cKeyPair(cParent):
    Prefix = "key"
    
    def Destroy(id):
        botoec2().delete_key_pair(KeyName = id)

    @staticmethod
    def CLIAdd(Name):
        return f"aws ec2 create-key-pair --key-name {Name} --query 'KeyMaterial' --output text > {Name}.pem"

    @staticmethod
    def CLIDel(Name):
        return f"aws ec2 delete-key-pair --key-name {Name}"


    @staticmethod
    def Create(Name):
        id = f"{cKeyPair.Prefix}-{Name}"
        private_key = botoec2().create_key_pair(KeyName=id)['KeyMaterial']

        try:
            with open(f'PrivateKeys\\{id}.pem', 'w') as key_file: key_file.write(private_key)
        except Exception as e:
            print(f"KeyPair.Create: An exception occurred: {type(e).__name__} - {e}")

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_key_pair(
            KeyName = id
        )


class cTag(cParent):
    @staticmethod
    def Create(id, Name, Value):
        botoec2().create_tags(
            Resources=[id],
            Tags=[
                {
                    'Key': Name,
                    'Value': Value
                },
            ]
        )

    @staticmethod
    def Delete(id, Name):
        botoec2().delete_tags(
            Resources=[id],
            Tags=[
                {'Key': Name}
            ]
        )

    @staticmethod
    def CLIAdd(Name):
        return f""

    @staticmethod
    def CLIDel(id, Name):
        return f"aws ec2 delete-tags --resources {id} --tags Key={Name}"


awsClassesNW = [
        cKeyPair,
        cVpc, cSecurityGroup, cSecurityGroupRule, cIpPermission, 
        cInternetGateway, cInternetGatewayAttachment,
        cNetworkAcl, cNetworkAclEntry,
    ]

awsClassesSN = [
        cSubnet,
        cRouteTable, cRouteTableAssociation, cRoute,
        cElasticIP, 
        cNATGateway,
    ]

awsClassesObj = [
        cReservation, cEC2, cNetworkInterface,
        cS3, 
    ]

Classes = awsClassesNW + awsClassesSN + awsClassesObj

Const = {
    'EC2.UserData.Apache' : ""\
                    + "#!/bin/bash\n"\
                    + "yum update -y\n"\
                    + "yum install httpd -y\n"\
                    + "systemctl start httpd\n"\
                    + "systemctl enable httpd\n",
    'EC2.InstanceType.t2.micro' : 't2.micro',
    'EC2.ImageId.Linux' : 'ami-0669b163befffbdfc',
}

class awsObjectList:
    def __init__(self, aws, clss):
        self.aws = aws
        self.Class = clss
        self.Map = {}

    def __getitem__(self, key):
        return self.Map[key]

    def __setitem__(self, key, value):
        self.Map[key] = value

    def Count(self):
        return len(self.Map)

    def View(self):
        return self.Class.GetClassView()
    
    def Append(self, id = None, parent = None, resp = None):
#       self.Objects = [self.Class(obj) for obj in self.GetObjects(parent)]
#       if not Class in Data:
#           Data[Class] = {}
#       if not hasattr(aws, Class.GetClassView()):
#           aws.setattr(wrapper)
            
        if resp == None:
            resp = self.Class.GetObjects(id)

        for index, el in enumerate(resp):
            obj = self.Class(self.aws, parent, index, el)
    #            Data[Class][obj.GetId()] = obj
            self.Map[obj.GetId()] = obj
#                self.List.append(id)

        self.aws.Save()


    def Create(self, *args):
        try:
            id = self.Class.Create(*args)
        except Exception as e:
            print(f"{self.View()}.Create: An exception occurred: {type(e).__name__} - {e}")
            return None

        self.Append(id)

        return id

    def DeleteInner(self, args, ClearFlag = False):
        if ClearFlag and hasattr(self.Class, "SkipDeletionOnClear") and self.Class.SkipDeletionOnClear:
            pass
        else:
            try:
                self.Class.Delete(*args)
            except Exception as e:
                print(f"{self.View()}.Delete: An exception occurred: {type(e).__name__} - {e}")
                return

        id = args[0]
        if id in self.Map:
#           self.Map.remove(id)
            del self.Map[id]
            self.aws.Save()

    def Delete(self, *args):
        self.DeleteInner(args, False)

    def Clear(self):
        keys_to_delete = list(self.Map.keys())
        index = len(keys_to_delete) - 1
        while index >= 0:
            id = keys_to_delete[index]
            self.DeleteInner((id,), True)
            index -= 1

    def Print(self):
        if len(self.Map) == 0 : return

        print(f"  {self.View()}: {len(self.Map)}")
        for id, obj in self.Map:
            print(f"{id}: {obj}")

class AWS:
    def __init__(self, path):
        self.Path = path

        for clss in Classes:
            wrapper = awsObjectList(self, clss)
            name = wrapper.View()
            setattr(self, name, wrapper)

        self.Load()

    def __getitem__(self, clss):
        key = clss.GetClassView()
        return getattr(self, key)

    def __setitem__(self, clss, wrap):
        key = clss.GetClassView()
        setattr(self, key, wrap)

    def Clear(self, clssList = None):
        if clssList == None:
            clssList = Classes

        for clss in reversed(clssList):
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.Clear()
    
#            if clss == cSecurityGroup:
#                break

    def Print(self):
        for clss in Classes:
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.Print()

    def prettify(self, elem):
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")


    def Save(self):
        root = ET.Element("AWS")

        for clss in Classes:
            name = clss.GetClassView()
            wrapper = getattr(self, name)

            category_element = ET.SubElement(root, name)
            for id, obj in wrapper.Map.items():
                id_element = ET.SubElement(category_element, f"id")
                id_element.text = id


        tree = self.prettify(root)
        with open(self.Path, "w") as file:
            file.write(tree)

    def Load(self):
        with open(self.Path, 'r') as file:
            xml_string = file.read()
        root = ET.fromstring(xml_string)

        for element in root:
            wrapper = getattr(self, element.tag)
#           wrapper.List = [child.text for child in element]
            for child in element:
                id = child.text
                wrapper.Append(id)
