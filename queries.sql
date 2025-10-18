-- name: top_rated_events
-- Top 5 highest rated events
SELECT e.Name, AVG(h.Rate) as AvgRate 
FROM events e 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY e.Id, e.Name 
ORDER BY AvgRate DESC LIMIT 5;

-- name: events_per_location
-- Number of events per location
SELECT l.Name, COUNT(e.Id) as EventCount 
FROM locations l 
JOIN events e ON l.Id = e.LocationId 
GROUP BY l.Name;

-- name: favorite_genres_per_user
-- Number of favorite genres per user
SELECT u.UserName, COUNT(fg.GenreId) as FavGenres 
FROM users u 
JOIN favoritegenres fg ON u.Id = fg.UserId 
GROUP BY u.UserName;

-- name: artists_most_events
-- Artists with the most events
SELECT a.Name, COUNT(ea.EventId) as EventCount 
FROM artists a 
JOIN eventartists ea ON a.Id = ea.ArtistId 
GROUP BY a.Name 
ORDER BY EventCount DESC;

-- name: avg_rate_per_genre
-- Average rating per genre
SELECT g.Name, AVG(h.Rate) as AvgRate 
FROM genres g 
JOIN events e ON g.Id = e.GenreId 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY g.Name;

-- name: interested_users_per_event
-- Number of interested users per event (date for time slider)
SELECT e.Name, COUNT(h.UserId) as InterestedCount, e.Date as EventDate
FROM events e 
JOIN eventhistory h ON e.Id = h.EventId 
WHERE h.IsInterested = 1 
GROUP BY e.Name, e.Date;

-- name: users_most_attended
-- Users with most attended events
SELECT u.UserName, COUNT(h.EventId) as AttendedCount 
FROM users u 
JOIN eventhistory h ON u.Id = h.UserId 
WHERE h.HasAttended = 1 
GROUP BY u.UserName 
ORDER BY AttendedCount DESC;

-- name: events_per_country
-- Number of events per country
SELECT c.Name, COUNT(e.Id) as EventCount 
FROM countries c 
JOIN locations l ON c.Id = l.CountryId 
JOIN events e ON l.Id = e.LocationId 
GROUP BY c.Name;

-- name: max_rate_per_artist
-- Max rating per artist
SELECT a.Name, MAX(h.Rate) as MaxRate 
FROM artists a 
JOIN eventartists ea ON a.Id = ea.ArtistId 
JOIN events e ON ea.EventId = e.Id 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY a.Name;

-- name: events_by_day
-- Event count by day
SELECT EXTRACT(YEAR FROM e.Date) as Year, EXTRACT(MONTH FROM e.Date) as Month, EXTRACT(DAY FROM e.Date) as Day, COUNT(e.Id) as EventCount
FROM genres g 
JOIN events e ON g.Id = e.GenreId 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY EXTRACT(YEAR FROM e.Date), EXTRACT(MONTH FROM e.Date), EXTRACT(DAY FROM e.Date)
ORDER BY Year, Month, Day;

-- name: rating_distribution
-- Aggregated rating distribution with join (events and eventhistory)
SELECT h.Rate, COUNT(*) as RatingCount
FROM events e
JOIN eventhistory h ON e.Id = h.EventId
WHERE h.Rate IS NOT NULL
GROUP BY h.Rate
ORDER BY h.Rate;

-- name: rating_vs_user
-- Event ratings vs user ID
SELECT UserId, Rate 
FROM eventhistory 
ORDER BY UserId, Rate;

-- name: events_by_date
-- Daily event counts for time slider
SELECT e.Date, COUNT(*) as EventCount, e.Name, g.Name as GenreName
FROM events e 
JOIN genres g ON e.GenreId = g.Id 
GROUP BY e.Date, e.Name, g.Name 
ORDER BY e.Date;
