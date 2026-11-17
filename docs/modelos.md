# Modelos de dados

Os modelos abaixo complementam os diagramas Mermaid e as decisões registradas na
[documentação de arquitetura](arquitetura.md).

## Modelo conceitual

[Abrir modelo conceitual em PDF](diagramas/modelo%20conceitual.pdf){ .md-button }

## Modelo lógico

[Abrir modelo lógico em PDF](diagramas/modelo%20logico.pdf){ .md-button }

!!! info "Precedência"

    Se houver divergência entre estes diagramas e as decisões aprovadas em
    `docs/arquitetura.md`, a documentação arquitetural deve ser revisada antes de qualquer
    alteração de implementação.

## Complemento de RF26 — ciência dos Termos

Fonte: [RF26](requisitos.md#rf26-transparencia-termos-e-ciencia-no-cadastro-269),
[modelo atualizado de usuários](arquitetura.md#usuarios) e migration `20261117_02`.
O registro de usuário recebe `termos_versao` (VARCHAR(32)) e `termos_ciencia_em`
(TIMESTAMPTZ), ambos nulos para contas anteriores ou ambos preenchidos em novos cadastros.
CHECK garante o par; não há mudança de relacionamentos ou índices. Os PDFs acima
são recortes anteriores e ainda não incluem esse complemento aditivo.
