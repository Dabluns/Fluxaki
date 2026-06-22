"""
Gera catalogo.json no formato exato do PRODUCTS do dashboard.
"""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ENTRADA = r"C:\Users\Usuario\Documents\fluxaki\produtos_filtrados.json"
SAIDA   = r"C:\Users\Usuario\Documents\fluxaki\catalogo.json"

PREFIXOS = [
    r'^saas\s*[-–]\s*', r'^saas[-–]', r'^-\s+', r'^–\s+',
    r'^\d{2}-\d{2}-\s*', r'^📌\s*', r'^🔗\s*', r'^👇\s*',
]

def limpar_nome(nome):
    nome = re.sub(r'\*+', '', nome).strip()
    # Remove emojis isolados no inicio
    nome = re.sub(r'^[\U0001F300-\U0001FAFF☀-➿\s]+', '', nome).strip()
    # Remove prefixos comuns que nao fazem parte do nome
    for p in PREFIXOS:
        nome = re.sub(p, '', nome, flags=re.IGNORECASE).strip()
    # Remove emojis do fim
    nome = re.sub(r'[\U0001F300-\U0001FAFF☀-➿🖥]+$', '', nome).strip()
    nome = nome.rstrip('*').strip()
    return nome[:70] if nome else None

def limpar_desc(desc):
    # Pega so as primeiras 2 linhas nao vazias, max 160 chars
    linhas = [l.strip() for l in desc.split('\n') if l.strip()]
    resumo = ' '.join(linhas[:2])
    resumo = re.sub(r'\*+', '', resumo).strip()
    return resumo[:160]

with open(ENTRADA, encoding='utf-8') as f:
    produtos = json.load(f)

catalogo = []
pulados = []
for p in produtos:
    nome = limpar_nome(p.get("name", ""))
    desc = limpar_desc(p.get("desc", ""))
    cat  = p.get("cat", "soft")

    # Descarta se nome ficou vazio, muito curto ou é só número/emoji
    if not nome or len(nome) < 5 or re.fullmatch(r'[\d\W]+', nome):
        pulados.append(p.get("name", "")[:60])
        continue

    item = {
        "id":        len(catalogo) + 1,
        "name":      nome,
        "cat":       cat,
        "tier":      p.get("tier", "free"),
        "desc":      desc,
        "icon":      cat,
        "links":     p.get("links", []),
        "downloads": 0,
        "rating":    4,
    }
    catalogo.append(item)

with open(SAIDA, "w", encoding='utf-8') as f:
    json.dump(catalogo, f, ensure_ascii=False, indent=2)

print(f"✅ {len(catalogo)} produtos → {SAIDA}")
if pulados:
    print(f"⚠️  {len(pulados)} pulados (nome inválido):")
    for x in pulados:
        print(f"   - {x}")
