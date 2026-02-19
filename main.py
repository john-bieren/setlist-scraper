#!/usr/bin/env python3

"""Scrapes setlist.fm for setlists and concert info from a list of URLs."""

import json
import sys

import pandas as pd
import requests
from tqdm import tqdm

from scrape import scrape_page


def main() -> None:
    """Scrapes setlist.fm for setlists and concert info from a list of URLs."""
    print("Loading concerts")
    setlists = load_setlists()
    concerts_df, songs_df = [pd.DataFrame() for _ in range(2)]

    print("Scraping setlists")
    session = requests.Session()
    for concerts_key, url in tqdm(enumerate(setlists), total=len(setlists)):
        page = session.get(url, timeout=10)
        if page.status_code == 404:
            tqdm.write(f'Skipped "{url}": the page does not exist')
            continue
        if page.status_code != 200:
            tqdm.write(f'Unexpected status code {page.status_code} returned by "{url}"')

        c_df, s_df = scrape_page(page, concerts_key)
        concerts_df = pd.concat([concerts_df, c_df])
        songs_df = pd.concat([songs_df, s_df])

    print("Saving data to CSV")
    csv_save(concerts_df, songs_df)

    print("Complete")


def load_setlists() -> list[str]:
    """Loads URLs from setlists.json, exits the script if there's an issue."""
    try:
        with open("setlists.json", "r", encoding="UTF-8") as file:
            setlists = json.load(file)
            if len(setlists) > 0:
                return setlists
    except FileNotFoundError:
        with open("setlists.json", "w", encoding="UTF-8") as file:
            json.dump([], file)
    print("Please put setlist links in setlists.json")
    sys.exit()


def csv_save(concerts_df: pd.DataFrame, songs_df: pd.DataFrame) -> None:
    """Saves data to CSV files."""
    # reset index so that the two tables can be joined on songs_df["concerts_key"]
    concerts_df.reset_index(drop=True, inplace=True)
    concerts_df.index.name = "key"
    while True:
        try:
            concerts_df.to_csv("concerts.csv", index=True)
            songs_df.to_csv("songs.csv", index=False)
            break
        except PermissionError:
            input("Close open CSV save file(s) to allow save, then press enter")


if __name__ == "__main__":
    main()
