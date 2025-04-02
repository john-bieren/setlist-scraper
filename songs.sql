WITH joined_concerts as (
	SELECT concerts.key, dates.Date, artists.Artist, venues.Venue, cities.City FROM concerts
	JOIN cities on concerts.cities_key = cities.key
	JOIN dates on concerts.dates_key = dates.key
	JOIN artists on concerts.artists_key = artists.key
	JOIN venues on concerts.venues_key = venues.key
)
SELECT
	joined_concerts.Date, joined_concerts.Artist as Performer, joined_concerts.Venue, joined_concerts.City,
	song_titles.Song, artists.Artist, performed_with.Artist as Performed_with, info FROM songs
JOIN joined_concerts ON songs.concerts_key = joined_concerts.key
JOIN song_titles ON songs.song_titles_key = song_titles.key
JOIN artists ON songs.artists_key = artists.key
JOIN artists performed_with ON songs.performed_with_artists_key = performed_with.key