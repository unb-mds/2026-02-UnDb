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
humana repetida. Homônimos, respostas parciais, perfil ausente ou histórico não
compatível geram pendências. Consultas incompletas nunca significam unicidade.

A fila `/moderacao/identidades` tem acesso separado dos comentários, filtro por
estado, páginas de 50 ocorrências, candidatos, links institucionais, prévia de
impacto, justificativa e histórico. Ações: confirmar associação, manter separados
ou deixar pendente sem decidir. A versão enviada impede decisão sobre dados
alterados por outra aba ou importação. Nenhuma avaliação individual é exposta.

- **PENDENTE:** exige revisão ou nova evidência da origem.
- **CONFIRMADA:** decisão/inferência registrada; aguarda aplicação.
- **SEPARADA:** decisão humana de manter esta ocorrência separada, preservada
  na reimportação. Não é uma regra generalizada para todo nome coincidente.
- **APLICADA:** vínculo institucional já utilizável.

Se não for necessário unir UUIDs existentes, o importador aplica a confirmação na
próxima observação daquela ocorrência. Se precisar reunir UUIDs e dependentes,
a operação fica CONFIRMADA até o comando administrativo em janela sem escritores.
O importador e a API não movem avaliações de registros já existentes.

A aplicação revalida o grupo inteiro. Colisões de usuário/professor/disciplina ou
conflitos institucionais bloqueiam o grupo sem descarte ou aplicação parcial;
a fila mostra `APLICACAO_BLOQUEADA`, mantendo a confirmação e sua auditoria.
A prévia de uma ocorrência não garante ausência de colisão entre outras origens
do grupo, que é conferida novamente pelo comando.

## Implantação, permissão e aplicação operacional

1. Publicar backend/frontend compatíveis e aplicar a migration `20261111_01` com
   a conexão administrativa. O papel novo começa falso para todas as contas.
2. Aplicar [GRANTs adicionais](https://github.com/unb-mds/2026-02-UnDb/blob/fix/207-identidades-moderacao/scripts/sql/207-acesso-identidades.sql) como
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
aceito na conversa. Nome sozinho ou lotação nunca basta.

As turmas antigas podem não estar acessíveis por estarem encerradas, conforme
informação do PO. Falta em consulta atual não desfaz identidade ou avaliações
históricas. Pendências por indisponibilidade podem persistir até a próxima execução;
a consulta em cache não é reaproveitada entre execuções.
