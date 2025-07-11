#!/usr/bin/env python3

"""Scrapes setlist.fm for setlists and concert info from a given list of URLs"""

from json import dump, load
from sys import exit as sys_exit

import pandas as pd
from requests import Session
from tqdm import tqdm

from save import csv_save, refactor_dfs, sqlite_save
from scrape import scrape_page

session = Session()

def main():
    print("Loading concerts")
    setlists = load_setlists()
    concerts_df, songs_df = (pd.DataFrame() for _ in range(2))

    print("Scraping setlists")
    for concerts_key, url in tqdm(enumerate(setlists), total=len(setlists)):
        page = session.get(url, timeout=10)
        if page.status_code == 404:
            tqdm.write(f'Skipped "{url}": the page does not exist')
            continue
        if page.status_code != 200:
            tqdm.write(f'Unexpected status code {page.status_code} returned by "{url}"')

        c_df, s_df = scrape_page(concerts_key, page)
        concerts_df = pd.concat([concerts_df, c_df])
        songs_df = pd.concat([songs_df, s_df])

    print("Saving data to CSV")
    csv_save(concerts_df, songs_df)

    print("Saving data to SQLite")
    dfs_dict = refactor_dfs(concerts_df, songs_df)
    sqlite_save(dfs_dict)

    print("Complete")

def load_setlists():
    """Load URLs from setlists.json, exit the script if there's an issue"""
    try:
        with open("setlists.json", "r", encoding="UTF-8") as file:
            setlists = load(file)
            if len(setlists) == 0:
                print("Please put setlist links in setlists.json")
            else:
                return setlists
    except FileNotFoundError:
        with open("setlists.json", "w", encoding="UTF-8") as file:
            dump([], file)
        print("Please put setlist links in setlists.json")
    sys_exit()

if __name__ == "__main__":
    main()
