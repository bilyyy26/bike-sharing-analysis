import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# Konfigurasi halaman
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# ─────────────────────────────────────────────
# Load & cache data
# ─────────────────────────────────────────────
@st.cache_data
def load_day_data():
    df = pd.read_csv("main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

@st.cache_data
def load_hour_data():
    df = pd.read_csv("hour.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    yr_map     = {0: 2011, 1: 2012}
    df['season_label'] = df['season'].map(season_map)
    df['year']         = df['yr'].map(yr_map)
    return df

day_df  = load_day_data()
hour_df = load_hour_data()

# ─────────────────────────────────────────────
# Sidebar – Filter
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Sesuaikan tampilan dashboard menggunakan filter di bawah ini.")

# Filter Tanggal
st.sidebar.subheader("📅 Rentang Tanggal")
min_date = day_df['dteday'].min().date()
max_date = day_df['dteday'].max().date()

start_date = st.sidebar.date_input("Tanggal Mulai", value=min_date, min_value=min_date, max_value=max_date)
end_date   = st.sidebar.date_input("Tanggal Akhir", value=max_date, min_value=min_date, max_value=max_date)

# Filter Musim
st.sidebar.subheader("🌤️ Musim & Cuaca")
season_options  = ['All Season', 'Spring', 'Summer', 'Fall', 'Winter']
selected_season = st.sidebar.selectbox("Musim", season_options)

weather_options  = ['All Weather', 'Clear/Partly Cloudy', 'Mist/Cloudy', 'Light Rain/Snow']
selected_weather = st.sidebar.selectbox("Kondisi Cuaca", weather_options)

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard Proyek Analisis Data | Bike Sharing Dataset")

# ─────────────────────────────────────────────
# Validasi tanggal & Filter data
# ─────────────────────────────────────────────
try:
    if start_date > end_date:
        st.warning("⚠️ Tanggal mulai tidak boleh lebih besar dari tanggal akhir. Silakan sesuaikan kembali.")
        st.stop()

    filtered_df = day_df[
        (day_df['dteday'].dt.date >= start_date) &
        (day_df['dteday'].dt.date <= end_date)
    ].copy()

    if selected_season != 'All Season':
        filtered_df = filtered_df[filtered_df['season_label'] == selected_season]

    if selected_weather != 'All Weather':
        filtered_df = filtered_df[filtered_df['weather_label'] == selected_weather]

    if len(filtered_df) == 0:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")
        st.stop()

except Exception as e:
    st.error(f"Terjadi kesalahan pada filter tanggal: {e}. Pastikan start date dan end date diisi dengan lengkap.")
    st.stop()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("🚲 Bike Sharing Dashboard")
st.markdown(
    "Dashboard ini menyajikan analisis interaktif data peminjaman sepeda "
    "dari sistem **Capital Bikeshare**, Washington D.C., tahun **2011–2012**."
)
st.markdown("---")

# ─────────────────────────────────────────────
# Metrik Ringkasan
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Hari",           f"{len(filtered_df):,}")
col2.metric("Total Peminjaman",     f"{filtered_df['cnt'].sum():,}")
col3.metric("Rata-rata Harian",     f"{filtered_df['cnt'].mean():,.0f}")
col4.metric("Peminjaman Tertinggi", f"{filtered_df['cnt'].max():,}")

st.markdown("---")

# ─────────────────────────────────────────────
# Pertanyaan 1: Pengaruh Musim & Cuaca
# ─────────────────────────────────────────────
st.subheader("📊 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Peminjaman Harian")

col_left, col_right = st.columns(2)

with col_left:
    season_order  = ['Spring', 'Summer', 'Fall', 'Winter']
    weather_order = ['Clear/Partly Cloudy', 'Mist/Cloudy', 'Light Rain/Snow']
    avail_seasons = [s for s in season_order if s in filtered_df['season_label'].unique()]
    avail_weather = [w for w in weather_order if w in filtered_df['weather_label'].unique()]

    heatmap_data = (
        filtered_df[filtered_df['weather_label'].isin(avail_weather)]
        .groupby(['season_label', 'weather_label'])['cnt']
        .mean().unstack()
        .reindex(index=avail_seasons, columns=avail_weather)
    )

    fig1 = px.imshow(
        heatmap_data,
        text_auto='.0f',
        color_continuous_scale='Blues',
        title='Rata-rata Peminjaman: Musim x Kondisi Cuaca',
        labels=dict(x='Kondisi Cuaca', y='Musim', color='Rata-rata Peminjaman')
    )
    fig1.update_layout(title_font_size=13)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    season_avg = filtered_df.groupby('season_label')['cnt'].mean().reindex(avail_seasons).reset_index()
    season_avg.columns = ['Musim', 'Rata-rata']
    season_avg = season_avg.sort_values('Rata-rata', ascending=True)

    fig2 = px.bar(
        season_avg,
        x='Rata-rata',
        y='Musim',
        orientation='h',
        title='Rata-rata Peminjaman Harian per Musim',
        color='Rata-rata',
        color_continuous_scale='Blues',
        text='Rata-rata'
    )
    fig2.update_traces(texttemplate='%{text:,.0f}', textposition='inside')
    fig2.update_layout(title_font_size=13, coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

st.info(
    "**Insight:** Peminjaman tertinggi terjadi saat musim **Fall** dengan cuaca **cerah**, "
    "sedangkan terendah pada musim **Spring** dengan **hujan/salju**. "
    "Cuaca cerah secara konsisten meningkatkan jumlah peminjaman di semua musim."
)
st.markdown("---")

# ─────────────────────────────────────────────
# Pertanyaan 2: Pola Per Jam
# ─────────────────────────────────────────────
st.subheader("⏰ Pertanyaan 2: Perbandingan Distribusi Jam Sibuk – Kasual vs. Terdaftar")

try:
    hour_filtered = hour_df[
        (hour_df['dteday'].dt.date >= start_date) &
        (hour_df['dteday'].dt.date <= end_date)
    ]

    workday = hour_filtered[hour_filtered['workingday'] == 1].groupby('hr')[['casual', 'registered']].mean().reset_index()
    holiday = hour_filtered[hour_filtered['workingday'] == 0].groupby('hr')[['casual', 'registered']].mean().reset_index()

    fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         subplot_titles=('Hari Kerja (Senin-Jumat)', 'Hari Libur & Akhir Pekan'))

    # Hari kerja
    fig3.add_trace(go.Scatter(x=workday['hr'], y=workday['casual'],
                              name='Kasual (Kerja)', line=dict(color='#1565C0', width=2.5),
                              mode='lines+markers', marker=dict(size=4)), row=1, col=1)
    fig3.add_trace(go.Scatter(x=workday['hr'], y=workday['registered'],
                              name='Terdaftar (Kerja)', line=dict(color='#42A5F5', width=2.5),
                              mode='lines+markers', marker=dict(size=4)), row=1, col=1)

    # Hari libur
    fig3.add_trace(go.Scatter(x=holiday['hr'], y=holiday['casual'],
                              name='Kasual (Libur)', line=dict(color='#1565C0', width=2.5, dash='dash'),
                              mode='lines+markers', marker=dict(size=4)), row=2, col=1)
    fig3.add_trace(go.Scatter(x=holiday['hr'], y=holiday['registered'],
                              name='Terdaftar (Libur)', line=dict(color='#42A5F5', width=2.5, dash='dash'),
                              mode='lines+markers', marker=dict(size=4)), row=2, col=1)

    fig3.update_layout(
        title='Pola Aktivitas Per Jam: Kasual vs. Terdaftar',
        title_font_size=13,
        height=550,
        hovermode='x unified'
    )
    fig3.update_xaxes(title_text='Jam', tickmode='linear', tick0=0, dtick=2, row=2, col=1)
    fig3.update_yaxes(title_text='Rata-rata Peminjaman')

    st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.warning(f"Data per jam tidak dapat dimuat: {e}")

st.info(
    "**Insight:** Pengguna **terdaftar** pada hari kerja memiliki pola bimodal (08:00 & 17:00) — "
    "mencerminkan perjalanan komuter. Di hari libur, polanya bergeser ke siang hari seperti "
    "pengguna **kasual**, menandakan penggunaan rekreatif."
)
st.markdown("---")

# ─────────────────────────────────────────────
# Analisis Lanjutan: Clustering
# ─────────────────────────────────────────────
st.subheader("🔬 Analisis Lanjutan: Clustering Intensitas Penggunaan")

q1 = day_df['cnt'].quantile(0.25)
q3 = day_df['cnt'].quantile(0.75)

def usage_cluster(cnt):
    if cnt < q1:   return 'Rendah'
    elif cnt < q3: return 'Sedang'
    else:          return 'Tinggi'

filtered_df['usage_cluster'] = filtered_df['cnt'].apply(usage_cluster)

cluster_order  = ['Rendah', 'Sedang', 'Tinggi']
cluster_colors = {'Rendah': '#BBDEFB', 'Sedang': '#42A5F5', 'Tinggi': '#1565C0'}

col_a, col_b = st.columns(2)

with col_a:
    cluster_count = filtered_df['usage_cluster'].value_counts().reindex(cluster_order).fillna(0).reset_index()
    cluster_count.columns = ['Cluster', 'Jumlah']

    fig4 = px.pie(
        cluster_count,
        names='Cluster',
        values='Jumlah',
        title='Proporsi Hari per Cluster',
        color='Cluster',
        color_discrete_map=cluster_colors,
        hole=0.3
    )
    fig4.update_layout(title_font_size=13)
    st.plotly_chart(fig4, use_container_width=True)

with col_b:
    cp = filtered_df.groupby('usage_cluster')['temp_c'].mean().reindex(cluster_order).fillna(0).reset_index()
    cp.columns = ['Cluster', 'Suhu']

    fig5 = px.bar(
        cp,
        x='Cluster',
        y='Suhu',
        title='Rata-rata Suhu per Cluster',
        color='Cluster',
        color_discrete_map=cluster_colors,
        text='Suhu'
    )
    fig5.update_traces(texttemplate='%{text:.1f}°C', textposition='inside')
    fig5.update_layout(title_font_size=13, showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

st.info(
    "**Insight:** Cluster **Tinggi** berkorelasi kuat dengan suhu hangat dan musim gugur/panas. "
    "Cluster **Rendah** dominan di musim semi/dingin dengan suhu rendah. "
    "Informasi ini berguna untuk perencanaan armada sepeda berdasarkan kondisi cuaca."
)
st.markdown("---")
st.caption("Proyek Analisis Data | Bike Sharing Dataset | Capital Bikeshare Washington D.C. 2011-2012")
