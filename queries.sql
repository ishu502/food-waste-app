-- 1. Providers & receivers count per city
SELECT p.City,
       COUNT(DISTINCT p.Provider_ID) AS Providers,
       COALESCE(rc.Receivers, 0) AS Receivers
FROM providers p
LEFT JOIN (
    SELECT City, COUNT(DISTINCT Receiver_ID) AS Receivers
    FROM receivers
    GROUP BY City
) rc ON rc.City = p.City
GROUP BY p.City;


-- 2. Provider type contributing most by quantity
SELECT fl.Provider_Type, SUM(fl.Quantity) AS Total_Quantity
FROM food_listings fl
GROUP BY fl.Provider_Type
ORDER BY Total_Quantity DESC;


-- 3. Provider contact info for a given city
SELECT p.Name, p.Type AS Provider_Type, p.City, p.Contact
FROM providers p
WHERE p.City = 'Andersonville';



-- 4. Receivers who claimed the most (Completed)
SELECT r.Name, r.Type, COUNT(*) AS Completed_Claims
FROM claims c
JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID, r.Name, r.Type
ORDER BY Completed_Claims DESC;


-- 5. Total quantity available
SELECT COALESCE(SUM(Quantity), 0) AS Total_Quantity
FROM food_listings;

-- 6. City with highest number of listings
SELECT p.City, COUNT(*) AS Listings
FROM food_listings fl
JOIN providers p ON p.Provider_ID = fl.Provider_ID
GROUP BY p.City
ORDER BY Listings DESC;

-- 7. Most common food types
SELECT Food_Type, COUNT(*) AS Frequency
FROM food_listings
GROUP BY Food_Type
ORDER BY Frequency DESC;

-- 8. Claims per food item
SELECT fl.Food_ID, fl.Food_Name, COUNT(c.Claim_ID) AS Claims_Count
FROM food_listings fl
LEFT JOIN claims c ON c.Food_ID = fl.Food_ID
GROUP BY fl.Food_ID, fl.Food_Name
ORDER BY Claims_Count DESC;

-- 9. Provider with most successful (Completed) claims
SELECT p.Name, COUNT(*) AS Completed_Claims
FROM claims c
JOIN food_listings fl ON fl.Food_ID = c.Food_ID
JOIN providers p ON p.Provider_ID = fl.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID
ORDER BY Completed_Claims DESC;

-- 10. Claims status percentages
SELECT Status,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS Percentage
FROM claims
GROUP BY Status;

-- 11. Average quantity claimed per receiver (completed)
SELECT r.Name, ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Claimed
FROM claims c
JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
JOIN food_listings fl ON fl.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID
ORDER BY Avg_Quantity_Claimed DESC;


-- 12. Meal type most claimed
SELECT fl.Meal_Type, COUNT(*) AS Completed_Claims
FROM claims c
JOIN food_listings fl ON fl.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY fl.Meal_Type
ORDER BY Completed_Claims DESC;

-- 13. Total quantity donated by each provider
SELECT p.Name, SUM(fl.Quantity) AS Total_Quantity_Listed
FROM food_listings fl
JOIN providers p ON p.Provider_ID = fl.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Quantity_Listed DESC;

-- 14. Listings expiring within next 3 days
SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, p.City, fl.Expiry_Date
FROM food_listings fl
JOIN providers p ON p.Provider_ID = fl.Provider_ID
WHERE date(fl.Expiry_Date) <= date('now', '+3 day')
ORDER BY fl.Expiry_Date;


-- 15. Top cities by completed claims
SELECT p.City, COUNT(*) AS Completed_Claims
FROM claims c
JOIN food_listings fl ON fl.Food_ID = c.Food_ID
JOIN providers p ON p.Provider_ID = fl.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.City
ORDER BY Completed_Claims DESC;
