# Olist E-commerce Executive Dashboard (Power BI + Tableau)

A one-page executive dashboard of ~100K orders from Olist, a Brazilian online marketplace (2017–2018). It is built twice, once in **Power BI** and once in **Tableau**, from the same cleaned star schema.

**[▶ View the live Tableau dashboard](PASTE_TABLEAU_PUBLIC_LINK)** · [Power BI PDF export](powerbi/olist_dashboard.pdf)

![Power BI dashboard](images/powerbi_dashboard.png)

## Business question
How is the marketplace performing, and what should leadership focus on to grow revenue and customer satisfaction?

## KPIs tracked
| KPI | Definition |
|---|---|
| Revenue | Sum of item prices (excludes freight) |
| Orders / AOV | Order count; revenue ÷ orders |
| Repeat customer % | Customers with 2+ orders ÷ all customers |
| On-time delivery % | Delivered on or before the estimated date ÷ delivered orders |
| Avg review score | Mean 1–5 star review per order |

## Key findings
> Replace these with your numbers from `prep/build_model.py` and the dashboard.

1. **Revenue grew X% from H1 2017 to H1 2018**, with a spike in Nov 2017 (Black Friday).
2. **Late deliveries hurt satisfaction:** late orders average **X★** vs **X★** on time.
3. **Almost no repeat buyers:** only **X%** of customers ordered more than once.
4. **Revenue is concentrated:** São Paulo brings in **X%**, and the top 3 categories bring in **X%**.

## Recommendations
1. **Fix delivery in the slowest states.** Set carrier SLAs and better delivery estimates → higher reviews.
2. **Launch a retention program** (second-order discount, email flows). Even a small rise in repeat rate is a large revenue gain.
3. **Grow outside SP.** Test free-shipping thresholds in states where freight is a high share of order value.

## Data model
Python (pandas) turns the 9 raw tables into a star schema:

- `fact_orders` (order level): revenue, freight, delivery, review
- `fact_order_items` (item level): price, product, seller
- `dim_customers`, `dim_products`, `dim_sellers`, `dim_date`

![Model](images/powerbi_model.png)

Cleaning decisions: canceled and unavailable orders are removed. The data is limited to Jan 2017 – Aug 2018 because the edge months are incomplete. `customer_unique_id` is used as the customer key, since Olist's `customer_id` changes with every order.

## Power BI vs Tableau: what I noticed
- *Power BI:* relationships + DAX measures; time intelligence needs a marked date table.
- *Tableau:* faster for exploring a flat extract; needed LOD expressions to avoid double counting order-level fields.
- *(add your own notes)*

## Repo layout
```
prep/build_model.py         raw CSVs → clean star schema
powerbi/measures.dax        all DAX measures
powerbi/olist_dashboard.pbix
tableau/calculated_fields.md
docs/build_guide.md         step-by-step build notes
images/                     screenshots
```

## Reproduce
1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) into `data/raw/`
2. `pip install pandas && python prep/build_model.py`
3. Open `powerbi/olist_dashboard.pbix`, or connect Tableau to `data/clean/olist_flat.csv`

**Tools:** Python (pandas) · Power BI (DAX) · Tableau Public
**Data:** Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0)
