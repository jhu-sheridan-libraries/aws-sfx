# AWS SFX 
A python script to generate a cloudformation template, create or update the stacks.  Includes python script, playbook, etc.

## Getting Started
It is recommended that this is run in a python virtual environment (I used virtualenvwrapper and virtualenv).

### Prerequisites
- Python 3.6 (might work with 2.7, but has not been tested)
- Python pip
- Access to the msel-cf-templates S3 bucket via IAM (contact Derek for access)z
- IAM access to Cloudformation, EC2, Route53, etc

### Preparing Environment

``` bash
mkvirtualenv -p /usr/local/bin/python3.6 awssfx
workon awssfx
git clone https://www.github.com/jhu-sheridan-libraries/aws-sfx.git
cd aws-sfx
pip install -r requirements.txt

aws configure
# complete configuration and provide your aws key id and secret key
```

### Creating and updating Cloudformation scripts

``` bash
# Switch to the existing virtual environment
workon awssfx
python template.py -p myawsprofile
```

This creates a new Cloudformation Stack called Test-SFX and two substacks that include a VPC, Subnet, RouteTable, some routes and an InternetGateway.  The main stack creates a SecurityGroup, EC2 instance, ElasticIP and a Route53 RecordSet for sfx-test.cloud.library.jhu.edu.
