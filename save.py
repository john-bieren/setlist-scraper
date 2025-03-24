#!/usr/bin/env python3

'''Functions for saving data to SQLite'''

from sqlite3 import OperationalError, connect
from warnings import simplefilter

import pandas as pd


def csv_save(concerts_df, songs_df):
    '''Save data to .csv files'''
    # reset index so that the two tables can be joined on songs_df['concerts_key']
    concerts_df.reset_index(drop=True, inplace=True)
    concerts_df.index.name = 'key'
    while True:
        try:
            concerts_df.to_csv("concerts.csv", index=True)
            songs_df.to_csv("songs.csv", index=False)
            break
        except PermissionError:
            input("One or both of the .csv save files are open. Close them to allow save, then press enter")

def refactor_dfs(concerts_df, songs_df):
    '''Create new tables for redundant data and insert foreign keys where necessary'''
    # create foreign keys for certain columns
    dates_dict = dict_make(concerts_df, "date")
    artists_dict = dict_make(concerts_df, "artist")
    venues_dict = dict_make(concerts_df, "venue")
    cities_dict = dict_make(concerts_df, "city")
    song_titles_dict = dict_make(songs_df, "song")

    # add arists that appear in the db but aren't one of the headline performers
    foreign_key = len(artists_dict)
    for col in ('artist', 'performed_with'):
        for artist in songs_df[col].unique():
            if artist not in artists_dict:
                artists_dict[artist] = foreign_key
                foreign_key += 1

    # df.replace() throws a future warning about downcasting, infer_objects fixes the problem
    simplefilter(action="ignore", category=FutureWarning)

    # replace values with their foreign keys
    for col, dictionary in (
            ('date', dates_dict),
            ('artist', artists_dict),
            ('venue', venues_dict),
            ('city', cities_dict),
            ):
        concerts_df[col] = concerts_df[col].replace(dictionary).infer_objects(copy=False)
    for col in ('artist', 'performed_with'):
        songs_df[col] = songs_df[col].replace(artists_dict).infer_objects(copy=False)
    songs_df['song'] = songs_df['song'].replace(song_titles_dict).infer_objects(copy=False)

    # rename foreign key columns to reflect the table that they refer to
    concerts_df.rename(
        columns = {
            'date': 'dates_key',
            'artist': 'artists_key',
            'venue': 'venues_key',
            'city': 'cities_key'
        }, inplace=True
    )
    songs_df.rename(
        columns = {
            'song': 'song_titles_key',
            'artist': 'artists_key',
            'performed_with': 'performed_with_artists_key'
        }, inplace=True
    )

    # create the tables which the foreign keys refer to
    dates_df = df_make(dates_dict, 'Date')
    artists_df = df_make(artists_dict, 'Artist')
    venues_df = df_make(venues_dict, 'Venue')
    cities_df = df_make(cities_dict, 'City')
    song_titles_df = df_make(song_titles_dict, 'Song')

    # return a dictionary of table names and their contents
    return {
        "concerts": concerts_df,
        "songs": songs_df,
        "dates": dates_df,
        "artists": artists_df,
        "venues": venues_df,
        "cities": cities_df,
        "song_titles": song_titles_df
    }

def dict_make(df, col, key_start=0):
    '''Create a dictionary of foreign keys for the values of a dataframe column'''
    dictionary = {}
    key = key_start
    for item in df[col].unique():
        dictionary[item] = key
        key += 1
    return dictionary

def df_make(dictionary, column_name):
    '''Create a dataframe from a foreign key dictionary to use as a database table'''
    # swap the keys and values so that the leftmost column is the keys
    swapped_dict = {y: x for x, y in dictionary.items()}
    return pd.DataFrame.from_dict(swapped_dict, orient='index', columns=[column_name])

def sqlite_save(dfs_dict):
    '''Save data to setlist_scraper.db'''
    # table names and the name of the column for each foreign key table
    TABLES = (
        ("concerts", ""),
        ("songs", ""),
        ("dates", "Date"),
        ("artists", "Artist"),
        ("venues", "Venue"),
        ("cities", "City"),
        ("song_titles", "Song")
    )

    # connect to db
    db_cursor = connect('setlist_scraper.db')
    cursor = db_cursor.cursor()

    # interact with database; loop breaks when work is done, continues on errors
    while True:
        try:
            # delete the existing tables so they can be replaced entirely
            for table_name, _ in TABLES:
                cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

            # create tables
            cursor.execute('''
            CREATE TABLE concerts (
                key INTEGER PRIMARY KEY,
                dates_key INTEGER NOT NULL,
                artists_key INTEGER NOT NULL,
                venues_key INTEGER NOT NULL,
                cities_key INTEGER NOT NULL,
                FOREIGN KEY (dates_key) REFERENCES dates(key) ON DELETE CASCADE,
                FOREIGN KEY (artists_key) REFERENCES artists(key) ON DELETE CASCADE,
                FOREIGN KEY (venues_key) REFERENCES venues(key) ON DELETE CASCADE,
                FOREIGN KEY (cities_key) REFERENCES cities(key) ON DELETE CASCADE
            )'''
            )
            cursor.execute('''
            CREATE TABLE songs (
                key INTEGER PRIMARY KEY,
                concerts_key INTEGER,
                song_titles_key INTEGER NOT NULL,
                artists_key INTEGER NOT NULL,
                performed_with_artists_key INTEGER,
                info TEXT,
                FOREIGN KEY (concerts_key) REFERENCES concerts(key) ON DELETE CASCADE,
                FOREIGN KEY (song_titles_key) REFERENCES song_titles(key) ON DELETE CASCADE,
                FOREIGN KEY (artists_key) REFERENCES artists(key) ON DELETE CASCADE,
                FOREIGN KEY (performed_with_artists_key) REFERENCES artists(key) ON DELETE CASCADE
            )'''
            )

            # create foreign key tables
            for table_name, col_name in TABLES[2:]:
                cursor.execute(f"CREATE TABLE {table_name} (key INTEGER, {col_name} TEXT)")

            # save data to tables
            for table_name, df in dfs_dict.items():
                df.reset_index(drop=True, inplace=True)
                df.index.name = 'key'
                df.to_sql(name=table_name, con=db_cursor, if_exists="append")

            db_cursor.commit()
            db_cursor.close()
            break

        except OperationalError:
            input("setlist_scraper.db is locked. Please close it to allow save, then press enter")
