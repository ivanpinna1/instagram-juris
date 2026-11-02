# Publicador de jurisprudência — @ivan.pinna

Três publicações por dia (carrossel + Reel + story) a partir da base de enunciados do TCU sobre licitações e
contratos, publicados automaticamente pela API oficial do Instagram.

- `render.py` — gera as artes (carrossel 1080×1350 e story 1080×1920) a partir de `post.json`.
- `fila.py` — escolhe os próximos acórdãos e monta a `agenda.json`.
- `reel.py` — monta o Reel (vídeo 9:16) com música sorteada; o mesmo vídeo vai para o story.
- `publicar.py` — roda no GitHub Actions às 8h, 13h e 20h e publica o que estiver vencido.
- `ROTINA.md` — roteiro e regras editoriais do lote semanal.

## Como aprovar a semana

Toda semana chega um **Pull Request** com os posts. Abra a aba *Files changed* para ver as
imagens e as legendas. Se estiver tudo certo, clique em **Merge pull request**: os posts passam a
valer e são publicados nos dias e horários previstos. Para pedir ajuste, comente no Pull Request.

## Secrets (Settings → Secrets and variables → Actions)

- `IG_TOKEN` — token do usuário do sistema "Robo Publicacoes" (portfólio BM de Ivan Pinna,
  app Publicador Ivan Pinna), sem expiração. Para trocá-lo, gere outro em Configurações do
  negócio → Usuários do sistema → Robo Publicacoes → Gerar token, e substitua o valor aqui.
- `IG_USER_ID` — ID da conta do Instagram (17841401897076656).
