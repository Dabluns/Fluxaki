"""
Gera catalogo_slim.json — versao compacta para o npoint.io
Mantem so: id, name, cat, tier, icon, link (primeiro link limpo), downloads, rating
"""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ENTRADA = r"C:\Users\Usuario\Documents\fluxaki\catalogo.json"
SAIDA   = r"C:\Users\Usuario\Documents\fluxaki\catalogo_slim.json"

def limpar_link(url):
    # Remove artefatos colados no final da URL (markdown, emojis, linhas decorativas)
    url = re.sub(r'[\)\]\.\,]+$', '', url.strip())
    # Remove tudo após caracteres não-URL (emojis, ▬, etc.)
    url = re.split(r'[^\x00-\x7F\-\_\~\:\?\/\=\&\#\@\!\$\%\+\,\;\(\)\[\]\.]+', url)[0]
    return url.rstrip(')].,')

with open(ENTRADA, encoding='utf-8') as f:
    produtos = json.load(f)

slim = []
for p in produtos:
    links = [limpar_link(l) for l in p.get('links', []) if l.startswith('http')]
    link = links[0] if links else ''

    slim.append({
        'id':        p['id'],
        'name':      p['name'],
        'cat':       p['cat'],
        'tier':      p['tier'],
        'icon':      p['cat'],
        'link':      link,
        'downloads': 0,
        'rating':    p.get('rating', 4),
    })

with open(SAIDA, 'w', encoding='utf-8') as f:
    json.dump(slim, f, ensure_ascii=False, separators=(',', ':'))

import os
size = os.path.getsize(SAIDA)
print(f'✅ {len(slim)} produtos → {SAIDA}')
print(f'   Tamanho: {size/1024:.1f} KB')
