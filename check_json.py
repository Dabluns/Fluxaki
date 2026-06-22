import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\Usuario\Documents\fluxaki\analise_grupos.json', encoding='utf-8') as f:
    d = json.load(f)

for grupo, info in d.items():
    topicos = info.get('topicos', {})
    total_msgs = sum(len(t['mensagens_relevantes']) for t in topicos.values())
    print(f"\nGRUPO: {grupo}")
    print(f"  Topicos encontrados: {len(topicos)}")
    print(f"  Total msgs relevantes: {total_msgs}")
    print()
    for titulo, t in topicos.items():
        n = len(t['mensagens_relevantes'])
        print(f"    [{t['id']}] {titulo}: {n} msgs")

print("\n\n--- AMOSTRA DE MENSAGENS RELEVANTES ---")
for grupo, info in d.items():
    for titulo, t in info.get('topicos', {}).items():
        msgs = t['mensagens_relevantes']
        if msgs:
            print(f"\n[{grupo}] > {titulo}")
            for m in msgs[:3]:
                print(f"  {m['data']} | links: {m['links']}")
                print(f"  {m['texto'][:200]}")
                print()
