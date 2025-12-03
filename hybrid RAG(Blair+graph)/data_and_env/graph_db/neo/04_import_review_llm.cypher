// 04_import_review_llm.cypher
// Load reviews_sentiment.csv and create Review, Feature, and Sentiment nodes

LOAD CSV WITH HEADERS FROM 'file:///reviews_sentiment.csv' AS row
WITH row
WHERE row.review_id IS NOT NULL AND row.feature IS NOT NULL AND row.sentiment IS NOT NULL

CALL {
    WITH row
    // 1. Match User who wrote this review (using review_id stored on User)
    MATCH (u:User {review_id: row.review_id})

    // 2. Create/Merge Review Node
    MERGE (r:Review {review_id: row.review_id})
    MERGE (u)-[:WROTE]->(r)

    // 3. Create Feature Node (Unique per review to capture specific context)
    // We use both feature name and review_id to make it unique to this review instance
    MERGE (f:Feature {name: row.feature, review_id: row.review_id})
    MERGE (r)-[:USER_SAID]->(f)

    // 4. Create Sentiment Node (Shared nodes: Positive, Negative, Neutral)
    MERGE (s:Sentiment {value: row.sentiment})
    MERGE (f)-[:HAS_SENTIMENT]->(s)

} IN TRANSACTIONS OF 1000 ROWS;
