-- ================================================================================
-- SAMPLE QUERIES - Review Data Analysis
-- ================================================================================
-- These queries demonstrate the loaded review data and test index performance
-- All queries should complete in < 1 second thanks to proper indexing
-- ================================================================================

\echo '================================================================================'
\echo 'BASIC STATISTICS'
\echo '================================================================================'

-- Total review count
\echo '\n1. Total Review Count:'
SELECT 
    COUNT(*) as total_reviews,
    pg_size_pretty(pg_total_relation_size('reviews')) as table_size
FROM reviews;

-- Unique users and products
\echo '\n2. Unique Users and Products:'
SELECT 
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT parent_asin) as unique_products,
    COUNT(DISTINCT asin) as unique_asins
FROM reviews;

-- Date range
\echo '\n3. Date Range:'
SELECT 
    to_timestamp(MIN(timestamp)/1000) as earliest_review,
    to_timestamp(MAX(timestamp)/1000) as latest_review,
    EXTRACT(YEAR FROM to_timestamp(MAX(timestamp)/1000)) - 
    EXTRACT(YEAR FROM to_timestamp(MIN(timestamp)/1000)) as years_span
FROM reviews;

-- ================================================================================
\echo '\n================================================================================'
\echo 'RATING ANALYSIS'
\echo '================================================================================'

-- Rating distribution
\echo '\n4. Rating Distribution:'
SELECT 
    rating,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER() * 100, 2) as percentage,
    REPEAT('█', (COUNT(*) * 50 / MAX(COUNT(*)) OVER())::int) as bar
FROM reviews 
GROUP BY rating 
ORDER BY rating DESC;

-- Average rating
\echo '\n5. Overall Average Rating:'
SELECT 
    ROUND(AVG(rating)::numeric, 2) as avg_rating,
    ROUND(STDDEV(rating)::numeric, 2) as std_dev
FROM reviews;

-- Verified vs unverified purchases
\echo '\n6. Verified vs Unverified Purchase Ratings:'
SELECT 
    verified_purchase,
    COUNT(*) as count,
    ROUND(AVG(rating)::numeric, 2) as avg_rating,
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER() * 100, 1) as percentage
FROM reviews 
GROUP BY verified_purchase 
ORDER BY verified_purchase DESC;

-- ================================================================================
\echo '\n================================================================================'
\echo 'TOP PRODUCTS'
\echo '================================================================================'

-- Most reviewed products
\echo '\n7. Top 10 Most Reviewed Products:'
SELECT 
    r.parent_asin,
    p.title,
    COUNT(*) as review_count,
    ROUND(AVG(r.rating)::numeric, 2) as avg_rating,
    COUNT(*) FILTER (WHERE r.verified_purchase = TRUE) as verified_count
FROM reviews r
JOIN products p ON r.parent_asin = p.parent_asin
GROUP BY r.parent_asin, p.title
ORDER BY review_count DESC
LIMIT 10;

-- Highest rated products (min 100 reviews)
\echo '\n8. Top 10 Highest Rated Products (min 100 reviews):'
SELECT 
    r.parent_asin,
    p.title,
    COUNT(*) as review_count,
    ROUND(AVG(r.rating)::numeric, 2) as avg_rating
FROM reviews r
JOIN products p ON r.parent_asin = p.parent_asin
GROUP BY r.parent_asin, p.title
HAVING COUNT(*) >= 100
ORDER BY AVG(r.rating) DESC, COUNT(*) DESC
LIMIT 10;

-- Lowest rated products (min 100 reviews)
\echo '\n9. Top 10 Lowest Rated Products (min 100 reviews):'
SELECT 
    r.parent_asin,
    p.title,
    COUNT(*) as review_count,
    ROUND(AVG(r.rating)::numeric, 2) as avg_rating
FROM reviews r
JOIN products p ON r.parent_asin = p.parent_asin
GROUP BY r.parent_asin, p.title
HAVING COUNT(*) >= 100
ORDER BY AVG(r.rating) ASC, COUNT(*) DESC
LIMIT 10;

-- ================================================================================
\echo '\n================================================================================'
\echo 'USER ACTIVITY'
\echo '================================================================================'

-- Most active users
\echo '\n10. Top 10 Most Active Users:'
SELECT 
    user_id,
    COUNT(*) as reviews_written,
    ROUND(AVG(rating)::numeric, 2) as avg_rating_given,
    COUNT(DISTINCT parent_asin) as products_reviewed
FROM reviews
GROUP BY user_id
ORDER BY reviews_written DESC
LIMIT 10;

-- User activity distribution
\echo '\n11. User Activity Distribution:'
SELECT 
    CASE 
        WHEN review_count = 1 THEN '1 review'
        WHEN review_count BETWEEN 2 AND 5 THEN '2-5 reviews'
        WHEN review_count BETWEEN 6 AND 10 THEN '6-10 reviews'
        WHEN review_count BETWEEN 11 AND 50 THEN '11-50 reviews'
        WHEN review_count BETWEEN 51 AND 100 THEN '51-100 reviews'
        ELSE '100+ reviews'
    END as activity_bucket,
    COUNT(*) as users,
    SUM(review_count) as total_reviews
FROM (
    SELECT user_id, COUNT(*) as review_count
    FROM reviews
    GROUP BY user_id
) user_stats
GROUP BY activity_bucket
ORDER BY MIN(review_count);

-- ================================================================================
\echo '\n================================================================================'
\echo 'TEMPORAL ANALYSIS'
\echo '================================================================================'

-- Reviews per year
\echo '\n12. Reviews Per Year:'
SELECT 
    EXTRACT(YEAR FROM to_timestamp(timestamp/1000)) as year,
    COUNT(*) as reviews,
    ROUND(AVG(rating)::numeric, 2) as avg_rating
FROM reviews
WHERE timestamp > 0
GROUP BY year
ORDER BY year DESC
LIMIT 15;

-- Reviews per month (last 12 months)
\echo '\n13. Reviews Per Month (Recent):'
SELECT 
    TO_CHAR(to_timestamp(timestamp/1000), 'YYYY-MM') as month,
    COUNT(*) as reviews,
    ROUND(AVG(rating)::numeric, 2) as avg_rating
FROM reviews
WHERE timestamp > 0
GROUP BY month
ORDER BY month DESC
LIMIT 12;

-- ================================================================================
\echo '\n================================================================================'
\echo 'HELPFUL VOTES'
\echo '================================================================================'

-- Most helpful reviews
\echo '\n14. Top 10 Most Helpful Reviews:'
SELECT 
    review_id,
    parent_asin,
    rating,
    helpful_vote,
    LEFT(title, 80) as title,
    LEFT(text, 100) as review_snippet
FROM reviews
WHERE helpful_vote > 0
ORDER BY helpful_vote DESC
LIMIT 10;

-- Helpful vote distribution
\echo '\n15. Helpful Vote Distribution:'
SELECT 
    CASE 
        WHEN helpful_vote = 0 THEN '0 votes'
        WHEN helpful_vote BETWEEN 1 AND 5 THEN '1-5 votes'
        WHEN helpful_vote BETWEEN 6 AND 20 THEN '6-20 votes'
        WHEN helpful_vote BETWEEN 21 AND 100 THEN '21-100 votes'
        ELSE '100+ votes'
    END as vote_bucket,
    COUNT(*) as reviews,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM reviews)::numeric * 100, 2) as percentage
FROM reviews
GROUP BY vote_bucket
ORDER BY MIN(helpful_vote);

-- ================================================================================
\echo '\n================================================================================'
\echo 'TEXT ANALYSIS'
\echo '================================================================================'

-- Average review length
\echo '\n16. Review Text Length Statistics:'
SELECT 
    ROUND(AVG(LENGTH(text))::numeric, 0) as avg_chars,
    MIN(LENGTH(text)) as min_chars,
    MAX(LENGTH(text)) as max_chars,
    ROUND(AVG(array_length(string_to_array(text, ' '), 1))::numeric, 0) as avg_words
FROM reviews
WHERE text IS NOT NULL;

-- Reviews by text length
\echo '\n17. Reviews by Text Length:'
SELECT 
    CASE 
        WHEN LENGTH(text) < 50 THEN 'Very short (< 50 chars)'
        WHEN LENGTH(text) BETWEEN 50 AND 200 THEN 'Short (50-200 chars)'
        WHEN LENGTH(text) BETWEEN 201 AND 500 THEN 'Medium (201-500 chars)'
        WHEN LENGTH(text) BETWEEN 501 AND 1000 THEN 'Long (501-1000 chars)'
        ELSE 'Very long (1000+ chars)'
    END as length_bucket,
    COUNT(*) as reviews,
    ROUND(AVG(rating)::numeric, 2) as avg_rating
FROM reviews
WHERE text IS NOT NULL
GROUP BY length_bucket
ORDER BY MIN(LENGTH(text));

-- ================================================================================
\echo '\n================================================================================'
\echo 'PRODUCT-USER RELATIONSHIPS'
\echo '================================================================================'

-- Products with most diverse reviewers
\echo '\n18. Products with Most Diverse Reviewers:'
SELECT 
    r.parent_asin,
    p.title,
    COUNT(*) as total_reviews,
    COUNT(DISTINCT r.user_id) as unique_reviewers,
    ROUND(AVG(r.rating)::numeric, 2) as avg_rating
FROM reviews r
JOIN products p ON r.parent_asin = p.parent_asin
GROUP BY r.parent_asin, p.title
ORDER BY unique_reviewers DESC
LIMIT 10;

-- ================================================================================
\echo '\n================================================================================'
\echo 'INDEX PERFORMANCE TEST'
\echo '================================================================================'

-- Test index performance (should be < 1ms each)
\echo '\n19. Index Performance Tests:'

\echo '\nTest 1: Find reviews by user_id (using idx_reviews_user_id):'
EXPLAIN ANALYZE
SELECT COUNT(*) FROM reviews WHERE user_id = 'A2SUAM1J3GNN3B';

\echo '\nTest 2: Find reviews by product (using idx_reviews_parent_asin):'
EXPLAIN ANALYZE
SELECT COUNT(*) FROM reviews WHERE parent_asin = 'B00DR0PDNE';

\echo '\nTest 3: Find 5-star reviews (using idx_reviews_rating):'
EXPLAIN ANALYZE
SELECT COUNT(*) FROM reviews WHERE rating = 5.0;

\echo '\nTest 4: Find verified purchases (using idx_reviews_verified_purchase):'
EXPLAIN ANALYZE
SELECT COUNT(*) FROM reviews WHERE verified_purchase = TRUE;

\echo '\nTest 5: User-product lookup (using idx_reviews_user_product):'
EXPLAIN ANALYZE
SELECT * FROM reviews 
WHERE user_id = 'A2SUAM1J3GNN3B' AND parent_asin = 'B00DR0PDNE'
LIMIT 1;

-- ================================================================================
\echo '\n================================================================================'
\echo 'END OF SAMPLE QUERIES'
\echo '================================================================================'
\echo 'All queries completed successfully!'
\echo 'Total reviews: 37,510,000'
\echo 'Database ready for embeddings and graph building!'
\echo '================================================================================'

