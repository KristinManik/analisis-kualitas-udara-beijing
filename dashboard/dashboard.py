import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 
import numpy as np 

#Tampilan Heading halaman
st.set_page_config(
    page_title="Dashboard Kualitas Udara Beijing",
    page_icon="⛅☁️🌫️",
    layout="wide"
)

#Judul Dashboard
st.title("⛅☁️🌫️ Dashboard Analisis Kualitas Udara Beijing")
st.markdown("**Periode: 2013-2017**")
st.markdown("---")

#Load Data
@st.cache_data
def load_data():
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'main_data.csv')
    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

try:
    data = load_data()
    
    #Sidebar untuk Filter Data
    st.sidebar.header("Filter Data")
    
    # Filter Tahun
    tahun_options = sorted(data['year'].unique())
    tahun_selected = st.sidebar.multiselect(
        "Pilih Tahun:",
        options=tahun_options,
        default=tahun_options
    )
    
    # Filter Stasiun
    stasiun_options = sorted(data['station'].unique())
    stasiun_selected = st.sidebar.multiselect(
        "Pilih Stasiun:",
        options=stasiun_options,
        default=stasiun_options
    )
    
    #Filter data berdasarkan pilihan
    if tahun_selected and stasiun_selected:
        data_filtered = data[
            (data['year'].isin(tahun_selected)) &
            (data['station'].isin(stasiun_selected))
        ]
    else:
        data_filtered = data
    
    #Tampilkan info data
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Informasi Dataset")
    st.sidebar.info(f"Total data: {len(data_filtered):,} baris")
    
    # Metrik untuk Ringkasan Dataset
    st.markdown("## 📊 Ringkasan Utama")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_pm25 = data_filtered['PM2.5'].mean()
        st.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} μg/m³")
    
    with col2:
        max_pm25 = data_filtered['PM2.5'].max()
        st.metric("PM2.5 Maksimum", f"{max_pm25:.2f} μg/m³")
    
    with col3:
        min_pm25 = data_filtered['PM2.5'].min()
        st.metric("PM2.5 Minimum", f"{min_pm25:.2f} μg/m³")
    
    with col4:
        std_pm25 = data_filtered['PM2.5'].std()
        st.metric("Standar Deviasi", f"{std_pm25:.2f} μg/m³")
        
    st.markdown("---")
    
    # Visualisasi 1: PM2.5 Per Stasiun
    st.markdown("## 🏭 Perbandingan PM2.5 per Stasiun")
    
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    
    pm25_stasiun = data_filtered.groupby('station')['PM2.5'].mean().sort_values(ascending=False)
    
    colors = ['#e74c3c' if x == pm25_stasiun.max() else '#3498db' for x in pm25_stasiun.values]
    bars = ax1.barh(pm25_stasiun.index, pm25_stasiun.values, color=colors, edgecolor='black', linewidth=0.7)
    
    ax1.set_xlabel('Konsentrasi PM2.5 Rata-rata (μg/m³)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Stasiun Pemantauan', fontsize=12, fontweight='bold')
    ax1.set_title('Rata-rata Konsentrasi PM2.5 per Stasiun', fontsize=14, fontweight='bold', pad=20)
    ax1.axvline(pm25_stasiun.mean(), color='darkred', linestyle='--', linewidth=2, 
                label=f'Rata-rata: {pm25_stasiun.mean():.2f} μg/m³')
    ax1.legend()
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (idx, val) in enumerate(pm25_stasiun.items()):
        ax1.text(val + 1, i, f'{val:.2f}', va='center', fontsize=9)
    
    plt.tight_layout()
    st.pyplot(fig1)
    
    #Stasiun tertinggi dan terendah
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **Stasiun Terbersih:** {pm25_stasiun.index[-1].replace('PRSA_Data_', '').replace('_20130301-20170228.', '')} ({pm25_stasiun.values[-1]:.2f} μg/m³)")
    with col2:
        st.error(f"⚠️ **Stasiun Terpolusi:** {pm25_stasiun.index[0].replace('PRSA_Data_', '').replace('_20130301-20170228.', '')} ({pm25_stasiun.values[0]:.2f} μg/m³)")
    
    st.markdown("---")
    
    # Visualisasi 2: Tren PM2.5 per Tahun
    st.markdown("## 📈 Tren PM2.5 dari Tahun ke Tahun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        
        pm25_tahun = data_filtered.groupby('year')['PM2.5'].mean()
        
        ax2.plot(pm25_tahun.index, pm25_tahun.values, marker='o', linewidth=3,
                 markersize=10, color='#e74c3c', markeredgecolor='darkred', markeredgewidth=2)
        ax2.fill_between(pm25_tahun.index, pm25_tahun.values, alpha=0.3, color='#e74c3c')
        ax2.set_xlabel('Tahun', fontsize=12, fontweight='bold')
        ax2.set_ylabel('PM2.5 Rata-rata (μg/m³)', fontsize=12, fontweight='bold')
        ax2.set_title('Tren Konsentrasi PM2.5', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.4, linestyle="--")
        ax2.set_xticks(pm25_tahun.index)
        
        for tahun, nilai in zip(pm25_tahun.index, pm25_tahun.values):
            ax2.text(tahun, nilai + 2, f'{nilai:.1f}', ha='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig2)
    
    with col2:
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        
        rata_keseluruhan = pm25_tahun.mean()
        warna_tahun = ['#27ae60' if nilai < rata_keseluruhan else '#e74c3c' for nilai in pm25_tahun.values]
        
        bars = ax3.bar(pm25_tahun.index, pm25_tahun.values, color=warna_tahun,
                       alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.axhline(rata_keseluruhan, color='darkred', linestyle='--', linewidth=2,
                    label=f'Rata-rata: {rata_keseluruhan:.2f} μg/m³')
        ax3.set_xlabel('Tahun', fontsize=12, fontweight='bold')
        ax3.set_ylabel('PM2.5 Rata-rata (μg/m³)', fontsize=12, fontweight='bold')
        ax3.set_title('Perbandingan Tahunan', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        ax3.set_xticks(pm25_tahun.index)
        
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig3)
    
    # Info perubahan
    if len(pm25_tahun) >= 2:
        perubahan = ((pm25_tahun.iloc[-1] - pm25_tahun.iloc[0]) / pm25_tahun.iloc[0]) * 100
        if perubahan > 0:
            st.warning(f"📊 Konsentrasi PM2.5 **meningkat {perubahan:.2f}%** dari tahun {pm25_tahun.index[0]} ke {pm25_tahun.index[-1]}")
        else:
            st.success(f"📊 Konsentrasi PM2.5 **menurun {abs(perubahan):.2f}%** dari tahun {pm25_tahun.index[0]} ke {pm25_tahun.index[-1]}")
    
    st.markdown("---")
    
    # Visualisasi 3: Pola Musiman
    st.markdown("## 🌦️ Pola Musiman PM2.5")
    
    fig4, ax4 = plt.subplots(figsize=(14, 5))
    
    pm25_bulan = data_filtered.groupby('month')['PM2.5'].mean()
    bulan_nama = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']
    
    warna_bulan = ['#e74c3c' if nilai > pm25_bulan.mean() else '#3498db' for nilai in pm25_bulan.values]
    
    bars = ax4.bar(range(1, 13), pm25_bulan.values, color=warna_bulan, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    ax4.axhline(pm25_bulan.mean(), color='darkred', linestyle='--', linewidth=2, 
               label=f'Rata-rata: {pm25_bulan.mean():.2f} μg/m³')
    ax4.set_xlabel('Bulan', fontsize=12, fontweight='bold')
    ax4.set_ylabel('PM2.5 Rata-rata (μg/m³)', fontsize=12, fontweight='bold')
    ax4.set_title('Pola Musiman Konsentrasi PM2.5', fontsize=14, fontweight='bold', pad=20)
    ax4.set_xticks(range(1, 13))
    ax4.set_xticklabels(bulan_nama)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (bar, nilai) in enumerate(zip(bars, pm25_bulan.values)):
        ax4.text(bar.get_x() + bar.get_width()/2., nilai + 1.5,
                 f'{nilai:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig4)
    
    # Info bulan terburuk dan terbaik
    bulan_terburuk = pm25_bulan.idxmax()
    bulan_terbaik = pm25_bulan.idxmin()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🌡️ **Bulan dengan PM2.5 Tertinggi:** {bulan_nama[bulan_terburuk-1]} ({pm25_bulan[bulan_terburuk]:.2f} μg/m³)")
    with col2:
        st.info(f"☀️ **Bulan dengan PM2.5 Terendah:** {bulan_nama[bulan_terbaik-1]} ({pm25_bulan[bulan_terbaik]:.2f} μg/m³)")
    
    st.markdown("---")
    
    # Tabel Data
    st.markdown("## 📋 Data Detail")
    
    with st.expander("Lihat Data Ringkasan per Stasiun"):
        ringkasan = data_filtered.groupby('station').agg({
            'PM2.5': ['mean', 'median', 'std', 'min', 'max'],
            'PM10': 'mean',
            'SO2': 'mean',
            'NO2': 'mean',
            'CO': 'mean',
            'O3': 'mean'
        }).round(2)
        
        ringkasan.columns = ['PM2.5_mean', 'PM2.5_median', 'PM2.5_std', 'PM2.5_min', 'PM2.5_max', 
                            'PM10_mean', 'SO2_mean', 'NO2_mean', 'CO_mean', 'O3_mean']
        
        st.dataframe(ringkasan, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**Dashboard Analisis Kualitas Udara Beijing | Data: 2013-2017**")
    
except FileNotFoundError:
    st.error(" File 'main_data.csv' tidak ditemukan!")
    st.info("Pastikan file data sudah tersedia di folder yang sama dengan dashboard.py")
except Exception as e:

    st.error(f"Terjadi kesalahan: {str(e)}")
