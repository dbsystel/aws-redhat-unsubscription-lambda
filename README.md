# aws-redhat-unsubscription-lambda
This is an AWS lambda function that will automatically unsubscribe EC2 instances running on RHEL once they are being terminated. The only pre-condition is that the instance is tagged with the subscription UUID in the tag "RedHatRegistrationUuid".
