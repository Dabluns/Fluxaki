"""
Fluxaki - Filtro de Qualidade
Remove conteudo irrelevante/ilegal e mantem so produtos
relacionados a automacao, marketing digital e ferramentas.
"""

import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ENTRADA = r"C:\Users\Usuario\Documents\fluxaki\produtos_raw.json"
SAIDA   = r"C:\Users\Usuario\Documents\fluxaki\produtos_filtrados.json"

# ── Remover se o texto contiver qualquer um desses ───────────────────
BANLIST = [
    # Hacking / ilegal
    "hack", "cracker", "fluxion", "quebrar senha", "wi-fi", "wifi",
    "documentos editáveis", "rg,", "cpf,", "faturas", "documentos falsos",
    "petições para advogados", "arquivos jurídicos", "jurídico",
    "banco de dados intagram", "banco de dados instagram",
    "500 milhões de leads", "37 milhões de leads",
    "adicionar pessoas ao telegram",
    # Midia pirata / entretenimento
    "temporadas dublado", "temporadas", "série", "episódio",
    "vikings", "cartoon", "anime", "efeitos sonoros", "10 mil músicas",
    "trilha", "sublimação para caneca", "papercraft",
    "posters da marvel", "rifas", "painel de rifas", "refrigeração",
    # Software pirata
    "photoshop 2024", "corel draw 2024", "capcut pro apk",
    "drivers",
    # Design puro / criacao de conteudo social sem foco em automacao
    "logos editáveis", "5000 fontes", "67 mil logos",
    "imagens em alta resolução", "banco de imagem",
    "34.000 imagens pngs", "imagens pngs",
    "pack cine punch", "pack fx presents",
    "letras 3d em png", "pack de mockups",
    "mockups premium", "10,35gb de mockup",
    "kit papelaria", "capas de profissões",
    "pack artes do canva", "pack canva gospel",
    "pack 70+ de cartões",
    "pack materiais de estudo sobre refrigeração",
    "pack com 450k de estampas",
    "super pack de desenhos para photoshop",
    "pack letras",
    "livros da bíblia", "mapas mentais da biblia",
    "bible", "gospel",
    "conteúdo blackrat", "conteúdos blackrat",
    "pegar streamings", "bot youtube views",
    "mega pack hack instagram",
    "link do repertório abaixo",
    "pack de 1 gb de conteúdos [arte",
    "pack posters",
    "8gb de imagem",
    "pack free pick premium mockup",
    "paleta mágica de edição",
    # Conteudo social puro (videos tiktok/instagram sem foco em marketing)
    "conteúdo pra tiktok", "vídeos milionários",
    "pack de videos do ruyter", "pack's desing +400gb",
    "pack de edição igust", "pack de thumbnail igust",
    "mais conteúdo tiktok", "pack de fitas",
    "pack texturas", "pack emojis", "amostras de design de camiseta",
    "75 flyers", "musicas", "músicas",
    # Medicina / off-topic
    "medicina", "disciplinas para os correios",
    # Telemarketing / spam
    "37 milhões de leads",
]

# ── Manter se tiver pelo menos UM desses ────────────────────────────
ALLOWLIST = [
    # Automacao e marketing
    "automação", "automacao", "bot", "whatsapp", "wpp", "zap",
    "typebot", "type bot", "crm", "lead", "funil", "pipeline",
    "copy", "copywriting", "e-mail", "email marketing", "newsletter",
    "sequência", "campanha", "broadcast",
    # IA e ferramentas digitais
    "ia ", " ia", "gpt", "chatgpt", "claude", "prompt", "inteligência artificial",
    "ferramenta", "ferramentas", "script", "scripts",
    "saas", "sistema", "software", "api", "integração", "integracao",
    # Negócios e vendas
    "vendas", "afiliado", "tráfego", "gestor de tráfego",
    "marketing digital", "negócios", "dropshipping", "drop",
    "shopify", "fornecedor", "loja digital", "loja virtual",
    "produto digital", "renda extra", "estratégia", "kiwify",
    # Conteudo especifico do catalogo
    "typebot", "n8n", "zapier", "make.com", "notion",
    "planilha", "excel", "google sheets",
    "pagina de vendas", "página de vendas", "páginas de venda",
    "pages de venda", "elementor",
    "isca digital", "funil de vendas",
    "pack de copy", "modelos de copy", "modelo de copy",
    "pack viral", "pack milionário",
    "social media", "gestor", "tráfego pago",
    "criativo", "criativos",
    # E-commerce e web
    "loja pronta", "lojas prontas", "tema shopify", "temas shopify",
    "tema drop", "temas drop", "template", "templates",
    "cartão digital", "card digital", "quiz", "sender",
    "gerador", "contrato", "contratos",
    "plr", "empreendedor", "finanças", "renda",
    "toolkit", "http toolkit", "wa sender",
    "página", "web designer",
]

def deve_remover(nome, desc):
    texto = (nome + " " + desc).lower()
    for b in BANLIST:
        if b.lower() in texto:
            return True, b
    return False, None

def deve_manter(nome, desc):
    texto = (nome + " " + desc).lower()
    for a in ALLOWLIST:
        if a.lower() in texto:
            return True, a
    return False, None


def main():
    with open(ENTRADA, encoding='utf-8') as f:
        produtos = json.load(f)

    mantidos    = []
    removidos   = []
    sem_match   = []

    for p in produtos:
        nome = p.get("name", "")
        desc = p.get("desc", "")

        # Descartar itens cujo nome é só uma URL (sem contexto para o usuario)
        if nome.strip().startswith("http") and len(nome.strip().split()) == 1:
            removidos.append({"id": p["id"], "name": nome[:60], "motivo": "bare_url"})
            continue

        banido, motivo_ban = deve_remover(nome, desc)
        if banido:
            removidos.append({"id": p["id"], "name": nome[:60], "motivo": motivo_ban})
            continue

        relevante, motivo_allow = deve_manter(nome, desc)
        if relevante:
            mantidos.append(p)
        else:
            sem_match.append({"id": p["id"], "name": nome[:60], "cat": p.get("cat")})

    # Renumerar IDs
    for i, p in enumerate(mantidos, 1):
        p["id"] = i

    # Salvar filtrados
    with open(SAIDA, "w", encoding='utf-8') as f:
        json.dump(mantidos, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Total entrada:   {len(produtos)}")
    print(f"Mantidos:        {len(mantidos)}")
    print(f"Removidos:       {len(removidos)}")
    print(f"Sem match:       {len(sem_match)} (revisao manual)")
    print(f"\n✅ Salvo em: {SAIDA}")
    print(f"{'='*60}")

    # Mostrar o que foi mantido
    print("\n── MANTIDOS ──────────────────────────────────────────")
    for p in mantidos:
        print(f"  [{p['id']:3}] [{p['cat']}] [{p['tier']}] {p['name'][:65]}")

    # Mostrar sem match para revisao
    if sem_match:
        print(f"\n── SEM MATCH (revisar manualmente) ──────────────────")
        for x in sem_match:
            print(f"  [{x['id']:3}] [{x['cat']}] {x['name'][:65]}")

    # Resumo por categoria
    print("\n── RESUMO POR CATEGORIA ──────────────────────────────")
    cats = {}
    for p in mantidos:
        cats[p['cat']] = cats.get(p['cat'], 0) + 1
    for cat, n in sorted(cats.items()):
        print(f"  {cat:6}: {n} produtos")


if __name__ == "__main__":
    main()
