"""
AWS Classes Module

This module provides a classes representing a behaivour of AWS objects

Classes:

Methods:

Usage:
- ...

Author: Pavel ERESKO
"""

import boto3
from botocore.exceptions import ClientError

import io
import zipfile
import json
import stat

from ObjectModel import *

def bt(aws_service):
    return boto3.Session(
        profile_name = AWS.PROFILE
    ).client(
        aws_service
    )

def Id17(id):
    return id[-17:]

# id parameter passing
pPar = 0
pList = 1
pFilter = 2
pString = 3

def idpar(field, id, ParType = pList):
    params = {}

    if id is not None:
        if ParType == pPar:
            params[field] = id
        if ParType == pList:
            params[field] = [id]
        elif ParType == pFilter:
            params["Filters"] = [{
                'Name': field,
                'Values': [id]
            }]
        elif ParType == pString:
            params["Filter"] = f'{field}="{id}"'
    
    return params

def Wait(waiter_name, resource_param, resource_id):
    waiter = bt('ec2').get_waiter(waiter_name)

    waiter.wait(
        **{f"{resource_param}": [resource_id]},
        WaiterConfig={
            'Delay': 3,
            'MaxAttempts': 100
        }
    )


class cParent(ObjectModelItem):
    Icon = "AWS"
    Prefix = ""


class cTag(cParent):
    @staticmethod
    def create(id, Name, Value):
        bt('ec2').create_tags(
            Resources=[id],
            Tags=[
                {
                    'Key': Name,
                    'Value': Value
                },
            ]
        )

    @staticmethod
    def delete(id, Name):
        bt('ec2').delete_tags(
            Resources=[id],
            Tags=[
                {'Key': Name}
            ]
        )

    @staticmethod
    def cli_add(Name):
        return f""

    @staticmethod
    def cli_del(id, Name):
        return f"aws ec2 delete-tags --resources {id} --tags Key={Name}"


class cReservation(cParent): 
    Icon = "Res_Amazon-EC2_Instance_48"
    Show = False
    Color = "#FFC18A"

    @staticmethod
    def fields():
        return {
                    "ReservationId" : (cReservation, FIELD.ID),
                    "OwnerId"       : str,
                    "Groups"        : ([str]), # !!!
                    "Instances"     : ([cEC2]),
                }
    
    @staticmethod
    def get_objects(id=None):
        resp = bt('ec2').describe_instances(**idpar('reservation-id', id, pFilter))
        return resp['Reservations']


class cEC2(cParent): 
    Prefix = "i"
    Draw = DRAW.ALL
    Icon = "Arch_Amazon-EC2_48"
    Color = "#FFC18A"

    @staticmethod
    def fields():
        return {
                    "ParentId" : (cReservation, FIELD.LINK_OUT),
                    "InstanceId" : (cEC2, FIELD.ID),
                    "SubnetId" : (cSubnet, FIELD.OWNER),
                    'Tags' : ({"Key" : "Value"}),
                    'VpcId': cVpc,
                    'KeyPairId': (cKeyPair, FIELD.LINK_IN),
                    # 'SecurityGroups': [{'GroupName': 'secgrup-antony', 'GroupId': 'sg-0e050b1cd54e6fcc8'}]
                    # 'NetworkInterfaces': [{'Attachment': {...}, 'Description': '', 'Groups': [...], 'Ipv6Addresses': [...], 'MacAddress': '06:02:cb:61:9c:7b', 'NetworkInterfaceId': 'eni-06ef5645d896ee146', 'OwnerId': '047989593255', 'PrivateIpAddress': '10.222.2.11', 'PrivateIpAddresses': [...], ...}]
                }
    
    @staticmethod
    def get_objects(id=None):
        resp = bt('ec2').describe_instances(**idpar('InstanceIds', id))
        res = []
        for reservation in resp['Reservations']:
            for inst in reservation["Instances"]:
                inst["ParentId"] = reservation["ReservationId"]
                res.append(inst)
        return res

    def get_ext(self):
        return f"{getattr(self, 'PlatformDetails', '-')}"

    @staticmethod
    def create(Name, ImageId, InstanceType, KeyPairId, SubnetId, Groups=[], PrivateIpAddress=None, UserData=""):
        id = bt('ec2').run_instances(
            ImageId = ImageId,
            InstanceType = InstanceType,
            KeyName = cKeyPair.IdToName(KeyPairId),
            NetworkInterfaces=[
                {
                    'SubnetId': SubnetId,
                    'DeviceIndex': 0,
                    'AssociatePublicIpAddress': True if PrivateIpAddress is not None else False,
                    'PrivateIpAddress': PrivateIpAddress,
                    'Groups': Groups,
                }
            ],
            UserData = UserData,
            MinCount = 1,
            MaxCount = 1
        )['Instances'][0]['InstanceId']

        cTag.create(id, "Name", f"{cEC2.Prefix}-{Name}")

        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').terminate_instances(
            InstanceIds=[id]
        )

        Wait('instance_terminated', "InstanceIds", id)

    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)

        if hasattr(self, "KeyName"):
            setattr(self, "KeyPairId", cKeyPair.NameToId(self.KeyName))

class cInternetGateway(cParent): 
    Prefix = "igw"
    Icon = "Arch_Amazon-API-Gateway_48"
    Color = "#F9BBD9"

    @staticmethod
    def fields():
        return {
                    "InternetGatewayId" : (cInternetGateway, FIELD.ID),
                    'Attachments' : ([cInternetGatewayAttachment]),
                    'Tags' : ({"Key" : "Value"}),
                }
    
    @staticmethod
    def get_objects(id=None):
        resp = bt('ec2').describe_internet_gateways(**idpar('InternetGatewayIds', id))
        return resp['InternetGateways']


    @staticmethod
    def create(Name):
        id = bt('ec2').create_internet_gateway()['InternetGateway']['InternetGatewayId']
        cTag.create(id, "Name", f"{cInternetGateway.Prefix}-{Name}")
        return id

    @staticmethod
    def delete(id):
        bt('ec2').delete_internet_gateway(
            InternetGatewayId = id
        )


class cInternetGatewayAttachment(cParent): 
    Prefix = "igw-attach"
    Icon = "Gateway"
    Draw = DRAW.VIEW
    Color = "#F488BB"
    DontFetch = True
    ListName = "Attachments"

    @staticmethod
    def fields():
        return {
                    "ParentId" : (cInternetGateway, FIELD.LIST_ITEM),
                    "ListName" : (str, FIELD.LIST_NAME),
                    "VpcId" : (cVpc, FIELD.LINK_IN),
                }
    
    def get_view(self):
        return f"{Id17(self.VpcId)}"

    @staticmethod
    def get_objects(id=None):
        return cInternetGateway.get_objects_by_index(id, "Attachments", "VpcId")
    
    def get_id(self):
        return f"{self.ParentId}{ID_DV}{self.VpcId}"

    @staticmethod
    def create(InternetGatewayId, VpcId):
        resp = bt('ec2').attach_internet_gateway(InternetGatewayId=InternetGatewayId, VpcId=VpcId)
        return f"{InternetGatewayId}{ID_DV}{VpcId}"

    @staticmethod
    def delete(id):
        InternetGatewayId, _, VpcId = id.rpartition(ID_DV)
        bt('ec2').detach_internet_gateway(
            InternetGatewayId=InternetGatewayId, VpcId=VpcId
        )


class cNATGateway(cParent): 
    Prefix = "nat"
    Icon = "Res_Amazon-VPC_NAT-Gateway_48"
    Color = '#c19fff'

    @staticmethod
    def fields():
        return {
                    "NatGatewayId"        : (cNATGateway, FIELD.ID),
                    "SubnetId"            : (cSubnet    , FIELD.OWNER),
                    "VpcId"               : (cVpc       , FIELD.LINK_IN),
                    'Tags'                : ({"Key" : "Value"}),
                    "NatGatewayAddresses" : ([cElasticIPAssociation], FIELD.LINK_IN),
                    # 'CreateTime': datetime.datetime(2024, 1, 30, 16, 38, 41, tzinfo=tzutc())
                }
    
    @staticmethod
    def get_objects(id=None):
        resp = bt('ec2').describe_nat_gateways(**idpar('NatGatewayIds', id))
        return resp['NatGateways']
    
    def get_view(self):
        return f"NAT"

    @staticmethod
    def create(Name, SubnetId, AllocationId):
        id = bt('ec2').create_nat_gateway(SubnetId = SubnetId, AllocationId = AllocationId)['NatGateway']['NatGatewayId']

        cTag.create(id, "Name", f"{cNATGateway.Prefix}-{Name}")

        Wait('nat_gateway_available', "NatGatewayIds", id)

        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').delete_nat_gateway(NatGatewayId = id)

        Wait('nat_gateway_deleted', "NatGatewayIds", id)


class cElasticIPAssociation(cParent): 
    # DontFetch = True
    ListName = "Addresses"

    @staticmethod
    def fields():
        return {
                    'ParentId'           : (cNATGateway, FIELD.LIST_ITEM),
                    'ListName'           : (str, FIELD.LIST_NAME),
                    "Id"      : (cElasticIPAssociation, FIELD.ID),
                    "View"    : (str, FIELD.VIEW),
                    "AllocationId"       : (cElasticIP, FIELD.LINK_IN),
                    "NetworkInterfaceId" : (cNetworkInterface, FIELD.LINK_IN),
                    'Tags'               : ({"Key" : "Value"}),
                }
    
    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)
        self.Id   = f"{self.ParentId}{ID_DV}{self.AssociationId}"
        self.View = f"{self.AssociationId}"

    @staticmethod
    def get_objects(id=None):
        filters = []
        if id:
            filters.append({
                'Name': 'association-id',
                'Values': [id]
            })

        resp = bt('ec2').describe_addresses(Filters=filters)
        return resp["Addresses"]

    @staticmethod
    def create(allocation_id, instance_id):
        resp = bt('ec2').associate_address(AllocationId=allocation_id, InstanceId=instance_id)
        return f"{resp['AssociationId']}"

    @staticmethod
    def delete(id):
        RouteTableId, _, AssociationId = id.rpartition(ID_DV)
        bt('ec2').disassociate_address(AssociationId = AssociationId)

class cSecurityGroup(cParent):
    Prefix = "sg"
    Icon = "SecurityGroup"
    Color = "#ff9999"

    @staticmethod
    def fields():
        return {
                    "GroupId"    : (str , FIELD.ID),
                    "VpcId"      : (cVpc, FIELD.OWNER),
#                    "IpPermissions"       : ([cSecurityGroupRule]),
#                    "IpPermissionsEgress" : ([cSecurityGroupRule]),
                }
    
    @staticmethod
    def get_objects(id=None):
        return bt('ec2').describe_security_groups(**idpar('GroupIds', id))['SecurityGroups']

    def get_view(self):
        return f"{self.GroupName}"

    @staticmethod
    def create(Name, Description, Vpc):
        sgName = f"{cSecurityGroup.Prefix}-{Name}"

        id = bt('ec2').create_security_group(
            GroupName = Name,
            Description = Description,
            VpcId = Vpc
        )['GroupId']

        cTag.create(id, "Name", sgName)

        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').delete_security_group(
            GroupId=id
        )

class cSecurityGroupRule(cParent):
    Prefix = "sgr"
    ListName = "Rules"

    @staticmethod
    def fields():
        return {
                    'SecurityGroupRuleId': cSecurityGroupRule,
                    'GroupId': (cSecurityGroup, FIELD.LIST_ITEM),
                    'ListName': (str, FIELD.LIST_NAME),
                }
    
    @staticmethod
    def create(GroupId, IpProtocol, FromToPort, CidrIp):
        id = bt('ec2').authorize_security_group_ingress(
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

        return f"{GroupId}{ID_DV}{id}"
        
    @staticmethod
    def delete(id):
        security_group_id, _, security_group_rule_id = id.rpartition(ID_DV)
        bt('ec2').revoke_security_group_ingress(
            GroupId=security_group_id,
            SecurityGroupRuleIds=[security_group_rule_id]
        )

    def get_id(self):
        return f"{self.GroupId}{ID_DV}{self.SecurityGroupRuleId}"

    @staticmethod
    def get_objects(id=None):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_security_group_rules.html
        # security-group-rule-id - The ID of the security group rule.
        # group-id - The ID of the security group.

        par_id = None; cur_id = None
        if id is not None:
            par_id, _, cur_id = id.rpartition(ID_DV)

        filters = []
        if par_id:
            filters.append({
                'Name': 'group-id',
                'Values': [par_id]
            })

        cur_ids = []
        if cur_id:
            cur_ids.append(cur_id)

        resp = bt('ec2').describe_security_group_rules(
            Filters=filters,
            SecurityGroupRuleIds=cur_ids
        )
        return resp['SecurityGroupRules']

    def get_view(self):
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
    Draw = DRAW.ALL
    Icon = "Subnet"
    Color = '#c8b7ea'

    @staticmethod
    def fields():
        return {
                    "SubnetId" : (cSubnet, FIELD.ID),
                    "VpcId" : (cVpc, FIELD.OWNER),
                    'Tags' : ({"Key" : "Value"}),
                }
# 'Ipv6CidrBlockAssociationSet': []
# 'PrivateDnsNameOptionsOnLaunch': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}


    @staticmethod
    def get_objects(id=None):
        response = bt('ec2').describe_subnets(**idpar('SubnetIds', id))['Subnets']
        return response
    
    def get_ext(self):
        return f"{getattr(self, 'CidrBlock', '-')}"

    @staticmethod
    def create(Name, Vpc, CidrBlock):
        id = bt('ec2').create_subnet(
            VpcId = Vpc,
            CidrBlock = CidrBlock,
#           AvailabilityZone='us-east-1a'
        )["Subnet"]["SubnetId"]

        cTag.create(id, "Name", f"{cSubnet.Prefix}-{Name}")

        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').delete_subnet(
            SubnetId = id
        )

    

class cNetworkAcl(cParent): 
    Prefix = "nacl"
    Icon = "Res_Amazon-VPC_Network-Access-Control-List_48"
    Color = "#d7c1ff"

    @staticmethod
    def fields():
        return {
                    "NetworkAclId" : (cNetworkAcl, FIELD.ID),
                    'VpcId': (cVpc, FIELD.OWNER),
                    'OwnerId': (str, FIELD.OWNER),
                    'Entries': ([cNetworkAclEntry], FIELD.OWNER),
                    'Tags' : ({"Key" : "Value"}),
                    #),[{'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': True, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'allow', 'RuleNumber': 100}, {'CidrBlock': '0.0.0.0/0', 'Egress': False, 'Protocol': '-1', 'RuleAction': 'deny', 'RuleNumber': 32767}]
                    # 'Associations': [{'NetworkAclAssociationId': 'aclassoc-0c867a11b811c5be1', 'NetworkAclId': 'acl-0334606b00fe7551c', 'SubnetId': 'subnet-06678d33e23eba72f'}]
                }
    
    @staticmethod
    def get_objects(id=None):
        return bt('ec2').describe_network_acls(**idpar('NetworkAclIds', id))['NetworkAcls']


class cNetworkAclEntry(cParent): 
    Prefix = "nacle"
    Icon = "NetworkAccessControlList"
    Color = '#d7c1ff'
    DontFetch = True
    ListName = "Entries"

    @staticmethod
    def fields():
        return {
            "ParentId": (cNetworkAcl, FIELD.LIST_ITEM),
            "ListName": (cNetworkAcl, FIELD.LIST_NAME),
            "Id"      : (cNetworkAclEntry, FIELD.ID),
            "Ext"     : (str, FIELD.EXT ),
            "View"    : (str, FIELD.VIEW),
        }

    @staticmethod
    def get_objects(id=None):
        return cNetworkAcl.get_objects_by_index(id, "Entries", "RuleNumber")

    
    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)
        self.Id   = f"{self.ParentId}{ID_DV}{self.RuleNumber}"
        self.View = f"{self.RuleAction} - {getattr(self, 'CidrBlock', '*')}- {self.RuleNumber}:{self.Protocol} {getattr(self, 'PortRange', '')}"


class cRouteTable(cParent): 
    Prefix = "rtb"
    Icon = "Res_Amazon-Route-53_Route-Table_48"
    Color = '#c19fff'

    @staticmethod
    def fields():
        return {
                    "RouteTableId" : (cRouteTable, FIELD.ID),
                    "VpcId" : (cVpc, FIELD.OWNER),
                    "Routes" : ([cRoute]),
                    "Associations" : ([cRouteTableAssociation]),
                    'OwnerId': (str, FIELD.OWNER),
                    'Tags' : ({"Key" : "Value"}),
                    # 'PropagatingVgws': []
                }
    
    @staticmethod
    def get_objects(id=None):
        return bt('ec2').describe_route_tables(**idpar('RouteTableIds', id))['RouteTables']

    @staticmethod
    def create(Name, VpcId):
        id = bt('ec2').create_route_table(VpcId = VpcId)['RouteTable']['RouteTableId']

        cTag.create(id, "Name", f"{cRouteTable.Prefix}-{Name}")
        return id

    @staticmethod
    def delete(id):
        bt('ec2').delete_route_table(
            RouteTableId = id
        )

class cRouteTableAssociation(cParent):
    Prefix = "rtba"
    Draw = DRAW.ALL
    Color = '#c19fff'
    ListName = "Associations"
    Index = None

    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)
        self.Id   = f"{self.RouteTableId}{ID_DV}{self.RouteTableAssociationId}"
        self.View = f"{Id17(self.SubnetId)}" if hasattr(self, "SubnetId") else "-"
        self.Ext  = f"{Id17(self.SubnetId)}" if hasattr(self, "SubnetId") else "-"

    @staticmethod
    def fields():
        return {
#                    "ParentId"               : (cRouteTable, fList),
                    'Id'  : (str, FIELD.ID),
                    'Ext' : (str, FIELD.EXT),
                    'View': (str, FIELD.VIEW),
                    'RouteTableId'           : (cRouteTable, FIELD.LIST_ITEM),
                    'ListName'               : (cRouteTable, FIELD.LIST_NAME),
                    'SubnetId'               : (cSubnet, FIELD.LINK_IN),
#                    'AssociationState'       : str, #!!!
                } # +

    @staticmethod
    def get_objects(id=None):
        return cRouteTable.get_objects_by_index(id, "Associations", 'RouteTableAssociationId')

    # def get_id(self):
    #     return f"{self.RouteTableId}{ID_DV}{self.RouteTableAssociationId}"

    # def get_ext(self):
    #     if hasattr(self, "SubnetId"):
    #         return f"{Id17(self.SubnetId)}"
    #     return "-"
    
    # def get_view(self):
    #     return f"Route[{self.Index}]"
    

    @staticmethod
    def create(RouteTableId, SubnetId):
        resp = bt('ec2').associate_route_table(SubnetId = SubnetId, RouteTableId = RouteTableId)
        return f"{RouteTableId}{ID_DV}{resp['AssociationId']}"

    @staticmethod
    def delete(id):
        RouteTableId, _, AssociationId = id.rpartition(ID_DV)
        bt('ec2').disassociate_route_table(
            AssociationId = AssociationId
        )


class cRoute(cParent):
    Prefix = "route"
    Draw = DRAW.ALL-DRAW.ID
    Icon = "Route"
    Color = '#c19fff'
    Index = None
    DontFetch = True
    ListName = "Routes"

    @staticmethod
    def fields():
        return {
                    'ListName'             : (cRouteTable      , FIELD.LIST_NAME),
                    "ParentId"             : (cRouteTable      , FIELD.LIST_ITEM),
                    "GatewayId"            : (cInternetGateway , FIELD.LINK_OUT),
                    "InstanceId"           : (cEC2             , FIELD.LINK_OUT),
                    "NatGatewayId"         : (cNATGateway      , FIELD.LINK_OUT),
                    "NetworkInterfaceId"   : (cNetworkInterface, FIELD.LINK_OUT),

                    "GatewayId_local"      : (cVpc             , FIELD.LINK_IN),
                } # +

    @staticmethod
    def get_objects(id=None):
        return cRouteTable.get_objects_by_index(id, "Routes", int)
    
    def get_id(self):
        return f"{self.ParentId}{ID_DV}{self.DestinationCidrBlock}"

    def get_view(self):
#        return f"{self.Index}"
        return f"{getattr(self, 'DestinationCidrBlock', '-')}"

    def get_ext(self):
        return f"{getattr(self, 'DestinationCidrBlock', '-')}"

    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)

        if hasattr(self, "GatewayId") and self.GatewayId == "local":
            self.GatewayId = None
            setattr(self, "GatewayId_local", cRouteTable.get_objects(self.ParentId)[0]["VpcId"])

    @staticmethod
    def create(RouteTableId, DestinationCidrBlock, GatewayId = None, NatGatewayId = None):
        args = {
            "RouteTableId": RouteTableId,
            "DestinationCidrBlock": DestinationCidrBlock,
        }

        if GatewayId is not None:
            args["GatewayId"] = GatewayId
        
        if NatGatewayId is not None:
            args["NatGatewayId"] = NatGatewayId

        resp = bt('ec2').create_route(**args)

        return f"{RouteTableId}{ID_DV}{DestinationCidrBlock}"
    
    @staticmethod
    def delete(id):
        RouteTableId, _, DestinationCidrBlock = id.rpartition(ID_DV)

        try:
            bt('ec2').delete_route(
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
    Draw = DRAW.ALL
    Icon = "VPC"
    Color = '#E3D5FF'

    @staticmethod
    def fields():
        return {
                    "VpcId"           : (cVpc, FIELD.ID),
                    "NetworkAclId"    : (cNetworkAcl),
                    'Tags'            : ({"Key" : "Value"})
#                    'CidrBlockAssociationSet' : [{'AssociationId': 'vpc-cidr-assoc-070bb...bcc9c9695b', 'CidrBlock': '10.222.0.0/16', 'CidrBlockState': {...}}],
                }
    
    @staticmethod
    def get_objects(id=None):
        resp = bt('ec2').describe_vpcs(**idpar('VpcIds', id))
        return resp['Vpcs']
    
    def get_ext(self):
        return f"{getattr(self, 'CidrBlock', '-')}"
    
    @staticmethod
    def create(Name, CidrBlock):
        id = bt('ec2').create_vpc(CidrBlock=CidrBlock)['Vpc']['VpcId']
        cTag.create(id, "Name", f"{cVpc.Prefix}-{Name}")
        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').delete_vpc(
            VpcId = id
        )
    
    @staticmethod
    def cli_add(Name, CidrBlock):
        return f"id000000001"

class cNetworkInterface(cParent): 
    Prefix = "ni"
    Icon = "Res_Amazon-VPC_Elastic-Network-Interface_48"
    Color = '#c19fff'
    ListName = "NetworkInterfaces"

    @staticmethod
    def fields():
        return {
                    "NetworkInterfaceId" : (cNetworkInterface, FIELD.ID),
                    "VpcId"              : cVpc,
                    "SubnetId"           : (cSubnet, FIELD.LIST_ITEM),
                    "ListName"           : (cSubnet, FIELD.LIST_NAME),
#                    "PrivateIpAddresses" : str, # print("Private IP Addresses:", [private_ip['PrivateIpAddress'] for private_ip in network_interface['PrivateIpAddresses']])
#                    "Attachment"         : str, #    print("Attachment ID:", network_interface['Attachment']['AttachmentId'])
                }
    
    @staticmethod
    def get_objects(id=None):
        return bt('ec2').describe_network_interfaces(**idpar('NetworkInterfaceIds', id))['NetworkInterfaces']

    @staticmethod
    def cli_add(Name, CidrBlock, fdrgtd):
        return f"id000000002"


class cS3(cParent): 
    Prefix = "s3"
    Icon = "Arch_Amazon-Simple-Storage-Service_48"
    DontFetch = True

    @staticmethod
    def fields():
        return {
                    "Name" : (cS3, FIELD.ID),
#                    'CreationDate': datetime.datetime(2023, 9, 29, 12, 28, 16, tzinfo=tzutc())
                }
    
    @staticmethod
    def get_objects(id=None):
        if id is None:
            response = bt('s3').list_buckets()
            return response['Buckets']
        else:
            response = bt('s3').head_bucket(Bucket=id)
            return [response]



class cElasticIP(cParent):
    Prefix = "eipassoc"
    Icon = "ElasticIP"
    Color = "#ffc28c"

    @staticmethod
    def fields():
        return {
                    'AllocationId': (cElasticIP, FIELD.ID),
                    'Tags': ({"Key" : "Value"}),
                }
    
    @staticmethod
    def create(Name):
        id = bt('ec2').allocate_address(Domain='vpc')['AllocationId']
        cTag.create(id, "Name", f"{cElasticIP.Prefix}-{Name}")
        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').release_address(
            AllocationId = id
        )

    @staticmethod
    def get_objects(id=None):
        resp = bt('ec2').describe_addresses(**idpar('AllocationIds', id))
        return resp['Addresses']


class cKeyPair(cParent):
    Prefix = "key"
    DontFetch = True
    Icon = "KeyPair"
    
    @staticmethod
    def fields():
        return {
                    'KeyPairId': (cKeyPair, FIELD.ID),
                    'Tags': ({"Key" : "Value"}),
                }
    
    def Destroy(id):
        bt('ec2').delete_key_pair(KeyPairId = id)

    @staticmethod
    def cli_add(Name):
        return f"aws ec2 create-key-pair --key-name {Name} --query 'KeyMaterial' --output text > {Name}.pem"

    @staticmethod
    def cli_del(Name):
        return f"aws ec2 delete-key-pair --key-name {Name}"

    @staticmethod
    def get_objects(id=None):
        response = bt('ec2').describe_key_pairs(**idpar('KeyPairIds', id))
        return response['KeyPairs']


    @staticmethod
    def create(Name):
        KeyName = f"{cKeyPair.Prefix}-{Name}"
        resp = bt('ec2').create_key_pair(KeyName=KeyName)

        private_key = resp['KeyMaterial']
        try:
            with open(f'PrivateKeys\\{KeyName}.pem', 'w') as key_file: key_file.write(private_key)
        except Exception as e:
            print(f"KeyPair.create: An exception occurred: {type(e).__name__} - {e}")

        id = resp['KeyPairId']

        return id
    
    @staticmethod
    def delete(id):
        bt('ec2').delete_key_pair(KeyPairId = id)

    @staticmethod
    def IdToName(KeyPairId):
    #   KeyName = boto3.resource('ec2').KeyPair(KeyPairId).key_name # does not work
        resp = bt('ec2').describe_key_pairs(KeyPairIds=[KeyPairId])
        KeyName = resp['KeyPairs'][0]['KeyName']
        return KeyName
    
    @staticmethod
    def NameToId(Name):
        resp = bt('ec2').describe_key_pairs(KeyNames=[Name])
        KeyPairId = resp['KeyPairs'][0]['KeyPairId']
        return KeyPairId

    def get_view(self):
        return f"{self.KeyName}"


class cSNS(cParent):
    DontFetch = True
    Icon = "Arch_Amazon-Simple-Notification-Service_48"

    @staticmethod
    def create(Name):
        resp = bt('sns').create_topic(Name=Name)
        return resp['TopicArn']


class cUser(cParent):
    Icon = "Res_User_48_Light"

    @staticmethod
    def get_objects(id=None):
        if id is None:
            response = bt('iam').list_users()
            return response['Users']
        
        else:
            response = bt('iam').get_user(UserName=id)
            return [response['User']]

    def get_id(self):
        return f"{self.UserName}"


class cGroup(cParent):
    Icon = "Res_Users_48_Light"

    @staticmethod
    def get_objects(id=None):
        if id is None:
            response = bt('iam').list_groups()
            return response['Groups']
        
        else:
            response = bt('iam').get_group(GroupName=id)
            return [response['Group']]

    def get_id(self):
        return f"{self.GroupName}"


class cRole(cParent):
    DontFetch = True
    Icon = "Res_AWS-Identity-Access-Management_Role_48"

    @staticmethod
    def get_objects(id = None):
        if id is None:
            response = bt('iam').list_roles()
            return response['Roles']
        
        else:
            response = bt('iam').get_role(RoleName=id)
            return [response['Role']]

    def get_id(self):
        return f"{self.RoleName}"


    
class cFunction(cParent):
    Icon = "Arch_AWS-Lambda_48"
    Color = "#ffc28c"

    @staticmethod
    def fields():
        return {
                    'FunctionName': (cFunction, FIELD.ID),
                    'Tags': ({"Key" : "Value"}),
                }

    @staticmethod
    def get_objects(id=None):
        if id is None:
            response = bt('lambda').list_functions()
            return response['Functions']
        else:
            response = bt('lambda').get_function(FunctionName=id)
            return [response["Configuration"]]
        
    @staticmethod
    def create(Name, Code):
        handler = 'lambda_function.lambda_handler'
        runtime = 'python3.12'
        role_arn = 'arn:aws:iam::047989593255:role/lambda-s3-role'

        data_bytes = Code.encode()
        with io.BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr('lambda_function.py', data_bytes)

                file_info = zip_file.getinfo('lambda_function.py')
                unix_st_mode = stat.S_IFLNK | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
                file_info.external_attr = unix_st_mode << 16 

            zipped_data = zip_buffer.getvalue()

        response = bt('lambda').create_function(
            FunctionName=Name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zipped_data},
            Timeout=30,
            MemorySize=128,
        )        
        return response['FunctionName']
    
    @staticmethod
    def delete(id):
        bt('lambda').delete_function(FunctionName=id)

    def Invoke(id, payload):
        response = bt('lambda').invoke(
            FunctionName=id,
            InvocationType='RequestResponse',  # Или 'Event' для асинхронного вызова
            Payload=str(payload).replace("'",'"')
        )

        result = response['Payload'].read().decode('utf-8')
        result = json.loads(result)
        return result


class cDBInstance(cParent):
    Icon = "Arch_Amazon-RDS_48"
    Color = "#e998ed"

    @staticmethod
    def fields():
        return {
                    'DBInstanceIdentifier': (cDBInstance, FIELD.ID),
                    'DBSubnetGroupName': (cDBSubnetGroup, FIELD.OWNER),
                    'Tags': ({"Key" : "Value"}),
                }

    @staticmethod
    def get_objects(id = None):
        response = bt('rds').describe_db_instances(**idpar('DBInstanceIdentifier', id, pPar))
        return response['DBInstances']

    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)

        if hasattr(self, "DBSubnetGroup"):
            setattr(self, "DBSubnetGroupName", self.DBSubnetGroup["DBSubnetGroupName"])
    
    @staticmethod
    def create(Name, DBSubnetGroupName, User, Pass):
        response = bt('rds').create_db_instance(
            DBInstanceIdentifier = Name,
            DBInstanceClass = AWS.Const['RDS.InstanceType'],
            Engine = AWS.Const['RDS.Engine'],
            MasterUsername=User,
            MasterUserPassword=Pass,
            AllocatedStorage=20,
            DBSubnetGroupName=DBSubnetGroupName,
            MultiAZ=False,
            PubliclyAccessible=True,
        )

        return response['DBInstance']['DBInstanceIdentifier']

    @staticmethod
    def delete(id, SkipFinalSnapshot = True):
        bt('rds').delete_db_instance(
            DBInstanceIdentifier = id,
            SkipFinalSnapshot = SkipFinalSnapshot
        )        
    
class cDBSubnetGroup(cParent):
    Icon = "Arch_Amazon-RDS_48"
    Color = "#f2c4f4"

    @staticmethod
    def fields():
        return {
                    'DBSubnetGroupName': (cDBSubnetGroup, FIELD.ID),
                    'VpcId': (cVpc, FIELD.OWNER),
                    'Subnets': [cDBSubnetGroupSubnet],
                }

    @staticmethod
    def get_objects(id = None):
        response = bt('rds').describe_db_subnet_groups(**idpar('DBSubnetGroupName', id, pPar))
        return response['DBSubnetGroups']
    
    @staticmethod
    def create(Name, DBSubnetGroupDescription, SubnetIds):
        response = bt('rds').create_db_subnet_group(
            DBSubnetGroupName = Name,
            DBSubnetGroupDescription=DBSubnetGroupDescription,
            SubnetIds = SubnetIds
        )
        return response['DBSubnetGroup']['DBSubnetGroupName']

    @staticmethod
    def delete(id):
        response = bt('rds').delete_db_subnet_group(DBSubnetGroupName=db)
        return

class cDBSubnetGroupSubnet(cParent):
    Index = None
    ListName = "Subnets"

    @staticmethod
    def fields():
        return {
                    'Id'  : (str, FIELD.ID),
                    'SubnetIdentifier': (cSubnet, FIELD.LINK_IN),
                    'ParentId': (cDBSubnetGroup, FIELD.LIST_ITEM),
                    'ListName': (str, FIELD.LIST_NAME),
                    'View': (str, FIELD.VIEW),
                }

    def __init__(self, aws, id_query, Index, resp, do_auto_save=True):
        super().__init__(aws, id_query, Index, resp, do_auto_save)
        self.Id   = f"{self.ParentId}{ID_DV}{self.SubnetIdentifier}"
        self.View = f"{self.SubnetIdentifier}"

    @staticmethod
    def get_objects(id = None):
        return cDBSubnetGroup.get_objects_by_index(id, "Subnets", 'SubnetIdentifier')

class cDynamoDB(cParent):
    Icon = "Arch_Amazon-DynamoDB_48"
    Color = "#e998ed"

    @staticmethod
    def fields():
        return {
                    'TableName': (cDynamoDB, FIELD.ID),
                }

    @staticmethod
    def get_objects(id = None):
        if id is None:
            response = bt('dynamodb').list_tables()
            res = []
            for curid in response["TableNames"]:
                res += cDynamoDB.get_objects(curid)
            return res
        
        else:
            response = bt('dynamodb').describe_table(TableName = id)
            return [response["Table"]]

    @staticmethod
    def create(id):
        attribute_definitions = [
            {'AttributeName': 'id', 'AttributeType': 'N'}, # Add other attribute definitions as needed
        ]
        key_schema = [
            {'AttributeName': 'id', 'KeyType': 'HASH'}, # Add other key schema elements as needed
        ]
        provisioned_throughput = {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}

        response = bt('dynamodb').create_table(
            TableName=id,
            AttributeDefinitions=attribute_definitions,
            KeySchema=key_schema,
            ProvisionedThroughput=provisioned_throughput
        )
        return id

    @staticmethod
    def delete(id):
        response = bt('dynamodb').delete_table(TableName=id)
        return


class AWS(ObjectModel):
    def __init__(self, profile, path, do_auto_load = True, do_auto_save = True):

        setattr(AWS, "PROFILE", profile)

        super().__init__(
            path,
            do_auto_load,
            do_auto_save, 
            {
                'EC2.UserData.Apache' : ""\
                                + "#!/bin/bash\n"\
                                + "yum update -y\n"\
                                + "yum install httpd -y\n"\
                                + "systemctl start httpd\n"\
                                + "systemctl enable httpd\n",
                'EC2.InstanceType' : 't2.micro',
                'EC2.ImageId.Linux' : 'ami-0669b163befffbdfc',

                'RDS.InstanceType' : 'db.t3.micro',
                'RDS.Engine' : 'mysql',
                'DrawRDS' : 'Vpc, Subnet, RDS'
            },
            {
                'VPC' : [
                    cKeyPair,
                    cVpc, cSecurityGroup, cSecurityGroupRule,
                    cInternetGateway, cInternetGatewayAttachment,
                    cNetworkAcl, cNetworkAclEntry,
                ],
                'SUBNET' : [
                    cSubnet,
                    cRouteTable, cRoute, cRouteTableAssociation,
                    cElasticIP, 
                    cNATGateway, cElasticIPAssociation, 
                ],
                'RDS' : [cDBSubnetGroup, cDBSubnetGroupSubnet, cDBInstance, cDynamoDB],
                'AMI' : [cUser, cGroup, cRole],
                'OTHER' : [
                    cReservation, cEC2, cNetworkInterface,
                    cS3,
                    cSNS,
                    cFunction,
                ],
            }
        )
