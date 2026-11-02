#!/usr/bin/env python3
"""Gera o Reel (vídeo 9:16) a partir das telas do carrossel, com música sorteada.

Uso: python3 reel.py posts/<id> [--musicas <pasta>] [--seed N]
- Usa as telas reel_NN.jpg (1080x1920) geradas pelo render.py com o mesmo conteúdo do carrossel.
- O tempo de cada tela é proporcional ao texto (entre 4 e 9 s), com transição suave.
- A música é sorteada entre os .mp3 da pasta (padrão: assets/musicas, ou MUSICAS_DIR),
  com entrada e saída suaves. O nome da faixa usada é gravado em post.json ("musica").
Saída: posts/<id>/reel.mp4
"""
import json, os, random, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
XF = 0.6  # duração da transição


def texto_do_slide(s):
    partes = [s.get(k, "") for k in ("titulo", "subtitulo", "citacao", "fonte", "texto", "tag")]
    partes += s.get("paragrafos", [])
    return " ".join(p for p in partes if p)


def dur_slide(s):
    n = len(texto_do_slide(s))
    return max(4.0, min(9.0, 3.0 + n / 45))


def duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def gerar(pasta, musicas_dir=None, seed=None):
    pasta = Path(pasta).resolve()
    post = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    slides = post["carrossel"]
    imgs = [pasta / f"reel_{i:02d}.jpg" for i in range(1, len(slides) + 1)]
    durs = [dur_slide(s) for s in slides]
    total = sum(durs) - XF * (len(durs) - 1)
    if total > 58:  # o mesmo vídeo vai para o story, que aceita no máximo 60 s
        fator = (58 + XF * (len(durs) - 1)) / sum(durs)
        durs = [d * fator for d in durs]
        total = sum(durs) - XF * (len(durs) - 1)

    mdir = Path(musicas_dir or os.environ.get("MUSICAS_DIR") or RAIZ / "assets" / "musicas")
    faixas = sorted(p for p in mdir.rglob("*.mp3"))
    if not faixas:
        sys.exit(f"Nenhuma música .mp3 em {mdir}")
    rnd = random.Random(seed)
    faixa = rnd.choice(faixas)
    dmus = duracao(faixa)
    inicio = 0.0 if dmus < total + 20 else round(rnd.uniform(0, min(30, dmus - total - 5)), 1)

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for im, d in zip(imgs, durs):
        cmd += ["-loop", "1", "-t", f"{d:.2f}", "-framerate", "30", "-i", str(im)]
    cmd += ["-ss", f"{inicio}", "-i", str(faixa)]
    f = []
    for i in range(len(imgs)):
        f.append(f"[{i}:v]scale=1080:1920,setsar=1,format=yuv420p,fps=30[v{i}]")
    ant, acum = "v0", durs[0]
    for i in range(1, len(imgs)):
        off = acum - XF
        f.append(f"[{ant}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}]")
        ant, acum = f"x{i}", off + durs[i]
    a = len(imgs)
    f.append(f"[{a}:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=0.8,"
             f"afade=t=out:st={max(0, total - 2):.2f}:d=2,volume=0.85[aud]")
    cmd += ["-filter_complex", ";".join(f), "-map", f"[{ant}]", "-map", "[aud]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-movflags", "+faststart", "-t", f"{total:.2f}",
            str(pasta / "reel.mp4")]
    subprocess.run(cmd, check=True)
    post["musica"] = faixa.name
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"reel.mp4 gerado ({total:.1f} s) com a música: {faixa.name}")


if __name__ == "__main__":
    a = sys.argv
    mus = a[a.index("--musicas") + 1] if "--musicas" in a else None
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else None
    gerar(a[1], mus, seed)
