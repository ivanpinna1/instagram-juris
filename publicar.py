#!/usr/bin/env python3
"""Publica no Instagram (API oficial, login do Instagram) os itens vencidos da agenda.

Roda no GitHub Actions. Variáveis de ambiente:
  IG_TOKEN       token de usuário do sistema do Meta, sem expiração (Secret)
  IG_USER_ID     ID da conta profissional do Instagram (Secret ou variável)
  IMG_BASE_URL   opcional; padrão: raw.githubusercontent.com/<repo>/main
  IG_API         opcional; padrão: https://graph.facebook.com/v26.0
  DRY_RUN=1      só mostra o que faria

agenda.json: lista de {"id", "quando" (ISO com fuso), "tipo": "carrossel"|"reel"|"story",
                       "imagens": [caminhos] ou "video": caminho (reel e story em vídeo), "legenda" (carrossel e reel)}
publicados.json: {id: {"media_id", "em"}} — mantido pelo próprio script.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
API = os.environ.get("IG_API", "https://graph.facebook.com/v26.0").rstrip("/")
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


def aguardar(container, tentativas=30):
    for _ in range(tentativas):
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
    if item["tipo"] == "reel":
        extra = {"thumb_offset": str(item["thumb_offset"])} if item.get("thumb_offset") is not None else {}
        c = chamar("POST", f"{USER}/media", media_type="REELS", video_url=url_img(item["video"]),
                   caption=item.get("legenda", ""), share_to_feed="true", **extra)["id"]
        aguardar(c, tentativas=72)  # vídeo: até 6 min de processamento
        return chamar("POST", f"{USER}/media_publish", creation_id=c)["id"]
    if item["tipo"] == "story" and item.get("video"):
        c = chamar("POST", f"{USER}/media", media_type="STORIES", video_url=url_img(item["video"]))["id"]
        aguardar(c, tentativas=72)
        return chamar("POST", f"{USER}/media_publish", creation_id=c)["id"]
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


def diagnostico():
    """Testa o token nos dois endereços da API e mostra quais contas ele enxerga (sem expor o token)."""
    print("--- diagnóstico ---")
    testes = [
        ("https://graph.facebook.com/v26.0", "me", {"fields": "id,name"}),
        ("https://graph.facebook.com/v26.0", "me/accounts", {"fields": "name,instagram_business_account{id,username}"}),
        ("https://graph.facebook.com/v26.0", USER, {"fields": "id,username"}),
        ("https://graph.instagram.com", "me", {"fields": "user_id,username,account_type"}),
        ("https://graph.instagram.com", USER, {"fields": "id,username"}),
    ]
    for base, cam, par in testes:
        par = dict(par, access_token=TOKEN)
        url = f"{base}/{cam}?" + urllib.parse.urlencode(par)
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                print("OK ", base, cam, r.read().decode()[:600])
        except urllib.error.HTTPError as e:
            print("ERR", base, cam, e.code, e.read().decode(errors="replace").replace(TOKEN, "***")[:300])


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
        arqs = item.get("imagens") or [item["video"]]
        print(f"→ {item['id']} ({item['tipo']}, {len(arqs)} arquivo(s))")
        if DRY:
            for c in arqs:
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
    if falhas:
        diagnostico()
    return 1 if falhas else 0


class _Dup:
    """Escreve a saída no terminal e em ultima_execucao.log (gravado no repositório)."""
    def __init__(self, *fs): self.fs = fs
    def write(self, t):
        t = t.replace(TOKEN, "***") if TOKEN else t
        for f in self.fs: f.write(t)
    def flush(self):
        for f in self.fs: f.flush()


if __name__ == "__main__":
    with open(RAIZ / "ultima_execucao.log", "w", encoding="utf-8") as log:
        log.write(datetime.now(timezone.utc).isoformat() + "\n")
        sys.stdout = sys.stderr = _Dup(sys.__stdout__, log)
        try:
            cod = main()
        except Exception as e:
            print("ERRO GERAL:", repr(e)); cod = 1
        print("código de saída:", cod)
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    sys.exit(cod)
