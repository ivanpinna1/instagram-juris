# Rotina semanal — posts de jurisprudência do TCU (@ivan.pinna)

Este arquivo orienta a tarefa agendada que prepara o lote da semana. O publicador
(`publicar.py`, via GitHub Actions) só publica o que estiver em `agenda.json` na branch `main`;
por isso **nada vai ao ar sem o merge do Pull Request pelo Ivan**.

## Passo a passo

1. Baixar a base do acervo: Artifact `read` em `https://claude.ai/artifact/1XDw8XdzSCTSLXL4fpaD2Z`,
   caminho `references/tcu/enunciados.tsv` (é a base atualizada pelo "atualize o acervo").
2. `python3 fila.py proximos <enunciados.tsv> --n 12` → candidatos em ordem do mais recente
   para o mais antigo, já filtrados (Informativos de L&C e, dos Boletins, só "Licitação" e
   "Contrato Administrativo") e sem acórdãos já usados.
3. Para cada dia útil da semana seguinte (seg a sex), escolher **um** enunciado para o carrossel e
   **outro** para o story "Você sabia?". Pular enunciados de alcance muito restrito ou meramente
   processuais; preferir os úteis a licitantes (habilitação, propostas, impugnação, recursos,
   execução e reequilíbrio de contratos).
4. Criar `posts/<AAAA-MM-DD>_ac<numero>-<ano>/post.json` no formato do post-modelo
   `posts/2026-11-03_ac2788-2026/post.json`, com `usa` listando as chaves dos dois acórdãos.
5. `python3 fila.py agendar posts/<pasta> <AAAA-MM-DD>` para cada dia (gera as imagens e agenda:
   8h story "Você sabia?", 12h carrossel, 18h story de chamada). Conferir as imagens geradas
   (o render avisa se algum texto transbordou; nesse caso, encurtar o texto).
6. Criar a branch `lote-<AAAA-MM-DD>`, commitar e abrir Pull Request para `main` com a lista dos
   posts e as capas, e avisar o Ivan para revisar e fazer o merge.

## Regras editoriais

- Fidelidade total ao enunciado. Citação entre aspas **somente** com o texto literal do enunciado
  (trecho cortado leva "(...)"). Explicações em linguagem simples, sem acrescentar fatos do caso
  que a base não traz e sem inventar jurisprudência.
- Fonte sempre completa: "TCU, Acórdão nº/ano – Colegiado, Rel. Min. Fulano. Boletim de
  Jurisprudência nº X" ou "Informativo de Licitações e Contratos nº X".
- Não mencionar nomes de responsáveis ou apenados.
- Enunciados anteriores a 2021 (Lei 8.666/1993): só usar se o entendimento persistir sob a Lei
  14.133/2021, e dizer isso expressamente no post.
- Carrossel de 5 a 7 telas: capa com pergunta ou afirmação-gancho; a prática ou o problema; o
  que o TCU decidiu (citação + fonte); por que (fundamento legal); na prática, para quem licita;
  tela final "Curta, salve e compartilhe".
- Legenda: gancho, resumo em 2 ou 3 parágrafos, "👉 Curta, salve e compartilhe" e até 10
  hashtags (#licitações #lei14133 #tcu e temáticas).
- Story 1 (chamada): "Novo post no feed" + manchete. Story 2: "Você sabia?" com o enunciado literal
  (curto) e a fonte.
