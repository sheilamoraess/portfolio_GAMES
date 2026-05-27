import requests
import json

query = '''
SELECT ?developerLabel ?countryLabel WHERE {
  ?developer wdt:P31/wdt:P279* wd:Q210167. # instance of subclass of video game developer
  ?developer wdt:P17 ?country.              # country
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
'''
url = 'https://query.wikidata.org/sparql'
try:
    r = requests.get(url, params={'format': 'json', 'query': query}, headers={'User-Agent': 'SteamMarketBot/1.0'})
    r.raise_for_status()
    data = r.json()
    results = data['results']['bindings']
    print(f"Encontrados: {len(results)} desenvolvedores com pais")
    for item in results[:10]:
        print(f"{item.get('developerLabel', {}).get('value')} -> {item.get('countryLabel', {}).get('value')}")
    
    # Save a small dictionary to disk to map developers to countries
    dev_map = {}
    for item in results:
        dev = item.get('developerLabel', {}).get('value')
        country = item.get('countryLabel', {}).get('value')
        if dev and country:
            dev_map[dev] = country
            
    with open('wikidata_devs.json', 'w', encoding='utf-8') as f:
        json.dump(dev_map, f, indent=2)
except Exception as e:
    print(f'Error: {e}')
