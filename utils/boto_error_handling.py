from botocore.exceptions import ClientError

UNAUTH_ERRORS = ('UnauthorizedOperation',
                 'AccessDeniedException')


def yield_handling_errors(func, *args, **kwargs):    
    try:
        for result in func(*args, **kwargs):
            yield result
    except ClientError as e:
        if e.response['Error']['Code'] in UNAUTH_ERRORS:
            print("%s" % e)
        else:
            print("Unexpected error: %s" % e)
