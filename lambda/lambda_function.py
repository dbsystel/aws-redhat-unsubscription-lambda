# Copyright: DB Systel GmbH
# License: Apache-2.0
import boto3
import json
from botocore.vendored import requests

ssm = boto3.client('ssm')
relevant_events = ['EC2 Instance State-change Notification']


def handler(event, context):
    status_code = 500
    if event['detail-type'] in relevant_events:
        print('Received EC2 termination event, will check if a RedHat unsubscription is necessary.')
        detail = event['detail']

        if detail and detail['state'] == 'terminated' and detail['instance-id']:
            instance_id = detail['instance-id']
            print('Will check if instance with ID \'' + instance_id + '\' has a subscription tag.')

            subscription_id = get_redhat_subscription_id(instance_id)
            if subscription_id:
                status_code = delete_subscription(subscription_id)
            else:
                print('Did not find a subscription id for instance with ID \'' + instance_id +
                      '\' so there is nothing to do.')
        else:
            print('Did not find an instance id in the event.')
    else:
        print('Did not receive an EC2 termination event, so there is nothing to do.')
        status_code = 200
    return {
        'statusCode': status_code,
        'body': json.dumps('RedHat unsubscription executed.')
    }


def get_redhat_subscription_id(instance_id):
    subscription_id = ''
    ec2 = boto3.client('ec2')
    instance_tags = ec2.describe_tags(Filters=[{
            'Name': 'resource-id',
            'Values': [
                instance_id
            ]
        },
        {
            'Name': 'key',
            'Values': [
                'RedHatRegistrationUuid'
            ]
        }])
    tags = instance_tags[u'Tags']
    if tags and len(tags) > 0:
        print('Found \'RedHatRegistrationUuid\' tag, will try to unsubscribe this instance.')
        tag = tags[0]
        subscription_id = tag[u'Value']
    else:
        print('Did not find \'RedHatRegistrationUuid\' tag, so there is nothing to do for this instance.')
    return subscription_id


def delete_subscription(subscription_id):
    request_url = 'https://subscription.rhn.redhat.com/subscription/consumers/' + subscription_id

    print('Retrieving RedHat credentials from SSM.')
    username = get_value_from_ssm('redhat-subscription-username', False)
    password = get_value_from_ssm('redhat-subscription-password', True)

    print('Deleting subscription ' + subscription_id + ' for user ' + username)
    response = requests.delete(request_url, auth=(username, password), verify='./redhat-uep.pem')
    print(response)

    code = response.status_code
    if code == 204:
        print('Successfully deleted the RedHat subscription ' + subscription_id)
    else:
        print('Got a response with code ' + code + '. Probably did not delete the subscription.')
    return code


def get_value_from_ssm(name, decrypt):
    value = ''
    response = ssm.get_parameter(Name=name, WithDecryption=decrypt)
    if response:
        param = response['Parameter']
        if param:
            value = param['Value']
        else:
            print('SSM response does not contain Parameter object.')
    else:
        print('Did not get a valid response from SSM for parameter: ' + name)
    return value
