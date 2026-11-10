# Build guide (about 2 days)

## Day 1, morning: data (1–2 hours)

1. Download the dataset from Kaggle: <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>
2. Unzip all 9 CSVs into `data/raw/`.
3. `pip install pandas`, then run `python prep/build_model.py`.
4. Write down the headline numbers it prints. You'll use them in the README.

The script removes canceled and unavailable orders. It also keeps only Jan 2017 – Aug 2018, because the first and last months are nearly empty. Explain both choices in the README, since saying why you cleaned the data a certain way is part of what you're showing.

## Day 1, afternoon: Power BI version

**Load and model**
1. Get Data > Text/CSV and load all six `fact_*` and `dim_*` files. Don't load `olist_flat`.
2. In Model view, create these relationships (one-to-many, single direction):
   - `dim_date[date]` → `fact_orders[purchase_date]`
   - `dim_customers[customer_unique_id]` → `fact_orders[customer_unique_id]`
   - `dim_products[product_id]` → `fact_order_items[product_id]`
   - `dim_sellers[seller_id]` → `fact_order_items[seller_id]`
   - `dim_date[date]` → `fact_order_items[purchase_date]`
3. Select `dim_date` and choose Table tools > **Mark as date table** > `date`.
4. Sort `dim_date[month]` by `month_num` (Column tools > Sort by column).
5. Add the measures from `powerbi/measures.dax`.
6. Take a screenshot of the Model view. A star schema shows recruiters you understand data modeling.

**Layout (one page, 16:9)**
```
┌──────────────────────────────────────────────────────────────┐
│ Olist E-commerce Performance 2017–2018      [Year] [State]   │
│ subtitle: Dashboard Subtitle measure                         │
├─────────┬─────────┬─────────┬─────────┬─────────┬────────────┤
│ Revenue │ Orders  │  AOV    │ Repeat %│ On-time%│ Avg review │  ← KPI cards
├─────────┴─────────┴─────────┴─────────┼─────────┴────────────┤
│ Monthly revenue (line) + 3M avg       │ Review score:         │
│                                       │ on time vs late (bar) │
├───────────────────────────────────────┼──────────────────────┤
│ Top 10 categories by revenue (bar)    │ Revenue by state      │
│                                       │ (bar or filled map)   │
└───────────────────────────────────────┴──────────────────────┘
```
- Use the **Card (new)** visual for the KPIs, with `Revenue YoY %` as a reference label on the Revenue card.
- Keep slicers to Year and Customer State only.
- Use one accent color for highlights and grey for everything else. Avoid a rainbow palette.
- Save as `powerbi/olist_dashboard.pbix`. Then File > Export > PDF, and take a PNG screenshot into `images/powerbi_dashboard.png`.

## Day 2, morning: Tableau Public version

1. Connect to `data/clean/olist_flat.csv`.
2. Create the fields in `tableau/calculated_fields.md`.
3. Build six sheets (the KPI tiles, Monthly trend, Category bar, State map, Review vs delivery), then put them on one dashboard sized 1200 × 800.
4. Add **Purchase Date (Year)** and **Customer State** as filters, set to *Apply to all worksheets using this data source*.
5. Use the map sheet as a filter: Dashboard > Actions > Add Filter Action. Recruiters like clickable dashboards.
6. Save to Tableau Public, copy the link, and save a screenshot as `images/tableau_dashboard.png`.

Building the same dashboard in both tools is a good talking point. Put a short "Power BI vs Tableau: what I noticed" note in the README (for example, DAX measures vs LOD expressions, or star schema vs a flat extract).

## Day 2, afternoon: insights write-up

Fill in the **Key findings** and **Recommendations** sections of the README with your own numbers. Look into these questions:

- **Delivery → reviews.** Compare the average review on late orders with on-time orders. In this dataset the gap is usually large.
- **Retention.** The repeat-customer % is very low. Olist mostly brings in new customers, so a retention program is an obvious lever.
- **Concentration.** What share of revenue do the top 3 categories and the top state (SP) bring in?
- **Seasonality.** Look at Nov 2017 (Black Friday) against the trend.
- **Freight.** In which states is freight a high % of order value? Do those states also have lower reviews?

Write each recommendation as **finding → action → expected impact**. For example: "Late orders average ~2.5★ vs ~4.3★ on time → set carrier SLAs for the North/Northeast routes → raise the average review and repeat purchases."

## Finish

- Push to GitHub (see the README for the folder layout). Add `data/raw/` to `.gitignore`, because the Kaggle files are large and are Olist's data.
- Pin the repo on your GitHub profile.
- Resume bullet: *"Built an executive KPI dashboard in Power BI and Tableau on 100K+ Brazilian e-commerce orders (star schema, DAX, LOD); found that late deliveries cut review scores by ~X points and recommended carrier SLAs."*
