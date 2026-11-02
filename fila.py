#!/usr/bin/env python3
"""Fila editorial: escolhe os próximos acórdãos e agenda os posts gerados.

  python3 fila.py proximos <enunciados.tsv> [--n 10]
      Lista (JSON) os próximos enunciados de licitações e contratos ainda não usados,
      do mais recente para o mais antigo, sem repetir acórdão.
  python3 fila.py agendar posts/<id> AAAA-MM-DD
      Renderiza o post e o põe na agenda: story "você sabia?" às 8h e carrossel às 12h
      (horário de Brasília); o story de chamada é compartilhado pelo app, com link. Marca os acórdãos como usados.
"""
import csv, json, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
USADOS = RAIZ / "usados.json"
AGENDA = RAIZ / "agenda.json"
TEMAS = ("Licitação", "Contrato Administrativo")


def carregar(p, padrao):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao


def chave(acordao, colegiado):
    return f"{acordao.strip()}|{colegiado.strip()}"


def ano(x):
    anos = re.findall(r"(?:19|20)\d\d", x["sessoes"] + " " + x["acordao"])
    return max(anos) if anos else "0"


def proximos(tsv, n):
    usados = set(carregar(USADOS, {}))
    linhas = list(csv.DictReader(open(tsv, encoding="utf-8"), delimiter="\t"))
    vistos, saida = set(), []
    for idx in range(len(linhas) - 1, -1, -1):  # o arquivo está em ordem cronológica
        x = linhas[idx]
        if x["informativo"].startswith("BJ"):
            tema = re.sub(r"^\[[^\]]*\]\s*", "", x["contexto"]).split(".")[0]
            if tema not in TEMAS:
                continue
        k = chave(x["acordao"], x["colegiado"])
        if k in usados or k in vistos or not x["acordao"].strip():
            continue
        vistos.add(k)
        saida.append({"chave": k, "linha": idx + 2, "ano": ano(x),
                      "lei_antiga": ano(x) < "2021", **{c: x[c] for c in
                      ("informativo", "sessoes", "acordao", "colegiado", "relator", "enunciado", "contexto")}})
        if len(saida) >= n:
            break
    print(json.dumps(saida, ensure_ascii=False, indent=1))


def agendar(pasta, dia):
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    subprocess.run([sys.executable, str(RAIZ / "render.py"), str(pasta / "post.json")], check=True)
    rel = pasta.resolve().relative_to(RAIZ).as_posix()
    nc, ns = len(post.get("carrossel", [])), len(post.get("stories", []))
    agenda = [i for i in carregar(AGENDA, []) if not i["id"].startswith(post["id"] + ":")]
    if ns >= 2:
        agenda.append({"id": f"{post['id']}:story-voce-sabia", "quando": f"{dia}T08:00:00-03:00",
                       "tipo": "story", "imagens": [f"{rel}/story_02.jpg"]})
    agenda.append({"id": f"{post['id']}:carrossel", "quando": f"{dia}T12:00:00-03:00", "tipo": "carrossel",
                   "imagens": [f"{rel}/carrossel_{i:02d}.jpg" for i in range(1, nc + 1)],
                   "legenda": post["legenda"]})
    agenda.sort(key=lambda i: i["quando"])
    AGENDA.write_text(json.dumps(agenda, ensure_ascii=False, indent=2), encoding="utf-8")
    usados = carregar(USADOS, {})
    for k in post.get("usa", []):
        usados[k] = post["id"]
    USADOS.write_text(json.dumps(usados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"agendado {post['id']} para {dia}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "proximos":
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10
        proximos(sys.argv[2], n)
    elif cmd == "agendar":
        agendar(sys.argv[2], sys.argv[3])
