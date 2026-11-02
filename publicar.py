#!/usr/bin/env python3
"""Publica no Instagram (API oficial, login do Instagram) os itens vencidos da agenda.

Roda no GitHub Actions. Variáveis de ambiente:
  IG_TOKEN       token de acesso de longa duração (Secret)
  IG_USER_ID     ID da conta profissional do Instagram (Secret ou variável)
  IMG_BASE_URL   opcional; padrão: raw.githubusercontent.com/<repo>/main
  IG_API         opcional; padrão: https://graph.instagram.com
  DRY_RUN=1      só mostra o que faria

agenda.json: lista de {"id", "quando" (ISO com fuso), "tipo": "carrossel"|"story",
                       "imagens": [caminhos no repositório], "legenda" (só carrossel)}
publicados.json: {id: {"media_id", "em"}} — mantido pelo próprio script.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
API = os.environ.get("IG_API", "https://graph.instagram.com").rstrip("/")
TOKEN = os.environ.get("IG_TOKEN", "")
USER = os.environ.get("IG_USER_ID", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
BASE = os.environ.get("IMG_BASE_URL") or f"https://raw.githubusercontent.com/{REPO}/main"
DRY = os.environ.get("DRY_RUN") == "1"


def chamar(metodo, caminho, **params):
    params["access_token"] = TOKEN
    dados = urllib.parse.urlencode(params).encode()
    url = f"{API}/{caminho}"
    if metodo == "GET":
        req = urllib.request.Request(url + "?" + dados.decode())
    else:
        req = urllib.request.Request(url, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace").replace(TOKEN, "***")
        raise RuntimeError(f"{metodo} {caminho}: HTTP {e.code} {corpo}") from None


def aguardar(container):
    for _ in range(30):
        st = chamar("GET", container, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {container} com status {st}")
        time.sleep(5)
    raise RuntimeError(f"container {container} não ficou pronto a tempo")


def url_img(caminho):
    return f"{BASE}/{urllib.parse.quote(caminho)}"


def publicar(item):
    imgs = [url_img(c) for c in item["imagens"]]
    if item["tipo"] == "story":
        c = chamar("POST", f"{USER}/media", image_url=imgs[0], media_type="STORIES")["id"]
    elif len(imgs) == 1:
        c = chamar("POST", f"{USER}/media", image_url=imgs[0], caption=item.get("legenda", ""))["id"]
    else:
        filhos = []
        for u in imgs[:10]:
            f = chamar("POST", f"{USER}/media", image_url=u, is_carousel_item="true")["id"]
            aguardar(f); filhos.append(f)
        c = chamar("POST", f"{USER}/media", media_type="CAROUSEL", children=",".join(filhos),
                   caption=item.get("legenda", ""))["id"]
    aguardar(c)
    return chamar("POST", f"{USER}/media_publish", creation_id=c)["id"]


def main():
    agenda = json.loads((RAIZ / "agenda.json").read_text(encoding="utf-8"))
    pub_f = RAIZ / "publicados.json"
    publicados = json.loads(pub_f.read_text(encoding="utf-8")) if pub_f.exists() else {}
    agora = datetime.now(timezone.utc)
    vencidos = [i for i in agenda if i["id"] not in publicados
                and datetime.fromisoformat(i["quando"]) <= agora]
    vencidos.sort(key=lambda i: i["quando"])
    if not vencidos:
        print("Nada a publicar agora."); return 0
    if not DRY and not (TOKEN and USER):
        print("Faltam IG_TOKEN e/ou IG_USER_ID."); return 1
    falhas = 0
    for item in vencidos:
        print(f"→ {item['id']} ({item['tipo']}, {len(item['imagens'])} imagem(ns))")
        if DRY:
            for c in item["imagens"]:
                print("   ", url_img(c))
            continue
        try:
            mid = publicar(item)
            publicados[item["id"]] = {"media_id": mid, "em": datetime.now(timezone.utc).isoformat()}
            pub_f.write_text(json.dumps(publicados, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"   publicado: {mid}")
        except Exception as e:
            falhas += 1
            print(f"   ERRO: {e}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
