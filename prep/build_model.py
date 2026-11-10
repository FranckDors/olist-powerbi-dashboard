"""
Olist e-commerce -> clean star schema for Power BI and Tableau.

Usage:
    1. Download the Olist dataset from Kaggle:
       https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
    2. Unzip all CSVs into data/raw/
    3. Run:  python prep/build_model.py

Outputs (data/clean/):
    fact_orders.csv       one row per order (delivery, review, revenue)
    fact_order_items.csv  one row per item sold
    dim_customers.csv     one row per real customer (customer_unique_id)
    dim_products.csv      products with English category names
    dim_sellers.csv       sellers
    dim_date.csv          calendar table
    olist_flat.csv        everything joined at item level (easiest for Tableau)
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

# The first and last months of the dataset are nearly empty, which makes
# trend lines look like a crash. Keep the full, reliable months only.
START, END = "2017-01-01", "2018-08-31"
EXCLUDED_STATUSES = {"canceled", "unavailable"}


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}.csv")


def main() -> None:
    orders = read("olist_orders_dataset")
    items = read("olist_order_items_dataset")
    customers = read("olist_customers_dataset")
    products = read("olist_products_dataset")
    translation = read("product_category_name_translation")
    reviews = read("olist_order_reviews_dataset")
    payments = read("olist_order_payments_dataset")
    sellers = read("olist_sellers_dataset")

    # ---------- Orders ----------
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for c in date_cols:
        orders[c] = pd.to_datetime(orders[c], errors="coerce")

    orders = orders[
        orders["order_purchase_timestamp"].between(START, f"{END} 23:59:59")
        & ~orders["order_status"].isin(EXCLUDED_STATUSES)
    ].copy()

    orders["purchase_date"] = orders["order_purchase_timestamp"].dt.normalize()
    delivered = orders["order_delivered_customer_date"]
    orders["delivery_days"] = (delivered - orders["order_purchase_timestamp"]).dt.days
    orders["is_delivered"] = delivered.notna().astype(int)
    orders["is_late"] = (
        delivered.notna() & (delivered.dt.normalize() > orders["order_estimated_delivery_date"])
    ).astype(int)

    # Customer key: customer_id is per-order in Olist; customer_unique_id is the real person.
    orders = orders.merge(
        customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left"
    )

    # Order-level money from items (price = product revenue, freight = shipping)
    item_totals = items.groupby("order_id").agg(
        item_count=("order_item_id", "count"),
        product_revenue=("price", "sum"),
        freight=("freight_value", "sum"),
    )
    orders = orders.merge(item_totals, on="order_id", how="inner")

    # One review per order (keep the latest if duplicates)
    rev = (
        reviews.assign(review_creation_date=pd.to_datetime(reviews["review_creation_date"]))
        .sort_values("review_creation_date")
        .drop_duplicates("order_id", keep="last")[["order_id", "review_score"]]
    )
    orders = orders.merge(rev, on="order_id", how="left")

    # Main payment type (largest payment on the order)
    main_pay = (
        payments.sort_values("payment_value", ascending=False)
        .drop_duplicates("order_id")[["order_id", "payment_type", "payment_installments"]]
    )
    orders = orders.merge(main_pay, on="order_id", how="left")

    # Repeat-customer flag: is this the customer's 2nd+ order?
    orders = orders.sort_values("order_purchase_timestamp")
    orders["customer_order_number"] = orders.groupby("customer_unique_id").cumcount() + 1

    fact_orders = orders[
        [
            "order_id", "customer_unique_id", "purchase_date", "order_status",
            "item_count", "product_revenue", "freight", "payment_type",
            "payment_installments", "review_score", "is_delivered", "is_late",
            "delivery_days", "customer_order_number",
        ]
    ]

    # ---------- Items ----------
    fact_items = items[items["order_id"].isin(fact_orders["order_id"])].merge(
        fact_orders[["order_id", "customer_unique_id", "purchase_date"]], on="order_id"
    )[
        ["order_id", "order_item_id", "product_id", "seller_id",
         "customer_unique_id", "purchase_date", "price", "freight_value"]
    ]

    # ---------- Dimensions ----------
    dim_customers = (
        customers.drop_duplicates("customer_unique_id")[
            ["customer_unique_id", "customer_city", "customer_state"]
        ]
    )
    dim_customers = dim_customers[
        dim_customers["customer_unique_id"].isin(fact_orders["customer_unique_id"])
    ]

    dim_products = products.merge(translation, on="product_category_name", how="left")
    dim_products["category"] = (
        dim_products["product_category_name_english"]
        .fillna(dim_products["product_category_name"])
        .fillna("unknown")
        .str.replace("_", " ")
        .str.title()
    )
    dim_products = dim_products[["product_id", "category", "product_weight_g"]]

    dim_sellers = sellers[["seller_id", "seller_city", "seller_state"]]

    dates = pd.date_range(START, END, freq="D")
    dim_date = pd.DataFrame({"date": dates})
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter"] = "Q" + dim_date["date"].dt.quarter.astype(str)
    dim_date["month_num"] = dim_date["date"].dt.month
    dim_date["month"] = dim_date["date"].dt.strftime("%b")
    dim_date["year_month"] = dim_date["date"].dt.strftime("%Y-%m")
    dim_date["weekday"] = dim_date["date"].dt.strftime("%a")

    # ---------- Flat file for Tableau ----------
    flat = (
        fact_items.merge(dim_products, on="product_id", how="left")
        .merge(dim_customers, on="customer_unique_id", how="left")
        .merge(dim_sellers, on="seller_id", how="left")
        .merge(
            fact_orders.drop(columns=["customer_unique_id", "purchase_date"]),
            on="order_id", how="left",
        )
    )

    outputs = {
        "fact_orders": fact_orders,
        "fact_order_items": fact_items,
        "dim_customers": dim_customers,
        "dim_products": dim_products,
        "dim_sellers": dim_sellers,
        "dim_date": dim_date,
        "olist_flat": flat,
    }
    for name, df in outputs.items():
        df.to_csv(CLEAN / f"{name}.csv", index=False)
        print(f"{name:18s} {len(df):>8,} rows")

    # Quick sanity numbers to put in your README
    print("\n--- Headline numbers ---")
    print(f"Revenue (product):  R$ {fact_orders['product_revenue'].sum():,.0f}")
    print(f"Orders:             {len(fact_orders):,}")
    print(f"Avg order value:    R$ {fact_orders['product_revenue'].mean():,.2f}")
    print(f"Customers:          {fact_orders['customer_unique_id'].nunique():,}")
    repeat = (fact_orders.groupby('customer_unique_id').size() > 1).mean()
    print(f"Repeat customer %:  {repeat:.1%}")
    d = fact_orders[fact_orders["is_delivered"] == 1]
    print(f"On-time delivery %: {1 - d['is_late'].mean():.1%}")
    print(f"Avg review score:   {fact_orders['review_score'].mean():.2f}")
    print("Avg review, on time vs late:",
          d.groupby("is_late")["review_score"].mean().round(2).to_dict())


if __name__ == "__main__":
    main()
