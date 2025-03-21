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