def get_principal_name(sts_caller_identity_output):
    # arn:aws:iam::231051035917:user/s3user
    arn = sts_caller_identity_output['sts']['Arn']
    type_name = arn.split(':')[5]
    return type_name.split('/')
