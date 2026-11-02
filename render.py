#!/usr/bin/env python3
"""Gera as artes de um post (carrossel 4:5 e stories 9:16) em JPEG.

Uso: python3 render.py posts/<id>/post.json [--tema escuro|claro]
O tema também pode vir em post.json ("tema"); padrão: escuro.
Saída: posts/<id>/carrossel_01.jpg ... e posts/<id>/story_01.jpg ...
"""
import html, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent
A = (RAIZ / "assets").as_uri()

TEMAS = {
    "escuro": """--bg:#0c0c0c;--ink:#f3efe6;--sub:#b9b2a3;--gold1:#ecd28f;--gold2:#b8862b;--gold:#d4ad5c;
      --card:rgba(255,255,255,.045);--cardline:rgba(212,173,92,.35);--line:rgba(212,173,92,.55);
      --fundo:repeating-linear-gradient(135deg,rgba(255,255,255,.028) 0 2px,transparent 2px 11px),
              radial-gradient(ellipse at 85% 95%,rgba(212,173,92,.16),transparent 55%),#0c0c0c;""",
    "claro": """--bg:#f5f1ea;--ink:#1a1a1a;--sub:#5d574d;--gold1:#c99b3e;--gold2:#8f6516;--gold:#a97c24;
      --card:#ffffff;--cardline:rgba(169,124,36,.35);--line:rgba(169,124,36,.6);
      --fundo:radial-gradient(ellipse at 85% 95%,rgba(169,124,36,.13),transparent 55%),#f5f1ea;""",
}

FONTES = "".join(
    f"@font-face{{font-family:{fam};font-weight:{w};src:url({A}/fonts/{arq}-latin-{w}-normal.woff2)}}"
    for fam, arq, ws in (("PF", "playfair-display", (600, 700, 800)), ("IN", "inter", (400, 500, 600, 700)),
                         ("CZ", "cinzel", (600, 700)))
    for w in ws)

CSS = FONTES + """
:root{TEMA}
*{margin:0;padding:0;box-sizing:border-box}
body{width:Wpx;height:Hpx;background:var(--fundo);font-family:IN,sans-serif;color:var(--ink);overflow:hidden;position:relative}
.marca{position:absolute;left:64px;top:56px;display:flex;align-items:center;gap:18px}
.marca img{height:78px}
.marca .nome{font-family:CZ;font-weight:700;font-size:34px;letter-spacing:5px;line-height:1;
  background:linear-gradient(180deg,var(--gold1),var(--gold2));-webkit-background-clip:text;color:transparent}
.marca .area{font-size:15px;letter-spacing:4.2px;color:var(--sub);margin-top:9px;font-weight:500}
.topo-dir{position:absolute;right:64px;top:74px;text-align:right;font-size:24px;color:var(--sub);font-weight:500;letter-spacing:1px}
.topo-dir b{display:block;color:var(--gold);font-family:PF;font-size:34px;letter-spacing:0}
.foto{position:absolute;right:-10px;bottom:0;height:FOTOHpx;-webkit-mask-image:linear-gradient(180deg,#000 78%,transparent 100%)}
.corpo{position:absolute;left:72px;right:72px;top:TOPOpx;bottom:BASEpx;display:flex;flex-direction:column;justify-content:JUSTIFY}
.capa .corpo{right:RCAPApx}
.tag{align-self:flex-start;border:2px solid var(--gold);color:var(--gold);font-weight:600;font-size:22px;letter-spacing:3.5px;
  padding:10px 20px;border-radius:40px;margin-bottom:36px;text-transform:uppercase}
h1{font-family:PF;font-weight:800;font-size:CAPApx;line-height:1.12;letter-spacing:-.3px}
h1 b,h2 b,blockquote b{font-weight:inherit;background:linear-gradient(180deg,var(--gold1),var(--gold2));-webkit-background-clip:text;color:transparent}
.subt{max-width:520px;margin-top:36px;font-size:28px;font-weight:500;color:var(--sub);line-height:1.4;padding-left:22px;border-left:4px solid var(--gold)}
.num{font-family:PF;font-weight:700;font-size:30px;color:var(--gold);letter-spacing:2px;margin-bottom:14px}
h2{font-family:PF;font-weight:700;font-size:60px;line-height:1.12;margin-bottom:40px}
p{font-size:TEXTOpx;line-height:1.52;color:var(--ink);margin-bottom:28px;opacity:.93}
p b{font-weight:700;color:var(--gold)}
.aspas{font-family:PF;font-weight:800;font-size:220px;line-height:.55;height:96px;
  background:linear-gradient(180deg,var(--gold1),var(--gold2));-webkit-background-clip:text;color:transparent}
blockquote{font-family:PF;font-weight:600;font-size:CITApx;line-height:1.38;padding:6px 0 0 0}
.fonte{margin-top:40px;padding-top:26px;border-top:2px solid var(--line);font-size:25px;color:var(--sub);line-height:1.5}
.fonte b{color:var(--ink);font-weight:600}
.pe{position:absolute;left:72px;right:72px;bottom:54px;display:flex;justify-content:space-between;align-items:center;
  font-size:24px;color:var(--sub);font-weight:500;letter-spacing:1px}
.pe .seta{color:var(--gold);font-weight:600;letter-spacing:2px;text-transform:uppercase;font-size:22px}
.filete{position:absolute;left:72px;right:72px;bottom:110px;height:2px;background:linear-gradient(90deg,var(--line),transparent)}
.icones{display:flex;gap:56px;margin:44px 0 46px}
.icones div{text-align:center;font-weight:600;font-size:22px;color:var(--sub);letter-spacing:2px;text-transform:uppercase}
.icones svg{width:96px;height:96px;display:block;margin:0 auto 12px}
.servicos{font-size:27px;line-height:1.5;color:var(--sub);max-width:600px}
.servicos b{color:var(--gold);font-weight:600}
"""

ICONES = """<div class="icones">
<div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="color:var(--gold)" stroke-width="1.6" stroke-linejoin="round"><path d="M12 20.5s-7.5-4.6-9.2-9.3C1.6 7.8 3.9 4.5 7.3 4.5c2 0 3.6 1.1 4.7 2.7 1.1-1.6 2.7-2.7 4.7-2.7 3.4 0 5.7 3.3 4.5 6.7-1.7 4.7-9.2 9.3-9.2 9.3z"/></svg>Curta</div>
<div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="color:var(--gold)" stroke-width="1.6" stroke-linejoin="round"><path d="M6 3.5h12v17l-6-4.5-6 4.5z"/></svg>Salve</div>
<div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="color:var(--gold)" stroke-width="1.6" stroke-linejoin="round"><path d="M21.5 3.5 2.5 10l7.5 3 3 7.5z M10 13l11.5-9.5"/></svg>Compartilhe</div>
</div>"""


def md(t):
    t = html.escape(t)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t).replace("\n", "<br>")


def slide(s, w, h, tema, idx, total, story):
    tipo = s["tipo"]
    com_foto = tipo in ("capa", "cta")
    v = {"W": w, "H": h, "TOPO": 230 if not story else 300,
         "BASE": (150 if not story else 200) if not com_foto else (560 if not story else 900),
         "JUSTIFY": "center" if not com_foto else "flex-start",
         "FOTOH": 640 if not story else 980, "RCAPA": 72,
         "CAPA": s.get("tam", 74 if not story else 84), "TEXTO": s.get("tam_texto", 36 if not story else 44),
         "CITA": s.get("tam_cit", 44 if not story else 52)}
    if com_foto:
        v["TOPO"] = 220 if not story else 300
        v["BASE"] = 130 if not story else 200
        v["RCAPA"] = 72
    css = CSS.replace("TEMA", TEMAS[tema])
    for k in ("FOTOH", "TOPO", "BASE", "RCAPA", "CAPA", "TEXTO", "CITA", "W", "H"):
        css = css.replace(f"{k}px", f"{v[k]}px")
    css = css.replace("JUSTIFY", v["JUSTIFY"])

    marca = (f'<div class="marca"><img src="{A}/brasao.png"><div><div class="nome">IVAN PINNA</div>'
             f'<div class="area">LICITAÇÕES E CONTRATOS</div></div></div>')
    dir_ = (f'<div class="topo-dir"><b>{idx:02d}/{total:02d}</b>@ivan.pinna</div>' if not story
            else '<div class="topo-dir">@ivan.pinna</div>')
    foto = f'<img class="foto" src="{A}/foto_recorte.png">' if com_foto else ""

    if tipo == "capa":
        c = f'<div class="tag">{md(s.get("tag", "Jurisprudência do TCU"))}</div><h1>{md(s["titulo"])}</h1>'
        if s.get("subtitulo"):
            c += f'<div class="subt">{md(s["subtitulo"])}</div>'
    elif tipo == "texto":
        c = (f'<div class="num">{s.get("num", "")}</div>' if s.get("num") else "") + f'<h2>{md(s["titulo"])}</h2>'
        c += "".join(f"<p>{md(p)}</p>" for p in s["paragrafos"])
    elif tipo == "citacao":
        c = f'<div class="num">{md(s["titulo"])}</div>' if s.get("titulo") else ""
        c += f'<div class="aspas">“</div><blockquote>{md(s["citacao"])}</blockquote>'
        if s.get("fonte"):
            c += f'<div class="fonte">{md(s["fonte"])}</div>'
    elif tipo == "cta":
        c = f'<h1>{md(s.get("titulo", "Curta, **salve** e compartilhe"))}</h1>{ICONES}'
        if s.get("texto"):
            c += f'<div class="servicos">{md(s["texto"])}</div>'
    else:
        raise ValueError(tipo)

    if story:
        pe = f'<div class="pe"><span class="seta">{md(s.get("rodape", "Post completo no feed"))}</span><span></span></div>'
    elif idx < total:
        pe = '<div class="filete"></div><div class="pe"><span>Jurisprudência comentada</span><span class="seta">Arraste →</span></div>'
    else:
        pe = ""
    if com_foto and not story and idx < total:
        pe = '<div class="pe"><span class="seta">Arraste para o lado →</span><span></span></div>'
    cls = "capa" if com_foto else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body class="{cls}">{foto}{marca}{dir_}<div class="corpo">{c}</div>{pe}</body></html>')


def render(post_json, tema=None):
    post_json = Path(post_json).resolve()
    post = json.loads(post_json.read_text(encoding="utf-8"))
    tema = tema or post.get("tema", "escuro")
    out = post_json.parent
    gerados = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, slides, (w, h), story in (("carrossel", post.get("carrossel", []), (1080, 1350), False),
                                           ("story", post.get("stories", []), (1080, 1920), True)):
            pg = b.new_page(viewport={"width": w, "height": h})
            for i, s in enumerate(slides, 1):
                tmp = out / f"_{nome}.html"
                tmp.write_text(slide(s, w, h, tema, i, len(slides), story), encoding="utf-8")
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
    tema = sys.argv[sys.argv.index("--tema") + 1] if "--tema" in sys.argv else None
    render(sys.argv[1], tema)
