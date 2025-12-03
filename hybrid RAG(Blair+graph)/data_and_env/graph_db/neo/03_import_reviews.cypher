// 03_import_reviews.cypher
// Load reviews.csv and create User nodes linked to Products and VerifiedStatus
LOAD CSV WITH HEADERS FROM 'file:///reviews.csv' AS row
WITH row
WHERE
  row.review_id IS NOT NULL AND
  row.parent_asin IS NOT NULL AND
  row.user_id IS NOT NULL

CALL {
  WITH row
  // 1. Match the Product
  MATCH (p:Product {parent_asin: row.parent_asin})

  // 2. Create/Merge User node and store review_id
  MERGE (u:User {user_id: row.user_id})
  SET u.review_id = row.review_id

  // 3. Connect User to Product
  MERGE (u)-[:REVIEWED]->(p)

  // 4. Handle Verified Purchase Status
  // Create the status node (True or False)
  MERGE (vs:VerifiedStatus {value: toBoolean(row.verified_purchase)})

  // Connect User to the status node
  MERGE (u)-[:verified_purchase]->(vs)

} IN TRANSACTIONS OF 1000 ROWS;