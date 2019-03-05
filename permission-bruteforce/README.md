# Enumerate IAM

The following code will attempt to enumerate operations that a given set of AWS AccessKeys
can perform.

# Source

The original version of this script was found at in [this gist](https://gist.github.com/darkarnium/1df59865f503355ef30672168063da4e)
and developed by [darkarnium](https://gist.github.com/darkarnium).

## Usage
```
Usage: enumerate-iam.py [OPTIONS]

  IAM Account Enumerator.

  This code provides a mechanism to attempt to validate the permissions
  assigned to a given set of AWS tokens.

Options:
  --access-key TEXT     An AWS Access Key Id to check
  --secret-key TEXT     An AWS Secret Access Key to check
  --session-token TEXT  An AWS Session Token to check
  --help                Show this message and exit.
```

## Example

```
$ python enumerate-iam.py --access-key <KEY> --secret-key <SECRET>
2017-05-06 00:16:05,164 - 5692 - [INFO] Starting scrape for access-key-id "<KEY>"
2017-05-06 00:16:06,107 - 5692 - [ERROR] Failed to get everything at once (get_account_authorization_details) :(
2017-05-06 00:16:06,210 - 5692 - [INFO] -- Account ARN : arn:aws:iam::NNNNNNNNNNN:user/some-other-user
2017-05-06 00:16:06,210 - 5692 - [INFO] -- Account Id  : NNNNNNNNNNN
2017-05-06 00:16:06,210 - 5692 - [INFO] -- Account Path: user/some-other-user
2017-05-06 00:16:06,321 - 5692 - [INFO] User "some-other-user" has 1 attached policies
2017-05-06 00:16:06,321 - 5692 - [INFO] -- Policy "some-policy" (arn:aws:iam::NNNNNNNNNNN:policy/some-policy)
2017-05-06 00:16:06,436 - 5692 - [INFO] User "some-other-user" has 1 inline policies
2017-05-06 00:16:06,436 - 5692 - [INFO] -- Policy "policygen-some-other-user-201705060014"
2017-05-06 00:16:06,543 - 5692 - [INFO] User "some-other-user" has 0 groups associated
2017-05-06 00:16:06,543 - 5692 - [INFO] Attempting common-service describe / list bruteforce.
...
```

```
$ python enumerate-iam.py --access-key <KEY> --secret-key <SECRET>
2017-05-05 23:52:27,194 - 3060 - [INFO] Starting scrape for access-key-id "<KEY>"
2017-05-05 23:52:28,206 - 3060 - [ERROR] Failed to get everything at once (get_account_authorization_details) :(
2017-05-05 23:52:28,293 - 3060 - [ERROR] Failed to retrieve any IAM data for this key.
2017-05-05 23:52:28,293 - 3060 - [INFO] -- Account ARN : arn:aws:iam::NNNNNNNNNNN:user/some-user
2017-05-05 23:52:28,293 - 3060 - [INFO] -- Account Id  : NNNNNNNNNNN
2017-05-05 23:52:28,293 - 3060 - [INFO] -- Account Path: user/some-user
2017-05-05 23:52:28,293 - 3060 - [INFO] Attempting common-service describe / list bruteforce.
2017-05-05 23:52:28,301 - 3060 - [INFO] Checking ACM (Certificate Manager)
2017-05-05 23:52:28,737 - 3060 - [ERROR] -- list_certificates() failed
2017-05-05 23:52:28,762 - 3060 - [INFO] Checking CFN (CloudFormation)
2017-05-05 23:52:29,184 - 3060 - [ERROR] -- describe_stacks() failed
2017-05-05 23:52:29,193 - 3060 - [INFO] Checking CloudHSM
2017-05-05 23:52:29,611 - 3060 - [ERROR] -- list_hsms() failed
2017-05-05 23:52:29,625 - 3060 - [INFO] Checking CloudSearch
2017-05-05 23:52:30,069 - 3060 - [ERROR] -- list_domain_names() failed
2017-05-05 23:52:30,078 - 3060 - [INFO] Checking CloudTrail
2017-05-05 23:52:30,529 - 3060 - [ERROR] -- describe_trails() failed
2017-05-05 23:52:30,536 - 3060 - [INFO] Checking CloudWatch
2017-05-05 23:52:30,926 - 3060 - [ERROR] -- describe_alarm_history() failed
2017-05-05 23:52:30,936 - 3060 - [INFO] Checking CodeCommit
2017-05-05 23:52:31,338 - 3060 - [ERROR] -- list_repositories() failed
2017-05-05 23:52:31,374 - 3060 - [INFO] Checking CodeDeploy
2017-05-05 23:52:31,782 - 3060 - [ERROR] -- list_applications() failed
2017-05-05 23:52:31,881 - 3060 - [ERROR] -- list_deployments() failed
2017-05-05 23:52:31,953 - 3060 - [INFO] Checking EC2 (Elastic Compute)
2017-05-05 23:52:32,345 - 3060 - [ERROR] -- describe_instances() failed
2017-05-05 23:52:32,440 - 3060 - [ERROR] -- describe_images() failed
2017-05-05 23:52:32,539 - 3060 - [ERROR] -- describe_addresses() failed
2017-05-05 23:52:32,630 - 3060 - [ERROR] -- describe_hosts() failed
2017-05-05 23:52:32,721 - 3060 - [ERROR] -- describe_nat_gateways() failed
2017-05-05 23:52:32,819 - 3060 - [ERROR] -- describe_key_pairs() failed
2017-05-05 23:52:32,917 - 3060 - [ERROR] -- describe_snapshots() failed
2017-05-05 23:52:33,013 - 3060 - [ERROR] -- describe_volumes() failed
2017-05-05 23:52:33,111 - 3060 - [ERROR] -- describe_tags() failed
2017-05-05 23:52:33,207 - 3060 - [ERROR] -- describe_tags() failed
2017-05-05 23:52:33,305 - 3060 - [ERROR] -- describe_vpcs() failed
2017-05-05 23:52:33,319 - 3060 - [INFO] Checking ECS (DOCKER DOCKER DOCKER DOCKER ...)
2017-05-05 23:52:33,713 - 3060 - [ERROR] -- describe_clusters() failed
2017-05-05 23:52:33,730 - 3060 - [INFO] Checking ElasticBeanstalk
2017-05-05 23:52:34,167 - 3060 - [INFO] -- describe_applications() worked!
2017-05-05 23:52:34,352 - 3060 - [INFO] -- describe_environments() worked!
2017-05-05 23:52:34,365 - 3060 - [INFO] Checking ELB (Elastic Load Balancing)
2017-05-05 23:52:34,749 - 3060 - [ERROR] -- describe_load_balancers() failed
2017-05-05 23:52:34,763 - 3060 - [INFO] Checking ELBv2 (Elastic Load Balancing)
2017-05-05 23:52:35,135 - 3060 - [ERROR] -- describe_load_balancers() failed
2017-05-05 23:52:35,151 - 3060 - [INFO] Checking ElasticTranscoder
2017-05-05 23:52:35,561 - 3060 - [ERROR] -- list_pipelines() failed
2017-05-05 23:52:35,572 - 3060 - [INFO] Checking DynamoDB
2017-05-05 23:52:35,960 - 3060 - [ERROR] -- list_tables() failed
2017-05-05 23:52:36,003 - 3060 - [INFO] Checking IoT
2017-05-05 23:52:36,217 - 3060 - [ERROR] -- list_things() failed
2017-05-05 23:52:36,331 - 3060 - [ERROR] -- describe_endpoint() failed
2017-05-05 23:52:36,342 - 3060 - [INFO] Checking Kinesis
2017-05-05 23:52:36,733 - 3060 - [ERROR] -- list_streams() failed
2017-05-05 23:52:36,806 - 3060 - [INFO] Checking KMS (Key Management Service)
2017-05-05 23:52:37,229 - 3060 - [ERROR] -- list_keys() failed
2017-05-05 23:52:37,255 - 3060 - [INFO] Checking Lambda
2017-05-05 23:52:37,663 - 3060 - [ERROR] -- list_functions() failed
2017-05-05 23:52:37,701 - 3060 - [INFO] Checking OpsWorks
2017-05-05 23:52:38,197 - 3060 - [INFO] -- describe_stacks() worked!
2017-05-05 23:52:38,252 - 3060 - [INFO] Checking RDS (Relational Database Service)
2017-05-05 23:52:38,726 - 3060 - [ERROR] -- describe_db_clusters() failed
2017-05-05 23:52:38,821 - 3060 - [ERROR] -- describe_db_instances() failed
2017-05-05 23:52:38,858 - 3060 - [INFO] Checking Route53 (DNS)
2017-05-05 23:52:39,250 - 3060 - [ERROR] -- list_hosted_zones() failed
2017-05-05 23:52:39,539 - 3060 - [INFO] Checking S3 (Simple Storage Service)
2017-05-05 23:52:39,928 - 3060 - [ERROR] -- list_buckets() failed
2017-05-05 23:52:39,956 - 3060 - [INFO] Checking SES (Simple Email Service)
2017-05-05 23:52:40,344 - 3060 - [ERROR] -- list_identities() failed
2017-05-05 23:52:40,361 - 3060 - [INFO] Checking SNS (Simple Notification Service)
2017-05-05 23:52:40,750 - 3060 - [ERROR] -- list_topics() failed
2017-05-05 23:52:40,767 - 3060 - [INFO] Checking SQS (Simple Queue Service)
2017-05-05 23:52:41,151 - 3060 - [ERROR] -- list_queues() failed
2017-05-05 23:52:41,171 - 3060 - [INFO] Checking Support
2017-05-05 23:52:41,571 - 3060 - [ERROR] -- describe_cases() failed
```
