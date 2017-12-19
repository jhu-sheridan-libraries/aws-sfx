#!/usr/bin/evn python

from troposphere import Ref, Join, Template, Parameter, GetAtt, Base64
from troposphere.ec2 import Instance, SecurityGroup, SecurityGroupIngress, SecurityGroupRule, EIP, EIPAssociation, Tags
from troposphere.cloudformation import Stack
from troposphere.route53 import *
from troposphere.iam import Role, InstanceProfile

import datetime
import boto3


class SFXTemplate:
    def __init__(self):
        self.template = Template()

    def buildParameters(self):
        self.paramKeyName=self.template.add_parameter(Parameter(
            "KeyName",
            Description='SSH Keyname to start',
            Type='AWS::EC2::KeyPair::KeyName'
        ))

        self.paramImageId=self.template.add_parameter(Parameter(
            "ImageId",
            Description='Image ID of the AMI used to create the Instance',
            Type='AWS::EC2::Image::Id',
        ))

    def buildTemplate(self):
        self.role = self.template.add_resource(Role(
            "SFX-TestRole",
            
            
        self.vpc = self.template.add_resource(Stack(
            'Vpc',
            TemplateURL="https://s3.amazonaws.com/msel-cf-templates/vpc.template",
            Parameters={
                'Department': 'LAG'
            }
        ))

        self.subnet = self.template.add_resource(Stack(
            'Subnet',
            TemplateURL='https://s3.amazonaws.com/msel-cf-templates/subnet.template',
            Parameters={
                'VPCID': GetAtt(self.vpc, 'Outputs.VpcId'),
                'CidrBlock': '10.0.1.0/24',
                'Department': 'LAG',
                'MapPublicIP': 'True',
                'RouteTableId': GetAtt(self.vpc, 'Outputs.RouteTableId'),
            }
        ))

        securitygroup = self.template.add_resource(SecurityGroup(
            "SecurityGroup",
            GroupDescription='SFX ports SSH, HTTP, HTTPS',
            VpcId=GetAtt(self.vpc, 'Outputs.VpcId'),
            SecurityGroupIngress=[
                SecurityGroupRule(
                    CidrIp='0.0.0.0/0',
                    Description='Allow SSH (port 22) from all',
                    FromPort='22',
                    ToPort='22',
                    IpProtocol='tcp',
                ),
                SecurityGroupRule(
                    CidrIp='0.0.0.0/0',
                    Description='Allow HTTP (port 80) from all',
                    FromPort='80',
                    ToPort='80',
                    IpProtocol='tcp',
                ),
                SecurityGroupRule(
                    CidrIp='0.0.0.0/0',
                    Description='Allow HTTPS (port 443) from all',
                    FromPort='443',
                    ToPort='443',
                    IpProtocol='tcp',
                ),                                
            ]
            ))

        self.eip = self.template.add_resource(EIP('EIP'))
        self.instance=self.template.add_resource(Instance(
            'SFXInstance',
            ImageId=Ref(self.paramImageId),
            KeyName=Ref(self.paramKeyName),
            SubnetId=GetAtt(self.subnet, 'Outputs.SubnetId'),
            SecurityGroupIds=[Ref(securitygroup)],
            Tags=Tags(
                Name='SFX Test Instance',
                Department='LAG',
                Project='SFX',
            ),
            UserData=Base64(Ref(self.userdata)),
        ))

        self.template.add_resource(EIPAssociation(
            "EIPAssoc",
            EIP=Ref(self.eip),
            InstanceId=Ref(self.instance),
        ))

        self.template.add_resource(RecordSetType(
            "dnsRecord",
            HostedZoneName=Join("", ['cloud.library.jhu.edu', '.']),
            Comment="SFX-Test",
            Name=Join('', ['sfx-test', ".", "cloud.library.jhu.edu"]),
            Type="A",
            TTL="300",
            ResourceRecords=[GetAtt(self.instance, 'PublicIp')],
        ))

            

    def upload(self):
        import sys
        
        session = boto3.Session(profile_name='jhu')
        cf_client = session.client('cloudformation')
        stacks=cf_client.describe_stacks()
        datestamp=f"{datetime.datetime.now():%Y%m%d%H%M%S}"

        update = False
        for stack in stacks['Stacks']:
            if stack['StackName'] == 'SFX-Test':
                update = True

        if update:
            waiter = cf_client.get_waiter('stack_update_complete')
            createdict=cf_client.update_stack(
                StackName='SFX-Test',
                TemplateBody=self.template.to_json(),
                Parameters=[
                    {
                        'ParameterKey':'KeyName',
                        'UsePreviousValue': True
                    },
                    {
                        'ParameterKey': 'ImageId',
                        'UsePreviousValue': True
                    },
                ],
                ClientRequestToken='sfxtest-clouformation-update-'+datestamp
            )
            print ('Updating...')
        else:
            waiter = cf_client.get_waiter('stack_create_complete')
            createdict=cf_client.create_stack(
                StackName='SFX-Test',
                TemplateBody=self.template.to_json(),
                Parameters=[
                    {
                        'ParameterKey':'KeyName',
                        'ParameterValue': 'operations',
                    },
                    {
                        'ParameterKey': 'ImageId',
                        'ParameterValue': 'ami-6f3f4915',
                    },
                ],
                ClientRequestToken='sfxtest-clouformation-create-'+datestamp
            )
            print ('Creating...')

        waiter.wait(StackName='SFX-Test')

        
    def __str__(self):
        return(self.template.to_json())

def main():
    sfx = SFXTemplate()
    sfx.buildParameters()
    sfx.buildTemplate()

    sfx.upload()
if __name__ == '__main__':
    main()

