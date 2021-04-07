import streamlit as st
import tempfile
import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np


#os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

st.set_page_config(layout="wide", initial_sidebar_state='auto')

st.title("SIMULACIÓN SISTEMA DE PUNTUACIÓN: LIGA ESPAÑOLA")


def gen_clasificacion(
    df,
    puntos_victoria=3,
    puntos_empate=1,
    coef_goles_win=0,
    coef_goles_loss=0,
    coef_goles_draw=0):

    # Def función cálculo de puntos
    def process_result(row):
        if row.FTR == 'H':
            clasi.loc[r.HomeTeam]['Puntos'] += puntos_victoria + (row.FTHG * coef_goles_win)
            clasi.loc[r.HomeTeam]['Goles_a_favor'] += row.FTHG
            clasi.loc[r.HomeTeam]['Goles_en_contra'] += row.FTAG
            clasi.loc[r.AwayTeam]['Puntos'] += row.FTAG * coef_goles_loss
            clasi.loc[r.AwayTeam]['Goles_a_favor'] += row.FTAG
            clasi.loc[r.AwayTeam]['Goles_en_contra'] += row.FTHG
        elif row.FTR == 'A':
            clasi.loc[r.HomeTeam]['Puntos'] +=  (row.FTHG * coef_goles_loss)
            clasi.loc[r.HomeTeam]['Goles_a_favor'] += row.FTHG
            clasi.loc[r.HomeTeam]['Goles_en_contra'] += row.FTAG
            clasi.loc[r.AwayTeam]['Puntos'] += puntos_victoria + (row.FTAG * coef_goles_win)
            clasi.loc[r.AwayTeam]['Goles_a_favor'] += row.FTAG
            clasi.loc[r.AwayTeam]['Goles_en_contra'] += row.FTHG
        elif row.FTR == 'D':
            clasi.loc[r.HomeTeam]['Puntos'] += puntos_empate + (row.FTHG * coef_goles_draw)
            clasi.loc[r.HomeTeam]['Goles_a_favor'] += row.FTHG
            clasi.loc[r.HomeTeam]['Goles_en_contra'] += row.FTAG
            clasi.loc[r.AwayTeam]['Puntos'] += puntos_empate + (row.FTAG * coef_goles_draw)
            clasi.loc[r.AwayTeam]['Goles_a_favor'] += row.FTAG
            clasi.loc[r.AwayTeam]['Goles_en_contra'] += row.FTHG

    # Definir e inicializar dataframe final
    clasi = None
    clasi = pd.DataFrame(columns=['Equipo','Goles_a_favor','Goles_en_contra','Puntos'])

    clasi.Equipo = df.AwayTeam.unique()
    clasi.Goles_a_favor = 0
    clasi.Goles_en_contra = 0
    clasi.Puntos = 0
    clasi.set_index('Equipo', inplace=True)

    # Procesar resultados
    for ix, r in df.iterrows():
        process_result(r)

    # Ordenar
    clasi.sort_values(by=['Puntos'], ascending=False, inplace=True)
    clasi['Posicion'] =  np.array(range(1,21))
    return clasi



def get_fig(clas):
    clas.reset_index(drop=False, inplace=True)
    colors = [['greenyellow', 'turquoise','turquoise','turquoise','turquoise',
               'white', 'white','white','white','white','white','white','white','white','white','white','white',
              'orangered','orangered','orangered']
              ]
    fig = go.Figure(data=[go.Table(
      header=dict(
        values=["<b>POSICIÓN</b>","<b>EQUIPO</b>", "<b>GOLES A FAVOR</b>", "<b>GOLES EN CONTRA</b>", "<b>PUNTOS</b>"],
        line_color='darkslategray', fill_color='lightskyblue',
        align='center', font=dict(color='black', size=11)
      ),
      cells=dict(
        values=[clas.Posicion, clas.Equipo, clas.Goles_a_favor, clas.Goles_en_contra, clas.Puntos],
        line_color=['black'], fill_color=colors,
        align='center', font=dict(color='black', size=11)
      )),
    ])

    return fig





# Add a selectbox to the sidebar:
temporada = st.sidebar.selectbox(
    'Temporada',
    ('2019-20', '2018-19', '2017-18', '2016-17', '2015-16', '2014-15', '2013-14', '2012-13', '2011-12', '2010-11'),
)

# Add a slider to the sidebar:
coef_goles_win = st.sidebar.slider(
    'Coef. goles ganador:',
    0.0, 1.0, 0.0
)
coef_goles_loss = st.sidebar.slider(
    'Coef. goles perdedor:',
    0.0, 1.0, 0.0
)
coef_goles_draw = st.sidebar.slider(
    'Coef. goles empate:',
    0.0, 1.0, 0.0
)


df = pd.read_csv(str(temporada) + '.csv',  header=0, usecols=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG','FTR'])

f1 = go.FigureWidget(get_fig(gen_clasificacion(df)))
f1.update_layout(width=700, height=900)
f2 = go.FigureWidget(get_fig(gen_clasificacion(df)))
f2.update_layout(width=700, height=900)


st.header("El menú de la izquierda te permite ajustar coeficiente multiplicadores de goles marcados por partido y las tablas te muestran la clasificación original y cómo habrían quedado con el sistema de coeficientes aplicado.")

#st.subheader('Parámetros actuales:\nPuntos por vitoria: {}, Puntos por empate: {}, Coef_ganador: {}, Coef_perdedor: {}, Coef_empate: {}'.format(puntos_win, puntos_empate, coef_goles_win, coef_goles_loss, coef_goles_draw))
st.subheader('Parámetros actuales:\nCoef_ganador: {}, Coef_perdedor: {}, Coef_empate: {}'.format(coef_goles_win, coef_goles_loss, coef_goles_draw))


with f2.batch_update():
        #clasificacion = pd.DataFrame(columns=['Equipo','Goles_a_favor','Goles_en_contra','Puntos'])
        df = pd.read_csv(str(temporada) + '.csv',  header=0, usecols=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG','FTR'])
        clasificacion = gen_clasificacion(df)
        clasificacion.reset_index(drop=False, inplace=True)

        tmp_clas = gen_clasificacion(df,
                                      coef_goles_win=float(coef_goles_win),
                                      coef_goles_loss=float(coef_goles_loss),
                                      coef_goles_draw=float(coef_goles_draw)
                                      )
        tmp_clas.reset_index(drop=False, inplace=True)
        tmp_clas.Posicion = np.array(range(1,21))

        pos_dif = [row.Posicion - clasificacion.loc[clasificacion.Equipo == row.Equipo].Posicion.values[0] for ix,row in tmp_clas.iterrows()]
        colors = [['limegreen' if p<0 else 'red' if p>0 else 'white' for p in pos_dif]]
        tmp_clas['CambioPosicion'] = ['+'+str(abs(p)) if p<0 else '-'+str(p) if p>0 else '=' for p in pos_dif]

        f2.add_traces(
            [go.Table(
          header=dict(
            values=["<b>POSICIÓN</b>","<b>CAMBIO POSICIÓN</b>","<b>EQUIPO</b>", "<b>GOLES A FAVOR</b>", "<b>GOLES EN CONTRA</b>", "<b>PUNTOS</b>"],
            line_color='darkslategray', fill_color='lightskyblue',
            align='center', font=dict(color='black', size=11)
          ),
          cells=dict(
            values=[tmp_clas.Posicion, tmp_clas.CambioPosicion, tmp_clas.Equipo, tmp_clas.Goles_a_favor, tmp_clas.Goles_en_contra, tmp_clas.Puntos],
            line_color=['black'], fill_color=colors,
            align='center', font=dict(color='black', size=11)
          ))
        ]
        )



col1, col2 = st.beta_columns([1,1])


col1.header("Clasificación Original")
col1.plotly_chart(f1, use_column_width=True)

col2.header("Clasificación Modificada")
col2.plotly_chart(f2, use_column_width=True)
st.write('Si te apetece ... échale un ojo a mi novela Operación Matrioska, disponible en amazon* :sunglasses:')
st.markdown("""<a href="https://www.amazon.es/Operacion-Matrioska-Alvaro-Botija/dp/1505512336/ref=cm_cr_arp_d_product_top?ie=UTF8">Operación Matrioska</a>""", unsafe_allow_html=True)
