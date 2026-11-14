# Identidades docentes e fila de revisão — #207

Escopo autorizado por Nicolas na conversa de 11/11/2026, após investigação dos
perfis públicos e aprovação da regra de associação e da fila de dúvidas.
Fonte de produto: RF23 em [requisitos](requisitos.md). Evolução técnica no ADR 07.

## Fluxo entregue

O importador real consulta a busca global de docentes e a aba de graduação dos
perfis, com cache somente durante sua execução e intervalo entre buscas de nomes.
Associa automaticamente apenas um perfil com nome completo normalizado, disciplina,
ID do componente e semestre compatíveis. O identificador do perfil fica separado
do SIAPE legado; não se inventa SIAPE nem se promove identidade_confirmada.
Novas turmas/unidades/semestres reutilizam o UUID institucional sem confirmação
humana repetida. A evolução híbrida autorizada em 13/11/2026 permite associação
local por nome completo + unidade quando a busca não encontra perfil ou o
histórico não confirma a disciplina. Múltiplos perfis exigem revisão inicial.
Consultas incompletas nunca significam ausência ou unicidade.

A fila `/moderacao/identidades` tem acesso separado dos comentários, filtro por
estado, páginas de 50 ocorrências, candidatos, links institucionais, prévia de
impacto, justificativa e histórico. Ações: confirmar associação, manter separados
ou deixar pendente sem decidir. A versão enviada impede decisão sobre dados
alterados por outra aba ou importação. Nenhuma avaliação individual é exposta.

- **PENDENTE:** exige revisão ou nova evidência da origem.
- **CONFIRMADA:** decisão/inferência registrada; aguarda aplicação.
- **SEPARADA:** decisão humana de manter esta ocorrência separada, preservada
  na reimportação. Não é uma regra generalizada para todo nome coincidente.
- **APLICADA:** vínculo já utilizável; `ASSOCIACAO_LOCAL` distingue o fallback
  provisório de uma associação institucional.

Se não for necessário unir UUIDs existentes, o importador aplica a confirmação na
próxima observação daquela ocorrência. Se precisar reunir UUIDs e dependentes,
a operação fica CONFIRMADA até o comando administrativo em janela sem escritores.
O importador e a API não movem avaliações de registros já existentes.

A aplicação revalida o grupo inteiro. Colisões de usuário/professor/disciplina ou
conflitos institucionais bloqueiam o grupo sem descarte ou aplicação parcial;
a fila mostra `APLICACAO_BLOQUEADA`, mantendo a confirmação e sua auditoria.
A prévia de uma ocorrência não garante ausência de colisão entre outras origens
do grupo, que é conferida novamente pelo comando.

Decisões aguardam o lock da importação por até cinco segundos. Em caso de
contenção, a API faz rollback e retorna 409 para atualizar a fila e tentar
novamente; nenhuma decisão parcial é registrada. A
[revisão da PR #225](estudos/revisao-pr-225.md) registra as correções e verificações.

## Implantação, permissão e aplicação operacional

1. Publicar backend/frontend compatíveis e aplicar as migrations até `20261113_01` com
   a conexão administrativa. O papel novo começa falso para todas as contas.
2. Aplicar GRANTs adicionais de `scripts/sql/207-acesso-identidades.sql` como
   administrador no banco correto. Os GRANTs anteriores de #164/#170 continuam
   necessários. A API recebe leitura e apenas as escritas da decisão; não recebe
   UPDATE em professores, avaliações ou correspondências por esta entrega.
3. Conceder a permissão específica apenas às pessoas designadas pelo PO, com a
   conexão administrativa. Não modifica o papel de moderador de comentários:

   ```sh
   python -m app.commands.identidades papel pessoa@aluno.unb.br conceder
   # Reverter o papel:
   python -m app.commands.identidades papel pessoa@aluno.unb.br revogar
   ```

4. Executar importação manual/agendada pelo fluxo existente. O coletor de ofertas
   continua separado da API. Os testes com coletores simulados não acionam rede;
   testes podem injetar uma consulta institucional em `salvar_oferta`.
5. Revisar PENDENTES pela interface. Para unir dados existentes, conferir plano,
   origens/destinos, backup completo e restauração, **pausar API, importador e todos
   os demais escritores**, inclusive processos antigos. Configurar `DATABASE_URL`
   administrativa para o banco pretendido, com código/migration compatíveis, e
   executar somente nessa janela:

   ```sh
   python -m app.commands.identidades aplicar --confirmo-janela-sem-escritores-e-backup
   ```

   O comando exige PostgreSQL, mantém os locks/rollback da #223 e aplica grupos
   por identificador institucional. Retorna código 2 se algum grupo foi bloqueado;
   grupos independentes sem conflito podem ser concluídos. Confira cada resultado.
   `CONFIRMADA` nunca é apresentada como união concluída apenas pela decisão na UI.
6. Conferir busca, disciplinas, avaliações/históricos, IDs antigos, reimportação e
   RNF02 antes de reabrir escritores. Não usar avaliações fictícias em docentes
   reais para testar persistência pública.

Depois de aplicada uma identidade/pendência, o downgrade da nova migration é
recusado para preservar auditoria e vínculos. Recuperação de dados exige backup
completo na janela apropriada; remover alias/linhas manualmente não é rollback.
Nenhum comando desta entrega foi aplicado ao banco público na preparação da PR.

## Verificações e evidências

- Ruff e formatação, compilação e suíte backend: 218 testes executados, 217
  aprovados e um cenário específico de PostgreSQL pulado na suíte SQLite.
- PostgreSQL 16 descartável exclusivo `undb_207_test`: migrations completas até
  `20261111_01`, `alembic check` sem divergências; 30 testes de identidade e
  reconciliação aprovados, incluindo HTTP/permissões, colisões, rollback e timeout.
- GRANTs conferidos com papel limitado em PostgreSQL: fila/decisão/auditoria
  permitidas; escrita no catálogo recusada com SQLSTATE 42501.
  [Evidência](estudos/evidencias/issue-207-fila/privilegios.json).
- Frontend em Node 24/Linux com dependências do lockfile: lint, typecheck,
  **75 testes** e build padrão Next.js/Turbopack aprovados.
- Brave headless com HTTP controlado: 320/768/1280 px, candidato e prévia,
  navegação por Tab/foco, confirmação e atualização, 403 limpando os dados,
  409 sem sucesso indevido e ausência de overflow. [Resultado](estudos/evidencias/issue-207-fila/resultado.json),
  [320 px](estudos/evidencias/issue-207-fila/fila-320.png),
  [768 px](estudos/evidencias/issue-207-fila/fila-768.png),
  [1280 px](estudos/evidencias/issue-207-fila/fila-1280.png).

Os testes de interface usam apenas dados fictícios. Testes determinísticos não
comprovam cobertura geral da UnB nem implantação pública. A investigação real
anterior verificou 34 vínculos de sete docentes, em 2026.2 e 2027.1, incluindo
Gama, Matemática, Saúde Coletiva e Física. O perfil não fornece turma diretamente:
a associação permanece inferência institucional com o risco residual debatido e
aceito na conversa. Nome sozinho não basta: o fallback exige também a unidade
da oferta e ausência de perfil encontrado, com risco residual aceito pelo PO.

As turmas antigas podem não estar acessíveis por estarem encerradas, conforme
informação do PO. Falta em consulta atual não desfaz identidade ou avaliações
históricas. Pendências por indisponibilidade podem persistir até a próxima execução;
a consulta em cache não é reaproveitada entre execuções.

## Reavaliação seletiva de consultas inconclusivas

O comando abaixo consulta novamente apenas ocorrências `PENDENTE`, com motivo
`CONSULTA_INCONCLUSIVA` e sem decisão humana. Recupera componente, unidade,
semestre e turma do catálogo existente; ignora ocorrências sem oferta inequívoca
ou sem identificador do componente. Não reimporta ofertas nem inativa turmas.

A partir de `backend/`, a prévia é o comportamento padrão:

```bash
python -m app.commands.reavaliar_identidades --saida previa-identidades.json
```

Para gravar a reavaliação, executar novamente acrescentando `--aplicar`. Essa
segunda execução consulta a fonte novamente; o JSON anterior não é usado como
prova de identidade. O comando mostra progresso por ocorrência, reutiliza perfis
por nome durante a execução e tenta mais uma vez uma consulta inconclusiva.
A rede é consultada antes das transações de escrita. Cada ocorrência é gravada
em uma transação curta sob o lock existente e somente se sua versão, estado,
origem e campos ainda coincidirem com a seleção inicial. Uma decisão humana
ou atualização concorrente é preservada. Uma falha após commits anteriores não
os desfaz: conferir relatório/progresso e selecionar novamente as inconclusivas.

A operação exige as permissões existentes do importador, não uma conexão
administrativa. O relatório contém nomes e links institucionais: guardar como
artefato operacional, fora de commits. Prévia e reavaliação não movem avaliações,
comentários ou vínculos de turma, nem unem UUIDs. Casos reconhecidos que exijam
união passam a `CONFIRMADA` e continuam sujeitos à manutenção administrativa,
backup e janela sem escritores descritos acima. A API não precisa ser suspensa
para a reavaliação seletiva; evitar executá-la junto de outra importação.

## Modelo híbrido e consolidação por grupo (#207)

Decisão do PO em 13/11/2026: aceitar o risco residual de homônimos sem perfil encontrado na mesma unidade. O importador consulta primeiro o perfil institucional. `PERFIL_AUSENTE` e `DISCIPLINA_NAO_CONFIRMADA` permitem reutilizar `(nome_normalizado, unidade da oferta)`, sem declarar confirmação institucional da disciplina. Múltiplos perfis e consultas inconclusivas exigem uma primeira revisão explícita; uma associação local já registrada pode ser reutilizada durante indisponibilidade. Conflitos institucionais continuam bloqueados. A chave local não contém semestre ou turma e não une unidades distintas.

`identidades_locais` registra a chave provisória por nome e unidade, separada de `identidades_docentes`. O registro não recebe SIAPE nem marca de confirmação institucional. Uma associação local aplicada tem motivo `ASSOCIACAO_LOCAL`; ela é reavaliada em importações seguintes e pode ser promovida mantendo o UUID e as avaliações. Se o perfil já pertence a outro UUID, a união permanece administrativa. Quando um destino já consolidado muda, seus aliases são redirecionados diretamente ao destino final, preservando os links antigos sem cadeias.

Decisões humanas de manter separados impedem fallback automático para o mesmo nome/unidade. Duas identidades institucionais conhecidas na mesma chave bloqueiam a associação. O fallback não apaga avaliações conflitantes: elas bloqueiam o grupo inteiro.

### Preparação e ordem de execução

1. Publicar o código, aplicar Alembic até `20261113_01` e executar o SQL atualizado `scripts/sql/207-acesso-identidades.sql` como administrador. A migration apenas cria a tabela; não altera cadastros existentes.
2. Antes do fallback, usar a reavaliação seletiva e conferir perfis encontrados manualmente. O comando consulta o SIGAA novamente, verifica nome completo e disciplina/componente/semestre. Não usar JSON antigo como autorização de escrita.
3. Gerar a prévia dos grupos locais. Corrigir ou manter na moderação os bloqueios apresentados.
4. Para unir UUIDs antigos, parar API, importadores e outros escritores, criar backup completo e conferir sua restauração. Aplicar os grupos institucionais e depois os locais. Não misturar contas de importador e administrador.
5. Conferir fila, avaliações, vínculos e exemplos nas buscas antes de reativar a API. A prévia não exige suspender a aplicação.

Perfil indicado manualmente, inclusive quando o cadastro já recebeu fallback:

```bash
python -m app.commands.reavaliar_identidades \
  --perfil 'MARILUCIA ROCHA DE ALMEIDA PICANCO=404588' \
  --saida previa-marilucia.json
```

Adicionar `--aplicar` para gravar a reavaliação. Esse comando não move avaliações ou turmas entre UUIDs. Nenhum identificador de docente é hardcoded no importador. Um perfil já conhecido pode ser consultado diretamente caso a busca pública deixe de encontrá-lo, com nova validação do histórico.

Prévia do fallback, sem escrita:

```bash
python -m app.commands.identidades locais
```

Aplicação administrativa, somente na janela de manutenção com backup validado:

```bash
python -m app.commands.identidades aplicar \
  --confirmo-janela-sem-escritores-e-backup
python -m app.commands.identidades locais --aplicar \
  --confirmo-janela-sem-escritores-e-backup
```

Cada grupo é atômico e tem seu próprio commit. O progresso `[n/total]` vai para stderr após salvar o resultado; stdout mantém o JSON final. Em caso de interrupção, grupos concluídos permanecem aplicados; executar novamente processa apenas os restantes. Uma falha inesperada desfaz o grupo atual. Grupos bloqueados continuam para revisão, e o CLI retorna código 2. Isso substitui a antiga transação única de todo o lote.

A consolidação otimizada verifica identidades e colisões em conjuntos, move vínculos com `INSERT SELECT` e mantém IDs, datas, comentários e decisões das avaliações. O ganho depende da latência e do tamanho dos grupos; não usar o tempo local como promessa de duração em produção.


## Encerramento das pendências investigadas em 13/11/2026

A [investigação das 41 ocorrências](estudos/pendencias-finais-issue-207.md) fundamenta
a ampliação autorizada pelo PO. Nenhuma tabela ou migração nova é necessária.

`locais --incluir-revisadas` inclui também `HOMONIMOS` e `CONSULTA_INCONCLUSIVA`.
O operador deve conferir **todos os grupos da prévia** antes de aplicá-la; a opção
não significa que múltiplos perfis quaisquer representam a mesma pessoa.
A evidência dos candidatos permanece em `pendencias_identidade`, com motivo
`ASSOCIACAO_LOCAL_REVISADA`. Em novas ocorrências, o conjunto de identificadores
precisa ser exatamente o revisado e todos os nomes completos precisam corresponder.
Um perfil adicional ou diferente gera pendência. Não se escolhe um SIAPE arbitrário.

```bash
python -m app.commands.identidades locais --incluir-revisadas > previa-revisadas.json
```

Após conferir a prévia, suspender API e outros escritores e validar um backup
atualizado com restauração. Usar conexão administrativa somente nesse processo:

```bash
python -m app.commands.identidades locais --incluir-revisadas --aplicar \
  --confirmo-janela-sem-escritores-e-backup
```

O fallback de histórico incompleto passa a valer automaticamente para novos
semestres. Associações locais persistem no banco, sem depender do cache da coleta.
Decisões de separação e colisões de avaliações continuam bloqueando a união.
Uma nova ambiguidade exige revisão; este tratamento não promete eliminar toda
pendência futura. A opção não apaga nem corrige ofertas históricas ausentes na
consulta pública atual.
