import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# ==============================
# 1. LOAD DATA
# ==============================

rfm_raw_data = pd.read_csv("dashboard/rfm_raw_data.csv")
rfm_df = pd.read_csv("dashboard/rfm_df.csv")
product_order_df = pd.read_csv("dashboard/product_order_items_orders.csv")
orders_df = pd.read_csv("dashboard/orders.csv")


# Pastikan kolom tanggal berformat datetime
datetime_cols = ["order_purchase_timestamp"]
for col in datetime_cols:
    if col in orders_df.columns:
        orders_df[col] = pd.to_datetime(orders_df[col])
    if col in product_order_df.columns:
        product_order_df[col] = pd.to_datetime(product_order_df[col])
    if col in rfm_raw_data.columns:
        rfm_raw_data[col] = pd.to_datetime(rfm_raw_data[col])

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

main_rfm_raw_data = rfm_raw_data[(rfm_raw_data["order_purchase_timestamp"] >= str(start_date)) & 
                                      (rfm_raw_data["order_purchase_timestamp"] <= str(end_date))]


# ==============================
# 3. DASHBOARD 
# ==============================
st.header('Olist E-Commerce Dashboard 2016 - 2018 :sparkles:')

# --- SECTION 1: TREND DELIVERED ---

st.subheader("Monthly Delivered Orders Trend 2016 - 2018")

# Filter: Hanya ambil status 'delivered' 
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
    color="#72BCD4", 
    linewidth=2,
    ax=ax # Plot ke object axis Streamlit
)

# 
ax.set_title("Tren jumlah order yang berhasil terkirim (delivered) tiap bulan periode 2016 - 2018", fontsize=12)
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah order terkirim")
plt.xticks(rotation=45)
ax.grid(True, linestyle='--', alpha=0.5)

# Tampilkan di Streamlit
st.pyplot(fig)

# --- SECTION 2: TOP & BOTTOM PRODUCTS ---
st.subheader( "Best and Worst Performing Product by Number of Sales")

# Menghitung total terjual per kategori
product_sales_counts = main_product_order["product_category_name_english"].value_counts().reset_index()
product_sales_counts.columns = ['product_category', 'total_sold']
top_5_products = product_sales_counts.head(5).sort_values(by="total_sold", ascending = False) # 5 KATEGORI PRODUK TERLARIS
bottom_5_products = product_sales_counts.tail(5).sort_values(by="total_sold", ascending =True) # 5 KATEGORI PRODUK KURANG DIMINATI

# Custom warna
warna = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# VISUALISASI UNTUK 5 KATEGORI PRODUK TERLARIS
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
sns.barplot(x="total_sold", y="product_category", data=top_5_products, palette=warna, ax=ax[0])
ax[0].set_title("5 Best performing product  2016 - 2018", fontsize=18)
ax[0].set_xlabel("Jumlah terjual", fontsize = 18)
ax[0].set_ylabel("Product category", fontsize = 18)
ax[0].tick_params(axis='x', labelsize=18)
ax[0].tick_params(axis='y', labelsize=18)

# VISUALISASI UNTUK 5 KATEGORI KURANG DIMINATI
sns.barplot(x="total_sold", y="product_category", data=bottom_5_products, palette=warna, ax=ax[1])
ax[1].set_title("5 Worst performing product 2016 - 2018", fontsize=18)
ax[1].set_xlabel("Jumlah terjual", fontsize=18)
ax[1].set_ylabel("Product category", fontsize = 18)
ax[1].tick_params(axis='y', labelsize=18)
ax[1].tick_params(axis='x', labelsize=18)
ax[1].invert_xaxis() 
ax[1].yaxis.set_label_position("right") 
ax[1].yaxis.tick_right()

plt.tight_layout()

st.pyplot(fig)

# --- SECTION 3: PURCHASE HOUR ---
st.subheader(" Purchase Hour Distribution")
hourly_counts = main_orders['purchase_hour'].value_counts().sort_index().reset_index()
hourly_counts.columns = ['hour', 'count']

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='hour', y='count', data=hourly_counts, color="#72BCD4", ax=ax)
ax.set_title("Jam-jam dimana customer menekan tombol beli periode 2016 - 2018", fontsize=15)
plt.ylabel("Jumlah order")
st.pyplot(fig)

# --- SECTION 4: REVENUE CONTRIBUTION ---
st.subheader("Top 10 Category by Revenue Contribution 2016 - 2018")
rev_per_cat = main_product_order.groupby('product_category_name_english')['price'].sum().reset_index()
total_rev = rev_per_cat['price'].sum()
rev_per_cat['percent'] = (rev_per_cat['price'] / total_rev) * 100
top_10_rev = rev_per_cat.sort_values(by='price', ascending=False).head(10)

colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3",  "#D3D3D3",  "#D3D3D3"]

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='price', y='product_category_name_english', data=top_10_rev, palette=colors_, ax=ax)
for i, (v, p) in enumerate(zip(top_10_rev.price, top_10_rev.percent)):
    ax.text(v, i, f' {p:.1f}%', va='center', fontweight='bold')

plt.ticklabel_format(style='plain', axis='x')
plt.xlabel('Total Revenue (BRL)', fontsize=12)
plt.ylabel('Product Category', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()

st.pyplot(fig)


# Prepare for RFM ANALYSIS
rfm_date = main_rfm_raw_data['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

main_rfm_df = main_rfm_raw_data.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": "max", # untuk recency
    "order_id": "nunique",             # frequency
    "price": "sum"                     # monetary
})

main_rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

# Menghitung recency
main_rfm_df["recency"] = (rfm_date - main_rfm_df["max_order_timestamp"]).dt.days
main_rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

# --- SECTION 5: RFM ANALYSIS ---
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg Recency (days)", f"{main_rfm_df.recency.mean():.1f}")
with col2:
    st.metric("Avg Frequency", f"{main_rfm_df.frequency.mean():.2f}")
with col3:
    st.metric("Avg Monetary", f"BRL {main_rfm_df.monetary.mean():,.0f}")

# Membuat kanvas 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#72BCD4"] * 5

# --- Mengambil 8 karakter terakhir ID agar chartnya readable ---
rfm_plot_df = main_rfm_df.copy()
rfm_plot_df['customer_id_short'] = rfm_plot_df['customer_id'].str[-8:]

# 1. Top 5 Recency
top_recency = rfm_plot_df.sort_values(by="recency", ascending=True).head(5)
sns.barplot(y="customer_id_short", x="recency", data=top_recency, palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", fontsize=30)
ax[0].set_ylabel("Customer ID (Suffix)", fontsize=25)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis='x', labelsize=20)

# 2. Top 5 Frequency
top_frequency = rfm_plot_df.sort_values(by="frequency", ascending=False).head(5)
sns.barplot(y="customer_id_short", x="frequency", data=top_frequency, palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", fontsize=30)
ax[1].set_ylabel(None) 
ax[1].set_xlabel(None)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=20)

# 3. Top 5 Monetary
top_monetary = rfm_plot_df.sort_values(by="monetary", ascending=False).head(5)
sns.barplot(y="customer_id_short", x="monetary", data=top_monetary, palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", fontsize=30)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].tick_params(axis='y', labelsize=25)
ax[2].tick_params(axis='x', labelsize=20)

# Jarak horizontal antar grafik agar teks tidak menabrak bar di sebelah
plt.subplots_adjust(wspace=0.4) 
plt.tight_layout()

st.pyplot(fig)

st.caption('Olist Performance Analyzed by Greatly Hizkia Manua')


