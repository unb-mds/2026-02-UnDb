# Integração de denúncia de comentários e agradecimentos — Issue #193

**Estado:** integração de interface concluída e verificada conforme RF21 e decisões aprovadas.  
**Data da implementação:** 03/11/2026.  
**Rastreabilidade:** RF21, AC21-01, AC21-02, AC21-04, AC21-05 e decisões R2-DEC-06, R2-DEC-07, R2-DEC-08, R2-DEC-11, R2-DEC-12, R2-DEC-15.  
**Dependências consumidas:** APIs entregues pela PR #192 (`POST /api/comentarios/{versao_id}/denuncias`, `GET /api/agradecimentos`, `POST /api/agradecimentos/{id}/exibido`) e endpoints públicos de comentários de RF20 (`GET /api/professores/{id}/disciplinas/{id}/comentarios`).

---

## 1. Resumo da implementação

1. **Ação "Denunciar" sobre a versão publicada**:
   - Cada comentário exibido na jornada da disciplina vinculada ao professor (`/professores/[id]/disciplinas/[disciplinaId]`) disponibiliza a ação de denúncia operando estritamente sobre o UUID da versão publicada (`ComentarioVersao.id`).
   - Avaliação e critérios estruturados não são tratados como alvos.
2. **Seleção dos sete motivos fechados de RF21**:
   - `OFENSA_PESSOAL`, `XINGAMENTO`, `PALAVRAO`, `AMEACA`, `DISCRIMINACAO`, `EXPOSICAO_DADOS_PESSOAIS`, `SPAM`.
   - Sem justificativa livre textual, sem protocolo numérico e sem painel de acompanhamento posterior.
3. **Acesso universal (visitante e conta autenticada)**:
   - Denúncia permitida a visitantes anônimos e usuários autenticados (com ou sem e-mail confirmado).
   - Sem coleta de identidade, fingerprint ou IP do visitante no frontend.
4. **Respostas e erros HTTP reais**:
   - Confirmação real em status `201 Created` com a mensagem retornada pelo servidor.
   - Tratamento de `404 Not Found` (versão indisponível ou não publicada).
   - Tratamento de `409 Conflict` (denúncia aberta duplicada da mesma conta autenticada).
   - Tratamento de `422 Unprocessable Entity` (motivo/schema inválido).
   - Proteção contra duplo envio (desabilitação do botão de submissão e indicação de carregamento).
   - Não expõe contagens internas de denúncias nem status de suspensão.
5. **Agradecimentos a contas autenticadas**:
   - Consulta `GET /api/agradecimentos` com credenciais incluídas (`credentials: include`).
   - A consulta **não consome** mensagens.
   - Renderização no componente `AvisoAgradecimento` integrado no layout da aplicação.
   - Disparo de confirmação `POST /api/agradecimentos/{id}/exibido` após a exibição efetiva na interface, resultando no descarte pelo backend (`204 No Content`).
   - Não expõe identificadores da versão, do autor do comentário denunciado ou de outros denunciantes.
   - Visitantes sem sessão recebem lista vazia silenciosamente (sem rastreamento posterior).

---

## 2. Arquivos criados e alterados

| Arquivo | Finalidade |
|---|---|
| `frontend/src/lib/types/denuncia.ts` | Enum dos sete motivos fechados, rótulos textuais e tipos de denúncia e agradecimento. |
| `frontend/src/lib/types/comentario.ts` | Tipagem de comentários públicos (`id`, `texto`, `created_at`). |
| `frontend/src/lib/services/api-client.ts` | Suporte a respostas `204 No Content` sem falha de decodificação JSON. |
| `frontend/src/lib/services/denuncias.ts` | Funções de cliente HTTP para registrar denúncia, listar agradecimentos e confirmar exibição. |
| `frontend/src/lib/services/comentarios.ts` | Consulta de comentários públicos publicados por professor e disciplina. |
| `frontend/src/components/modal-denuncia.tsx` | Diálogo acessível para seleção do motivo e registro da denúncia com tratamento de erros. |
| `frontend/src/components/item-comentario.tsx` | Apresentação do comentário textual com botão e acionamento da denúncia. |
| `frontend/src/components/secao-comentarios.tsx` | Seção de comentários públicos integrada na rota de avaliação agregada. |
| `frontend/src/components/aviso-agradecimento.tsx` | Notificação de agradecimento persistente até a primeira exibição, com confirmação `POST exibido`. |
| `frontend/src/app/layout.tsx` | Inclusão de `AvisoAgradecimento` logo após o cabeçalho. |
| `frontend/src/app/professores/[id]/disciplinas/[disciplinaId]/page.tsx` | Integração dos comentários públicos na página da disciplina. |
| `frontend/tests/denuncia.test.mjs` | Testes unitários do serviço e validações (44 testes aprovados na suíte). |
| `frontend/tests/denuncia-browser.mjs` | Teste em navegador (Edge/Chromium) cobrindo desktop/mobile, 201, 404, 409 e agradecimentos. |
| `frontend/tests/run-tests.mjs` | Inclusão dos novos módulos na suíte `npm test`. |
| `frontend/package.json` | Scripts `test:denuncia` e atualização de `test:browser`. |
| `mkdocs.yml` | Adição deste estudo à navegação da documentação. |

---

## 3. Como testar manualmente

1. **Subir ambiente de desenvolvimento**:
   - Backend rodando em `http://localhost:8000`.
   - Frontend rodando em `http://localhost:3000` (`npm run dev`).
2. **Denúncia por visitante**:
   - Acesse uma disciplina de professor com comentários publicados, por exemplo `/professores/{id}/disciplinas/{disciplinaId}` sem estar logado.
   - Localize o comentário e clique em "Denunciar".
   - Verifique que o diálogo exibe os 7 motivos sem caixa de texto livre.
   - Selecione um motivo (ex.: "Spam") e clique em "Confirmar denúncia".
   - Verifique a mensagem: "Denúncia registrada. Obrigado por contribuir."
3. **Denúncia duplicada por conta autenticada**:
   - Faça login com uma conta de estudante (`/login`).
   - Retorne à disciplina e denuncie o mesmo comentário.
   - Ao tentar denunciar novamente a mesma versão pela mesma conta, verifique o aviso de erro: "Você já possui uma denúncia aberta para este comentário."
4. **Exibição de agradecimentos**:
   - Quando um comentário denunciado pela sua conta for suspenso (por atingir 50 denúncias) ou removido por um moderador humano, acesse a aplicação logado.
   - O banner de agradecimento será exibido no topo: "Obrigado por contribuir com a moderação do conteúdo."
   - Ao recarregar ou navegar para outra página, verifique que a mensagem foi consumida e não é exibida novamente.

---

## 4. Checklist dos critérios de conclusão

- [x] **Alvo de denúncia**: Ação "Denunciar" opera exclusivamente sobre o UUID da versão publicada retornado pela consulta pública. Critérios estruturados e avaliação não são alvos.
- [x] **Permissões e motivos de RF21**: Permitida denúncia por visitante e conta autenticada (mesmo sem e-mail confirmado). Seleção restrita aos sete motivos fechados, sem justificativa livre, protocolo ou painel de acompanhamento.
- [x] **Integração `POST /api/comentarios/{versao_id}/denuncias`**: Confirmação real em 201; tratamento de 404 (indisponível), 409 (duplicada aberta) e 422 (schema/motivo inválido). Sem contagens ou suspensão reveladas; duplo envio evitado.
- [x] **Integração de agradecimentos**: `GET /api/agradecimentos` e confirmação de primeira exibição via `POST /api/agradecimentos/{id}/exibido`. A consulta não consome mensagens; consumo ocorre no servidor após confirmação de exibição. Sem exposição de versão, autor ou outros denunciantes.
- [x] **Preservação de contexto e privacidade**: Sessão, critérios estruturados, layout e acessibilidade preservados. Visitantes não recebem acompanhamento posterior.
- [x] **Verificação automatizada e responsividade**: Testes unitários/integração cobrindo visitante, conta não confirmada, duplicidade, versão indisponível e agradecimento. Responsividade em 1280px e 320px sem rolagem horizontal.
- [x] **Rastreabilidade**: Fluxo integrado disponibilizado para a issue de testes integrados #163 rastreado a AC21-01, AC21-02, AC21-04 e AC21-05. A contagem de limiar e suspensão automática de AC21-03 permanecem no backend, sem recálculo pelo frontend.

---

## 5. Evidências e limitações para a #163

- **AC21-01**: Verificado. Visitantes e contas sem e-mail confirmado registram denúncias com qualquer um dos 7 motivos válidos e recebem confirmação 201; motivos fora da lista são rejeitados antes e no backend (422).
- **AC21-02**: Verificado. Mesma conta autenticada recebe erro 409 ao tentar segunda denúncia aberta para a mesma versão. Visitantes podem enviar repetições sem bloqueio de sessão.
- **AC21-04**: Verificado. A interface envia o UUID da versão específica clicada; não transfere denúncias para novas versões ou avaliações. Versões já suspensas ou retiradas retornam 404.
- **AC21-05**: Verificado. O endpoint `GET /api/agradecimentos` lista mensagens pendentes de suspensão/remoção para contas autenticadas; cada mensagem é confirmada individualmente via `POST /api/agradecimentos/{id}/exibido` e deixa de aparecer em consultas subsequentes.
- **Limitações**: A contagem de 50 denúncias e o gatilho de suspensão (AC21-03) pertencem exclusivamente ao backend e banco PostgreSQL; a interface não audita nem recalcula o limiar.
