import sqlite3
import json

conn = sqlite3.connect('data/steam_games.db')
try:
    conn.execute("ALTER TABLE games ADD COLUMN country TEXT DEFAULT 'Unknown'")
    print('Coluna country adicionada.')
except sqlite3.OperationalError:
    print('Coluna country ja existe.')

with open('wikidata_devs.json', 'r', encoding='utf-8') as f:
    dev_map = json.load(f)

cursor = conn.cursor()
cursor.execute("SELECT DISTINCT developer FROM games")
db_devs = [row[0] for row in cursor.fetchall() if row[0] != 'Unknown']

updates = []
dev_map_lower = {k.lower(): v for k, v in dev_map.items()}

for dev in db_devs:
    dev_l = dev.lower()
    if dev_l in dev_map_lower:
        updates.append((dev_map_lower[dev_l], dev))
    else:
        # Tentar match parcial se for uma empresa muito famosa
        for wiki_dev in dev_map_lower:
            if wiki_dev in dev_l and len(wiki_dev) > 4:
                updates.append((dev_map_lower[wiki_dev], dev))
                break

if updates:
    unique_updates = {dev: country for country, dev in updates}
    final_updates = [(country, dev) for dev, country in unique_updates.items()]
    
    cursor.executemany("UPDATE games SET country = ? WHERE developer = ?", final_updates)
    conn.commit()
    print(f'Enriquecimento concluido: {len(final_updates)} produtoras (e seus respectivos jogos) tiveram o pais mapeado!')
else:
    print('Nenhum match encontrado.')

cursor.execute("SELECT COUNT(*) FROM games WHERE country != 'Unknown'")
jogos_com_pais = cursor.fetchone()[0]
print(f'Total de jogos com pais mapeado no banco: {jogos_com_pais}')

# Exportar dataset de paises para o dashboard usar
import pandas as pd
df = pd.read_sql_query("SELECT country, COUNT(*) as total_jogos, AVG(approval_rate) as aprovacao, AVG(ivs) as ivs_medio FROM games WHERE country != 'Unknown' GROUP BY country ORDER BY total_jogos DESC", conn)
df.to_csv('data/processed/paises.csv', index=False)
print('Dataset paises.csv exportado para o dashboard.')

conn.close()
