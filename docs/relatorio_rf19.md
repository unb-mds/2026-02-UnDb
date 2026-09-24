1. Objetivo
Validar o comportamento do serviço de importação de dados do SIGAA perante cenários mistos de sucesso, erros de restrição de negócio (domínio) e falhas de parâmetros, garantindo que o sistema mantém a resiliência global sem interromper o fluxo de execução (conforme especificado no requisito RF19).

2. Massa de Testes Utilizada
Execução amostral com três unidades no parâmetro de entrada:
Ciência da Computação (ID/Nome real): Processamento de turmas e disciplinas.
Matemática (ID/Nome real): Processamento de turmas, gerando logs estruturados de validação de regras de negócio (ex: restrições de co-docência em turmas de Cálculo).
Física (Teste Falha): Injeção intencional de um parâmetro inválido/inexistente para testar o isolamento de exceções.


    === REGISTO DE EXECUÇÃO (RF19) ===
{
  "sucesso": false,
  "ano": "2026",
  "periodo": "2",
  "inicio": "2026-09-24T17:17:29.259413+00:00",
  "fim": "2026-09-24T17:17:39.359649+00:00",
  "departamentos": [
    {
      "departamento": "Ciência da Computação",
      "unidade_sigaa": "DEPTO CIÊNCIAS DA COMPUTAÇÃO - BRASÍLIA",
      "sucesso": false,
      "total_reportado": 108,
      "ofertas_extraidas": 108,
      "ofertas_processadas": 98,
      "erros": [
        "turma '02' de 'CIC0004': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '02' possui 2.",
        "turma '12' de 'CIC0004': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '12' possui 2.",
        "turma '01' de 'CIC0005': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '01' possui 2.",
        "turma '06' de 'CIC0007': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '06' possui 2.",
        "turma '12' de 'CIC0007': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '12' possui 2.",
        "turma '01' de 'CIC0152': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '01' possui 2.",
        "turma '01' de 'CIC0190': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '01' possui 3.",
        "turma '01' de 'CIC0208': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '01' possui 2.",
        "turma '01' de 'CIC0209': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '01' possui 2.",
        "turma '01' de 'CIC0247': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '01' possui 2."
      ]
    },
    {
      "departamento": "Matemática",
      "unidade_sigaa": "DEPARTAMENTO DE MATEMÁTICA - BRASÍLIA",
      "sucesso": false,
      "total_reportado": 130,
      "ofertas_extraidas": 130,
      "ofertas_processadas": 102,
      "erros": [
        "turma '02' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '02' possui 2.",
        "turma '03' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '03' possui 2.",
        "turma '04' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '04' possui 2.",
        "turma '05' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '05' possui 2.",
        "turma '06' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '06' possui 2.",
        "turma '07' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '07' possui 2.",
        "turma '08' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '08' possui 2.",
        "turma '09' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '09' possui 2.",
        "turma '10' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '10' possui 2.",
        "turma '11' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '11' possui 2.",
        "turma '12' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '12' possui 2.",
        "turma '13' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '13' possui 2.",
        "turma '14' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '14' possui 2.",
        "turma '15' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '15' possui 2.",
        "turma '16' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '16' possui 2.",
        "turma '17' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '17' possui 2.",
        "turma '18' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '18' possui 2.",
        "turma '19' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '19' possui 2.",
        "turma '21' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '21' possui 2.",
        "turma '22' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '22' possui 2.",
        "turma '23' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '23' possui 2.",
        "turma '28' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '28' possui 2.",
        "turma '29' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '29' possui 2.",
        "turma '30' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '30' possui 2.",
        "turma '31' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '31' possui 2.",
        "turma '32' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '32' possui 2.",
        "turma '34' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '34' possui 2.",
        "turma '35' de 'MAT0025': OfertaNaoPersistivelError: A oferta deve possuir exatamente um docente para o modelo atual; turma '35' possui 2."
      ]
    },
    {
      "departamento": "Física (Teste Falha)",
      "unidade_sigaa": "DEPARTAMENTO INVENTADO PARA FALHAR",
      "sucesso": false,
      "total_reportado": null,
      "ofertas_extraidas": 0,
      "ofertas_processadas": 0,
      "erros": [
        "ValueError: Opção não encontrada no formulário SIGAA: 'DEPARTAMENTO INVENTADO PARA FALHAR'"
      ]
    }
  ]
}

3. Evidências de Execução (Registo Estruturado)
O script validar_issue27.py foi executado com sucesso, gerando o seguinte relatório em formato JSON que comprova o isolamento dos erros e a continuidade do processo:

  "sucesso": false,
  "ano": "2026",
  "periodo": "2",
  "inicio": "2026-09-24T17:17:29.259413+00:00",
  "fim": "2026-09-24T17:17:39.359649+00:00",
  "departamentos": 
    

4. Persistência na Base de Dados
Verificação dos dados gravados com sucesso no PostgreSQL (porta 15432), comprovando que os dados válidos foram armazenados apesar das exceções tratadas nas restantes linhas.



                  id                  |            disciplina_id             |             professor_id             | semestre 
--------------------------------------+--------------------------------------+--------------------------------------+----------
 38a45b29-42fe-4842-88d0-0fd2c860e81f | 1260bc2f-60bc-4624-8540-f3b18bf06ee1 | 4ac2a469-9d9c-463c-91d3-affc1b00b043 | 2026.2
 f02128da-f17f-4f66-a003-efd4eee981f2 | 1260bc2f-60bc-4624-8540-f3b18bf06ee1 | 488efe46-b88b-4972-ad80-72b71d88a2f0 | 2026.2
 8a60e76c-621a-4403-a6e2-8bf1118f9708 | a4a45587-9186-4952-bbb9-78a608d5dbad | eb08c154-bc16-4452-baff-afbd5fab9e86 | 2026.2
 38229dc9-a388-4fbc-99ee-fdb70b104775 | e343a722-404e-4fa0-a6f3-2acf0c457529 | fedced0d-29e7-4753-8cdc-392719153633 | 2026.2
 0b8d04ca-324b-4e84-9b98-1f80bf598ca3 | e343a722-404e-4fa0-a6f3-2acf0c457529 | f50d6f96-a43d-4f35-a446-9c5edf382537 | 2026.2
(5 rows)


5. Conclusão
O requisito RF19 encontra-se validado e implementado com sucesso. O sistema lida com exceções de forma resiliente, registando detalhadamente os erros por departamento sem comprometer a estabilidade da aplicação.