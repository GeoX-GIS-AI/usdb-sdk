from main import availability
from s3 import get_bucket_region, init_s3_client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def test_availability():
    result = availability()
    assert isinstance(result, list)
    assert len(result) > 0
    first_result = result[0]
    assert first_result.endswith(".zip")
