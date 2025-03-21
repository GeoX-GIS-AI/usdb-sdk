import os
import re
import argparse
import threading
from pathlib import Path
from tqdm import tqdm
from s3 import init_s3_client

s3_client = init_s3_client()


def get_file_size(bucket, key):
    response = s3_client.head_object(Bucket=bucket, Key=key)
    return response["ContentLength"]


def download_with_progress(bucket, key, filename):
    file_size = get_file_size(bucket, key)

    # Create a progress bar
    progress = tqdm(
        total=file_size, unit="B", unit_scale=True, desc=f"Downloading {filename}"
    )

    def callback(chunk):
        progress.update(chunk)

    s3_client.download_file(
        Bucket=bucket, Key=key, Filename=filename, Callback=callback
    )
    progress.close()


def availability(show_list=True) -> list:
    pattern = r".*\.zip$"
    regex = re.compile(pattern)

    response = s3_client.list_objects_v2(Bucket=os.environ["AWS_BUCKET_NAME"])
    matching_files = [
        obj["Key"] for obj in response.get("Contents", []) if regex.match(obj["Key"])
    ]

    if not matching_files:
        print("No files found") if show_list else None
        return []
    if show_list:
        print("\nAvailable files:")
        for i, file in enumerate(matching_files, 1):
            print(f"{i}: {file}")

    return matching_files


def download_files(files_to_download):
    Path(os.environ["DOWNLOAD_DIR"]).mkdir(parents=True, exist_ok=True)
    threads = []
    for file in files_to_download:
        thread = threading.Thread(
            target=download_with_progress,
            args=(os.environ["AWS_BUCKET_NAME"], file, os.path.basename(file)),
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def handle_download(specific_file=None):
    available_files = availability()

    if not available_files:
        return

    if specific_file:
        if specific_file in available_files:
            download_files([specific_file])
        else:
            print(f"Error: File '{specific_file}' not found")
            return

    elif len(available_files) == 1:
        download_files(available_files)

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
                    print(f"Invalid selection: {sel}")
                    return
            download_files(selected_files)
        except ValueError:
            print("Invalid input. Please enter comma-separated numbers.")
            return


def main():
    parser = argparse.ArgumentParser(description="USDB SDK File Management")
    parser.add_argument(
        "action", choices=["availability", "download"], help="Action to perform"
    )
    parser.add_argument("filename", nargs="?", help="Specific file to download")

    args = parser.parse_args()

    if args.action == "availability":
        availability()
    elif args.action == "download":
        handle_download(args.filename)


if __name__ == "__main__":
    main()
