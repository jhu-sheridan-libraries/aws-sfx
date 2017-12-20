#!/bin/bash -xe

pip install awscli ansible --no-cache-dir
git clone https://www.github.com/jhu-sheridan-libraries/aws-sfx.git /tmp/deploy/aws-sfx

ansible-pull -d /tmp/deploy/aws-sfx/playbook.yml

#delete deployment directory
rm -rf /tmp/deploy
