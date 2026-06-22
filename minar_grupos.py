"""
Fluxaki - Minerador de Grupos Telegram
Descobre topicos via reply_to_top_id e minera mensagens relevantes
"""

import asyncio
import json
import re
import os
import sys
from dotenv import load_dotenv

# Fix encoding sem quebrar os prompts interativos do Telethon
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from telethon import TelegramClient
from telethon.tl.types import MessageService

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
API_ID   = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

GRUPOS_ALVO = [
    -1002100941446,  # Apollyon - Templo de Delfos
    -1002234411125,  # CVO ATUALIZADA
    -1002128076521,  # Cangaço VIP
]

KEYWORDS = [
    "automacao","automação","crm","email","whatsapp","bot","fluxo",
    "pipeline","template","notion","zapier","make","n8n","activecampaign",
    "hubspot","planilha","lead","funil","integracao","integração","api",
    "webhook","script","download","gratis","grátis","curso","ferramenta",
    "software","ia","chatgpt","gpt","inteligencia artificial","renda",
    "vender","venda","produto","afiliado","link","acesso","saas","drive",
    "mega","dropbox","mediafire","sistema","loja","digital",
]

PASTA   = r"C:\Users\Usuario\Documents\fluxaki"
SESSION = os.path.join(PASTA, "fluxaki_session")
SAIDA   = os.path.join(PASTA, "analise_grupos.json")

def tem_keyword(texto):
    t = texto.lower()
    return any(kw in t for kw in KEYWORDS)

def extrair_links(texto):
    return re.findall(r'https?://\S+', texto)


async def descobrir_topicos(client, entity, scan_limit=3000):
    """
    Varre mensagens para encontrar todos os topic IDs únicos
    via msg.reply_to.reply_to_top_id
    """
    topicos = {}  # topic_id -> titulo (descoberto depois)
    print(f"  Varrendo {scan_limit} mensagens para descobrir topicos...")

    async for msg in client.iter_messages(entity, limit=scan_limit):
        if isinstance(msg, MessageService):
            continue
        rt = getattr(msg, 'reply_to', None)
        if rt is None:
            continue
        top_id = getattr(rt, 'reply_to_top_id', None) or getattr(rt, 'reply_to_msg_id', None)
        forum  = getattr(rt, 'forum_topic', False)
        if top_id and forum:
            topicos.setdefault(top_id, None)

    print(f"  {len(topicos)} topicos encontrados: {list(topicos.keys())}")
    return topicos


async def nomear_topico(client, entity, topic_id):
    """Tenta pegar o nome do topico pela primeira mensagem do thread."""
    try:
        msgs = await client.get_messages(entity, ids=[topic_id])
        if msgs:
            m = msgs[0] if not isinstance(msgs, list) else msgs[0]
            if m:
                # mensagem de servico tem titulo do topico
                action = getattr(m, 'action', None)
                titulo = getattr(action, 'title', None)
                if titulo:
                    return titulo
                # fallback: texto da primeira mensagem
                txt = getattr(m, 'text', '') or ''
                return txt[:60].strip() or f"topico_{topic_id}"
    except Exception:
        pass
    return f"topico_{topic_id}"


async def puxar_mensagens(client, entity, topic_id=None, limite=400):
    relevantes = []
    kwargs = {"limit": limite}
    if topic_id:
        kwargs["reply_to"] = topic_id

    async for msg in client.iter_messages(entity, **kwargs):
        if isinstance(msg, MessageService):
            continue
        texto = getattr(msg, 'text', '') or ''
        if not texto.strip():
            continue
        links = extrair_links(texto)
        if tem_keyword(texto) or links:
            relevantes.append({
                "id":    msg.id,
                "data":  str(msg.date)[:10],
                "texto": texto[:600],
                "links": links,
            })
    return relevantes


async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()
    print("\n✅ Conectado!\n" + "=" * 60)

    resultado = {}

    for grupo_id in GRUPOS_ALVO:
        try:
            entity = await client.get_entity(grupo_id)
            nome   = getattr(entity, 'title', str(grupo_id))
            print(f"\n📂 GRUPO: {nome}")
            print("-" * 60)

            resultado[nome] = {"id": grupo_id, "topicos": {}}

            # Descobrir topicos
            topicos_ids = await descobrir_topicos(client, entity, scan_limit=3000)

            if not topicos_ids:
                # Grupo simples sem forum
                print("  Sem topicos — lendo canal principal...")
                msgs = await puxar_mensagens(client, entity, limite=500)
                resultado[nome]["topicos"]["canal_principal"] = {
                    "id": None, "mensagens_relevantes": msgs
                }
                print(f"  {len(msgs)} msgs relevantes")
            else:
                for tid in topicos_ids:
                    titulo = await nomear_topico(client, entity, tid)
                    print(f"\n    ▶ [{tid}] {titulo}")
                    msgs = await puxar_mensagens(client, entity, topic_id=tid, limite=400)
                    resultado[nome]["topicos"][titulo] = {
                        "id": tid, "mensagens_relevantes": msgs
                    }
                    print(f"       {len(msgs)} msgs relevantes")

        except Exception as e:
            print(f"  ❌ Erro: {e}")

    # Salvar
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)

    print("\n" + "=" * 60)
    print(f"✅ Salvo em: {SAIDA}")

    # Resumo
    for nome, info in resultado.items():
        total = sum(len(t["mensagens_relevantes"]) for t in info["topicos"].values())
        print(f"\n  {nome}")
        print(f"  {len(info['topicos'])} topicos | {total} msgs relevantes")
        for titulo, t in info["topicos"].items():
            n = len(t["mensagens_relevantes"])
            print(f"    [{t['id']}] {titulo}: {n} msgs")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
