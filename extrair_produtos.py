"""
Fluxaki - Extrator de Produtos
Le o analise_grupos.json e filtra apenas mensagens com links reais
de download/acesso, estruturando no formato do catalogo.
"""

import json
import re
import os
import sys
import io
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PASTA  = r"C:\Users\Usuario\Documents\fluxaki"
ENTRADA = os.path.join(PASTA, "analise_grupos.json")
SAIDA   = os.path.join(PASTA, "produtos_raw.json")

# ── Topicos relevantes (nome exato como esta no JSON) ──────────────────
TOPICOS_RELEVANTES = {
    # TIER 1
    "CURSOS":                        {"grupo": "CVO", "cat_hint": "soft"},
    "BOTS TELEGRAM":                 {"grupo": "CVO", "cat_hint": "wa"},
    "ARQUIVOS MISTURADÃO":           {"grupo": "CVO", "cat_hint": "soft"},
    "𝘽𝙊𝙉Û𝙎 𝘾𝙑𝙊":                    {"grupo": "CVO", "cat_hint": "soft"},
    "𝙎𝙊𝙁𝙏𝙒𝘼𝙍𝙀":                      {"grupo": "CVO", "cat_hint": "soft"},
    "𝗦𝗔𝗔𝗦 𝗘 𝗦𝗖𝗥𝗜𝗣𝗧𝗦":               {"grupo": "CVO", "cat_hint": "soft"},
    "TypeBot":                       {"grupo": "CVO", "cat_hint": "wa"},
    "AI Tools":                      {"grupo": "Apollyon", "cat_hint": "ia"},
    "Vitrine Serviços":              {"grupo": "Apollyon", "cat_hint": "soft"},
    # TIER 2
    "ESTRATÉGIAS/CAIXA RÁPIDO":     {"grupo": "CVO", "cat_hint": "soft"},
    "DROPSHIPING MATERIAIS":         {"grupo": "CVO", "cat_hint": "soft"},
    "CANVA PRO":                     {"grupo": "CVO", "cat_hint": "soft"},
    "MODELOS DE COPY":               {"grupo": "CVO", "cat_hint": "email"},
    "𝘿𝙊𝘼𝙍 𝙁𝙀𝙍𝙍𝘼𝙈𝙀𝙉𝙏𝘼𝙎 𝙀 𝘾𝙐𝙍𝙎𝙊𝙎": {"grupo": "CVO", "cat_hint": "soft"},
    "EBOOS":                         {"grupo": "CVO", "cat_hint": "soft"},
    "PACK GESTOR DE TRÁFEGO":        {"grupo": "CVO", "cat_hint": "soft"},
    "Finanças":                      {"grupo": "Apollyon", "cat_hint": "soft"},
    "𝙀𝙨𝙘𝙤𝙡𝙞𝙣𝙝𝙖 𝙙𝙤 𝘼𝙯𝙖𝙯𝙚𝙡":         {"grupo": "Apollyon", "cat_hint": "soft"},
    # Cangaço VIP — grupo simples sem fórum
    "canal_principal":               {"grupo": "Cangaço VIP", "cat_hint": "soft"},
}

# ── Dominios que indicam produto/arquivo real para download ──────────
DOMINIOS_DOWNLOAD = [
    "mega.nz",
    "drive.google.com/drive",
    "drive.google.com/file",
    "dropbox.com",
    "mediafire.com",
    "github.com",
    "notion.so",
    "wetransfer.com",
    "1drv.ms",
    "onedrive.live.com",
    "sendspace.com",
]

DOMINIOS_VENDA = [
    "kiwify.com.br",
    "hotmart.com",
    "eduzz.com",
    "monetizze.com",
    "tribopay.com.br",
    "ticto.com.br",
    "pay.hotmart",
]

# Links que parecem download mas nao sao produtos uteis
DOMINIOS_IGNORAR = [
    "chat.whatsapp.com", "instagram.com", "facebook.com",
    "youtube.com", "youtu.be", "tiktok.com", "twitter.com",
    "x.com", "google.com/search", "bit.ly", "linktr.ee",
    "linkin.bio", "t.co", "t.me",           # telegram links = convites/bots
    "nudify", "adulto", "nsfw",
]

# Palavras que indicam conteudo irrelevante ou ilegal — descartar msg inteira
CONTEUDO_BANIDO = [
    "nudify", "nude", "nicho adulto", "pack adulto", "contas premium",
    "senha:", "email:", "login:", "conta gratis", "netflix gratis",
    "hbo max", "amazon prime gratis", "iptv",
    "cassino", "aposta", "igaming", "blaze",
]

# ── Palavras para inferir categoria ───────────────────────────────────
CAT_KEYWORDS = {
    "crm":   ["crm","pipeline","lead","funil","vendas","cliente","prospecção"],
    "email": ["email","e-mail","newsletter","nurturing","sequência","copy","copywriting","disparo"],
    "wa":    ["whatsapp","wpp","zap","bot","typebot","atendimento","broadcast","chatbot"],
    "ia":    ["ia","gpt","chatgpt","claude","gemini","inteligência artificial","ai","llm","prompt"],
    "soft":  ["script","saas","software","sistema","api","webhook","integração","automação",
               "automacao","zapier","make","n8n","notion","planilha","excel","ferramenta",
               "curso","ebook","e-book","pack","pacote","template","kit"],
}

def inferir_cat(texto, hint="soft"):
    t = texto.lower()
    scores = {cat: sum(1 for kw in kws if kw in t) for cat, kws in CAT_KEYWORDS.items()}
    melhor = max(scores, key=scores.get)
    return melhor if scores[melhor] > 0 else hint

def inferir_tier(texto, links):
    t = texto.lower()
    # links de venda = pro
    for l in links:
        for d in DOMINIOS_VENDA:
            if d in l:
                return "pro"
    # palavras de venda = pro
    if any(p in t for p in ["r$","reais","comprar","adquirir","pagar","valor","preço","acesso vip"]):
        return "pro"
    return "free"

def conteudo_banido(texto):
    t = texto.lower()
    return any(b in t for b in CONTEUDO_BANIDO)

def link_valido(url):
    for d in DOMINIOS_IGNORAR:
        if d in url:
            return False
    return True

def tem_link_download(links):
    for url in links:
        if not link_valido(url):
            continue
        for d in DOMINIOS_DOWNLOAD + DOMINIOS_VENDA:
            if d in url:
                return True
    return False

links_vistos = set()

def link_duplicado(links):
    """Retorna True se todos os links ja foram vistos antes."""
    chaves = tuple(sorted(links))
    if chaves in links_vistos:
        return True
    links_vistos.add(chaves)
    return False

def limpar_texto(texto):
    # Remove emojis de formatacao excessiva, limpa espacos
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

def extrair_nome(texto):
    """Tenta extrair o nome do produto da primeira linha nao vazia."""
    linhas = [l.strip() for l in texto.split('\n') if l.strip()]
    if not linhas:
        return "Produto sem nome"
    nome = linhas[0]
    # Remove emojis do inicio
    nome = re.sub(r'^[\U00010000-\U0010ffff☀-➿\U0001F300-\U0001FAFF\s]+', '', nome).strip()
    # Remove marcadores
    nome = re.sub(r'^[#\*\-\•\→\►\▶️\🔝\📦\📚\🎁\💰]+\s*', '', nome).strip()
    return nome[:80] if nome else "Produto sem nome"


def main():
    with open(ENTRADA, encoding='utf-8') as f:
        dados = json.load(f)

    produtos = []
    pid = 1
    stats = {"topicos_lidos": 0, "msgs_analisadas": 0, "produtos_extraidos": 0}

    for grupo_nome, grupo_info in dados.items():
        for topico_titulo, topico_info in grupo_info.get("topicos", {}).items():

            # Verifica se o topico esta na lista de relevantes
            match_titulo = None
            for titulo_ref in TOPICOS_RELEVANTES:
                # Comparacao flexivel (ignora espaços extras e maiusculas)
                if titulo_ref.strip().lower() in topico_titulo.strip().lower() or \
                   topico_titulo.strip().lower() in titulo_ref.strip().lower():
                    match_titulo = titulo_ref
                    break

            if not match_titulo:
                continue

            meta = TOPICOS_RELEVANTES[match_titulo]
            stats["topicos_lidos"] += 1
            print(f"\n📂 {grupo_nome} > {topico_titulo}")

            for msg in topico_info.get("mensagens_relevantes", []):
                stats["msgs_analisadas"] += 1
                texto = msg.get("texto", "")
                links = msg.get("links", [])

                # Descartar conteudo banido (ilegal/irrelevante)
                if conteudo_banido(texto):
                    continue

                # Filtrar apenas mensagens com link de download real
                links_validos = [l for l in links if link_valido(l)]
                if not tem_link_download(links_validos):
                    continue

                # Filtrar links uteis (download ou venda)
                links_uteis = [l for l in links_validos if
                               any(d in l for d in DOMINIOS_DOWNLOAD + DOMINIOS_VENDA)]

                # Descartar duplicatas pelo conjunto de links
                if link_duplicado(tuple(sorted(links_uteis))):
                    continue

                nome  = extrair_nome(texto)
                cat   = inferir_cat(texto, meta["cat_hint"])
                tier  = inferir_tier(texto, links_uteis)
                desc  = limpar_texto(texto)[:300]

                produto = {
                    "id":        pid,
                    "name":      nome,
                    "cat":       cat,
                    "icon":      cat,
                    "tier":      tier,
                    "desc":      desc,
                    "links":     links_uteis,
                    "downloads": 0,
                    "rating":    4,
                    "fonte":     f"{grupo_nome} > {topico_titulo}",
                    "data":      msg.get("data", ""),
                    "msg_id":    msg.get("id"),
                }
                produtos.append(produto)
                pid += 1
                stats["produtos_extraidos"] += 1
                print(f"  ✅ [{pid-1}] {nome[:60]} | {cat} | {tier}")

    # Salvar
    with open(SAIDA, "w", encoding='utf-8') as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"Topicos lidos:       {stats['topicos_lidos']}")
    print(f"Mensagens analisadas:{stats['msgs_analisadas']}")
    print(f"Produtos extraidos:  {stats['produtos_extraidos']}")
    print(f"\n✅ Salvo em: {SAIDA}")
    print("=" * 60)
    print("\nPROXIMO PASSO: revise produtos_raw.json e me diga quais")
    print("manter, editar ou remover antes de subir ao catalogo.")


if __name__ == "__main__":
    main()
