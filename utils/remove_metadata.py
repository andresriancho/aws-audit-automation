def remove_metadata(boto_response):
    boto_response.pop('ResponseMetadata', None)
    return boto_response
