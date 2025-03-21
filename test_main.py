import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch
import pytest
from main import availability, download_files, handle_download, main
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


@pytest.mark.asyncio
async def test_availability():
    result = await availability()
    assert isinstance(result, list)
    assert len(result) > 0
    first_result = result[0]
    assert first_result.endswith(".zip")


@pytest.mark.asyncio
async def test_availability_no_credentials():
    with patch.dict(
        "os.environ", {"AWS" "_ACCESS_KEY_ID": "", "AWS_SECRET_ACCESS_KEY": ""}
    ):
        result = await availability()
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_download_files():
    with TemporaryDirectory() as tmp_dir:
        with patch.dict("os.environ", {"DOWNLOAD_DIR": tmp_dir}):
            first_available_file = (await availability())[0]
            await download_files([first_available_file])
            downloaded_path = os.path.join(tmp_dir, Path(first_available_file).name)
            # assert os.path.exists(downloaded_path)
            assert os.path.getsize(downloaded_path) > 0
            assert os.path.isfile(downloaded_path)
            os.remove(downloaded_path)

@pytest.mark.asyncio
async def test_handle_download():
    with TemporaryDirectory() as tmp_dir:
        with patch.dict("os.environ", {"DOWNLOAD_DIR": tmp_dir}):
            first_available_file = (await availability())[0]
            await handle_download(first_available_file)
            downloaded_path = os.path.join(tmp_dir, Path(first_available_file).name)
            # assert os.path.exists(downloaded_path)
            assert os.path.getsize(downloaded_path) > 0
            assert os.path.isfile(downloaded_path)
            os.remove(downloaded_path)       


def test_main_availability(capsys):
    with patch("sys.argv", ["script", "availability"]):
        main()

    captured = capsys.readouterr()
    assert "Available files:" in captured.out


@pytest.mark.asyncio
async def test_main_invalid_action():
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["script", "invalid"]):
            main()

    assert exc_info.value.code != 0
