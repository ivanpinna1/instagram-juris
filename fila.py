#!/usr/bin/env python3
"""Fila editorial: escolhe os próximos acórdãos e agenda os posts gerados.

  python3 fila.py proximos <enunciados.tsv> [--n 10]
      Lista (JSON) os próximos enunciados de licitações e contratos ainda não usados,
      do mais recente para o mais antigo, sem repetir acórdão.
  python3 fila.py agendar posts/<id> AAAA-MM-DDTHH:MM [--musicas <pasta>]
      Gera as telas e o Reel (música sorteada) e agenda carrossel + Reel + story (o próprio Reel) no mesmo horário
      (Brasília). Horários padrão do dia: 08:00, 13:00 e 20:00. Marca os acórdãos como usados.
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


def agendar(pasta, quando, musicas=None):
    """quando: AAAA-MM-DDTHH:MM (horário de Brasília). Carrossel e Reel saem no mesmo horário."""
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    subprocess.run([sys.executable, str(RAIZ / "render.py"), str(pasta / "post.json")], check=True)
    cmd = [sys.executable, str(RAIZ / "reel.py"), str(pasta)] + (["--musicas", musicas] if musicas else [])
    subprocess.run(cmd, check=True)
    post = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    rel = pasta.resolve().relative_to(RAIZ).as_posix()
    nc = len(post.get("carrossel", []))
    iso = f"{quando}:00-03:00"
    agenda = [i for i in carregar(AGENDA, []) if not i["id"].startswith(post["id"] + ":")]
    agenda.append({"id": f"{post['id']}:carrossel", "quando": iso, "tipo": "carrossel",
                   "imagens": [f"{rel}/carrossel_{i:02d}.jpg" for i in range(1, nc + 1)],
                   "legenda": post["legenda"]})
    agenda.append({"id": f"{post['id']}:reel", "quando": iso, "tipo": "reel",
                   "video": f"{rel}/reel.mp4", "legenda": post["legenda"]})
    agenda.append({"id": f"{post['id']}:story", "quando": iso, "tipo": "story",
                   "video": f"{rel}/reel.mp4"})
    agenda.sort(key=lambda i: i["quando"])
    AGENDA.write_text(json.dumps(agenda, ensure_ascii=False, indent=2), encoding="utf-8")
    usados = carregar(USADOS, {})
    for k in post.get("usa", []):
        usados[k] = post["id"]
    USADOS.write_text(json.dumps(usados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"agendado {post['id']} para {quando}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "proximos":
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10
        proximos(sys.argv[2], n)
    elif cmd == "agendar":
        mus = sys.argv[sys.argv.index("--musicas") + 1] if "--musicas" in sys.argv else None
        agendar(sys.argv[2], sys.argv[3], mus)
