import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Analisis Penjualan Interaktif", layout="wide")  
st.title("Analisis Penjualan Interaktif: Kategori, Wilayah, dan Waktu")  

# File uploader widget
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "xls", "xlsx"])

# Check if a file has been uploaded
if fl is not None:
    filename = fl.name
    st.write(f"Uploaded file: {filename}")

    try:
        # Handle CSV files
        if filename.endswith('.csv'):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
            st.write(df)

        # Handle Excel files (.xls or .xlsx)
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            # Try using the openpyxl engine for modern .xlsx files
            try:
                df = pd.read_excel(fl, engine='openpyxl')
            except Exception as e:
                # In case of error with openpyxl, try xlrd for older .xls files
                try:
                    df = pd.read_excel(fl, engine='xlrd')
                except Exception as ex:
                    st.error(f"Error loading Excel file: {ex}")
                    st.stop()

            st.write(df)
        else:
            st.error("Invalid file format. Please upload a CSV or Excel file.")
    
    except Exception as e:
        st.error(f"Error reading the file: {e}")
else:
    # Fallback: Use a default file if no file is uploaded
    os.chdir(r"/Users/annisaaalyahafiza/Downloads/bismillah visdat/code")
    try:
        df = pd.read_excel("Sample - Superstore.xls", engine='xlrd')  # Use xlrd for .xls files
        st.write(df)
    except Exception as e:
        st.error(f"Error loading default file: {e}")

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
    fig = px.pie(filtered_df, 
                 values="Sales", 
                 names="Region", 
                 hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside", 
                      marker=dict(colors=["#FAD0C9", "#F8C8D3", "#F5A7B8", "#F2C0C9"]))  # Soft Pink colors
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))

with cl1:
    with st.expander("Data Berdasarkan Kategori"):
        st.write(category_df.style.background_gradient(cmap="Pastel1"))  # Menggunakan colormap pink
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("Data Berdasarkan Wilayah"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Pastel1"))  # Menggunakan colormap pastel yang lembut
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

## Time Series Analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Analisis Berdasarkan Waktu')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()

# Membuat grafik garis dengan warna pink dan bayangan di bawahnya
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")

# Menambahkan warna pink pada garis dan bayangan di bawahnya
fig2.update_traces(line=dict(color="#F5A7B8", width=4),  # Garis warna pink soft
                   fill='tozeroy',  # Mengisi area bawah grafik dengan bayangan
                   fillcolor='rgba(245, 167, 184, 0.3)')  # Bayangan dengan warna pink lembut (transparan)

# Menampilkan grafik
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Data Berdasarkan Waktu:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a TreeMap based on Region, Category, Sub-Category
st.subheader("Tampilan Penjualan menggunakan TreeMap")
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
st.subheader("Ringkasan Penjualan Sub-Kategori Berdasarkan Bulan")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "magenta")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Pastel2_r"))

st.subheader("Melihat Data Keseluruhan")
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Pastel1"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")