import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

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
def load_data():
    df = pd.read_csv("main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

@st.cache_data
def load_hour():
    df = pd.read_csv("hour.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    season_map = {1:'Spring',2:'Summer',3:'Fall',4:'Winter'}
    yr_map     = {0:2011,1:2012}
    df['season_label'] = df['season'].map(season_map)
    df['year']         = df['yr'].map(yr_map)
    return df

day_df = load_data()

# ─────────────────────────────────────────────
# Sidebar – Filter
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Sesuaikan tampilan dashboard menggunakan filter di bawah ini.")

year_options    = sorted(day_df['year'].unique())
selected_years  = st.sidebar.multiselect("Tahun", year_options, default=year_options)

season_options  = ['Spring', 'Summer', 'Fall', 'Winter']
selected_seasons = st.sidebar.multiselect("Musim", season_options, default=season_options)

weather_options = ['Clear/Partly Cloudy', 'Mist/Cloudy', 'Light Rain/Snow']
selected_weather = st.sidebar.multiselect("Kondisi Cuaca", weather_options, default=weather_options)

filtered_df = day_df[
    (day_df['year'].isin(selected_years)) &
    (day_df['season_label'].isin(selected_seasons)) &
    (day_df['weather_label'].isin(selected_weather))
].copy()

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard Proyek Analisis Data | Bike Sharing Dataset")

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
    avail_seasons  = [s for s in season_order  if s in filtered_df['season_label'].unique()]
    avail_weather  = [w for w in weather_order if w in filtered_df['weather_label'].unique()]

    heatmap_data = (
        filtered_df[filtered_df['weather_label'].isin(avail_weather)]
        .groupby(['season_label','weather_label'])['cnt']
        .mean().unstack()
        .reindex(index=avail_seasons, columns=avail_weather)
    )
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    sns.heatmap(heatmap_data, ax=ax1, annot=True, fmt='.0f', cmap='YlOrRd',
                linewidths=0.5, cbar_kws={'label': 'Rata-rata Peminjaman'})
    ax1.set_title('Rata-rata Peminjaman: Musim x Kondisi Cuaca', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Kondisi Cuaca')
    ax1.set_ylabel('Musim')
    ax1.tick_params(axis='x', rotation=15)
    ax1.tick_params(axis='y', rotation=0)
    plt.tight_layout()
    st.pyplot(fig1)

with col_right:
    season_avg = filtered_df.groupby('season_label')['cnt'].mean().reindex(avail_seasons)
    s_colors   = {'Spring':'#4CAF50','Summer':'#FF9800','Fall':'#F44336','Winter':'#2196F3'}
    fig2, ax2  = plt.subplots(figsize=(7, 4))
    bars = ax2.bar(avail_seasons, season_avg,
                   color=[s_colors[s] for s in avail_seasons],
                   edgecolor='white', linewidth=1.2, zorder=3)
    if len(season_avg) > 0:
        max_s = season_avg.idxmax()
        min_s = season_avg.idxmin()
        for season, bar in zip(avail_seasons, bars):
            label = ''
            if season == max_s: label = 'Tertinggi'
            elif season == min_s and max_s != min_s: label = 'Terendah'
            if label:
                ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+80,
                         label, ha='center', fontsize=8, fontweight='bold', color='#333')
            ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()/2,
                     f'{season_avg[season]:,.0f}', ha='center', va='center',
                     fontsize=10, color='white', fontweight='bold')
    ax2.set_title('Rata-rata Peminjaman Harian per Musim', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Musim')
    ax2.set_ylabel('Rata-rata Peminjaman')
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{int(x):,}'))
    ax2.set_ylim(0, (season_avg.max()*1.25) if len(season_avg)>0 else 10000)
    ax2.grid(axis='y', alpha=0.5, zorder=0)
    ax2.set_axisbelow(True)
    plt.tight_layout()
    st.pyplot(fig2)

st.info(
    "**Insight:** Peminjaman tertinggi terjadi saat musim **Fall** dengan cuaca **cerah**, "
    "sedangkan terendah pada musim **Spring** dengan **hujan/salju**. "
    "Cuaca cerah secara konsisten meningkatkan jumlah peminjaman di semua musim."
)
st.markdown("---")

# ─────────────────────────────────────────────
# Pertanyaan 2: Pola Per Jam
# ─────────────────────────────────────────────
st.subheader("⏰ Pertanyaan 2: Pola Aktivitas Per Jam – Kasual vs. Terdaftar")

try:
    hour_df      = load_hour()
    hour_filtered = hour_df[hour_df['year'].isin(selected_years)]
    workday = hour_filtered[hour_filtered['workingday']==1].groupby('hr')[['casual','registered']].mean()
    holiday = hour_filtered[hour_filtered['workingday']==0].groupby('hr')[['casual','registered']].mean()

    hours       = list(range(24))
    hour_labels = [f'{h:02d}:00' for h in hours]

    fig3, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig3.suptitle('Pola Aktivitas Per Jam: Kasual vs. Terdaftar', fontsize=13, fontweight='bold')

    def plot_hourly(ax, data, title):
        ax.plot(hours, data['casual'],     color='#FF7043', linewidth=2.5,
                marker='o', markersize=3, label='Kasual')
        ax.plot(hours, data['registered'], color='#1565C0', linewidth=2.5,
                marker='s', markersize=3, label='Terdaftar')
        for col, color in [('casual','#FF7043'),('registered','#1565C0')]:
            ph = data[col].idxmax()
            pv = data[col].max()
            ax.annotate(f'{ph:02d}:00\n({pv:.0f})', xy=(ph, pv),
                        xytext=(ph+1.5, pv*0.88), fontsize=8, color=color, fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.1))
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel('Rata-rata Peminjaman', fontsize=9)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.35)
        ax.fill_between(hours, data['casual'],     alpha=0.08, color='#FF7043')
        ax.fill_between(hours, data['registered'], alpha=0.08, color='#1565C0')

    plot_hourly(axes[0], workday, 'Hari Kerja (Senin-Jumat)')
    plot_hourly(axes[1], holiday, 'Hari Libur & Akhir Pekan')
    axes[1].set_xlabel('Jam', fontsize=9)
    axes[1].set_xticks(hours[::2])
    axes[1].set_xticklabels(hour_labels[::2], rotation=45, fontsize=7)
    plt.tight_layout()
    st.pyplot(fig3)

except Exception as e:
    st.warning(f"Data per jam tidak dapat dimuat: {e}. Pastikan folder `data/` tersedia.")

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
cluster_colors = {'Rendah':'#EF5350','Sedang':'#FFA726','Tinggi':'#66BB6A'}

col_a, col_b = st.columns(2)

with col_a:
    cluster_count = filtered_df['usage_cluster'].value_counts().reindex(cluster_order).fillna(0)
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    ax4.pie(cluster_count,
            labels=cluster_order,
            colors=[cluster_colors[c] for c in cluster_order],
            autopct='%1.1f%%', startangle=140,
            wedgeprops={'edgecolor':'white','linewidth':1.5})
    ax4.set_title('Proporsi Hari per Cluster', fontsize=11, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig4)

with col_b:
    cp = filtered_df.groupby('usage_cluster')['temp_c'].mean().reindex(cluster_order).fillna(0)
    fig5, ax5 = plt.subplots(figsize=(5, 4))
    bars5 = ax5.bar(cluster_order, cp,
                    color=[cluster_colors[c] for c in cluster_order],
                    edgecolor='white', linewidth=1.2)
    for bar, val in zip(bars5, cp):
        ax5.text(bar.get_x()+bar.get_width()/2, bar.get_height()/2,
                 f'{val:.1f}°C', ha='center', va='center',
                 fontsize=11, color='white', fontweight='bold')
    ax5.set_title('Rata-rata Suhu per Cluster', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Suhu (°C)')
    ax5.set_ylim(0, (cp.max()*1.3) if cp.max()>0 else 30)
    ax5.grid(axis='y', alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig5)

st.info(
    "**Insight:** Cluster **Tinggi** berkorelasi kuat dengan suhu hangat dan musim gugur/panas. "
    "Cluster **Rendah** dominan di musim semi/dingin dengan suhu rendah. "
    "Informasi ini berguna untuk perencanaan armada sepeda berdasarkan kondisi cuaca."
)
st.markdown("---")
st.caption("Proyek Analisis Data | Bike Sharing Dataset | Capital Bikeshare Washington D.C. 2011-2012")
