"""Todo de una vez.

  python pipeline.py preparar   → busca, filtra, genera y publica (hazlo 1 vez por semana o al cambiar de zona)
  python pipeline.py enviar     → envíos del día + seguimientos + entrega a quien haya pagado (prográmalo cada día laborable a las 9:30)
  python pipeline.py todo       → las dos cosas
Añade --real para enviar de verdad (sin él, el envío es una simulación).
"""
import subprocess
import sys

PY = sys.executable
real = ["--real"] if "--real" in sys.argv else []
modo = sys.argv[1] if len(sys.argv) > 1 else "todo"

pasos = []
if modo in ("preparar", "todo"):
    pasos += [["1_buscar.py"], ["2_filtrar.py"], ["3_generar.py", "--capturas"], ["4_publicar.py"]]
if modo in ("enviar", "todo"):
    pasos += [["5_enviar.py", *real]]
    if real:
        pasos += [["6_entregar.py"]]

for p in pasos:
    print(f"\n══════ {p[0]} ══════")
    if subprocess.call([PY, *p]) != 0:
        sys.exit(f"Paró en {p[0]}")
print("\n✓ Hecho. Revisa datos/leads.csv")
