#!/usr/bin/env python3

'''Functions for scraping setlist pages'''

import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import Session

session = Session()

def scrape_page(concerts_key, url):
    '''Get songs and concert info from page'''
    # get page content
    page = session.get(url, timeout=10)
    if page.status_code != 200:
        print(f"\nUnexpected status code returned: {page.status_code}")
    soup = bs(page.content, "html.parser")
    content = soup.find("div", {"class": "row main"})

    # create the concerts dataframe
    date_section = content.find("div", {"class": "dateBlock"})
    date = date_section.text.strip().replace("\n", ", ") # this outputs "MMM, DD, YYYY"
    headline = content.find("div", {"class": "setlistHeadline"})
    artist, venue = (i.text for i in headline.find_all("a")[0:2])
    concert_df = pd.DataFrame({'date': [date], 'artist': [artist]})
    concert_df[['venue', 'city']] = venue.split(", ", maxsplit=1)

    # create the songs dataframe
    songs_content = content.find("div", {"class": "setlistContent"})
    songs_list = songs_content.find_all("li", {"class": "setlistParts song"})
    concerts_key_col = [concerts_key for _ in range(len(songs_list))]
    songs_df = pd.DataFrame(concerts_key_col, columns=['concerts_key'])
    songs_df[['song', 'artist', 'performed_with', 'info']] = ""

    songs_df = add_song_info(songs_df, songs_list, artist)
    # these columns use += ending with ", " to handle multiple entries, so remove the trailing ", "
    for col in ('performed_with', 'info'):
        songs_df[col] = songs_df[col].str.strip(", ")

    return concert_df, songs_df

def add_song_info(songs_df, songs_list, artist):
    '''Add the additional info from the notes listed for each song'''
    for song_index, song in enumerate(songs_list):
        songs_df.loc[song_index, 'song'] = song.find("div", {"class": "songPart"}).text.strip()
        songs_df.loc[song_index, 'artist'] = artist # set default value for artist column
        song_info = song.find("div", {"class": "infoPart"}).text
        song_info = song_info.replace("\n", "").replace("\xa0", " ").strip()

        if song_info:
            # split out the individual info notes and whether they contain a link
            # [1:] because [0] is empty since song_info starts with "("
            text_info_list = ["(" + s for s in song_info.split("(")[1:]]
            # look for a link in each piece of info
            html_info_list = str(song.find("div", {"class": "infoPart"})).split("(")[1:]
            link_in_info = ["<a" in i for i in html_info_list]

            # using .split("(") to break up the notes fails if there are nested parentheses
            # i.e. song #19 on /setlist/billy-joel/2016/safeco-field-seattle-wa-5bfeb3ec.html
            text_info_list, link_in_info = fix_nested_parens(text_info_list, link_in_info)

            for info_index, info in enumerate(text_info_list):
                # these keywords should only be counted if there's a link to an artist
                if link_in_info[info_index]:
                    # note if song was originally recorded by a different artist
                    if "cover)" in info:
                        songs_df.loc[song_index, 'artist'] = info.replace("cover)", "").strip("( ")
                    elif "song)" in info:
                        songs_df.loc[song_index, 'artist'] = info.replace("song)", "").strip("( ")
                    # note if song was performed with additional guest artist(s)
                    elif "(with " in info:
                        additional_artist = info.replace("(with ", "").strip(" )")
                        songs_df.loc[song_index, 'performed_with'] += f"{additional_artist}, "
                # if none of the above just put the note in the info column
                    else:
                        songs_df.loc[song_index, 'info'] += f"{info.strip("()")}, "
                else:
                    songs_df.loc[song_index, 'info'] += f"{info.strip("()")}, "
    return songs_df

def fix_nested_parens(text_info_list, link_in_info):
    '''Adjust info lists to handle nested parentheses'''
    merge_indicies = []
    # find the indicies which need to be merged with the subsequent index
    for i, text in enumerate(text_info_list):
        if text[-1] != ")":
            merge_indicies.append(i)

    # merge the indicies as necessary
    for index in merge_indicies:
        text_info_list[index] = "".join(text_info_list[index:index+2])
        del text_info_list[index+1]
        link_in_info[index] = any(link_in_info[index:index+2])
        del link_in_info[index+1]

    return text_info_list, link_in_info
