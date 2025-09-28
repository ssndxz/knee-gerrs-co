-- Query for Topic 1: Top 5 highest rated events (analyzes event popularity based on user ratings)
SELECT e.Name, AVG(h.Rate) as AvgRate 
FROM events e 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY e.Id, e.Name 
ORDER BY AvgRate DESC LIMIT 5;

-- Query for Topic 2: Number of events per location (identifies geographic hotspots for events)
SELECT l.Name, COUNT(e.Id) as EventCount 
FROM locations l 
JOIN events e ON l.Id = e.LocationId 
GROUP BY l.Name;

-- Query for Topic 3: Number of favorite genres per user (examines user preferences for genres)
SELECT u.UserName, COUNT(fg.GenreId) as FavGenres 
FROM users u 
JOIN favoritegenres fg ON u.Id = fg.UserId 
GROUP BY u.UserName;

-- Query for Topic 4: Artists with the most events (highlights popular artists by performance count)
SELECT a.Name, COUNT(ea.EventId) as EventCount 
FROM artists a 
JOIN eventartists ea ON a.Id = ea.ArtistId 
GROUP BY a.Name 
ORDER BY EventCount DESC;

-- Query for Topic 5: Average rate per genre (assesses genre popularity based on event ratings)
SELECT g.Name, AVG(h.Rate) as AvgRate 
FROM genres g 
JOIN events e ON g.Id = e.GenreId 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY g.Name;

-- Query for Topic 6: Number of interested users per event (measures user interest in upcoming events)
SELECT e.Name, COUNT(h.UserId) as InterestedCount 
FROM events e 
JOIN eventhistory h ON e.Id = h.EventId 
WHERE h.IsInterested = 1 
GROUP BY e.Name;

-- Query for Topic 7: Users with most attended events (tracks user engagement through attendance)
SELECT u.UserName, COUNT(h.EventId) as AttendedCount 
FROM users u 
JOIN eventhistory h ON u.Id = h.UserId 
WHERE h.HasAttended = 1 
GROUP BY u.UserName 
ORDER BY AttendedCount DESC;

-- Query for Topic 8: Number of events per country (analyzes international distribution of events)
SELECT c.Name, COUNT(e.Id) as EventCount 
FROM countries c 
JOIN locations l ON c.Id = l.CountryId 
JOIN events e ON l.Id = e.LocationId 
GROUP BY c.Name;

-- Query for Topic 9: Max rate per artist (identifies highest-rated performances by artists)
SELECT a.Name, MAX(h.Rate) as MaxRate 
FROM artists a 
JOIN eventartists ea ON a.Id = ea.ArtistId 
JOIN events e ON ea.EventId = e.Id 
JOIN eventhistory h ON e.Id = h.EventId 
GROUP BY a.Name;

-- Query for Topic 10: Number of users per location (examines user base by geographic area)
SELECT l.Name, COUNT(u.Id) as UserCount 
FROM locations l 
JOIN users u ON l.Id = u.LocationId 
GROUP BY l.Name;