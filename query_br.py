import sqlite3
import pandas as pd

conn = sqlite3.connect('data/steam_games.db')
df_br = pd.read_sql_query("SELECT * FROM games WHERE country = 'Brazil'", conn)
print(f'Total de jogos do Brasil: {len(df_br)}')
if len(df_br) > 0:
    print('Gêneros mais comuns no BR:')
    print(df_br['genre'].value_counts())
    print('\nAprovação Média BR:', df_br['approval_rate'].mean())
    print('IVS Médio BR:', df_br['ivs'].mean())
    print('Preço Médio BR:', df_br['price_usd'].mean())
conn.close()
