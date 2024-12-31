import streamlit as st
import pandas as pd
import requests  # Import requests
import io 
import plotly.express as px
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Analisis Penjualan Interaktif", layout="wide")  
st.title("Analisis Penjualan Interaktif: Kategori, Wilayah, dan Waktu")  

# File Uploader di Streamlit
uploaded_file = st.file_uploader("Upload a file", type=["xls", "xlsx"])

if uploaded_file is not None:
    # Jika ada file yang diupload, baca file tersebut
    try:
        df = pd.read_excel(uploaded_file)
        st.write(df)
    except Exception as e:
        st.error(f"Error loading uploaded file: {e}")
else:
    # Jika tidak ada file yang diupload, gunakan file default dari GitHub
    try:
        # URL file default di GitHub (gunakan raw link untuk file)
        url = "https://github.com/anisalyahfza/Final-Project-Visdat/raw/main/Sample%20-%20Superstore.xls"
        response = requests.get(url)
        response.raise_for_status()  # Pastikan file dapat diakses
        # Membaca file .xls yang diunduh
        df = pd.read_excel(io.BytesIO(response.content), engine='xlrd')  # Gunakan engine xlrd untuk file .xls
        st.write(df)
    except Exception as e:
        st.error(f"Error loading default file from GitHub: {e}")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

##SIDEBAR CODE##
st.sidebar.header("Pilih yang Ingin Kamu Cari: ")
region = st.sidebar.multiselect("Silakan pilih Wilayah", df["Region"].unique()) # Create for Region
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Silakan pilih Provinsi", df2["State"].unique()) # Create for State
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Silakan pilih Kota",df3["City"].unique()) # Create for City

# Filter the data based on Region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

##VISUALISASI DATA
# Bar Chart
with col1:
    st.subheader("Penjualan Berdasarkan Kategori")
    # Keterangan penjelasan dengan rata kiri-kanan
    st.markdown("""
    <div style="text-align: justify;">
        Dengan grafik ini, pengguna dapat dengan mudah melihat kategori mana yang memiliki performa penjualan terbaik dan mana yang perlu perhatian lebih. 
        Ini membantu dalam pengambilan keputusan untuk mengidentifikasi produk yang paling menguntungkan dan merencanakan strategi pemasaran yang lebih efektif.
    </div>
    """, unsafe_allow_html=True)
    
    # Bar Chart
    fig = px.bar(category_df, 
                 x="Category", 
                 y="Sales", 
                 text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn", 
                 color="Category", 
                 color_discrete_sequence=["#FAD0C9", "#F8C8D3", "#F5A7B8"])  # Soft Pink colors
    st.plotly_chart(fig, use_container_width=True, height=200)

# Pie Chart
with col2:
    st.subheader("Penjualan Berdasarkan Wilayah")
    # Keterangan penjelasan dengan rata kiri-kanan
    st.markdown("""
    <div style="text-align: justify;">
        Dengan visualisasi ini, pengguna dapat dengan mudah melihat performa penjualan di setiap wilayah, mengidentifikasi area dengan penjualan tertinggi dan terendah, serta mengamati pola atau tren yang mungkin ada. Fitur ini memungkinkan Superstore Giant untuk memahami wilayah mana yang perlu diperhatikan atau ditargetkan lebih intensif untuk meningkatkan penjualan.
    </div>
    """, unsafe_allow_html=True)
    fig = px.pie(filtered_df, 
                 values="Sales", 
                 names="Region", 
                 hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside", 
                      marker=dict(colors=["#FAD0C9", "#F8C8D3", "#F5A7B8", "#F2C0C9"]))  # Soft Pink colors
    st.plotly_chart(fig, use_container_width=True)

# Penjelasan sebelum tabel
st.subheader("Melihat dan Mengunduh Data Berdasarkan Kategori dan Wilayah")
st.markdown("""
Pengguna dapat melihat data penjualan secara lengkap berdasarkan kategori dan wilayah. 
Data ini dapat diunduh dalam format CSV untuk analisis lebih lanjut. 
Pilih kategori atau wilayah untuk melihat informasi penjualan lebih detail, dan klik tombol unduh untuk menyimpan data tersebut.
""")

cl1, cl2 = st.columns((2))

# Data Berdasarkan Kategori
with cl1:
    with st.expander("Data Berdasarkan Kategori"):
        st.write(category_df.style.background_gradient(cmap="Pastel1"))  # Menggunakan colormap pink
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

# Data Berdasarkan Wilayah
with cl2:
    with st.expander("Data Berdasarkan Wilayah"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Pastel1"))  # Menggunakan colormap pastel yang lembut
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')
# Pilihan indikator di bagian utama
st.header("Pemilihan Metrik untuk Visualisasi")
st.markdown("""
Pengguna dapat memilih metrik seperti penjualan, laba, atau kuantitas untuk menyesuaikan visualisasi, seperti grafik bar.
""")
indikator = st.selectbox("Pilih indikator", ["Sales", "Quantity", "Profit"])

# Filter data berdasarkan pilihan indikator
st.subheader(f"Data Berdasarkan Indikator: {indikator}")
if indikator == "Sales":
    data_filtered = df[["Order Date", "Sales"]]
    total_value = df["Sales"].sum()
    avg_value = df["Sales"].mean()
elif indikator == "Quantity":
    data_filtered = df[["Order Date", "Quantity"]]
    total_value = df["Quantity"].sum()
    avg_value = df["Quantity"].mean()
elif indikator == "Profit":
    data_filtered = df[["Order Date", "Profit"]]
    total_value = df["Profit"].sum()
    avg_value = df["Profit"].mean()

# Tampilkan tabel data
st.dataframe(data_filtered)

# Visualisasi sederhana
st.subheader(f"Grafik {indikator} Harian")
st.line_chart(data_filtered.set_index("Order Date"))

# Menampilkan metrik terkait
st.subheader("Metrik Analisis")
st.markdown("""
<div style="text-align: justify;">
    Metrik Analisis, kode ini menampilkan dua nilai penting terkait indikator yang dipilih (Sales, Quantity, atau Profit):
    <ul>
        <li><b>Total: </b> Menunjukkan total keseluruhan dari nilai indikator yang dipilih (misalnya total penjualan, total kuantitas, atau total laba) selama periode yang dipilih.</li>
        <li><b>Rata-rata:</b> Menampilkan rata-rata harian dari indikator yang dipilih, memberikan gambaran umum tentang kinerja rata-rata indikator tersebut selama periode yang ditampilkan.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
st.metric(label="Total", value=f"{total_value:,.2f}")
st.metric(label="Rata-rata", value=f"{avg_value:,.2f}")


## Time Series Analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Analisis Berdasarkan Waktu')

# Menambahkan keterangan dengan rata kiri-kanan
st.markdown("""
<div style="text-align: justify;">
    Grafik ini menunjukkan analisis penjualan berdasarkan waktu, dengan sumbu X yang merepresentasikan bulan dan tahun (month_year) dan sumbu Y yang menggambarkan jumlah penjualan (Amount). 
    Pengguna dapat melihat tren penjualan dari waktu ke waktu, serta fluktuasi yang mungkin terjadi pada periode-periode tertentu.
    Pengguna juga dapat mengunduh grafik ini dalam format PNG dengan mengklik ikon unduh di sudut kanan atas grafik. 
    Selain itu, grafik ini mendukung berbagai interaksi seperti:
    <ul>
        <li><b>Zoom In / Zoom Out:</b> Anda dapat melakukan zoom in atau zoom out dengan mengklik dan menarik pada area grafik.</li>
        <li><b>Full Screen:</b> Klik ikon di sudut kanan atas untuk menampilkan grafik dalam mode layar penuh.</li>
        <li><b>Pan:</b> Seret grafik untuk memindahkan tampilan secara horizontal atau vertikal.</li>
        <li><b>Hover:</b> Arahkan kursor ke titik pada grafik untuk melihat detail tambahan seperti nilai penjualan pada bulan tertentu.</li>
    </ul>
    Fitur-fitur ini memungkinkan pengguna untuk menganalisis data secara lebih mendalam dan fleksibel.
</div>
""", unsafe_allow_html=True)

# Membuat line chart dengan data yang dikelompokkan berdasarkan month_year
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()

# Membuat grafik garis dengan warna pink dan bayangan di bawahnya
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")

# Menambahkan warna pink pada garis dan bayangan di bawahnya
fig2.update_traces(line=dict(color="#F5A7B8", width=4),  # Garis warna pink soft
                   fill='tozeroy',  # Mengisi area bawah grafik dengan bayangan
                   fillcolor='rgba(245, 167, 184, 0.3)')  # Bayangan dengan warna pink lembut (transparan)

# Menampilkan grafik
st.plotly_chart(fig2, use_container_width=True)

# Menambahkan subheader dan keterangan dengan markdown
st.subheader("Analisis Penjualan Berdasarkan Waktu")
st.markdown("""
    Pengguna dapat melihat data penjualan secara lengkap berdasarkan waktu, dengan data yang dibagi berdasarkan bulan dan tahun (Month-Year) serta nilai penjualan (Amount).
    Pengguna dapat melihat perubahan nilai penjualan dari waktu ke waktu untuk mengidentifikasi tren atau pola musiman yang dapat membantu dalam perencanaan bisnis.
    """)
with st.expander("Data Berdasarkan Waktu:"):
    # Menampilkan tabel dengan background gradient
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    
    # Menyiapkan data untuk diunduh
    csv = linechart.to_csv(index=False).encode("utf-8")
    
    # Tombol untuk mengunduh data
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# Create a TreeMap based on Region, Category, Sub-Category
st.subheader("Tampilan Penjualan menggunakan TreeMap")

# Keterangan penjelasan dengan rata kiri-kanan
st.markdown("""
<div style="text-align: justify;">
    Visualisasi ini menampilkan penjualan berdasarkan wilayah, kategori, dan sub-kategori dalam bentuk TreeMap. 
    Dengan menggunakan TreeMap, pengguna dapat dengan mudah memahami hubungan hierarkis antara wilayah dan kategori produk, 
    serta melihat kontribusi penjualan dari masing-masing sub-kategori. 
    Pengguna juga dapat mengunduh TreeMap ini dalam format PNG dengan mengklik ikon unduh di sudut kanan atas grafik. 
</div>
""", unsafe_allow_html=True)

# TreeMap Visualization
fig3 = px.treemap(filtered_df, 
                  path=["Region", "Category", "Sub-Category"], 
                  values="Sales", 
                  hover_data=["Sales"],
                  color="Sub-Category",  # Menyesuaikan warna berdasarkan Sub-Category
                  color_discrete_sequence=[
                      "#FAD0C9", "#F8C8D3", "#F5A7B8", "#F2C0C9", 
                      "#F5B7B1", "#F7C9D9", "#F4B3D3", "#F1A6B8", 
                      "#E5A4C1", "#DFA7BB", "#F2C4D4", "#E8A9D1"
                  ])  # Soft pink colors yang berbeda-beda

fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

import plotly.figure_factory as ff
import pandas as pd

# Menambahkan st.subheader
st.subheader("Ringkasan Penjualan Sub-Kategori Berdasarkan Bulan")

# Menambahkan penjelasan visualisasi menggunakan st.markdown
st.markdown("""
Visualisasi ini menunjukkan ringkasan penjualan berdasarkan sub-kategori produk tiap bulan. 
Tabel ini memberikan wawasan tentang kinerja penjualan setiap sub-kategori sepanjang waktu, yang berguna untuk mengidentifikasi tren dan merencanakan strategi pemasaran yang lebih efektif. 
Selain itu, **Summary Table** di bawah ini menampilkan data penting seperti *Wilayah*, *Kategori*, *Sales*, dan *Profit*, yang memudahkan analisis dan pengambilan keputusan bisnis.
""")

## Membuat expander untuk menampilkan tabel
with st.expander("View Data"):
    # Menambahkan keterangan untuk "Summary Tabel" di tengah
    st.markdown("<h3 style='text-align: center;'>Summary</h3>", unsafe_allow_html=True)
    
    # Menampilkan DataFrame pertama untuk tabel summary
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="magenta")
    st.plotly_chart(fig, use_container_width=True)

    # Menambahkan keterangan untuk "Tabel Sub-Kategori Berdasarkan Bulan" di tengah
    st.markdown("<h3 style='text-align: center;'>Tabel Sub-Kategori Berdasarkan Bulan</h3>", unsafe_allow_html=True)
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    
    # Menampilkan tabel dengan style background gradient
    st.write(sub_category_Year.style.background_gradient(cmap="Pastel2_r"))

# Menambahkan subheader dan markdown
st.subheader("Melihat Data Keseluruhan")

# Keterangan atau penjelasan menggunakan markdown
st.markdown("""
<div style="text-align: justify;">
    Di bawah ini adalah tampilan data keseluruhan yang menunjukkan beberapa kolom dari dataset yang telah difilter. 
    Anda bisa melihat data dalam jumlah terbatas untuk memahami struktur dataset. 
    Data ini bisa diunduh jika diperlukan untuk analisis lebih lanjut.
</div>
""", unsafe_allow_html=True)

# Menampilkan data dengan expander
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Pastel1"))

# Tombol untuk mengunduh DataSet
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
