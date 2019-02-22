# aws-redhat-unsubscription-lambda
This is an AWS Lambda function that will automatically unsubscribe EC2 instances running RHEL once they are being terminated.

For now, you can use this function if you manually create a CloudWatch event rule and an IAM role as described in the requirements.
In the future, there will be a full CDK app that you can use to automatically deploy the Lambda function with the CloudWatch event rule and the IAM role.
Once the CDK app exists, the only manual task will be to add the RedHat credentials to SSM.

## Requirements
* Your RedHat credentials need to be stored in SSM as follows:
  * The username has to be a String named `redhat-subscription-username`.
  * The password has to be a SecureString named `redhat-subscription-password`.
* A CloudWatch event rule with the following event pattern is necessary:
  ```
  {
    "detail-type": [
      "EC2 Instance State-change Notification"
    ],
    "source": [
      "aws.ec2"
    ],
    "detail": {
      "state": [
        "terminated"
      ]
    }
  }
  ```
* An IAM role that has the `AWSLambdaBasicExecutionRole` policy and an inline policy with permissions similar to the following example:
  ```
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Action": "logs:*",
              "Resource": "*",
              "Effect": "Allow"
          },
          {
              "Action": "ec2:DescribeTags",
              "Resource": "*",
              "Effect": "Allow"
          },
          {
              "Action": [
                  "ssm:Describe*",
                  "ssm:Get*",
                  "ssm:List*"
              ],
              "Resource": "*",
              "Effect": "Allow"
          }
      ]
  }
  ```
  __Please adapt the permissions according to your individal AWS account structure - for example, if you want the Lambda to
  only operate on a certain CloudFormation stack or a certain SSM scope!__
* The instances to be handled by the Lambda are tagged with the subscription UUID in the tag `RedHatRegistrationUuid`.

## Setup
* Create the CloudWatch event rule and the IAM role as described in the requirements.
* Create the Lambda function in whichever way you want to do it - for example, you can zip the files of the subfolder `lambda` and use that zip file.
* Associate the Lambda function with the previously created IAM role.
* Link the previously created CloudWatch event rule as the Lambda function's trigger.
* Now every EC2 instance tagged with `RedHatRegistrationUuid` should be handle by the Lambda.

## Troubleshooting
* The Lambda function logs to CloudWatch, so you can read the logs there.
* Feel free to add more output to the Lambda function in your account - for example, if you want to output the full event that
  was received you can add `print(json.dumps(event))` to the beginning of the function.
