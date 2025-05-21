# -*- coding: utf-8 -*-
"""
Simulação com dados Argo e altimetria para analisar a relação entre altura da superfície do mar e a termoclina.
"""
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime as dtt
import matplotlib.dates as mdates
from scipy.interpolate import interp1d
import gsw

def main():
    # Abrir arquivos
    argo = nc.Dataset('B5903118_argo.nc')
    altimetro = nc.Dataset('AtlSW_CMEMS.nc')

    # Seleção de datas
    date_2015 = dtt.datetime(2015, 1, 1)
    date_2016 = dtt.datetime(2016, 12, 31)

    # Índices tempo altímetro
    t_alt_raw = altimetro['time'][:]
    idt_2015 = findate(t_alt_raw, date_2015)
    idt_2016 = findate(t_alt_raw, date_2016)
    t_alt = [dtt.date(1950, 1, 1) + dtt.timedelta(days=int(tt)) for tt in t_alt_raw[idt_2015:idt_2016]]
    t_alt = np.array(t_alt)

    # Índices tempo Argo
    t_arg_raw = argo['JULD_LOCATION'][:]
    idr_2015 = findate(t_arg_raw, date_2015)
    idr_2016 = findate(t_arg_raw, date_2016)
    t_arg = [dtt.date(1950, 1, 1) + dtt.timedelta(days=int(tt)) for tt in t_arg_raw[idr_2015:idr_2016]]
    t_arg = np.array(t_arg)

    # Variáveis principais
    lat_alt = altimetro['latitude'][:]
    lon_alt = altimetro['longitude'][:]
    lon_alt = np.where(lon_alt > 180, lon_alt - 360, lon_alt)
    sla = extrair_periodo(altimetro, 'sla', idt_2015, idt_2016)
    m_alt = np.mean(sla, axis=0)

    lat_arg = argo['LATITUDE'][idr_2015:idr_2016]
    lon_arg = argo['LONGITUDE'][idr_2015:idr_2016]
    p = argo['PRES'][idr_2015:idr_2016]
    T = argo['TEMP'][idr_2015:idr_2016]
    S = argo['PSAL'][idr_2015:idr_2016]

    ver = [6, 7, 8]
    inv = [1, 2, 12]
    i_ver = filtrar_mes(t_arg, ver)
    i_inv = filtrar_mes(t_arg, inv)
    T_ver, S_ver = T[i_ver], S[i_ver]
    T_inv, S_inv = T[i_inv], S[i_inv]

    # Hovmöller
    lat_ref = -44.875
    ilat = np.where(lat_alt == lat_ref)[0][0]
    z_hov = sla[:, ilat, :]

    # Isoterma 8ºC
    iso = [pertim(T[i], 8) for i in range(len(T))]
    p_iso = [p[i][iso[i]] for i in range(len(T))]

    # PDF único
    with PdfPages('figuras_analise_argo_altimetro.pdf') as pdf:

        # Figura 1 - Mapa com altimetria e rota
        plt.figure(figsize=(12, 8))
        x, y = np.meshgrid(lon_alt, lat_alt)
        plt.pcolormesh(x, y, m_alt, cmap='inferno')
        plt.colorbar().set_label('Altura média da superfície (m)', rotation=270)
        plt.contour(x, y, m_alt, colors='k', linewidths=0.3)
        plt.plot(lon_arg, lat_arg, 'c:', linewidth=3, label='Rota Argo (5903118)')
        plt.scatter(lon_arg[0], lat_arg[0], color='lime', label=f'{t_arg[0].strftime("%d-%b-%Y")} (Início)',
                    marker='d', s=100, zorder = 2)
        plt.legend(loc = 'upper left')
        plt.title('Média da AASM (2015-2016)', fontsize=14, fontweight='bold')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.gca().yaxis.set_major_formatter(lambda x, _: f'{abs(x)} °S')
        plt.gca().xaxis.set_major_formatter(lambda x, _: f'{abs(x)} °W')
        pdf.savefig()
        plt.close()

        # Figura 2 - TS com curvas de densidade
        plot_ts_diagram(S, T, S_ver, T_ver, S_inv, T_inv, pdf)

        # Figura 3 - Hovmöller
        plt.figure(figsize=(12, 8))
        plt.title('Diagrama de Hovmöller a -44.875°S', fontsize=14, fontweight='bold')
        plt.pcolormesh(lon_alt, t_alt, z_hov, cmap='PuOr')
        plt.colorbar().set_label('Altura da superfície (m)', rotation=270)
        plt.contour(lon_alt, t_alt, z_hov, colors='k', linewidths=0.2)
        plt.scatter(lon_arg, t_arg, color='red', label='Perfis Argo', s=10)
        plt.xlabel('Longitude')
        plt.ylabel('Data')
        plt.legend()
        plt.gca().xaxis.set_major_formatter(lambda x, _: f'{abs(x)} °W')
        plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        plt.ylim(t_alt[1], t_alt[-1])
        pdf.savefig()
        plt.close()

        
        # Figura 4 - Variação da isoterma de 8ºC e AASM interpolada na posição do Argo
        fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Subplot 1 - profundidade da isoterma de 8ºC
        axs[0].plot(t_arg, p_iso, marker='o', linestyle='-', color='darkblue')
        axs[0].invert_yaxis()
        axs[0].set_ylabel('Profundidade isoterma 8°C (m)', fontweight='bold')
        axs[0].set_title("Variação da isoterma de 8°C ao longo do tempo", fontsize=14, fontweight='bold')
        axs[0].grid(True)

        # Interpolar AASM nas posições do Argo
        sla_interp = []
        for i in range(len(t_arg)):
            time_idx = np.argmin(np.abs(t_alt - t_arg[i]))
            f_sla = interp1d(lon_alt, sla[time_idx, np.argmin(np.abs(lat_alt - lat_arg[i]))], bounds_error=False, fill_value=np.nan)
            sla_interp.append(f_sla(lon_arg[i]))

        # Subplot 2 - AASM na posição do Argo
        axs[1].plot(t_arg, sla_interp, marker='s', linestyle='-', color='firebrick')
        axs[1].set_ylabel('AASM (m)', fontweight='bold')
        axs[1].set_title("AASM na posição do Argo", fontsize=14, fontweight='bold')
        axs[1].grid(True)

        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        axs[1].set_xlabel('Data', fontweight='bold')
        fig.tight_layout()
        pdf.savefig()
        plt.close()

def findate(days_since, d_interesse):
    ref_date = dtt.datetime(1950, 1, 1)
    sp_days = (d_interesse - ref_date).days
    limite_2015 = (dtt.datetime(2015, 1, 1) - ref_date).days
    limite_2016 = (dtt.datetime(2016, 12, 31) - ref_date).days
    filtrados = np.where((days_since >= limite_2015) & (days_since <= limite_2016))[0]
    dt = np.abs(days_since[filtrados] - sp_days)
    idt = filtrados[np.argmin(dt)]
    return idt

def mes(data, meses):
    return data.month in meses

def pertim(dim, val):
    return np.where(np.abs(dim-val) == np.abs(dim-val).min())[0][0]

def extrair_periodo(dataset, var, id1, id2):
    return dataset[var][id1:id2]

def filtrar_mes(data_array, meses):
    return [idx for idx, date in enumerate(data_array) if mes(date, meses)]

def calcular_densidade(S, T, p, lon, lat):
    SA = gsw.SA_from_SP(S, p, lon, lat)
    CT = gsw.CT_from_t(SA, T, p)
    return gsw.rho(SA, CT, p)

def plot_ts_diagram(S, T, S_ver, T_ver, S_inv, T_inv, pdf):
    plt.figure(figsize=(12, 8))
    plt.title('Diagrama TS com Curvas de Densidade (Argo 5903118)', fontsize=14, fontweight='bold')
    plt.scatter(S, T, color='gray', label='Todos os dados', s=3)
    plt.scatter(S_ver, T_ver, color='red', label='Verão', s=5)
    plt.scatter(S_inv, T_inv, color='blue', label='Inverno', s=5)
    plt.xlabel('Salinidade', fontweight='bold')
    plt.ylabel('Temperatura (°C)', fontweight='bold')

    s_grid = np.linspace(33.5, 36, 100)
    t_grid = np.linspace(0, 20.5, 100)
    Sg, Tg = np.meshgrid(s_grid, t_grid)
    rho = gsw.rho(Sg, Tg, 0)
    cs = plt.contour(Sg, Tg, rho, colors='black', linewidths=0.5)
    plt.clabel(cs, fmt='%1.0f', fontsize=8)
    plt.legend()
    pdf.savefig()
    plt.close()

# Executa a função principal
main()
