import os
import boto3

def init_s3_client():
    """
    This function initializes an s3 client.
    Initialization should be at the top of the module and NOT in the function that uses it.
    This need for avoid multiple initializations of the client.

    Returns:
        Any: s3 client from boto3 or None if credentials are not provided.
    """
    endpoint_url = os.getenv(
        "AWS_ENDPOINT_URL", "https://s3.eu-central-2.wasabisys.com"
    )
    region = os.getenv("AWS_DEFAULT_REGION", "eu-central-2")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    try:
        assert (
            aws_access_key_id is not None
            and aws_secret_access_key is not None
            and region is not None
        )
    except AssertionError:
        return None

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )
    client = session.client(
        "s3",
        endpoint_url=endpoint_url,
        config=boto3.session.Config(
            max_pool_connections=50,
            connect_timeout=120,
            retries={"max_attempts": 10, "mode": "standard"},
        ),
    )
    return client


def get_bucket_region(bucket_name):
    """Get the region of an S3 bucket"""
    s3_client = init_s3_client()
    try:
        location = s3_client.get_bucket_location(Bucket=bucket_name)
        region = location['LocationConstraint']
        # AWS returns None for us-east-1 instead of a region string
        return 'us-east-1' if region is None else region
    except Exception as e:
        print(f"Error getting bucket region: {e}")
        return None