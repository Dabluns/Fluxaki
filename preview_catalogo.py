import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
with open(r'C:\Users\Usuario\Documents\fluxaki\catalogo.json', encoding='utf-8') as f:
    p = json.load(f)
print(f"Total: {len(p)} produtos\n")
for x in p[:15]:
    print(f"[{x['id']:2}] [{x['cat']}] {x['name'][:65]}")
