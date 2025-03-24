import os
import re
import argparse
import asyncio
from typing import List
from aiobotocore.session import get_session
from typing import AsyncGenerator
from pathlib import Path
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from dotenv import load_dotenv, find_dotenv

from s3 import init_s3_client

# Load environment variables from .env file
load_dotenv(find_dotenv())

# AWS Environment Variables
AWS_BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]
DOWNLOAD_DIR = os.environ["DOWNLOAD_DIR"]

# Initialize a single S3 session globally
session = get_session()


async def get_file_size(s3_client: AsyncGenerator, bucket: str, key: str) -> str:
    """
    Get file size from S3 metadata.

    Args:
        s3_client (AsyncGenerator): S3 client
        bucket (str): bucket name
        key (str): object key

    Returns:
        int: file size in bytes
    """
    response = await s3_client.head_object(Bucket=bucket, Key=key)
    return response["ContentLength"]


async def download_file(
    s3_client: AsyncGenerator,
    bucket: str,
    key: str,
    filename: str,
    progress: Progress,
    task_id: int,
) -> None:
    """
    Download a single file with progress tracking.

    Args:
        s3_client (AsyncGenerator): S3 client
        bucket (str): bucket name
        key (str): object key
        filename (str): name of the file to download
        progress (Progress): rich Progress instance
        task_id (int): task ID for the progress bar
    """
    file_path = Path(os.getenv("DOWNLOAD_DIR", ".")) / filename

    # Get file size
    response = await s3_client.head_object(Bucket=bucket, Key=key)
    file_size = response["ContentLength"]

    # Update progress bar total
    progress.update(task_id, total=file_size)

    # Stream download to file
    try:
        # Await get_object to get the actual response object
        response = await s3_client.get_object(Bucket=bucket, Key=key)
        body = response["Body"]

        # Open the file for writing
        with open(file_path, "wb") as f:
            while True:
                # Read 8192 bytes at a time from the body
                chunk = await body.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                progress.update(task_id, advance=len(chunk))
    except Exception as e:
        progress.stop_task(task_id)
        print(f"Error downloading {filename}: {e}")


async def availability(show_list: bool = True) -> list:
    """
    Fetch list of available .zip files from S3.

    Args:
        show_list (bool, optional): Sometimes we need just get a list of available files without print to console.
          Defaults to True.

    Returns:
        list: List of available .zip files
    """
    pattern = r".*\.zip$"
    regex = re.compile(pattern)

    async with init_s3_client() as s3_client:
        if s3_client is None:
            print("Error: AWS credentials not provided.")
            return []
        response = await s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        matching_files = [
            obj["Key"]
            for obj in response.get("Contents", [])
            if regex.match(obj["Key"])
        ]

    if not matching_files:
        print("No files found") if show_list else None
        return []

    if show_list:
        print("\nAvailable files:")
        for i, file in enumerate(matching_files, 1):
            print(f"{i}: {file}")

    return matching_files


async def download_files(files_to_download: List[str]):
    """
    Downloads multiple files concurrently, showing progress.

    Args:
        files_to_download (List[str]): List of files to download
    """
    Path(os.getenv("DOWNLOAD_DIR", ".")).mkdir(parents=True, exist_ok=True)

    async with init_s3_client() as s3_client:
        if s3_client is None:
            print("Error: AWS credentials not provided.")
            return

        with Progress(
            TextColumn("[bold blue]{task.fields[filename]}[/]"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TextColumn("•"),
            TextColumn("{task.fields[file_size]}"),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            tasks = []
            for file in files_to_download:
                filename = os.path.basename(file)
                # Get file size and format it
                file_size = await get_file_size(
                    s3_client, os.getenv("AWS_BUCKET_NAME"), file
                )
                formatted_size = f"{file_size / 1024 / 1024:.1f}MB"
                task_id = progress.add_task(
                    f"Downloading {filename}",
                    filename=filename,
                    file_size=formatted_size,
                    total=1,
                )
                tasks.append(
                    download_file(
                        s3_client,
                        os.getenv("AWS_BUCKET_NAME"),
                        file,
                        filename,
                        progress,
                        task_id,
                    )
                )

            await asyncio.gather(*tasks)


async def handle_download(specific_file: str = None):
    """
    Handle user selection for downloads.

    Args:
        specific_file (str, optional): File to download. Defaults to None.
    """
    show_list = specific_file is None
    available_files = await availability(show_list=show_list)

    if not available_files:
        return

    if specific_file:
        if specific_file in available_files:
            await download_files([specific_file])
        else:
            print(f"Error: File '{specific_file}' not found")
            return

    elif len(available_files) == 1:
        await download_files(available_files)

    else:
        print(
            "\nMultiple files found. Enter comma-separated numbers to download (e.g., 1,3):"
        )
        try:
            selections = input("> ").strip().split(",")
            selected_files = []
            for sel in selections:
                idx = int(sel.strip()) - 1
                if 0 <= idx < len(available_files):
                    selected_files.append(available_files[idx])
                else:
                    print(f"Invalid selection: {sel}. Skipping.")
            if not selected_files:
                return
            await download_files(selected_files)
        except ValueError:
            print("Invalid input. Please enter comma-separated numbers.")
            return


def main() -> None:
    """
    Main function to handle command line.
    """
    parser = argparse.ArgumentParser(description="USDB SDK File Management")
    parser.add_argument(
        "action", choices=["availability", "download"], help="Action to perform"
    )
    parser.add_argument("filename", nargs="?", help="Specific file to download")

    args = parser.parse_args()

    if args.action == "availability":
        asyncio.run(availability())
    elif args.action == "download":
        asyncio.run(handle_download(args.filename))


if __name__ == "__main__":
    main()
