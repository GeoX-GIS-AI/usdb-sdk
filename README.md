## USDB SDK File Management

### Installation
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/requirements.txt
```

### Usage
```
usage: main.py [-h] {availability,download} [filename]

USDB SDK File Management

positional arguments:
  {availability,download}
                        Action to perform
  filename              Specific file to download

options:
  -h, --help            show this help message and exit
```

#### Check files availability
```
python main.py availability

Available files:
1: Release_1/New_Hampshire_Footprints_1.1.zip
2: Release_1/New_Hampshire_Footprints_1.zip
3: Release_1/New_Jersey_Footprints_1.zip
4: Release_1/Pennsylvania_Footprints_1.zip
5: Release_2/New_Hampshire_Footprints_2.zip
6: Release_3/NH_2025-03_gpkg.zip
```

#### Download files

In download mode, the user can select multiple files to download by entering the comma-separated numbers of the files. The download progress is displayed in the terminal.
Also you can specify the file name to download by providing the file name as the second argument.
```
# this command will download the file New_Hampshire_Footprints_1.1.zip
python main.py download Release_1/New_Hampshire_Footprints_1.1.zip
```

If bucket contains only one file, the file will be downloaded automatically, without asking for the user input.

If bucket contains multiple files, the user will be prompted to select the files to download.


```
python main.py download

Available files:
1: Release_1/New_Hampshire_Footprints_1.1.zip
2: Release_1/New_Hampshire_Footprints_1.zip
3: Release_1/New_Jersey_Footprints_1.zip
4: Release_1/Pennsylvania_Footprints_1.zip
5: Release_2/New_Hampshire_Footprints_2.zip
6: Release_3/NH_2025-03_gpkg.zip

Multiple files found. Enter comma-separated numbers to download (e.g., 1,3):
> 1,4,5
New_Hampshire_Footprints_1.1.zip ━━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━  41% • 73.1MB  • 0:00:12
Pennsylvania_Footprints_1.zip    ━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   9% • 835.7MB • 0:02:06
New_Hampshire_Footprints_2.zip   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸━━━━━━━━━━━  72% • 90.3MB  • 0:00:05
```


### Testing
```
$ pip install -r requirements/requirements_dev.txt
$ pytest test_main.py
```

### Environment Variables
```
AWS_BUCKET_NAME=bucket_name
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***
AWS_ENDPOINT_URL=https://s3.us-east-1.wasabisys.com
AWS_DEFAULT_REGION=us-east-1
DOWNLOAD_DIR=output  # path where the downloaded files will be stored
```