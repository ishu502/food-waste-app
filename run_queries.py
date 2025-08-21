import sqlite3
from tabulate import tabulate

# Connect to database
conn = sqlite3.connect("food_waste.db")
cursor = conn.cursor()

# Queries with titles
queries = [
    ("Providers & receivers count per city", """
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
    """),

    ("Provider type contributing most by quantity", """
        SELECT fl.Provider_Type, SUM(fl.Quantity) AS Total_Quantity
        FROM food_listings fl
        GROUP BY fl.Provider_Type
        ORDER BY Total_Quantity DESC;
    """),

    ("Provider contact info for a city", """
    SELECT p.Name, fl.Provider_Type, p.City, p.Contact
    FROM providers p
    LEFT JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
    WHERE p.City = 'Hyderabad'
    GROUP BY p.Provider_ID;
"""),


    ("Receivers who claimed the most (Completed)", """
    SELECT r.Name, r.Type, COUNT(*) AS Completed_Claims
    FROM claims c
    JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
    WHERE c.Status = 'Completed'
    GROUP BY r.Receiver_ID, r.Name, r.Type
    ORDER BY Completed_Claims DESC;
"""),


    ("Total quantity available", """
        SELECT COALESCE(SUM(Quantity), 0) AS Total_Quantity
        FROM food_listings;
    """),

    ("City with highest number of listings", """
        SELECT p.City, COUNT(*) AS Listings
        FROM food_listings fl
        JOIN providers p ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.City
        ORDER BY Listings DESC;
    """),

    ("Most common food types", """
        SELECT Food_Type, COUNT(*) AS Frequency
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Frequency DESC;
    """),

    ("Claims per food item", """
        SELECT fl.Food_ID, fl.Food_Name, COUNT(c.Claim_ID) AS Claims_Count
        FROM food_listings fl
        LEFT JOIN claims c ON c.Food_ID = fl.Food_ID
        GROUP BY fl.Food_ID, fl.Food_Name
        ORDER BY Claims_Count DESC;
    """),

    ("Provider with most successful claims", """
        SELECT p.Name, COUNT(*) AS Completed_Claims
        FROM claims c
        JOIN food_listings fl ON fl.Food_ID = c.Food_ID
        JOIN providers p ON p.Provider_ID = fl.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID
        ORDER BY Completed_Claims DESC;
    """),

    ("Claims status percentages", """
        SELECT Status,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS Percentage
        FROM claims
        GROUP BY Status;
    """),

    ("Average quantity claimed per receiver", """
        SELECT r.Name, ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Claimed
        FROM claims c
        JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings fl ON fl.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Receiver_ID
        ORDER BY Avg_Quantity_Claimed DESC;
    """),

    ("Meal type most claimed", """
        SELECT fl.Meal_Type, COUNT(*) AS Completed_Claims
        FROM claims c
        JOIN food_listings fl ON fl.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY fl.Meal_Type
        ORDER BY Completed_Claims DESC;
    """),

    ("Total quantity donated by each provider", """
        SELECT p.Name, SUM(fl.Quantity) AS Total_Quantity_Listed
        FROM food_listings fl
        JOIN providers p ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.Provider_ID
        ORDER BY Total_Quantity_Listed DESC;
    """),

    ("Listings expiring within next 3 days", """
        SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, p.City, fl.Expiry_Date
        FROM food_listings fl
        JOIN providers p ON p.Provider_ID = fl.Provider_ID
        WHERE DATE(fl.Expiry_Date) <= DATE('now', '+3 day')
        ORDER BY fl.Expiry_Date;
    """),

    ("Top cities by completed claims", """
        SELECT p.City, COUNT(*) AS Completed_Claims
        FROM claims c
        JOIN food_listings fl ON fl.Food_ID = c.Food_ID
        JOIN providers p ON p.Provider_ID = fl.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.City
        ORDER BY Completed_Claims DESC;
    """)
]

# Run and print results with table format
for title, query in queries:
    print("\n=== " + title + " ===")
    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]  # column names
    print(tabulate(rows, headers=headers, tablefmt="grid"))

conn.close()
