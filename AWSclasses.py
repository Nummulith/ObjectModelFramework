import boto3
from botocore.exceptions import ClientError

from xml.dom import minidom
import xml.etree.ElementTree as ET

fType  = 0
fId    = 1
fOwner = 2
fOut   = 3
fIn    = 4

#Draw
dView = 1 #0
dExt  = 2 #1
dIcon = 4 #2
dId   = 8 #3

dAll  = dView + dExt + dIcon + dId
dDef  = dAll - dExt

IdDv = "|"

def region():
    return "eu-central-1"
    return "eu-west-1"

def botoec2():
    return boto3.client('ec2', region_name = region())

def botos3():
    return boto3.client('s3' , region_name = region())

def Id17(id):
    return id[-17:]

def idpar(field, id):
    params = {}

    if id is not None:
        params[field] = [id]
    
    return params

def Wait(waiter_name, resource_param, resource_id):
    waiter = botoec2().get_waiter(waiter_name)

    waiter.wait(
        **{f"{resource_param}": [resource_id]},
        WaiterConfig={
            'Delay': 3,
            'MaxAttempts': 100
        }
    )

class cParent:
    Icon = "AWS"
    Show = True
    Draw = dDef
    Color = "#A9DFBF"
    Prefix = ""

    def __init__(self, aws, IdQuery, resp, DoAutoSave=True):
        if IdQuery != None:
            par_id, _, cur_id = IdQuery.rpartition(IdDv)
            if par_id != "":
                setattr(self, "ParentId", par_id)
            if hasattr(self, "Index") and cur_id != "" and cur_id != "*":
                setattr(self, "Index", int(cur_id))

        fields = type(self).Fields()
        for key, cfg in fields.items():
            if not key in resp:
                continue
            value = resp[key]
            field = fields[key][fType]
            if type(field) == list:
                if len(field) == 0:
                    continue
                if field[0] == str:
                    continue
                else:
                    aws[field[0]].Fetch(f"{self.GetId()}{IdDv}*", value, DoAutoSave)
            elif field == list:
                continue
            elif type(field) == dict:
                tkkey, tkval = next(iter(field.items()))
                for pair in value:
                    setattr(self, "Tag_" + pair[tkkey], pair[tkval])
                continue
            else:
                setattr(self, key, value)
        
        self.items = []

    def FieldsOfAKind(self, kind):
        return (key for key, value in self.Fields().items() if value[kind])

    def GetId(self):
        field = next(self.FieldsOfAKind(fId), None)

        if field == None:
            return f"{self.ParentId}{IdDv}{getattr(self, "Index", '0')}"
        
        return getattr(self, field)

    def GetOwner(self, aws):
        field = next(self.FieldsOfAKind(fOwner), None)
        if field != None:
            id = getattr(self, field, None)
            if id == None: return None

            clss = self.Fields()[field][fType]

            if not id in aws[clss].Map : return None

            owner = aws[clss].Map[id]
            return owner

        if hasattr(self, "ParentId"):
            if not self.ParentId in aws[self.ParentClass].Map:
                return None
            
            owner = aws[self.ParentClass].Map[self.ParentId]
            return owner

        return None

    def GetView(self):
        return f"{getattr(self, 'Tag_Name', self.GetId())}"

    @classmethod
    def GetObjectsByIndex(clss, id, ListField, FilterField):
        sg_id = None; ip_n = None
        if id != None:
            sg_id, _, ip_n = id.rpartition(IdDv)

        pars = clss.ParentClass.GetObjects(sg_id)

        res = []
        for par in pars:
            index = -1
            for permission in par[ListField]:
                index += 1

                if ip_n != None and ip_n != "" and ip_n != "*":
                    if ip_n != (str(index) if FilterField == int else permission[FilterField]):
                        continue

                res.append(permission)

        return res


    @staticmethod
    def GetObjects(id):
        return None

    
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
    Draw = dAll
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
                    'VpcId': (cVpc,False,False,False,False) ,
                    'KeyName': (str,False,False,False,False),
                    'KeyPairId': (cKeyPair,False,False,False,True),
                    'AmiLaunchIndex': (int,False,False,False,False),
                    'ImageId': (str,False,False,False,False),
                    'Architecture': (str,False,False,False,False),
                    'Hypervisor': (str,False,False,False,False),
                    'ClientToken': (str,False,False,False,False),
                    'PublicDnsName': (str,False,False,False,False),
                    'CurrentInstanceBootMode': (str,False,False,False,False),
                    'EbsOptimized': (bool,False,False,False,False),
                    'UsageOperation': (str,False,False,False,False),
                    'PrivateDnsName': (str,False,False,False,False),
                    'StateTransitionReason': (str,False,False,False,False),
                    'EnaSupport': (bool,False,False,False,False),
                    'RootDeviceName': (str,False,False,False,False),
                    'RootDeviceType': (str,False,False,False,False),
                    'SourceDestCheck': (bool,False,False,False,False),
                    'VirtualizationType': (str,False,False,False,False),
                    'BootMode': (str,False,False,False,False),
                }
    
# 'SecurityGroups': [{'GroupName': 'secgrup-antony', 'GroupId': 'sg-0e050b1cd54e6fcc8'}]

# 'LaunchTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'Monitoring': {'State': 'disabled'}
# 'Placement': {'AvailabilityZone': 'eu-central-1b', 'GroupName': '', 'Tenancy': 'default'}
# 'ProductCodes': []
# 'State': {'Code': 16, 'Name': 'running'}
# 'BlockDeviceMappings': [{'DeviceName': '/dev/xvda', 'Ebs': {...}}]
# 'NetworkInterfaces': [{'Attachment': {...}, 'Description': '', 'Groups': [...], 'Ipv6Addresses': [...], 'MacAddress': '06:02:cb:61:9c:7b', 'NetworkInterfaceId': 'eni-06ef5645d896ee146', 'OwnerId': '047989593255', 'PrivateIpAddress': '10.222.2.11', 'PrivateIpAddresses': [...], ...}]
# 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}
# 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}
# 'HibernationOptions': {'Configured': False}
# 'MetadataOptions': {'State': 'applied', 'HttpTokens': 'required', 'HttpPutResponseHopLimit': 2, 'HttpEndpoint': 'enabled', 'HttpProtocolIpv6': 'disabled', 'InstanceMetadataTags': 'disabled'}
# 'EnclaveOptions': {'Enabled': False}
# 'UsageOperationUpdateTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'PrivateDnsNameOptions': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}
# 'MaintenanceOptions': {'AutoRecovery': 'default'}

    
    @staticmethod
    def GetObjects(id):
        resp = botoec2().describe_instances(**idpar('InstanceIds', id))
        res = []
        for Reservation in resp['Reservations']:
            res = res + Reservation["Instances"]
        return res

    def GetExt(self):
        return f"{getattr(self, 'PlatformDetails', '-')}"

    @staticmethod
    def Create(Name, ImageId, InstanceType, KeyPairId, SubnetId, Groups=[], PrivateIpAddress=None, UserData=""):
        id = botoec2().run_instances(
            ImageId = ImageId,
            InstanceType = InstanceType,
            KeyName = cKeyPair.IdToName(KeyPairId),
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

        Wait('instance_terminated', "InstanceIds", id)

    def __init__(self, aws, IdQuery, resp, DoAutoSave=True):
        super().__init__(aws, IdQuery, resp, DoAutoSave)

        setattr(self, "KeyPairId", cKeyPair.NameToId(self.KeyName))

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
        resp = botoec2().describe_internet_gateways(**idpar('InternetGatewayIds', id))
        return resp['InternetGateways']


    @staticmethod
    def Create(Name):
        id = botoec2().create_internet_gateway()['InternetGateway']['InternetGatewayId']
        cTag.Create(id, "Name", f"{cInternetGateway.Prefix}-{Name}")
        return id

    @staticmethod
    def Delete(id):
        botoec2().delete_internet_gateway(
            InternetGatewayId = id
        )


class cInternetGatewayAttachment(cParent): 
    Prefix = "igw-attach"
    ParentClass = cInternetGateway
    Icon = "Gateway"
    Draw = dView
    Color = "#F488BB"

    @staticmethod
    def Fields():
        return {
                    "VpcId" : (cVpc,False,False,False,True),
                    'State' : (str,False,False,False,False),
                }
    
    def GetView(self):
        return f"{Id17(self.VpcId)}"

    @staticmethod
    def GetObjects(id):
        return cInternetGatewayAttachment.GetObjectsByIndex(id, "Attachments", "VpcId")
    
    def GetId(self):
        return f"{self.ParentId}{IdDv}{self.VpcId}"

    @staticmethod
    def Create(InternetGatewayId, VpcId):
        resp = botoec2().attach_internet_gateway(InternetGatewayId=InternetGatewayId, VpcId=VpcId)
        return f"{InternetGatewayId}{IdDv}{VpcId}"

    @staticmethod
    def Delete(id):
        InternetGatewayId, _, VpcId = id.rpartition(IdDv)
        botoec2().detach_internet_gateway(
            InternetGatewayId=InternetGatewayId, VpcId=VpcId
        )


class cNATGateway(cParent): 
    Prefix = "nat"
    Icon = "NATGateway"

    @staticmethod
    def Fields():
        return {
                    "NatGatewayId"        : (cNATGateway, True ,False,False,False),
                    "SubnetId"            : (cSubnet    , False,True ,False,False),
                    "State"               : (str        , False,False,False,False),
                    "VpcId"               : (cVpc       , False,False,False,True ),
                    "ConnectivityType"    : (str        , False,False,False,False),
                    'Tags'                : ({"Key" : "Value"},False,False,False,False),
                    "NatGatewayAddresses" : ([cAssociation], False,False,False,True),
# 'CreateTime': datetime.datetime(2024, 1, 30, 16, 38, 41, tzinfo=tzutc())
                }
    
    @staticmethod
    def GetObjects(id):
        resp = botoec2().describe_nat_gateways(**idpar('NatGatewayIds', id))
        return resp['NatGateways']
    
    def GetView(self):
        return f"NAT"

    @staticmethod
    def Create(Name, SubnetId, AllocationId):
        id = botoec2().create_nat_gateway(SubnetId = SubnetId, AllocationId = AllocationId)['NatGateway']['NatGatewayId']

        cTag.Create(id, "Name", f"{cNATGateway.Prefix}-{Name}")

        Wait('nat_gateway_available', "NatGatewayIds", id)

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_nat_gateway(NatGatewayId = id)

        Wait('nat_gateway_deleted', "NatGatewayIds", id)


class cAssociation(cParent): 
    ParentClass = cNATGateway

    @staticmethod
    def Fields():
        return {
                    'AssociationId'      : (cAssociation,True,False,False,False),
                    "AllocationId"       : (cElasticIP ,False,False,False,True),
                    "NetworkInterfaceId" : (cNetworkInterface ,False,False,False,False), # !!!!!!!!!!
                    'PrivateIp'          : (str ,False,False,False,False),
                    'PublicIp'           : (str ,False,False,False,False),
                    'IsPrimary'          : (bool ,False,False,False,False),
                    'Status'             : (str ,False,False,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
# 'Domain': 'vpc'
# 'NetworkInterfaceOwnerId': '047989593255'
# 'PrivateIpAddress': '10.3.1.21'
# 'PublicIpv4Pool': 'amazon'
# 'NetworkBorderGroup': 'eu-central-1'
                }
    
    @staticmethod
    def GetObjects(id):
#        return cAssociation.GetObjectsByIndex(id, "NATGatewayAddresses", "VpcId")
        
        filters = []
        if id:
            filters.append({
                'Name': 'association-id',
                'Values': [id]
            })

        resp = botoec2().describe_addresses(Filters=filters)
        
        return resp["Addresses"]

    @staticmethod
    def Create(allocation_id, instance_id):
        resp = botoec2().associate_address(AllocationId=allocation_id, InstanceId=instance_id)
        return f"{resp["AssociationId"]}"

    @staticmethod
    def Delete(id):
        RouteTableId, _, AssociationId = id.rpartition(IdDv)
        botoec2().disassociate_address(AssociationId = AssociationId)

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
#                    "IpPermissions"       : ([cSecurityGroupRule],False,False,False,False),
#                    "IpPermissionsEgress" : ([cSecurityGroupRule],False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(id):
        return botoec2().describe_security_groups(**idpar('GroupIds', id))['SecurityGroups']

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

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_security_group(
            GroupId=id
        )

class cSecurityGroupRule(cParent):
    Prefix = "sgr"
    ParentClass = cSecurityGroup

    @staticmethod
    def Fields():

        return {

                    'SecurityGroupRuleId': (cSecurityGroupRule, False,False ,False,False),
                    'GroupId':      (cSecurityGroup, False,True ,False,False),
                    'GroupOwnerId': (str, False,False ,False,False),
                    'IsEgress':     (bool, False,False ,False,False),
                    'IpProtocol':   (str, False,False ,False,False),
                    'FromPort':     (int, False,False ,False,False),
                    'ToPort':       (int, False,False ,False,False),
                    'CidrIpv4':     (str, False,False ,False,False),
#                    "IpRanges"   : (str, False,False,False,False),
        }
    
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
#            'Ipv6Ranges': []
#            'PrefixListIds': []
#            'UserIdGroupPairs': []
                }
            ]
        )["SecurityGroupRules"][0]["SecurityGroupRuleId"]

        return f"{GroupId}{IdDv}{id}"
        
    @staticmethod
    def Delete(id):
        security_group_id, _, security_group_rule_id = id.rpartition(IdDv)
        botoec2().revoke_security_group_ingress(
            GroupId=security_group_id,
            SecurityGroupRuleIds=[security_group_rule_id]
        )

    def GetId(self):
        return f"{self.GroupId}{IdDv}{self.SecurityGroupRuleId}"

    @staticmethod
    def GetObjects(id):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_security_group_rules.html
        # security-group-rule-id - The ID of the security group rule.
        # group-id - The ID of the security group.

        par_id = None; cur_id = None
        if id != None:
            par_id, _, cur_id = id.rpartition(IdDv)

        filters = []
        if par_id:
            filters.append({
                'Name': 'group-id',
                'Values': [par_id]
            })

        cur_ids = []
        if cur_id:
            cur_ids.append(cur_id)

        resp = botoec2().describe_security_group_rules(
            Filters=filters,
            SecurityGroupRuleIds=cur_ids
        )
        return resp['SecurityGroupRules']

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
    Draw = dAll
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
        return botoec2().describe_subnets(**idpar('SubnetIds', id))['Subnets']
    
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
                    'Entries': ([cNetworkAclEntry],False,True,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                    #),[{'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}]
                    # 'Associations': [{'NetworkAclAssociationId': 'aclassoc-0c867a11b811c5be1', 'NetworkAclId': 'acl-0334606b00fe7551c', 'SubnetId': 'subnet-06678d33e23eba72f'}]
                }
    
    @staticmethod
    def GetObjects(id):
        return botoec2().describe_network_acls(**idpar('NetworkAclIds', id))['NetworkAcls']


class cNetworkAclEntry(cParent): 
    Prefix = "nacle"
    ParentClass = cNetworkAcl
    Draw = dView + dExt
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
        return None
    
    def GetView(self):
        return f"{self.RuleNumber}:{self.Protocol} {getattr(self, 'PortRange', '')}"

    def GetExt(self):
        return f"{self.RuleAction} - {getattr(self, 'CidrBlock', '*')}"
    
    def GetId(self):
        return f"{self.RuleNumber}"


class cRouteTable(cParent): 
    Prefix = "rtb"
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
        return botoec2().describe_route_tables(**idpar('RouteTableIds', id))['RouteTables']

    @staticmethod
    def Create(Name, VpcId):
        id = botoec2().create_route_table(VpcId = VpcId)['RouteTable']['RouteTableId']

        cTag.Create(id, "Name", f"{cRouteTable.Prefix}-{Name}")
        return id

    @staticmethod
    def Delete(id):
        botoec2().delete_route_table(
            RouteTableId = id
        )

class cRouteTableAssociation(cParent):
    Prefix = "rtba"
    ParentClass = cRouteTable
    Draw = dExt
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
        return cRouteTableAssociation.GetObjectsByIndex(id, "Associations", 'RouteTableAssociationId')

    def GetId(self):
        return f"{self.RouteTableId}{IdDv}{self.RouteTableAssociationId}"

    def GetExt(self):
        return f"{Id17(self.SubnetId)}"
    
    def GetView(self):
        return f"Route[{self.Index}]"
    

    @staticmethod
    def Create(RouteTableId, SubnetId):
        resp = botoec2().associate_route_table(SubnetId = SubnetId, RouteTableId = RouteTableId)
        return f"{RouteTableId}{IdDv}{resp["AssociationId"]}"

    @staticmethod
    def Delete(id):
        RouteTableId, _, AssociationId = id.rpartition(IdDv)
        botoec2().disassociate_route_table(
            AssociationId = AssociationId
        )


class cRoute(cParent): 
    ParentClass = cRouteTable
    Prefix = "route"
    Draw = dAll-dId
    Icon = "Route"
    Color = "#7CCF9C"
    Index = None

    @staticmethod
    def Fields():
        return {
                    "DestinationCidrBlock" : (str              ,False,False,False,False),
                    "GatewayId"            : (cInternetGateway ,False,False,True ,False),
                    "InstanceId"           : (cEC2             ,False,False,True ,False),
                    "NatGatewayId"         : (cNATGateway      ,False,False,True ,False),
                    "NetworkInterfaceId"   : (cNetworkInterface,False,False,True ,False),
                    'Origin'               : (str              ,False,False,False,False),
                    'State'                : (str              ,False,False,False,False),

                    "GatewayId_local" : (cVpc,False,False,False,True),
                } # +

    @staticmethod
    def GetObjects(id):
        return cRoute.GetObjectsByIndex(id, "Routes", int)
    
    def GetId(self):
        return f"{self.ParentId}{IdDv}{self.DestinationCidrBlock}"

    def GetView(self):
        return f"{self.Index}"

    def GetExt(self):
        return f"{getattr(self, 'DestinationCidrBlock', '-')}"

    def __init__(self, aws, IdQuery, resp, DoAutoSave=True):

        super().__init__(aws, IdQuery, resp, DoAutoSave)

        if hasattr(self, "GatewayId") and self.GatewayId == "local":
            self.GatewayId = None
            setattr(self, "GatewayId_local", cRouteTable.GetObjects(self.ParentId)[0]["VpcId"])

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

        return f"{RouteTableId}{IdDv}{DestinationCidrBlock}"
    
    @staticmethod
    def Delete(id):
        RouteTableId, _, DestinationCidrBlock = id.rpartition(IdDv)

        try:
            botoec2().delete_route(
                RouteTableId = RouteTableId,
                DestinationCidrBlock = DestinationCidrBlock
            )
        except ClientError as e:
            if e.response['Error']['Message'][:25] == 'cannot remove local route':
                pass  # it is kinda ok
            else:
                raise # all other is not


class cVpc(cParent): 
    Prefix = "vpc"
    Draw = dAll
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
        return botoec2().describe_vpcs(**idpar('VpcIds', id))['Vpcs']
    
    def GetExt(self):
        return f"{getattr(self, 'CidrBlock', '-')}"
    
    @staticmethod
    def Create(Name, CidrBlock):
        id = botoec2().create_vpc(CidrBlock=CidrBlock)['Vpc']['VpcId']
        cTag.Create(id, "Name", f"{cVpc.Prefix}-{Name}")
        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_vpc(
            VpcId = id
        )
    
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
        return botoec2().describe_network_interfaces(**idpar('NetworkInterfaceIds', id))['NetworkInterfaces']

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
        if id == None:
            response = botos3().list_buckets()
            return response['Buckets']
        else:
            response = botos3().head_bucket(Bucket=id)
            return [response]



class cElasticIP(cParent):
    Prefix = "eipassoc"

    @staticmethod
    def Fields():
        return {
                    'AllocationId': (cElasticIP,True,False,False,False),
                    'PublicIp': (str,False,False,False,False),
                    'Domain': (str,False,False,False,False),
                    'Tags': ({"Key" : "Value"},False,False,False,False),
                    'PublicIpv4Pool': (str,False,False,False,False),
                    'NetworkBorderGroup': (str,False,False,False,False),
                }
    
    @staticmethod
    def Create(Name):
        id = botoec2().allocate_address(Domain='vpc')['AllocationId']
        cTag.Create(id, "Name", f"{cElasticIP.Prefix}-{Name}")
        return id
    
    @staticmethod
    def Delete(id):
        botoec2().release_address(
            AllocationId = id
        )

    @staticmethod
    def GetObjects(id):
        resp = botoec2().describe_addresses(**idpar('AllocationIds', id))
        return resp['Addresses']


class cKeyPair(cParent):
    Prefix = "key"
    
    @staticmethod
    def Fields():
        return {
                    'KeyPairId': (cKeyPair,True,False,False,False),
                    'KeyFingerprint': (str,False,False,False,False),
                    'KeyName': (str,False,False,False,False),
                    'KeyType': (str,False,False,False,False),
                    'Tags': ({"Key" : "Value"},False,False,False,False),
                    'CreateTime': (str,False,False,False,False),
                }
    
    def Destroy(id):
        botoec2().delete_key_pair(KeyPairId = id)

    @staticmethod
    def CLIAdd(Name):
        return f"aws ec2 create-key-pair --key-name {Name} --query 'KeyMaterial' --output text > {Name}.pem"

    @staticmethod
    def CLIDel(Name):
        return f"aws ec2 delete-key-pair --key-name {Name}"

    @staticmethod
    def GetObjects(id):
        response = botoec2().describe_key_pairs(**idpar('KeyPairIds', id))
        return response['KeyPairs']


    @staticmethod
    def Create(Name):
        KeyName = f"{cKeyPair.Prefix}-{Name}"
        resp = botoec2().create_key_pair(KeyName=KeyName)

        private_key = resp['KeyMaterial']
        try:
            with open(f'PrivateKeys\\{KeyName}.pem', 'w') as key_file: key_file.write(private_key)
        except Exception as e:
            print(f"KeyPair.Create: An exception occurred: {type(e).__name__} - {e}")

        id = resp['KeyPairId']

        return id
    
    @staticmethod
    def Delete(id):
        botoec2().delete_key_pair(KeyPairId = id)

    @staticmethod
    def IdToName(KeyPairId):
    #   KeyName = boto3.resource('ec2').KeyPair(KeyPairId).key_name # does not work
        resp = botoec2().describe_key_pairs(KeyPairIds=[KeyPairId])
        KeyName = resp['KeyPairs'][0]['KeyName']
        return KeyName
    
    @staticmethod
    def NameToId(Name):
        resp = botoec2().describe_key_pairs(KeyNames=[Name])
        KeyPairId = resp['KeyPairs'][0]['KeyPairId']
        return KeyPairId

    def GetView(self):
        return f"{self.KeyName}"
    
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
        cVpc, cSecurityGroup, cSecurityGroupRule,
        cInternetGateway, cInternetGatewayAttachment,
        cNetworkAcl, cNetworkAclEntry,
    ]

awsClassesSN = [
        cSubnet,
        cRouteTable, cRoute, cRouteTableAssociation,
        cElasticIP, 
        cNATGateway, cAssociation, 
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
    
    def Fetch(self, IdQuery = None, resp = None, DoAutoSave = True):
        if resp == None:
            try:
                resp = self.Class.GetObjects(IdQuery)
            except ClientError as e:
                if e.response['Error']['Code'][-9:] == '.NotFound':
                    return
                else:
                    raise

        sg_id = ""; ip_n = "*"
        if IdQuery != None:
            sg_id, _, ip_n = IdQuery.rpartition(IdDv)
            
        Index = -1
        for el in resp:
            Index += 1
            ip_nn = ip_n
            if ip_nn == "*":
                ip_nn = int(Index)

            obj = self.Class(self.aws, f"{sg_id}{IdDv}{ip_nn}", el, DoAutoSave)
            self.Map[obj.GetId()] = obj

        if DoAutoSave:
            self.aws.AutoSave()


    def Create(self, *args):
        try:
            id = self.Class.Create(*args)
        except Exception as e:
            print(f"{self.View()}.Create: An exception occurred: {type(e).__name__} - {e}")
            return None

        self.Fetch(id)

        return id

    def DeleteInner(self, args, ClearFlag = False):
        try:
            self.Class.Delete(*args)
        except Exception as e:
            print(f"{self.View()}.Delete: An exception occurred: {type(e).__name__} - {e}")
            return

        id = args[0]
        if id in self.Map:
            del self.Map[id]
            self.aws.AutoSave()

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
    def __init__(self, path, DoAutoLoad = True, DoAutoSave = True):
        self.Path = path
        self.DoAutoLoad = DoAutoLoad
        self.DoAutoSave = DoAutoSave

        for clss in Classes:
            wrapper = awsObjectList(self, clss)
            name = wrapper.View()
            setattr(self, name, wrapper)

        self.AutoLoad()

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
    
    def Print(self):
        for clss in Classes:
            name = clss.GetClassView()
            wrapper = getattr(self, name)
            wrapper.Print()

    def prettify(self, elem):
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")


    def Load(self):
        with open(self.Path, 'r') as file:
            xml_string = file.read()
        root = ET.fromstring(xml_string)

        for element in root:
            wrapper = getattr(self, element.tag)
            for child in element:
                id = child.text
                wrapper.Fetch(id, None, False)

    def AutoLoad(self):
        if self.DoAutoLoad:
            self.Load()

    def Save(self):
        root = ET.Element("AWS")

        for clss in Classes:
            name = clss.GetClassView()
            wrapper = getattr(self, name)

            category_element = ET.SubElement(root, name)
            for id, obj in wrapper.Map.items():
                id_element = ET.SubElement(category_element, f"id")
                id_element.text = str(id)


        tree = self.prettify(root)
        with open(self.Path, "w") as file:
            file.write(tree)

    def AutoSave(self):
        if self.DoAutoSave:
            self.Save()


    def Fetch(self):
        self[cVpc              ].Fetch()
        self[cSubnet           ].Fetch()
        self[cSecurityGroup    ].Fetch()
        self[cSecurityGroupRule].Fetch()

        self[cRouteTable      ].Fetch()
        self[cInternetGateway ].Fetch()
        self[cNATGateway      ].Fetch()
        self[cNetworkAcl      ].Fetch()
        self[cNetworkInterface].Fetch()

        self[cReservation     ].Fetch()
#       self[cS3              ].Fetch()
