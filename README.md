# Setlist Scraper

A script for collecting concert setlists from [setlist.fm](https://www.setlist.fm/). Given a list of setlist links, the scraper returns data on the concerts listed and their setlists.

## Install

Clone the repository:
```
git clone https://github.com/john-bieren/setlist-scraper.git
```
Install dependencies:
```
python -m pip install -r requirements.txt
```
**Note**: The tags in this repository do not correspond to releases, they simply indicate breaking changes.

## Usage

Create a file in the project directory named `setlists.json` or run `main.py` to have the file created for you. Enter the links for the setlists that you wish to scrape into `setlists.json` as a list, as demonstrated below.

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

Using analysis software, you can join `concerts.csv` to `songs.csv` using their `key` and `concerts_key` columns, respectively.
