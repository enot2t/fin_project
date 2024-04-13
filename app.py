# import bibl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from phik import phik_matrix
import psycopg2
from sqlalchemy import URL, create_engine, text
import streamlit as st


# connect to database
conn_str = "postgresql://enotdb_owner:zlmdgNMxH1T4@ep-raspy-recipe-a2buxdz7.eu-central-1.aws.neon.tech/enotdb?sslmode=require"
conn = create_engine(conn_str)

with conn.begin() as conn:
    query = text("""SELECT * FROM inflation""")
    df = pd.read_sql_query(query, conn)

# title
st.title("Проект: анализ зарплат в России")

# title sidebar table
st.sidebar.title("Таблица с данными")

# table
st.sidebar.dataframe(df)

st.header("Начальные показатели", anchor=None)

# start viz
col1, col2 = st.columns(2)


# Первый график - линейные графики
with col1:
    #plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x='Год', y='Инфляция')
    plt.xticks(rotation=90)
    plt.title("Динамика изменения инфляции")
    st.pyplot(plt)

# Второй график - столбчатая диаграмма инфляции
with col2:
    plt.clf()
    #plt.figure(figsize=(12, 8))
    sns.lineplot(data=df, x='Год', y='Рыболовство и рыбоводство', label='Рыболовство и рыбоводство')
    sns.lineplot(data=df, x='Год', y='Производство резиновых и пластмас', label='Производство резиновых и пластмас')
    sns.lineplot(data=df, x='Год', y='Образование', label='Образование')
    plt.title("Динамика изменения зарплаты по годам")
    plt.legend()
    plt.grid()
    st.pyplot(plt)


df['real_zp_obr'] = df['Образование'].shift(1) * ( df['Образование'] / df['Образование'].shift(1) * 100) / (100 + df['Инфляция'])
df['real_zp_fish'] = df['Рыболовство и рыбоводство'].shift(1) * ( df['Рыболовство и рыбоводство'] / df['Рыболовство и рыбоводство'].shift(1) * 100) / (100 + df['Инфляция'])
df['real_zp_gum'] = df['Производство резиновых и пластмас'].shift(1) * ( df['Производство резиновых и пластмас'] / df['Производство резиновых и пластмас'].shift(1) * 100) / (100 + df['Инфляция'])

df['%obr_inf'] = (df['real_zp_obr'] - df['Образование'].shift(1)) / df['Образование'].shift(1) * 100
df['%fish_inf'] = (df['real_zp_fish'] - df['Рыболовство и рыбоводство'].shift(1)) / df['Рыболовство и рыбоводство'].shift(1) * 100
df['%gum_inf'] = (df['real_zp_gum'] - df['Производство резиновых и пластмас'].shift(1)) / df['Производство резиновых и пластмас'].shift(1) * 100


correl = df[['%fish_inf', '%obr_inf', '%gum_inf', 'Инфляция']].phik_matrix()['Инфляция']


st.sidebar.header("Корреляция прироста зарплат по отношению к инфляции", anchor=None)

col1, col2, col3 = st.sidebar.columns(3)
# Метрики в столбцах
with col1:
    st.sidebar.metric("Рыболовство и рыбоводство", round(correl.iloc[0], 2))
with col2:
    st.sidebar.metric("Производство резиновых и пластмас", round(correl.iloc[1], 2))
with col3:
    st.sidebar.metric("Образование", round(correl.iloc[2], 2))

st.sidebar.header("Данные со средними зарплатами с учетом уровня инфляции", anchor=None)
# table with corr inflation
st.sidebar.dataframe(df)

st.header("Динамика прироста заработной платы по сравнению с предыдущим годом", anchor=None)
scol1, scol2, scol3 = st.columns(3)



with scol1:
    plt.clf()
    #plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Год', y='Инфляция', label='Инфляция')
    sns.lineplot(data=df, x='Год', y='%obr_inf', label='%obr_inf')
    plt.title(
        "Динамика приросты заработной платы по сравнению с предыдущим годом \n в соотношении с уровнем инфляции в отрасли Образование")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

with scol2:
    plt.clf()
    #plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Год', y='Инфляция', label='Инфляция')
    sns.lineplot(data=df, x='Год', y='%fish_inf', label='%fish_inf')
    plt.title(
        "Динамика прироста заработной платы по сравнению с предыдущим годом \n в соотношении с уровнем инфляции в отрасли Рыболовство и рыбоводство")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

with scol3:
    plt.clf()
    #plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Год', y='Инфляция', label='Инфляция')
    sns.lineplot(data=df, x='Год', y='%gum_inf', label='%gum_inf')
    plt.title(
        "Динамика прироста заработной платы по сравнению с предыдущим годом \n в соотношении с уровнем инфляции в отрасли Производство резиновых и пластмас")
    plt.legend()
    plt.legend()
    plt.grid()
    st.pyplot(plt)

st.header("Динамика прироста заработной платы по сравнению с предыдущим годом", anchor=None)

plt.clf()
plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='Год', y='real_zp_fish', label='Реальная зарплата "Рыболовство и рыбоводство"')
sns.lineplot(data=df, x='Год', y='real_zp_gum', label='Реальная зарплата "Производство резиновых и пластмас"')
sns.lineplot(data=df, x='Год', y='real_zp_obr', label='Реальная зарплата "Образование"')
plt.title("Динамика изменения реальных зарплат с учетом инфляции")
plt.legend()
plt.grid()
st.pyplot(plt)