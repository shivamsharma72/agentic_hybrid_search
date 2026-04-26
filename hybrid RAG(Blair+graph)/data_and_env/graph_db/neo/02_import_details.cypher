// 02_import_details.cypher
// Load products_relation.csv and create detailed relationships

LOAD CSV WITH HEADERS FROM 'file:///products_relation.csv' AS row
MATCH (p:Product {parent_asin: row.parent_asin})

// 1. Price Category
WITH p, row,
     CASE 
        WHEN toFloat(row.price) < 300 THEN 'Cheap'
        WHEN toFloat(row.price) >= 300 AND toFloat(row.price) < 700 THEN 'Budget'
        ELSE 'Expensive'
     END AS price_category
MERGE (pc:PriceCategory {name: price_category})
MERGE (p)-[:HAS_PRICE_CATEGORY]->(pc)

// 2. Rating
WITH p, row
WHERE row.rated IS NOT NULL AND row.rated <> ""
MERGE (r:Rating {value: row.rated})
MERGE (p)-[:IS_RATED]->(r)

// 3. Leaf Category
WITH p, row
WHERE row.Leaf_Category IS NOT NULL AND row.Leaf_Category <> ""
MERGE (c:Category {name: row.Leaf_Category})
MERGE (p)-[:IS_UNDER_THE_CATEGORY]->(c)

// 4. Color
WITH p, row
WHERE row.Color IS NOT NULL AND row.Color <> ""
MERGE (co:Color {name: row.Color})
MERGE (p)-[:IS_OF_COLOR]->(co)

// 5. Chipset Brand
WITH p, row
WHERE row.`Chipset Brand` IS NOT NULL AND row.`Chipset Brand` <> ""
MERGE (cb:ChipsetBrand {name: row.`Chipset Brand`})
MERGE (p)-[:HAS_A_PROCESSOR_OF]->(cb)

// 6. Operating System
WITH p, row
WHERE row.`Operating System` IS NOT NULL AND row.`Operating System` <> ""
MERGE (os:OS {name: row.`Operating System`})
MERGE (p)-[:HAS_OPERATING_SYSTEM]->(os)

// 7. Battery Life
WITH p, row
WHERE row.`Average Battery Life (in hours)` IS NOT NULL AND row.`Average Battery Life (in hours)` <> ""
MERGE (bl:BatteryLife {value: row.`Average Battery Life (in hours)`})
MERGE (p)-[:HAS_BATTERY_LIFE_OF]->(bl)

// 8. RAM Size
WITH p, row
WHERE row.RAM_Size IS NOT NULL AND row.RAM_Size <> ""
MERGE (rs:RAMSize {value: row.RAM_Size})
MERGE (p)-[:HAS_RAM]->(rs)

// 9. RAM Type
WITH p, row
WHERE row.RAM_Type IS NOT NULL AND row.RAM_Type <> ""
MERGE (rt:RAMType {name: row.RAM_Type})
MERGE (p)-[:HAS_A_RAM_TYPE]->(rt)

// 10. Storage Size
WITH p, row
WHERE row.Storage_Size IS NOT NULL AND row.Storage_Size <> ""
MERGE (ss:StorageSize {value: row.Storage_Size})
MERGE (p)-[:HAS_STORAGE_SIZE_OF]->(ss)

// 11. Storage Type
WITH p, row
WHERE row.Storage_Type IS NOT NULL AND row.Storage_Type <> ""
MERGE (st:StorageType {name: row.Storage_Type})
MERGE (p)-[:HAS_TYPE]->(st)

// 12. Screen Category
WITH p, row
WHERE row.Screen_Category IS NOT NULL AND row.Screen_Category <> ""
MERGE (sc:ScreenCategory {name: row.Screen_Category})
MERGE (p)-[:HAS_A_SCREEN_CATEGORY]->(sc)

// 13. Weight Category
WITH p, row
WHERE row.Weight_Category IS NOT NULL AND row.Weight_Category <> ""
MERGE (wc:WeightCategory {name: row.Weight_Category})
MERGE (p)-[:LAPTOP_IS_WEIGHT_CATEGORY]->(wc);
