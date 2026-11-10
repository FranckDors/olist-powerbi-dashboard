# Olist E-commerce Executive Dashboard (Power BI)

A one-page executive dashboard of **97,905 orders** from Olist, a Brazilian online marketplace (Jan 2017 – Aug 2018). It was built in **Power BI** on a star schema that I cleaned and modeled with **Python (pandas)**.

<img width="1316" height="738" alt="Screenshot 2026-11-10 173613" src="https://github.com/user-attachments/assets/8265e873-e277-45ff-8c90-c418d63cbad1" />


## Business question
How is the marketplace performing, and what should leadership focus on to grow revenue and customer satisfaction?

## Headline KPIs
| KPI | Value | Definition |
|---|---|---|
| Revenue | **R$ 13.4M** | Sum of item prices (excludes freight) |
| Orders | **97,905** | Orders that were not canceled or unavailable |
| Avg order value | **R$ 137** | Revenue ÷ orders |
| Customers | **94,703** | Unique customers (`customer_unique_id`) |
| Repeat customer % | **3.0%** | Customers with 2+ orders ÷ all customers |
| On-time delivery % | **93.2%** | Delivered on or before the estimated date ÷ delivered orders |
| Avg review score | **4.12 / 5** | Mean review per order |

## Key findings
1. **Late deliveries badly hurt satisfaction.** On-time orders average **4.29★**, but late orders average just **2.27★**, a drop of about **2 stars**. Only 6.8% of orders arrive late, yet they cause a large share of the bad reviews.
2. **Customers almost never come back.** Only **3.0%** of customers placed a second order. Growth depends almost entirely on finding new customers.
3. **Revenue is concentrated geographically.** São Paulo (SP) brings in by far the most revenue, ahead of RJ and MG.
4. **Seasonality.** Revenue grew through 2017 and peaked in **November 2017** (Black Friday).

## Recommendations
1. **Cut late deliveries.** Set delivery SLAs with carriers on the slowest routes and pad the estimated delivery dates where carriers often miss them. Turning late orders into on-time ones could lift the average review and protect seller ratings.
2. **Launch a retention program.** Offer a second-order discount, run post-delivery email flows, and target customers who left 5★ reviews. Moving the repeat rate from 3% to just 6% would double repeat revenue.
3. **Grow outside São Paulo.** Test free-shipping thresholds and regional promotions in high-potential states to reduce dependence on one market.

## Data model
Python (pandas) turns the 9 raw tables into a star schema:

- `fact_orders` (order level): revenue, freight, delivery status, review
- `fact_order_items` (item level): price, product, seller
- `dim_customers`, `dim_products`, `dim_sellers`, `dim_date` (marked as the date table)

**Cleaning decisions**
- Removed canceled and unavailable orders.
- Limited the data to Jan 2017 – Aug 2018, because the first and last months are incomplete and distort trends.
- Used `customer_unique_id` as the customer key, because Olist's `customer_id` changes with every order (using it would put repeat customers at 0%).
- Translated product categories from Portuguese to English.

**DAX measures:** Revenue, Orders, AOV, Customers, Repeat Customer %, On-Time Delivery %, and Avg Review (overall, on time, late). See [`powerbi/measures.dax`](powerbi/measures.dax).

## Repo layout
```
prep/build_model.py         raw CSVs → clean star schema
powerbi/olist_dashboard.pbix
powerbi/measures.dax        DAX measures
images/                     dashboard and model screenshots
docs/build_guide.md         build notes
```

## Reproduce
1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) into `data/raw/`
2. `pip install pandas` then `python prep/build_model.py`
3. Open `powerbi/olist_dashboard.pbix` and click **Refresh**

**Tools:** Python (pandas) · Power BI (DAX, data modeling)
**Data:** Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0)
