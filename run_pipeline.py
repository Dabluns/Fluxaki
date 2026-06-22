import subprocess, sys

steps = [
    ("Minerando grupos...",      "minar_grupos.py"),
    ("Extraindo produtos...",    "extrair_produtos.py"),
    ("Filtrando qualidade...",   "filtrar_produtos.py"),
    ("Gerando catalogo...",      "gerar_catalogo.py"),
]

for label, script in steps:
    print(f"\n{'='*60}")
    print(f"▶  {label}")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, script], cwd=r"C:\Users\Usuario\Documents\fluxaki")
    if result.returncode != 0:
        print(f"\n❌ Falhou em {script}. Pipeline interrompido.")
        sys.exit(1)

print("\n" + "="*60)
print("✅ Pipeline concluído! catalogo.json atualizado.")
print("="*60)
