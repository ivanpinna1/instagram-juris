# Rotina diária de reposição — posts de jurisprudência (@ivan.pinna)

Este arquivo orienta a tarefa agendada que mantém a agenda abastecida. O publicador
(`publicar.py`, via GitHub Actions) publica sozinho, às 8h, 13h e 20h (Brasília), tudo o que
estiver em `agenda.json` na branch `main`. **Não há aprovação manual**: o que entra na `main`
vai ao ar. Por isso as regras editoriais abaixo são obrigatórias.

## Meta de cada execução

Manter a agenda preenchida **até 5 dias à frente** (3 posts por dia: 08:00, 13:00 e 20:00).
Cada post = carrossel + Reel + story (o próprio Reel), no mesmo horário.

## Passo a passo

1. Preparar o ambiente:
   - Ligar o repositório `ivanpinna1/instagram-juris` (acesso de escrita) e cloná-lo.
   - Baixar a base de enunciados: Artifact `read` em
     `https://claude.ai/artifact/1XDw8XdzSCTSLXL4fpaD2Z`, caminho `references/tcu/enunciados.tsv`.
   - Copiar do computador do Ivan **todas** as músicas `.mp3` da pasta
     `F:\ObsExtras\Musicas-sem-rights` (listar com as subpastas, pois ele acrescenta faixas).
     As músicas ficam só na sessão; **nunca** commitá-las.
2. Ver em `agenda.json` quais horários dos próximos 5 dias (a partir de amanhã, se hoje já passou
   das 20h) ainda não têm carrossel agendado.
3. `python3 fila.py proximos <enunciados.tsv> --n 30` lista os candidatos, do mais recente para o
   mais antigo **pela data da sessão** (enunciados novos que entrarem na base com a atualização
   quinzenal do acervo passam automaticamente à frente dos antigos ainda não publicados), já filtrados (Informativos de Licitações e Contratos e, dos Boletins de
   Jurisprudência, só "Licitação" e "Contrato Administrativo") e sem acórdãos já usados.
   Escolher um enunciado por horário vago, preferindo os úteis a licitantes e contratados
   (habilitação, propostas, julgamento, impugnação, recursos, sanções, execução, pagamento,
   reajuste e reequilíbrio). Pular os meramente processuais ou de alcance muito restrito
   (por exemplo, pessoal, convênios ou tomada de contas sem tese sobre licitação/contrato).
4. Para cada um, criar `posts/<AAAA-MM-DD>_ac<numero>-<ano>/post.json` no formato dos posts já
   existentes (ver `posts/2026-11-03_ac2552-2026/post.json`), com `usa` contendo a chave
   `"<acórdão>|<colegiado>"`.
5. `python3 fila.py agendar posts/<pasta> <AAAA-MM-DDTHH:MM> --musicas <pasta das músicas>`
   para cada post. Isso gera as telas, o Reel com música sorteada e agenda carrossel, Reel e
   story. Conferir as capas geradas (e o aviso de texto transbordando, se houver).
6. Commitar direto na `main` e dar push (antes, `git pull --rebase`, pois o publicador também
   grava `publicados.json` e `ultima_execucao.log`).
7. Ler `ultima_execucao.log` da `main`: se a última execução falhou, relatar o erro ao Ivan
   (o log traz diagnóstico do token).

Se o computador do Ivan não estiver acessível (sem as músicas), não gerar posts: a folga de
5 dias cobre, e a execução do dia seguinte repõe. Avisar o Ivan apenas se a folga cair para
menos de 2 dias.

## Regras editoriais (obrigatórias, pois não há revisão humana)

- Fidelidade total ao enunciado do TCU. Citação entre aspas **somente** com o texto literal do
  enunciado (trecho cortado leva "(...)"). Explicações em linguagem simples, sem acrescentar
  fatos do caso, números, órgãos ou fundamentos que a base não traz. Dispositivos legais só
  quando citados no próprio enunciado ou quando o conteúdo do artigo for conhecido com segurança.
- Nunca inventar jurisprudência nem atribuir ao TCU o que ele não disse.
- Fonte sempre completa: "TCU, Acórdão nº/ano – Colegiado, Rel. Min. Fulano. Boletim de
  Jurisprudência nº X" ou "Informativo de Licitações e Contratos nº X", com as datas das sessões.
- Não mencionar nomes de responsáveis, apenados ou empresas.
- Enunciados anteriores a 2021 (Lei 8.666/1993): só usar se o entendimento persistir sob a Lei
  14.133/2021, e dizer isso expressamente no post.
- Carrossel de 7 telas: capa com pergunta ou afirmação-gancho; 01 — O problema; 02 — O que o TCU
  decidiu (citação + fonte); 03 — O fundamento; 04 — Na prática, para quem licita; tela de oferta
  dos serviços do escritório (o render.py insere sozinho, se faltar); tela final "Curta, salve e
  compartilhe" (com a foto do Ivan).
- Legenda: gancho, resumo em 2 ou 3 parágrafos, o parágrafo de oferta abaixo (sempre, igual),
  "👉 Curta, salve e compartilhe" e até 10 hashtags (#licitações #lei14133 #tcu e temáticas).
  Oferta: "💼 Sua empresa participa de licitações? Terceirize toda a área com quem é especialista:
  busca de oportunidades, operação da licitação, impugnações, recursos e medidas judiciais e
  perante os Tribunais de Contas. Comente QUERO ou chame no direct."
- Variar os temas ao longo do dia (não repetir o mesmo assunto nos três horários).
- Música: sorteada entre as faixas da pasta do Ivan; não publicar as faixas no repositório.
