# POC de viabilidade da coleta pública SIGAA — Issue #23

**Investigação executada em:** 13/09/2026 (resposta HTTP `Date`: 17:52:31 UTC)

**Escopo:** verificar RF16 com uma oferta pública real. Esta POC não implementa RF17–RF19,
persistência, job, fila ou API.

## Conclusão

- **Viabilidade:** **VIÁVEL COM RESSALVAS**.
- **Método:** **HTTP SUFICIENTE**.
- **Browser automation:** não necessária para o fluxo demonstrado; não foi instalada nem testada,
porque a resposta HTML ao postback HTTP contém os dados necessários.

## Caso real e navegação reproduzida

Caso usado: Graduação, `DEPTO CIÊNCIAS DA COMPUTAÇÃO - BRASÍLIA` (valor atual `508`),
período `2026.2`.

1. `GET https://sigaa.unb.br/sigaa/public/home.jsf` cria a sessão pública (`JSESSIONID`).
2. Na mesma sessão, `GET https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino`.
   A página devolveu o formulário `formTurma`, `javax.faces.ViewState=j_id1`, as opções
   atuais e o controle dinâmico `formTurma:j_id_jsp_1370969402_11=Buscar`.
3. Na mesma sessão, `POST https://sigaa.unb.br/sigaa/public/turmas/listar.jsf`, com nível
   `G`, unidade `508`, ano `2026`, período `2`, ViewState e botão lidos no passo anterior.
4. A resposta foi `200 OK` na própria rota, com rodapé `108 turmas encontrada(s)` e tabela
   HTML. Não houve JavaScript necessário para construir a tabela.

Os nomes do botão, ViewState e valores do formulário **não são constantes no código**: a
POC os extrai de cada resposta. O cookie fica somente em memória.

## Evidência: origem real → extração

Fonte: primeira linha de dados da resposta do POST acima, sob o agrupador exibido pelo SIGAA.

| Dado | Valor exibido na origem | Valor extraído pela POC | Resultado |
| --- | --- | --- | --- |
| Disciplina | `CIC0002 - FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO` | código `CIC0002`; nome `FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO` | OK |
| ID do componente | `177942`, no comando JSF do agrupador | `177942` | OK |
| Turma | `01` | `01` | OK |
| Período | `2026.2` | `2026.2` | OK |
| Professor | `MARIA EMILIA MACHADO TELLES WALTER (60h)` | `MARIA EMILIA MACHADO TELLES WALTER` | OK (carga horária removida) |

Na execução registrada, a saída da POC informou `108` ofertas extraídas e a origem exibiu `108` turmas encontradas.

## Como reproduzir

Pré-requisito: Python 3.12 (biblioteca padrão; nenhuma dependência nova) e acesso à internet.
Na raiz do repositório:

```bash
cd backend
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m app.scrapers.sigaa_poc --real
```

O primeiro comando executa os **testes determinísticos do parser**. Eles usam HTML mínimo
representativo da estrutura observada, não acessam o SIGAA e são os únicos apropriados para
automação no CI.

O segundo comando (`--real`) é uma **validação integrativa/manual contra o SIGAA real**:
faz consultas públicas, de leitura, e deve imprimir JSON contendo `total_reportado`,
`ofertas_extraidas` e a primeira oferta. Ele não é determinístico, não deve ser obrigatório
no CI e depende da disponibilidade e do comportamento atual do SIGAA. Serve como evidência
da investigação da Issue #23; falha, redirect ou divergência entre total e linhas devem ser
tratados como resultado integrativo inconclusivo/falha, não como aprovação.

## Fatos observados

- A consulta de turmas é JSF e usa ViewState, postback e sessão pública; sem preservar sessão
  o servidor pode redirecionar ao portal.
- Para o caso real, HTTP com cookie jar, GET inicial e POST form-encoded devolveu os dados
  completos em HTML. A tabela não dependeu de execução de JavaScript no cliente.
- Cada agrupador vincula a turma a um componente e expõe ID numérico de componente. A célula
  de docente traz texto e carga horária; ela não expõe SIAPE nem identificador inequívoco.
- Há casos de múltiplos docentes no mesmo campo, conforme o levantamento #22.

## Limitações e riscos

- O êxito cobre uma unidade e um período, não a cobertura de todos os departamentos (RF17),
  atualização (RF18) ou log operacional (RF19).
- Não foi confirmado identificador público estável de turma. A identidade professor–turma
  ainda é textual; homônimos e múltiplos docentes exigem decisão de modelo na Issue #24.
- JSF torna o coletor sensível a mudança de HTML, nomes de controles, sessão e ViewState.
  A implementação futura deve registrar por unidade falhas/redirects e continuar as demais,
  conforme RF19 e RNF07.
- Não foram testados paginação, limites internos, todos os períodos ou todas as unidades.
- Dados públicos e página externa podem mudar ou ficar indisponíveis; não há aprovação para
  inferir créditos a partir da carga horária.

## Impacto arquitetural e dependências

**Alternativa observada — HTTP com biblioteca padrão:** preserva a separação já documentada
(`scraper` fora da API e coleta antes de persistência), sem navegador, Docker adicional ou
dependência Python. Tem baixo custo operacional, mas requer parser resiliente ao HTML/JSF.

**Alternativa não acionada — automação de navegador:** seria justificável somente se um fluxo
futuro não devolvesse conteúdo suficiente via HTTP reproduzível. Ela acrescentaria runtime de
navegador, imagem/container maior, provável ajuste de CI/CD e custo de manutenção. Não há
evidência atual que justifique essa dependência estrutural.

**Recomendação proposta (não decisão aprovada):** para a implementação futura, começar com
cliente HTTP com sessão, extração dinâmica dos controles e validação de resposta; manter
automação de navegador fora do escopo até surgir evidência de insuficiência. A adoção do
coletor de produção, o modelo de identidade e qualquer dependência estrutural continuam
`Pending Decision` e exigem aprovação da equipe.
