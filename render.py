#!/usr/bin/env python3
"""Gera as artes de um post (carrossel 4:5 e stories 9:16) em JPEG, no modelo do escritório
(fundo preto, logotipo dourado centralizado no topo, foto de terno all black na tela final).

Uso: python3 render.py posts/<id>/post.json
Saída: posts/<id>/carrossel_NN.jpg, reel_NN.jpg (telas 9:16 do Reel) e story_NN.jpg
"""
import html, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent
A = (RAIZ / "assets").as_uri()

FONTES = "".join(
    f"@font-face{{font-family:{fam};font-weight:{w};src:url({A}/fonts/{arq}-latin-{w}-normal.woff2)}}"
    for fam, arq, ws in (("PF", "playfair-display", (600, 700, 800)), ("IN", "inter", (400, 500, 600, 700)),
                         ("CZ", "cinzel", (600, 700)))
    for w in ws)

CSS = FONTES + """
:root{--ink:#f4efe4;--sub:#b3ab9b;--gold1:#f0d898;--gold2:#b4842c;--gold:#d6b066;--line:rgba(214,176,102,.5)}
*{margin:0;padding:0;box-sizing:border-box}
body{width:Wpx;height:Hpx;background:#000;font-family:IN,sans-serif;color:var(--ink);overflow:hidden;position:relative}
.logo{position:absolute;left:50%;transform:translateX(-50%);top:LOGOTOPpx;width:LOGOWpx}
.trib{position:absolute;left:54px;top:46px;height:TRIBHpx}
.pg{position:absolute;right:60px;top:60px;font-family:CZ;font-weight:600;font-size:24px;letter-spacing:3px;color:var(--gold)}
.corpo{position:absolute;left:84px;right:84px;top:TOPOpx;bottom:BASEpx;display:flex;flex-direction:column;justify-content:center}
.centro{text-align:center;align-items:center}
.divisor{display:flex;align-items:center;gap:14px;justify-content:center;margin:0 auto 34px;width:360px}
.divisor:before,.divisor:after{content:"";flex:1;height:1.5px;background:linear-gradient(90deg,transparent,var(--gold))}
.divisor:after{background:linear-gradient(90deg,var(--gold),transparent)}
.divisor i{width:10px;height:10px;background:var(--gold);transform:rotate(45deg)}
.tag{font-family:CZ;font-weight:600;color:var(--gold);font-size:24px;letter-spacing:5px;text-transform:uppercase;margin-bottom:30px}
h1{font-family:PF;font-weight:700;font-size:CAPApx;line-height:1.14}
.ouro,h1 b,h2 b,blockquote b{font-weight:inherit;background:linear-gradient(180deg,var(--gold1),var(--gold2));-webkit-background-clip:text;color:transparent}
.subt{margin-top:38px;font-size:28px;color:var(--sub);letter-spacing:1px}
.num{font-family:CZ;font-weight:600;font-size:24px;color:var(--gold);letter-spacing:5px;margin-bottom:18px;text-transform:uppercase}
h2{font-family:PF;font-weight:700;font-size:58px;line-height:1.14;margin-bottom:38px}
p{font-size:TEXTOpx;line-height:1.55;margin-bottom:28px;color:#e9e3d6}
p b{font-weight:600;color:var(--gold)}
.aspas{font-family:PF;font-weight:800;font-size:200px;line-height:.5;height:80px;
  background:linear-gradient(180deg,var(--gold1),var(--gold2));-webkit-background-clip:text;color:transparent}
blockquote{font-family:PF;font-weight:600;font-size:CITApx;line-height:1.4}
.fonte{margin-top:40px;padding-top:26px;border-top:1.5px solid var(--line);font-size:25px;color:var(--sub);line-height:1.5}
.fonte b{color:var(--ink);font-weight:600}
.pe{position:absolute;left:84px;right:84px;bottom:56px;display:flex;justify-content:center;align-items:center;
  font-family:CZ;font-weight:600;font-size:22px;letter-spacing:4px;color:var(--gold);text-transform:uppercase}
.foto{position:absolute;left:50%;transform:translateX(-50%);bottom:0;height:FOTOHpx;
  -webkit-mask-image:linear-gradient(180deg,#000 82%,transparent 100%)}
.icones{display:flex;gap:64px;justify-content:center;margin:34px 0 0}
.icones div{text-align:center;font-family:CZ;font-weight:600;font-size:20px;color:var(--gold);letter-spacing:3px;text-transform:uppercase}
.icones svg{width:78px;height:78px;display:block;margin:0 auto 10px;color:var(--gold)}
.servicos{margin-top:30px;font-size:25px;line-height:1.5;color:var(--sub);text-align:center}
.servicos b{color:var(--gold);font-weight:600}
.oferta h2{font-size:52px;margin-bottom:22px}
.oferta .lead{font-size:30px;color:var(--sub);line-height:1.45;margin-bottom:30px}
.oferta ul{list-style:none;margin:0 0 34px}
.oferta li{font-size:31px;line-height:1.35;padding:15px 0 15px 46px;position:relative;border-bottom:1px solid rgba(214,176,102,.22)}
.oferta li:before{content:"";position:absolute;left:6px;top:28px;width:13px;height:13px;background:var(--gold);transform:rotate(45deg)}
.oferta .chamada{font-family:PF;font-weight:700;font-size:40px;line-height:1.25}
.oferta .chamada b{background:linear-gradient(180deg,var(--gold1),var(--gold2));-webkit-background-clip:text;color:transparent}
"""

OFERTA_PADRAO = {
    "tipo": "oferta",
    "titulo": "Sua empresa participa de **licitações**?",
    "lead": "Terceirize toda a área com quem é especialista:",
    "itens": ["Busca das melhores oportunidades", "Preparação e operação da licitação",
              "Impugnações e recursos administrativos",
              "Medidas judiciais e perante os Tribunais de Contas"],
    "chamada": "Comente **QUERO** ou chame no direct.",
}

# Reel (9:16): letras maiores, logotipo mais próximo do conteúdo e zona segura do Instagram
# (faixa inferior com legenda/@ e coluna direita com os botões ficam livres).
CSS_REEL = """
.logo{top:150px;width:364px}
.trib{top:160px;left:64px}
.corpo{top:480px;bottom:400px;left:110px;right:130px}
.centro{left:130px}
h1{font-size:REELCAPApx}
h2{font-size:72px;margin-bottom:44px}
p{font-size:REELTEXTOpx;margin-bottom:34px}
blockquote{font-size:REELCITApx}
.num,.tag{font-size:32px;margin-bottom:26px}
.subt{font-size:38px;margin-top:44px}
.fonte{font-size:33px;margin-top:46px}
.aspas{font-size:240px;height:96px}
.divisor{width:440px}
.cta-reel .corpo{top:470px;bottom:auto}
.cta-reel h1{font-size:84px}
.icones{gap:80px;margin-top:44px}
.icones svg{width:100px;height:100px}
.icones div{font-size:26px}
.servicos{font-size:34px;margin-top:38px}
.foto{height:900px}
.oferta h2{font-size:74px}
.oferta .lead{font-size:44px}
.oferta li{font-size:46px;padding:22px 0 22px 58px}
.oferta li:before{top:40px;width:17px;height:17px}
.oferta .chamada{font-size:56px}
"""

ICONES = """<div class="icones">
<div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M12 20.5s-7.5-4.6-9.2-9.3C1.6 7.8 3.9 4.5 7.3 4.5c2 0 3.6 1.1 4.7 2.7 1.1-1.6 2.7-2.7 4.7-2.7 3.4 0 5.7 3.3 4.5 6.7-1.7 4.7-9.2 9.3-9.2 9.3z"/></svg>Curta</div>
<div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M6 3.5h12v17l-6-4.5-6 4.5z"/></svg>Salve</div>
<div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M21.5 3.5 2.5 10l7.5 3 3 7.5z M10 13l11.5-9.5"/></svg>Compartilhe</div>
</div>"""


def md(t):
    t = html.escape(t)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t).replace("\n", "<br>")


def slide(s, w, h, idx, total, story, reel=False, tribunal="TCU"):
    tipo = s["tipo"]
    cta = tipo == "cta"
    grande = tipo in ("capa", "cta")
    v = {"W": w, "H": h,
         "LOGOW": (320 if grande else 230) if not story else (360 if grande else 280),
         "LOGOTOP": 56 if not story else 120,
         "TOPO": (330 if grande else 270) if not story else (470 if grande else 410),
         "BASE": 130 if not story else 230,
         "FOTOH": 650 if not story else 900,
         "TRIBH": (92 if tribunal == "TCU" else 88) if not story else (100 if tribunal == "TCU" else 84),
         "CAPA": s.get("tam", 66 if not story else 78),
         "TEXTO": s.get("tam_texto", 35 if not story else 42),
         "CITA": s.get("tam_cit", 42 if not story else 50)}
    if cta:
        v["TOPO"] = 270 if not story else 440
        v["BASE"] = v["FOTOH"] - 10
    css = CSS + (CSS_REEL.replace("REELCAPApx", f'{s.get("tam_reel", 92)}px')
                 .replace("REELTEXTOpx", f'{s.get("tam_texto_reel", 48)}px')
                 .replace("REELCITApx", f'{s.get("tam_cit_reel", 56)}px') if reel else "")
    for k in ("TRIBH", "LOGOTOP", "LOGOW", "FOTOH", "TOPO", "BASE", "CAPA", "TEXTO", "CITA", "W", "H"):
        css = css.replace(f"{k}px", f"{v[k]}px")

    cab = f'<img class="logo" src="{A}/logo_escritorio.png">'
    if tipo in ("capa", "texto", "citacao"):  # logotipo do tribunal nas telas de conteúdo
        cab += f'<img class="trib" src="{A}/tribunal_{tribunal.lower()}.png">'
    if not story and not grande:
        cab += f'<div class="pg">{idx:02d}/{total:02d}</div>'
    foto = f'<img class="foto" src="{A}/foto_terno.png">' if cta else ""
    centro = ""

    if tipo == "capa":
        centro = " centro"
        c = (f'<div class="tag">{md(s.get("tag", "Jurisprudência do TCU"))}</div>'
             f'<div class="divisor"><i></i></div><h1>{md(s["titulo"])}</h1>')
        if s.get("subtitulo"):
            c += f'<div class="subt">{md(s["subtitulo"])}</div>'
    elif tipo == "texto":
        c = (f'<div class="num">{md(s["num"])}</div>' if s.get("num") else "") + f'<h2>{md(s["titulo"])}</h2>'
        c += "".join(f"<p>{md(p)}</p>" for p in s["paragrafos"])
    elif tipo == "citacao":
        c = f'<div class="num">{md(s["titulo"])}</div>' if s.get("titulo") else ""
        c += f'<div class="aspas">“</div><blockquote>{md(s["citacao"])}</blockquote>'
        if s.get("fonte"):
            c += f'<div class="fonte">{md(s["fonte"])}</div>'
    elif tipo == "oferta":
        c = (f'<div class="num">Ivan Pinna · Advocacia</div><h2>{md(s["titulo"])}</h2>'
             f'<div class="lead">{md(s.get("lead", ""))}</div><ul>'
             + "".join(f"<li>{md(i)}</li>" for i in s["itens"]) +
             f'</ul><div class="chamada">{md(s.get("chamada", ""))}</div>')
    elif tipo == "cta":
        centro = " centro"
        c = f'<h1>{md(s.get("titulo", "Curta, **salve** e compartilhe"))}</h1>{ICONES}'
        if s.get("texto"):
            c += f'<div class="servicos">{md(s["texto"])}</div>'
    else:
        raise ValueError(tipo)

    if cta or reel:
        pe = ""
    elif story:
        pe = f'<div class="pe">{md(s.get("rodape", "Post completo no feed"))}</div>'
    elif idx < total:
        pe = '<div class="pe">Arraste para o lado →</div>'
    else:
        pe = ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body class="{"cta-reel" if (reel and cta) else ""} {"oferta" if tipo == "oferta" else ""}">{foto}{cab}<div class="corpo{centro}">{c}</div>{pe}</body></html>')


def render(post_json):
    post_json = Path(post_json).resolve()
    post = json.loads(post_json.read_text(encoding="utf-8"))
    # toda publicação leva a tela de oferta dos serviços antes da tela final
    car = post.get("carrossel", [])
    if car and not any(x["tipo"] == "oferta" for x in car):
        pos = next((i for i, x in enumerate(car) if x["tipo"] == "cta"), len(car))
        car.insert(pos, dict(OFERTA_PADRAO))
        post_json.write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    out = post_json.parent
    tribunal = post.get("fonte", {}).get("tribunal", "TCU")
    gerados = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, slides, (w, h), story, reel in (
                ("carrossel", post.get("carrossel", []), (1080, 1350), False, False),
                ("reel", post.get("carrossel", []), (1080, 1920), True, True),
                ("story", post.get("stories", []), (1080, 1920), True, False)):
            pg = b.new_page(viewport={"width": w, "height": h})
            for i, s in enumerate(slides, 1):
                tmp = out / f"_{nome}.html"
                tmp.write_text(slide(s, w, h, i, len(slides), story, reel, tribunal), encoding="utf-8")
                pg.goto(tmp.as_uri()); pg.wait_for_load_state("networkidle")
                pg.evaluate("document.fonts.ready")
                # ajusta o texto ao espaço: reduz as letras do conteúdo até caber (no máximo 30%)
                over = pg.evaluate("""(()=>{const c=document.querySelector('.corpo');const els=[...c.querySelectorAll('*')];
                  const base=els.map(e=>parseFloat(getComputedStyle(e).fontSize));let k=1;
                  while(c.scrollHeight>c.clientHeight+2 && k>0.7){k-=0.03;els.forEach((e,i)=>e.style.fontSize=(base[i]*k)+'px');}
                  return c.scrollHeight>c.clientHeight+2})()""")
                if over:
                    print(f"AVISO: texto transborda em {nome} {i}", file=sys.stderr)
                f = out / f"{nome}_{i:02d}.jpg"
                pg.screenshot(path=str(f), type="jpeg", quality=92)
                tmp.unlink(); gerados.append(f.name)
        b.close()
    print("gerados:", ", ".join(gerados))


if __name__ == "__main__":
    render(sys.argv[1])
