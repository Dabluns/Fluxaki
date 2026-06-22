import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = json.load(open(r'C:\Users\Usuario\Documents\fluxaki\produtos_raw.json', encoding='utf-8'))

print(f"Total extraido: {len(p)} produtos\n")

cats  = {}
tiers = {}
for x in p:
    cats[x['cat']]   = cats.get(x['cat'], 0) + 1
    tiers[x['tier']] = tiers.get(x['tier'], 0) + 1

print("Por categoria:", cats)
print("Por tier     :", tiers)
print()
print("Amostra (primeiros 15):")
for x in p[:15]:
    nome  = x['name'][:55]
    link  = x['links'][0][:60] if x['links'] else "(sem link)"
    print(f"  [{x['id']:3}] {nome}")
    print(f"        {x['cat']} | {x['tier']} | {link}")
    print()
