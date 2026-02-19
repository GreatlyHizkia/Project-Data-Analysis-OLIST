import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# ==============================
# 1. LOAD DATA
# ==============================

rfm_df = pd.read_csv("rfm_df.csv")
product_order_df = pd.read_csv("product_order_items_orders.csv")
orders_df = pd.read_csv("orders.csv")

# Pastikan kolom tanggal berformat datetime
datetime_cols = ["order_purchase_timestamp"]
for col in datetime_cols:
    if col in orders_df.columns:
        orders_df[col] = pd.to_datetime(orders_df[col])
    if col in product_order_df.columns:
        product_order_df[col] = pd.to_datetime(product_order_df[col])

# ==============================
# 2. SIDEBAR (FILTER TANGGAL)
# ==============================
min_date = orders_df["order_purchase_timestamp"].min()
max_date = orders_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    # Filter tanggal hanya untuk grafik yang membutuhkan rentang waktu
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan input user
main_orders = orders_df[(orders_df["order_purchase_timestamp"] >= str(start_date)) & 
                        (orders_df["order_purchase_timestamp"] <= str(end_date))]

main_product_order = product_order_df[(product_order_df["order_purchase_timestamp"] >= str(start_date)) & 
                                      (product_order_df["order_purchase_timestamp"] <= str(end_date))]

# ==============================
# 3. DASHBOARD 
# ==============================
st.header('Olist E-Commerce Dashboard :sparkles:')

# --- SECTION 1: TREND DELIVERED ---

st.subheader("Monthly Delivered Orders Trend")

# Filter: Hanya ambil status 'delivered' (Gunakan .copy() agar aman)
delivered_df = main_orders[main_orders['order_status'] == 'delivered'].copy()


# Pastikan kolom timestamp sudah datetime
delivered_df['order_purchase_timestamp'] = pd.to_datetime(delivered_df['order_purchase_timestamp'])

monthly_delivered = (
    delivered_df.groupby(delivered_df['order_purchase_timestamp'].dt.to_period('M'))['order_id']
    .nunique()
    .reset_index()
)
monthly_delivered.columns = ['month_year', 'total_orders_delivered']

# Ubah ke string untuk sumbu X
monthly_delivered['month_year'] = monthly_delivered['month_year'].astype(str)

# Membuat plot
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(
    data=monthly_delivered, 
    x='month_year', 
    y='total_orders_delivered', 
    marker='o', 
    color='blue', 
    linewidth=2,
    ax=ax # Plot ke object axis Streamlit
)

# Styling Tambahan
ax.set_title("Tren jumlah order yang berhasil terkirim (delivered) tiap bulan", fontsize=12)
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah order terkirim")
plt.xticks(rotation=45)
ax.grid(True, linestyle='--', alpha=0.5)

# Tampilkan di Streamlit
st.pyplot(fig)

# --- SECTION 2: TOP & BOTTOM PRODUCTS ---
st.subheader( "5 Best & Worst Selling Products")
# Menghitung total terjual per kategori
product_counts = main_product_order.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=False).reset_index()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10))
sns.barplot(x="order_id", y="product_category_name_english", data=product_counts.head(5), palette="Blues_r", ax=ax[0])
ax[0].set_title("5 Best Selling Products", fontsize=20)

sns.barplot(x="order_id", y="product_category_name_english", data=product_counts.tail(5).sort_values(by="order_id", ascending=True), palette="Reds_r", ax=ax[1])
ax[1].set_title("5 Worst Selling Products", fontsize=20)
ax[1].invert_xaxis(); ax[1].yaxis.set_label_position("right"); ax[1].yaxis.tick_right()
st.pyplot(fig)

# --- SECTION 3: PURCHASE HOUR ---
st.subheader(" Purchase Hour Distribution")
hourly_counts = main_orders['purchase_hour'].value_counts().sort_index().reset_index()
hourly_counts.columns = ['hour', 'count']

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='hour', y='count', data=hourly_counts, color="#90CAF9", ax=ax)
ax.set_title("Jam-jam dimana customer menekan tombol beli", fontsize=15)
st.pyplot(fig)

# --- SECTION 4: REVENUE CONTRIBUTION ---
st.subheader("Top 10 Category by Revenue Contribution")
rev_per_cat = main_product_order.groupby('product_category_name_english')['price'].sum().reset_index()
total_rev = rev_per_cat['price'].sum()
rev_per_cat['percent'] = (rev_per_cat['price'] / total_rev) * 100
top_10_rev = rev_per_cat.sort_values(by='price', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='price', y='product_category_name_english', data=top_10_rev, palette="viridis", ax=ax)
for i, (v, p) in enumerate(zip(top_10_rev.price, top_10_rev.percent)):
    ax.text(v, i, f' {p:.1f}%', va='center', fontweight='bold')
st.pyplot(fig)

# --- SECTION 5: RFM ANALYSIS ---
st.subheader("Best Customer Based on RFM Parameters")
# Karena RFM biasanya dihitung dari data keseluruhan, kita panggil rfm_df
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg Recency (days)", f"{rfm_df.recency.mean():.1f}")
with col2:
    st.metric("Avg Frequency", f"{rfm_df.frequency.mean():.2f}")
with col3:
    st.metric("Avg Monetary", f"BRL {rfm_df.monetary.mean():,.0f}")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(40, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

# Top 5 Recency
sns.barplot(y="customer_id", x="recency", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", fontsize=20)
# Top 5 Frequency
sns.barplot(y="customer_id", x="frequency", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", fontsize=20)
# Top 5 Monetary
sns.barplot(y="customer_id", x="monetary", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", fontsize=20)
st.pyplot(fig)

st.caption('Olist Performance Analyzed by Greatly Hizkia Manua')


