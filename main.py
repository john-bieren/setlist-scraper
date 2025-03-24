#!/usr/bin/env python3

'''Scrapes setlist.fm for setlists and concert info from a given list of URLs'''

from json import dump, load
from sys import exit as sys_exit

import pandas as pd
from tqdm import tqdm

from save import csv_save, refactor_dfs, sqlite_save
from scrape import scrape_page


def main():
    print("Loading concerts")
    link_list = load_link_list()
    concerts_df, songs_df = (pd.DataFrame() for _ in range(2))

    print("Scraping setlists")
    for concerts_key, url in tqdm(enumerate(link_list), total=len(link_list)):
        c_df, s_df = scrape_page(concerts_key, url)
        concerts_df = pd.concat([concerts_df, c_df])
        songs_df = pd.concat([songs_df, s_df])

    print("Saving data to .csv")
    csv_save(concerts_df, songs_df)

    print("Saving data to SQLite")
    dfs_dict = refactor_dfs(concerts_df, songs_df)
    sqlite_save(dfs_dict)

    print("Complete")

def load_link_list():
    '''Load URLs from link_list.json, exit the script if there's an issue'''
    try:
        with open("link_list.json", "r", encoding="UTF-8") as file:
            link_list = load(file)
            if len(link_list) == 0:
                print("Please put setlist links in link_list.json")
            else:
                return link_list
    except FileNotFoundError:
        with open("link_list.json", "w", encoding="UTF-8") as file:
            dump([], file)
        print("Please put setlist links in link_list.json")
    sys_exit()

if __name__ == "__main__":
    main()
