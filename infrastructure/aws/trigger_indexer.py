#!/usr/bin/env python3

import boto3
from datetime import datetime, timedelta
import sys
import os.path

# Usage: trigger_indexer.py <mozsearch-repo> <config-repo> <config-input> <branch> <channel>

def trigger(mozsearch_repo, config_repo, config_input, branch, channel):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')

    running = ec2.instances.filter(Filters=[{'Name': 'tag-key', 'Values': ['indexer']},
                                           {'Name': 'tag:channel', 'Values': [channel]},
                                           {'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in running:
        print("Terminating existing running indexer %s for channel %s" % (instance.instance_id, channel))
        instance.terminate()

    user_data = '''#!/usr/bin/env bash

cd ~ubuntu
sudo -i -u ubuntu ./update.sh "{branch}" "{mozsearch_repo}" "{config_repo}"
sudo -i -u ubuntu mozsearch/infrastructure/aws/main.sh index.sh 10 "{branch}" "{channel}" "{mozsearch_repo}" "{config_repo}" config "{config_input}"
'''.format(branch=branch, channel=channel, mozsearch_repo=mozsearch_repo, config_repo=config_repo, config_input=config_input)

    block_devices = []

    images = client.describe_images(Filters=[{'Name': 'name', 'Values': ['indexer-20.04']}])
    image_id = images['Images'][0]['ImageId']

    launch_spec = {
        'ImageId': image_id,
        'KeyName': 'Main Key Pair',
        'SecurityGroups': ['indexer-secure'],
        'UserData': user_data,
        'InstanceType': 'm5d.2xlarge',
        'BlockDeviceMappings': block_devices,
        'IamInstanceProfile': {
            'Name': 'indexer-role',
        },
        'TagSpecifications': [{
            'ResourceType': 'instance',
            'Tags': [{
                'Key': 'indexer',
                'Value': str(datetime.now())
            }, {
                'Key': 'channel',
                'Value': channel,
            }, {
                'Key': 'branch',
                'Value': branch,
            }, {
                'Key': 'mrepo',
                'Value': mozsearch_repo,
            }, {
                'Key': 'crepo',
                'Value': config_repo,
            }, {
                'Key': 'cfile',
                'Value': config_input,
            }],
        }],
    }
    return client.run_instances(MinCount=1, MaxCount=1, **launch_spec)


if __name__ == '__main__':
    mozsearch_repo = sys.argv[1]
    config_repo = sys.argv[2]
    config_input = sys.argv[3]
    branch = sys.argv[4]
    channel = sys.argv[5]

    trigger(mozsearch_repo, config_repo, config_input, branch, channel)
