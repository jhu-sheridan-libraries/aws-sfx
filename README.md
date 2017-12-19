# AWS SFX 
A python script to generate a cloudformation template, create or update the stacks.  Includes python script, playbook, etc.

## Getting Started
It is recommended that this is run in a python virtual environment (I used virtualenvwrapper and virtualenv).

### Prerequisites
- Python 3.6 (might work with 2.7, but has not been tested)
- Python pip

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



