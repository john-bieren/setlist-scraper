# Setlist Scraper

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A script for collecting concert setlists from [setlist.fm](https://www.setlist.fm/). Given a list of
setlist links, the scraper returns data on the concerts listed and their setlists.

## Install

Clone the repository and install dependencies:

```
pip install -r requirements.txt
```

Or install development dependencies:

```
pip install -r requirements-dev.txt
```

> [!NOTE]
> The tags in this repository do not correspond to releases, instead they indicate the conclusion of
a series of breaking changes. Since v3, commits with breaking changes are marked in the commit
message body.

## Usage

Create a file in the project directory named `setlists.json` or run `main.py` to have the file
created for you. Enter the links for the setlists that you wish to scrape into `setlists.json` as a
list, as demonstrated below.

```JSON
[
    "https://www.setlist.fm/setlist/paul-mccartney/2013/safeco-field-seattle-wa-33c6acbd.html",
    "https://www.setlist.fm/setlist/the-doobie-brothers/2018/keyarena-seattle-wa-73ed5635.html",
    "https://www.setlist.fm/setlist/steely-dan/2018/keyarena-seattle-wa-73ed5629.html",
    "https://www.setlist.fm/setlist/styx/2023/iccu-arena-moscow-id-2ba244de.html"
]
```

Run `main.py`. Upon completion, the data will be saved in two .csv files:

* `concerts.csv`, which contains information about the concerts.
* `songs.csv`, which contains information about the songs performed at each concert.

You can join `concerts.csv` to `songs.csv` using their `key` and `concerts_key` columns,
respectively:

```python
import pandas as pd
songs = pd.read_csv("songs.csv")
concerts = pd.read_csv("concerts.csv")
merged_songs = pd.merge(songs, concerts, left_on="concerts_key", right_on="key")
```
