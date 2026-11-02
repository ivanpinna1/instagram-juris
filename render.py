#!/usr/bin/env python3
"""Gera as artes de um post (carrossel 4:5 e stories 9:16) em JPEG.

Uso: python3 render.py posts/<id>/post.json
Saída: posts/<id>/carrossel_01.jpg ... e posts/<id>/story_01.jpg ...
"""
import html, json, os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent
ASSETS = (RAIZ / "assets").as_uri()

CSS = """
@font-face{font-family:P;font-weight:400;src:url(ASSETS/fonts/poppins-latin-400-normal.woff2)}
@font-face{font-family:P;font-weight:400;font-style:italic;src:url(ASSETS/fonts/poppins-latin-400-italic.woff2)}
@font-face{font-family:P;font-weight:500;src:url(ASSETS/fonts/poppins-latin-500-normal.woff2)}
@font-face{font-family:P;font-weight:600;src:url(ASSETS/fonts/poppins-latin-600-normal.woff2)}
@font-face{font-family:P;font-weight:700;src:url(ASSETS/fonts/poppins-latin-700-normal.woff2)}
@font-face{font-family:P;font-weight:800;src:url(ASSETS/fonts/poppins-latin-800-normal.woff2)}
:root{--bg:#EEEEEE;--ink:#141414;--sub:#4a4a4a;--gold:#C8962E;--gold2:#E3A21A;--teal:#2FA3C4}
*{margin:0;padding:0;box-sizing:border-box}
body{width:WIDTHpx;height:HEIGHTpx;background:var(--bg);font-family:P,sans-serif;color:var(--ink);overflow:hidden;position:relative}
.head{position:absolute;left:0;right:0;top:0;height:HEADpx}
.logo{position:absolute;left:56px;top:46px;width:250px}
.handle{position:absolute;left:62px;top:228px;color:var(--teal);font-weight:500;font-size:30px}
.foto{position:absolute;right:20px;top:4px;height:HEADpx}
.rotulo{position:absolute;left:330px;right:290px;top:96px;text-align:center;font-weight:700;font-size:40px;line-height:1.15}
.rotulo small{display:block;font-weight:600;font-size:22px;color:var(--gold);letter-spacing:3px;margin-top:10px;text-transform:uppercase}
.linha{position:absolute;left:56px;right:56px;top:HEADpx;height:5px;background:linear-gradient(90deg,var(--gold2),var(--gold) 60%,transparent)}
.corpo{position:absolute;left:72px;right:72px;top:CORPOTOPpx;bottom:120px;display:flex;flex-direction:column;justify-content:center}
.tag{display:inline-block;align-self:flex-start;background:var(--ink);color:#fff;font-weight:600;font-size:24px;letter-spacing:3px;padding:10px 22px;border-radius:6px;margin-bottom:34px;text-transform:uppercase}
h1{font-weight:800;font-size:CAPApx;line-height:1.14;letter-spacing:-.5px}
h1 b,h2 b{color:var(--gold)}
.subt{margin-top:34px;font-size:30px;font-weight:500;color:var(--sub);border-left:6px solid var(--gold2);padding-left:20px;line-height:1.35}
h2{font-weight:700;font-size:48px;line-height:1.15;margin-bottom:34px;color:var(--ink)}
h2:before{content:"";display:block;width:70px;height:7px;border-radius:4px;background:var(--gold2);margin-bottom:22px}
p{font-size:TEXTOpx;line-height:1.5;color:#222;margin-bottom:26px;text-align:left}
p b{font-weight:700;color:#000}
blockquote{font-size:CITApx;line-height:1.45;font-weight:500;background:#fff;border-radius:18px;padding:40px 44px;border-left:10px solid var(--gold);box-shadow:0 6px 24px rgba(0,0,0,.07)}
blockquote:before{content:"\\201C";display:block;font-size:110px;line-height:.6;color:var(--gold2);font-weight:800;height:46px}
.fonte{margin-top:28px;font-size:25px;color:var(--sub);line-height:1.45}
.fonte b{color:var(--ink)}
.pe{position:absolute;left:72px;right:72px;bottom:46px;display:flex;justify-content:space-between;align-items:center;font-size:28px}
.pe .arraste{font-weight:600;color:var(--gold)}
.pe .pg{font-weight:600;color:var(--sub)}
.cta{text-align:center;align-items:center}
.cta h1{font-size:76px}
.icones{display:flex;gap:70px;justify-content:center;margin:46px 0 40px}
.icones div{text-align:center;font-weight:600;font-size:26px;color:var(--sub)}
.icones svg{width:110px;height:110px;display:block;margin:0 auto 12px}
.servicos{background:#fff;border-radius:18px;padding:32px 40px;font-size:29px;line-height:1.5;color:#222;box-shadow:0 6px 24px rgba(0,0,0,.07);text-align:center}
.servicos b{color:var(--gold)}
"""

ICONES = """<div class="icones">
<div><svg viewBox="0 0 24 24" fill="none" stroke="#C8962E" stroke-width="1.8" stroke-linejoin="round"><path d="M12 20.5s-7.5-4.6-9.2-9.3C1.6 7.8 3.9 4.5 7.3 4.5c2 0 3.6 1.1 4.7 2.7 1.1-1.6 2.7-2.7 4.7-2.7 3.4 0 5.7 3.3 4.5 6.7-1.7 4.7-9.2 9.3-9.2 9.3z"/></svg>Curta</div>
<div><svg viewBox="0 0 24 24" fill="none" stroke="#C8962E" stroke-width="1.8" stroke-linejoin="round"><path d="M6 3.5h12v17l-6-4.5-6 4.5z"/></svg>Salve</div>
<div><svg viewBox="0 0 24 24" fill="none" stroke="#C8962E" stroke-width="1.8" stroke-linejoin="round"><path d="M21.5 3.5 2.5 10l7.5 3 3 7.5z M10 13l11.5-9.5"/></svg>Compartilhe</div>
</div>"""


def md(t):
    t = html.escape(t)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t).replace("\n", "<br>")


def cabecalho(rotulo, sub):
    return (f'<div class="head"><img class="logo" src="{ASSETS}/logo.png">'
            f'<div class="handle">@ivan.pinna</div>'
            f'<div class="rotulo">{md(rotulo)}<small>{md(sub)}</small></div>'
            f'<img class="foto" src="{ASSETS}/foto.png"></div><div class="linha"></div>')


def corpo(s):
    tipo = s["tipo"]
    if tipo == "capa":
        h = f'<div class="tag">{md(s.get("tag", "Jurisprudência do TCU"))}</div><h1>{md(s["titulo"])}</h1>'
        if s.get("subtitulo"):
            h += f'<div class="subt">{md(s["subtitulo"])}</div>'
        return f'<div class="corpo">{h}</div>'
    if tipo == "texto":
        ps = "".join(f"<p>{md(p)}</p>" for p in s["paragrafos"])
        return f'<div class="corpo"><h2>{md(s["titulo"])}</h2>{ps}</div>'
    if tipo == "citacao":
        h = f'<h2>{md(s["titulo"])}</h2>' if s.get("titulo") else ""
        h += f'<blockquote>{md(s["citacao"])}</blockquote>'
        if s.get("fonte"):
            h += f'<div class="fonte">{md(s["fonte"])}</div>'
        return f'<div class="corpo">{h}</div>'
    if tipo == "cta":
        h = f'<h1>{md(s.get("titulo", "Curta, **salve** e compartilhe"))}</h1>{ICONES}'
        if s.get("texto"):
            h += f'<div class="servicos">{md(s["texto"])}</div>'
        return f'<div class="corpo cta">{h}</div>'
    raise ValueError(tipo)


def pagina(s, w, h, rotulo, sub, idx, total, story=False):
    head = 300 if not story else 330
    vals = {"WIDTH": w, "HEIGHT": h, "HEAD": head, "CORPOTOP": head + 30,
            "CAPA": s.get("tam", 68 if not story else 86), "TEXTO": s.get("tam_texto", 37 if not story else 44),
            "CITA": s.get("tam_cit", 39 if not story else 44), "ASSETS": ASSETS}
    css = CSS
    for k, v in vals.items():
        css = css.replace(k + "px" if k not in ("ASSETS",) else k, f"{v}px" if k != "ASSETS" else str(v))
    pe = ""
    if not story:
        dir_ = '<span class="arraste">Arraste para o lado →</span>' if idx < total else '<span></span>'
        pe = f'<div class="pe">{dir_}<span class="pg">{idx}/{total}</span></div>'
    else:
        pe = f'<div class="pe"><span class="arraste">{md(s.get("rodape", "Confira o post completo no feed"))}</span><span></span></div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>'
            f'{cabecalho(rotulo, sub)}{corpo(s)}{pe}</body></html>')


def render(post_json):
    post_json = Path(post_json).resolve()
    post = json.loads(post_json.read_text(encoding="utf-8"))
    out = post_json.parent
    rot, sub = post.get("rotulo", "Jurisprudência"), post.get("sub_rotulo", "TCU · Licitações")
    gerados = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, slides, (w, h), story in (("carrossel", post.get("carrossel", []), (1080, 1350), False),
                                           ("story", post.get("stories", []), (1080, 1920), True)):
            pg = b.new_page(viewport={"width": w, "height": h})
            for i, s in enumerate(slides, 1):
                tmp = out / f"_{nome}.html"
                tmp.write_text(pagina(s, w, h, rot, sub, i, len(slides), story), encoding="utf-8")
                pg.goto(tmp.as_uri()); pg.wait_for_load_state("networkidle")
                pg.evaluate("document.fonts.ready")
                over = pg.evaluate("(()=>{const c=document.querySelector('.corpo');return c.scrollHeight>c.clientHeight+2})()")
                if over:
                    print(f"AVISO: texto transborda em {nome} {i}", file=sys.stderr)
                f = out / f"{nome}_{i:02d}.jpg"
                pg.screenshot(path=str(f), type="jpeg", quality=92)
                tmp.unlink(); gerados.append(f.name)
        b.close()
    print("gerados:", ", ".join(gerados))


if __name__ == "__main__":
    render(sys.argv[1])
