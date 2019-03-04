#!/bin/bash

aws --region=us-east-1 ec2 describe-network-interfaces --filters Name=group-id,Values=$1
