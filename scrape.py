#!/usr/bin/env python3

"""Functions for scraping setlist pages"""

import pandas as pd
from bs4 import BeautifulSoup as bs


def scrape_page(concerts_key, page):
    """Get songs and concert info from page"""
    soup = bs(page.content, "html.parser")

    # create the concerts dataframe
    date_section = soup.find("div", {"class": "dateBlock"})
    date = date_section.text.strip().replace("\n", ", ") # this outputs "MMM, DD, YYYY"
    date = date.replace(",", "", 1) # this outputs "MMM DD, YYYY"
    headline = soup.find("div", {"class": "setlistHeadline"})
    artist, venue = (i.text for i in headline.find_all("a")[0:2])
    concert_df = pd.DataFrame({"date": [date], "artist": [artist]})
    concert_df[["venue", "city"]] = venue.split(", ", maxsplit=1)

    # find concert note, if applicable
    concert_note = soup.find("p", {"class": "info fontSmall text-center"})
    if concert_note is not None:
        concert_df["note"] = concert_note.text.replace("Note:", "").strip()
    else:
        concert_df["note"] = ""

    # create the songs dataframe
    setlist_content = soup.find("div", {"class": "setlistContent"})
    songs_list = setlist_content.find_all("li", {"class": "setlistParts song"})
    concerts_key_col = [concerts_key for _ in range(len(songs_list))]
    songs_df = pd.DataFrame(concerts_key_col, columns=["concerts_key"])
    songs_df[["song", "artist", "performed_with", "info"]] = ""

    songs_df = add_song_info(songs_df, songs_list, artist)
    return concert_df, songs_df

def add_song_info(songs_df, songs_list, artist):
    """Add the additional info from the notes listed for each song"""
    for song_index, song in enumerate(songs_list):
        songs_df.loc[song_index, "song"] = song.find("div", {"class": "songPart"}).text.strip()
        songs_df.loc[song_index, "artist"] = artist # set default value for artist column
        song_info = song.find("div", {"class": "infoPart"}).text.strip().replace("\xa0", " ")

        if song_info:
            # split out the individual info notes
            text_info_list = song_info.split("\n(")
            # look for links to artists in each info note
            html_info_list = song.find("div", {"class": "infoPart"}).decode_contents().split("\n(")
            link_in_info = ["<a href=" in i for i in html_info_list[1:]]

            for info_index, info in enumerate(text_info_list):
                info = info.strip("()\n")
                # use these keywords if there's a link to an artist, otherwise add to "info"
                if link_in_info[info_index]:
                    # note if song was originally recorded by a different artist
                    if info.endswith(" cover"):
                        songs_df.loc[song_index, "artist"] = info[:-6]
                    elif info.endswith(" song"):
                        songs_df.loc[song_index, "artist"] = info[:-5]
                    # note if song was performed with additional guest artist(s)
                    elif info.startswith("with "):
                        additional_artist = info[5:].strip(")\n")
                        songs_df.loc[song_index, "performed_with"] += f"{additional_artist}, "
                    # if none of the above just put the note in the info column
                    else:
                        songs_df.loc[song_index, "info"] += f"{info}, "
                else:
                    songs_df.loc[song_index, "info"] += f"{info}, "

    # these columns use += ending with ", " to handle multiple entries, so remove the trailing ", "
    songs_df["performed_with"] = songs_df["performed_with"].str.strip(", ")
    songs_df["info"] = songs_df["info"].str.strip(", ")
    return songs_df
