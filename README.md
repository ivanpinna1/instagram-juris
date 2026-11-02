# Publicador de jurisprudência — @ivan.pinna

Três publicações por dia (carrossel + Reel + story) a partir da base de enunciados do TCU sobre licitações e
contratos, publicados automaticamente pela API oficial do Instagram.

- `render.py` — gera as artes (carrossel 1080×1350 e telas 1080×1920 do Reel) a partir de `post.json`.
- `fila.py` — escolhe os próximos acórdãos e monta a `agenda.json`.
- `reel.py` — monta o Reel (vídeo 9:16) com música sorteada; o mesmo vídeo vai para o story.
- `publicar.py` — roda no GitHub Actions às 8h, 13h e 20h e publica o que estiver vencido.
- `ROTINA.md` — roteiro e regras editoriais da reposição diária (tarefa agendada no Claude).

## Como funciona

Uma tarefa agendada no Claude roda nos dias úteis pela manhã e mantém `agenda.json` com cerca de
5 dias de posts. O GitHub Actions publica o que estiver vencido às 8h, 13h e 20h. Não há
aprovação manual. Para suspender uma publicação, apague o item correspondente de `agenda.json`.
O resultado de cada execução fica em `ultima_execucao.log` e `publicados.json`.

## Secrets (Settings → Secrets and variables → Actions)

- `IG_TOKEN` — token do usuário do sistema "Robo Publicacoes" (portfólio BM de Ivan Pinna,
  app Publicador Ivan Pinna), sem expiração. Para trocá-lo, gere outro em Configurações do
  negócio → Usuários do sistema → Robo Publicacoes → Gerar token, e substitua o valor aqui.
- `IG_USER_ID` — ID da conta do Instagram (17841401897076656).
