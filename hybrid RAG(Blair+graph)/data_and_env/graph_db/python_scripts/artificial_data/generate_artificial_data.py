import pandas as pd
import random
import faker
import os

# Initialize Faker
fake = faker.Faker()

# Constants
NUM_PRODUCTS = 10
NUM_REVIEWS = 30
NUM_SENTIMENTS = 50
OUTPUT_DIR = "/home/akshat/CSE_573/laptop_hybrid_search/agentic_hybrid_search/graph_db/python_scripts/artificial_data"

def generate_data():
    print("Generating artificial data...")
    
    # 1. Generate Products (10 entries)
    products = []
    parent_asins = []
    for _ in range(NUM_PRODUCTS):
        asin = fake.unique.bothify(text='B0########')
        parent_asins.append(asin)
        products.append({
            "parent_asin": asin,
            "Brand_Normalized": fake.company(),
            "Model Name": fake.word().capitalize() + " " + str(random.randint(1000, 9000)),
            "blair_embedding": str([random.uniform(-1, 1) for _ in range(10)]) # Mock embedding
        })
    df_products = pd.DataFrame(products)
    
    # 2. Generate Products Relation (10 entries, 1-to-1 with products)
    products_relation = []
    for asin in parent_asins:
        products_relation.append({
            "parent_asin": asin,
            "price": round(random.uniform(200, 2000), 2),
            "rated": round(random.uniform(1, 5), 1),
            "Leaf_Category": "Laptops",
            "Color": fake.color_name(),
            "Chipset Brand": random.choice(["Intel", "AMD", "Apple"]),
            "Operating System": random.choice(["Windows 11", "macOS", "Chrome OS"]),
            "Average Battery Life (in hours)": random.randint(4, 15),
            "RAM_Size": random.choice(["8GB", "16GB", "32GB"]),
            "RAM_Type": random.choice(["DDR4", "DDR5"]),
            "Storage_Size": random.choice(["256GB", "512GB", "1TB"]),
            "Storage_Type": "SSD",
            "Screen_Category": random.choice(["Standard", "OLED", "IPS"]),
            "Weight_Category": random.choice(["Light", "Medium", "Heavy"])
        })
    df_products_relation = pd.DataFrame(products_relation)

    # 3. Generate Reviews (30 entries)
    reviews = []
    review_ids = []
    for _ in range(NUM_REVIEWS):
        rid = fake.unique.random_int(min=10000, max=99999)
        review_ids.append(rid)
        reviews.append({
            "review_id": rid,
            "parent_asin": random.choice(parent_asins),
            "user_id": fake.bothify(text='USER#######'),
            "verified_purchase": random.choice([True, False])
        })
    df_reviews = pd.DataFrame(reviews)

    # 4. Generate Reviews Sentiment (50 entries)
    reviews_sentiment = []
    for _ in range(NUM_SENTIMENTS):
        reviews_sentiment.append({
            "review_id": random.choice(review_ids),
            "feature": random.choice(["Battery", "Screen", "Performance", "Price", "Design"]),
            "sentiment": random.choice(["Positive", "Negative", "Neutral"]),
            "reasons": fake.sentence()
        })
    df_reviews_sentiment = pd.DataFrame(reviews_sentiment)

    # Save to CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    df_products.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    df_products_relation.to_csv(os.path.join(OUTPUT_DIR, "products_relation.csv"), index=False)
    df_reviews.to_csv(os.path.join(OUTPUT_DIR, "reviews.csv"), index=False)
    df_reviews_sentiment.to_csv(os.path.join(OUTPUT_DIR, "reviews_sentiment.csv"), index=False)
    
    print(f"Files saved to {OUTPUT_DIR}")
    return df_products, df_products_relation, df_reviews, df_reviews_sentiment

def verify_data(df_products, df_products_relation, df_reviews, df_reviews_sentiment):
    print("\nVerifying data...")
    
    # Check counts
    assert len(df_products) == 10, f"Expected 10 products, got {len(df_products)}"
    assert len(df_products_relation) == 10, f"Expected 10 product relations, got {len(df_products_relation)}"
    assert len(df_reviews) == 30, f"Expected 30 reviews, got {len(df_reviews)}"
    assert len(df_reviews_sentiment) == 50, f"Expected 50 review sentiments, got {len(df_reviews_sentiment)}"
    print("Row counts verified.")

    # Check Primary Keys (Not Null & Unique)
    assert df_products['parent_asin'].is_unique, "Product parent_asin not unique"
    assert df_products['parent_asin'].isnull().sum() == 0, "Product parent_asin has nulls"
    
    assert df_products_relation['parent_asin'].is_unique, "Product relation parent_asin not unique"
    assert df_products_relation['parent_asin'].isnull().sum() == 0, "Product relation parent_asin has nulls"
    
    assert df_reviews['review_id'].is_unique, "Review review_id not unique"
    assert df_reviews['review_id'].isnull().sum() == 0, "Review review_id has nulls"
    print("Primary keys verified.")

    # Check Foreign Keys
    product_asins = set(df_products['parent_asin'])
    relation_asins = set(df_products_relation['parent_asin'])
    review_asins = set(df_reviews['parent_asin'])
    
    assert relation_asins.issubset(product_asins), "Product relation has orphan parent_asin"
    assert review_asins.issubset(product_asins), "Reviews have orphan parent_asin"
    
    review_ids = set(df_reviews['review_id'])
    sentiment_review_ids = set(df_reviews_sentiment['review_id'])
    
    assert sentiment_review_ids.issubset(review_ids), "Review sentiments have orphan review_id"
    print("Foreign keys verified.")
    
    print("\nVerification Successful!")

if __name__ == "__main__":
    df_p, df_pr, df_r, df_rs = generate_data()
    verify_data(df_p, df_pr, df_r, df_rs)
