# Publicador de jurisprudência do TCU — @ivan.pinna

Posts semanais (carrossel + stories) a partir da base de enunciados do TCU sobre licitações e
contratos, publicados automaticamente pela API oficial do Instagram.

- `render.py` — gera as artes (carrossel 1080×1350 e story 1080×1920) a partir de `post.json`.
- `fila.py` — escolhe os próximos acórdãos e monta a `agenda.json`.
- `publicar.py` — roda no GitHub Actions às 8h, 12h e 18h e publica o que estiver vencido.
- `ROTINA.md` — roteiro e regras editoriais do lote semanal.

## Como aprovar a semana

Toda semana chega um **Pull Request** com os posts. Abra a aba *Files changed* para ver as
imagens e as legendas. Se estiver tudo certo, clique em **Merge pull request**: os posts passam a
valer e são publicados nos dias e horários previstos. Para pedir ajuste, comente no Pull Request.

## Secrets (Settings → Secrets and variables → Actions)

- `IG_TOKEN` — token de usuário do sistema do app "Publicador Ivan Pinna" no Meta (não expira).
  Para trocá-lo, gere outro no painel do app e substitua o valor aqui.
- `IG_USER_ID` — ID da conta do Instagram (17841401897076656).
