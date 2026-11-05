#!/usr/bin/env python3
"""Fila editorial: escolhe os próximos acórdãos e agenda os posts gerados.

  python3 fila.py proximos <enunciados.tsv> [--n 10] [--tribunal TCU|TCE-ES]
      Lista (JSON) os próximos enunciados de licitações e contratos ainda não usados,
      do mais recente para o mais antigo, sem repetir acórdão.
  python3 fila.py agendar posts/<id> AAAA-MM-DDTHH:MM [--reel --musicas <pasta>]
      Gera as telas e agenda o carrossel (Brasília). Padrão: 1 carrossel por dia útil, às 13:00.
      Só com --reel gera também o Reel automático (música sorteada) e agenda Reel + story — desativado
      desde 05/11/2026 por baixo desempenho. Marca os acórdãos como usados.
  python3 fila.py vago
      Mostra o próximo horário livre (dia útil, 13:00) depois do último carrossel da agenda.
  python3 fila.py replanejar
      Reordena os posts ainda não publicados pelos horários reservados, do enunciado mais
      recente para o mais antigo (jurisprudência nova passa à frente).
"""
import csv, json, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
USADOS = RAIZ / "usados.json"
AGENDA = RAIZ / "agenda.json"
TEMAS = ("Licitação", "Contrato Administrativo")
TEMAS_TCE = ("LICITAÇÃO", "LICITAÇÕES E CONTRATOS", "CONTRATO ADMINISTRATIVO", "CONTRATAÇÃO", "CONCESSÃO PÚBLICA")


def carregar(p, padrao):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao


def chave(acordao, colegiado):
    return f"{acordao.strip()}|{colegiado.strip()}"


def ano(x):
    anos = re.findall(r"(?:19|20)\d\d", x["sessoes"] + " " + x["acordao"])
    return max(anos) if anos else "0"


MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
                                     "agosto", "setembro", "outubro", "novembro", "dezembro"], 1)}


def data_sessao(x):
    """Data da última sessão do enunciado, para ordenar do mais recente ao mais antigo.
    Ex.: '22, 23, 29 e 30 de setembro de 2026' -> (2026, 9, 30). Sem data legível: (0, 0, 0)."""
    t = x["sessoes"].lower().replace("º", "")
    meses = [(MESES[m], pos) for m in MESES for pos in [t.find(m)] if pos >= 0]
    anos = re.findall(r"(?:19|20)\d\d", t)
    if not meses or not anos:
        return (int(ano(x)), 0, 0)
    mes, pos = max(meses, key=lambda z: z[1])
    trecho = re.split(r";|\bde (?:" + "|".join(MESES) + r")\b", t[:pos])[-1]  # só os dias do último mês
    dias = [int(d) for d in re.findall(r"\b(\d{1,2})\b", trecho)] or [0]
    return (int(anos[-1]), mes, max(dias))


def proximos(tsv, n, tribunal="TCU"):
    """tribunal: TCU (padrão) ou sigla de tribunal de contas estadual (ex.: TCE-ES); as chaves de
    outros tribunais levam o prefixo da sigla para não colidir com os números do TCU."""
    usados = set(carregar(USADOS, {}))
    pref = "" if tribunal == "TCU" else tribunal + " "
    linhas = list(csv.DictReader(open(tsv, encoding="utf-8"), delimiter="\t"))
    vistos, saida = set(), []
    # do mais recente para o mais antigo pela data da sessão (não pela posição no arquivo):
    # enunciados novos que entrarem na base furam a fila automaticamente
    ordem = sorted(range(len(linhas)), key=lambda i: (data_sessao(linhas[i]), i), reverse=True)
    for idx in ordem:
        x = linhas[idx]
        if tribunal != "TCU" and (x.get("contexto", "").split(".")[0].strip() not in TEMAS_TCE
                                  or x.get("observacao")):
            continue  # TCE: só licitações e contratos, e nada com recurso pendente
        if tribunal == "TCU" and x["informativo"].startswith("BJ"):
            tema = re.sub(r"^\[[^\]]*\]\s*", "", x["contexto"]).split(".")[0]
            if tema not in TEMAS:
                continue
        k = pref + chave(x["acordao"], x["colegiado"])
        if pref:
            import hashlib
            k += "|" + hashlib.md5(re.sub(r"\W", "", x["enunciado"].lower())[:80].encode()).hexdigest()[:6]
        if k in usados or k in vistos or not x["acordao"].strip():
            continue
        vistos.add(k)
        saida.append({"chave": k, "linha": idx + 2, "ano": ano(x),
                      "lei_antiga": ano(x) < "2021", **{c: x[c] for c in
                      ("informativo", "sessoes", "acordao", "colegiado", "relator", "enunciado", "contexto")},
                      **{c: x[c] for c in ("fonte_completa", "ponto_atencao") if x.get(c)}})
        if len(saida) >= n:
            break
    print(json.dumps(saida, ensure_ascii=False, indent=1))


def agendar(pasta, quando, musicas=None, reel=False):
    """quando: AAAA-MM-DDTHH:MM (horário de Brasília). Com reel=True, Reel e story saem no mesmo horário."""
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    subprocess.run([sys.executable, str(RAIZ / "render.py"), str(pasta / "post.json")], check=True)
    if reel:
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
    if reel:
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


def vago(hora="13:00"):
    """Próximo dia útil (seg–sex) às `hora`, depois do último carrossel agendado e a partir de amanhã."""
    from datetime import date, timedelta
    ult = max([i["quando"][:10] for i in carregar(AGENDA, []) if i["tipo"] == "carrossel"] or ["2000-01-01"])
    d = max(date.fromisoformat(ult) + timedelta(1), date.today() + timedelta(1))
    while d.weekday() >= 5:
        d += timedelta(1)
    print(f"{d.isoformat()}T{hora}")


def replanejar(folga_min=20):
    """Redistribui os posts ainda não publicados pelos horários já reservados na agenda,
    do enunciado mais recente para o mais antigo. Assim, jurisprudência nova recém-agendada
    passa à frente dos posts antigos que ainda não saíram (nada é descartado)."""
    from datetime import datetime, timedelta, timezone
    agenda = carregar(AGENDA, [])
    publicados = carregar(RAIZ / "publicados.json", {})
    limite = datetime.now(timezone.utc) + timedelta(minutes=folga_min)
    futuros = {}
    for i in agenda:
        pid = i["id"].split(":")[0]
        if i["id"] in publicados or datetime.fromisoformat(i["quando"]) <= limite:
            futuros.pop(pid, None); futuros.setdefault("_travados", set()).add(pid); continue
        if pid not in futuros.get("_travados", set()):
            futuros.setdefault(pid, i["quando"])
    futuros.pop("_travados", None)
    if not futuros:
        print("nada a replanejar"); return
    def data_post(pid):
        f = json.loads((RAIZ / "posts" / pid / "post.json").read_text(encoding="utf-8")).get("fonte", {})
        return data_sessao({"sessoes": f.get("sessoes", ""), "acordao": f.get("acordao", "")})
    horarios = sorted(set(futuros.values()))
    ordem = sorted(futuros, key=data_post, reverse=True)
    novo = dict(zip(ordem, horarios))
    for i in agenda:
        pid = i["id"].split(":")[0]
        if pid in novo:
            i["quando"] = novo[pid]
    agenda.sort(key=lambda i: i["quando"])
    AGENDA.write_text(json.dumps(agenda, ensure_ascii=False, indent=2), encoding="utf-8")
    for pid in ordem:
        print(novo[pid][:16], pid)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "proximos":
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10
        trib = sys.argv[sys.argv.index("--tribunal") + 1] if "--tribunal" in sys.argv else "TCU"
        proximos(sys.argv[2], n, trib)
    elif cmd == "replanejar":
        replanejar()
    elif cmd == "agendar":
        mus = sys.argv[sys.argv.index("--musicas") + 1] if "--musicas" in sys.argv else None
        agendar(sys.argv[2], sys.argv[3], mus, reel="--reel" in sys.argv)
    elif cmd == "vago":
        vago()
