# Rotina diária de reposição — posts de jurisprudência (@ivan.pinna)

Esta rotina roda nos dias úteis às 10h23 e também logo após cada "atualize o acervo" do
Consultor Jurídico (a skill dispara a tarefa agendada), para que a jurisprudência nova seja
publicada já nos próximos horários.

Este arquivo orienta a tarefa agendada que mantém a agenda abastecida. O publicador
(`publicar.py`, via GitHub Actions) publica sozinho, às 13h (Brasília) dos dias úteis, tudo o que
estiver vencido em `agenda.json` na branch `main`. **Não há aprovação manual**: o que entra na `main`
vai ao ar. Por isso as regras editoriais abaixo são obrigatórias.

## Formato desde 05/11/2026 (decisão do Ivan)

Os números da conta mostraram que os Reels automáticos (telas + música) rendiam de 6 a 25
visualizações, menos que os carrosséis do mesmo tema, e muito menos que os Reels gravados pelo
Ivan. Além disso, 10 publicações por dia diluíam o alcance. Por isso:

- **1 carrossel por dia útil, às 13:00.** Nada de Reel ou story automático (`fila.py agendar` só
  gera o carrossel; a opção `--reel` existe, mas não deve ser usada).
- TCU e TCE-ES dividem o mesmo horário; a ordem é sempre do enunciado mais recente para o mais
  antigo (`fila.py replanejar`).
- **Roteiro semanal de Reel para o Ivan gravar** (ver passo 6).
- Músicas não são mais necessárias; não é preciso acessar o computador do Ivan.

## Passo a passo

1. Preparar o ambiente:
   - Ligar o repositório `ivanpinna1/instagram-juris` (acesso de escrita) e cloná-lo.
   - Baixar as bases: Artifact `read` em `https://claude.ai/artifact/1XDw8XdzSCTSLXL4fpaD2Z`,
     caminhos `references/tcu/enunciados.tsv` e, se existir, `references/tce-es/enunciados.tsv`.
2. Meta: agenda com carrossel em **todos os dias úteis dos próximos 10 dias úteis**. Se faltar,
   `python3 fila.py vago` mostra o próximo horário livre (dia útil, 13:00).
3. `python3 fila.py proximos <enunciados.tsv> --n 30` (e, para o TCE-ES,
   `python3 fila.py proximos <base do TCE-ES> --tribunal TCE-ES`) lista os candidatos, do mais
   recente para o mais antigo **pela data da sessão**, já filtrados (Informativos de Licitações e
   Contratos e, dos Boletins de Jurisprudência, só "Licitação" e "Contrato Administrativo") e sem
   acórdãos já usados. Escolher os úteis a licitantes e contratados (habilitação, propostas,
   julgamento, impugnação, recursos, sanções, execução, pagamento, reajuste e reequilíbrio). Pular
   os meramente processuais, os de alcance muito restrito e os itens de Informativo cujo texto na
   base é só o relato do caso, sem a tese do TCU.
4. Para cada um, criar `posts/<AAAA-MM-DD>_ac<numero>-<ano>/post.json` no formato dos posts já
   existentes (TCU: `posts/2026-11-03_ac2552-2026/post.json`; TCE-ES:
   `posts/2026-11-03_tcees-ac426-2026/post.json`), com `usa` contendo a chave exata mostrada por
   `proximos`. No TCE-ES, a capa leva `tag` com o tema e `subtitulo` "TCE-ES · Acórdão nº/ano –
   Colegiado"; fonte no padrão "TCE-ES, Acórdão nº/ano – Colegiado, Rel. Cons. Fulano. Informativo
   de Jurisprudência nº X"; `ponto_atencao` da base pode inspirar a tela "Na prática", reescrito.
5. `python3 fila.py agendar posts/<pasta> <AAAA-MM-DDTHH:MM>` para cada post (gera as telas e
   agenda o carrossel). Conferir as capas geradas (e o aviso de texto transbordando, se houver).
5-A. **Jurisprudência nova fura a fila.** Todo enunciado útil **mais recente** (pela data da sessão)
   do que o mais antigo dos carrosséis agendados e não publicados vira post agora, no horário de
   `fila.py vago`; depois rode `python3 fila.py replanejar` (os mais novos saem primeiro; nada é
   descartado).
6. **Roteiro semanal de Reel (na primeira execução de cada semana — segunda-feira, ou o primeiro
   dia útil da semana se segunda não houver execução).** Verificar se já existe
   `roteiros/<segunda-feira da semana>.md`; se não, escolher o enunciado de maior apelo prático
   para licitantes entre os mais recentes (agendados ou não) e escrever o roteiro com:
   - **Gancho (0–3 s):** uma frase falada que pare a rolagem, em forma de pergunta ou alerta
     dirigido a quem licita (ex.: "Se o edital te pede X, cuidado."), e o texto curto para a tela.
   - **Desenvolvimento (falado, 100–150 palavras, cerca de 45 s):** o problema, o que o TCU (ou
     TCE-ES) decidiu e o que a empresa deve fazer, em linguagem de conversa, frases curtas.
   - **Fechamento:** chamada para comentar ou salvar (variar a cada semana).
   - **Na tela/legenda:** o trecho literal do enunciado entre aspas (só se literal) e a fonte
     completa; legenda pronta (gancho, 2 parágrafos, a oferta padrão, "👉 Curta, salve e
     compartilhe", até 10 hashtags).
   - Sugestão de imagem de apoio (ex.: mostrar a cláusula do edital ou o acórdão na tela).
   Salvar em `roteiros/<AAAA-MM-DD>.md` no repositório **e** no Project (Projects
   `project_write`, caminho `instagram/roteiros/<AAAA-MM-DD>.md`), e avisar o Ivan por notificação
   (PushNotification) com o tema e o gancho. O roteiro segue todas as regras editoriais abaixo.
7. Commitar direto na `main` e dar push (antes, `git pull --rebase`, pois o publicador também
   grava `publicados.json` e `ultima_execucao.log`).
8. Ler `ultima_execucao.log` da `main`: se a última execução falhou, relatar o erro ao Ivan
   (o log traz diagnóstico do token).

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
- Variar a abertura da legenda (o gancho) e a forma dos parágrafos de resumo de um post para
  outro; só a oferta e o "Curta, salve e compartilhe" ficam fixos.
- Legenda: gancho, resumo em 2 ou 3 parágrafos, o parágrafo de oferta abaixo (sempre, igual),
  "👉 Curta, salve e compartilhe" e até 10 hashtags (#licitações #lei14133 #tcu e temáticas).
  Oferta: "💼 Sua empresa participa de licitações? Terceirize toda a área com quem é especialista:
  busca de oportunidades, operação da licitação, impugnações, recursos e medidas judiciais e
  perante os Tribunais de Contas. Comente QUERO ou chame no direct."
- Variar os temas de um dia para o outro (não repetir o mesmo assunto em dias seguidos).
- Nunca commitar músicas no repositório.
