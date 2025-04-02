SELECT dates.Date, artists.Artist, venues.Venue, cities.City FROM concerts
JOIN cities on concerts.cities_key = cities.key
JOIN dates on concerts.dates_key = dates.key
JOIN artists on concerts.artists_key = artists.key
JOIN venues on concerts.venues_key = venues.key