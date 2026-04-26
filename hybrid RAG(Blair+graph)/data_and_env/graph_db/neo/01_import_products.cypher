// 01_import_products.cypher
// Load products.csv and create Product nodes with parent_asin as ID, name from Brand+Model, and embeddings

LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row

// 1. Create Product Node
MERGE (p:Product {parent_asin: row.parent_asin})
SET p.name = row.Brand_Normalized + " " + row.`Model Name`,
    p.embedding = row.blair_embedding,
    // Keep other useful properties if needed, but user emphasized these
    p.brand = row.Brand_Normalized,
    p.model = row.`Model Name`

// 2. Create Brand Node and Relationship
WITH p, row
WHERE row.Brand_Normalized IS NOT NULL AND row.Brand_Normalized <> ""
MERGE (b:Brand {name: row.Brand_Normalized})
MERGE (p)-[:MANUFACTURED_BY]->(b);
