import os
from typing import AsyncGenerator
import aiobotocore
from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

@asynccontextmanager
async def init_s3_client() -> AsyncGenerator:
    """
    Initializes an async S3 client using aiobotocore.

    Returns:
        AsyncGenerator: async S3 client
    Yields:
        Iterator[AsyncGenerator]: async S3 client
    """
    endpoint_url = os.getenv(
        "AWS_ENDPOINT_URL", "https://s3.eu-central-2.wasabisys.com"
    )
    region = os.getenv("AWS_DEFAULT_REGION", "eu-central-2")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key_id or not aws_secret_access_key:
        yield None
        return

    session = get_session()
    async with session.create_client(
        "s3",
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=aiobotocore.config.AioConfig(
            max_pool_connections=50,
            connect_timeout=120,
            retries={"max_attempts": 10, "mode": "standard"},
        ),
    ) as s3_client:
        yield s3_client  # Async S3 client
