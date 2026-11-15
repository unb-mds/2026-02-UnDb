"""Gera tabelas auditáveis a partir da execução; biblioteca padrão apenas."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / 'dataset.json').read_text(encoding='utf8'))
r = json.loads((HERE / 'resultados.json').read_text(encoding='utf8'))
def num(v): return f'{v:.3f}'.replace('.', ',')
def pct(v): return f'{v*100:.1f}%'.replace('.', ',')
def ids(result, relevant):
    return ', '.join(x['label'] + (' **(FP)**' if x['label'] not in relevant else '')
                     for x in result) or '∅'

lines = ['# Evidências reproduzíveis — busca, Issue #251', '',
         '[Avaliação e interpretação](../../avaliacao-busca-autocomplete-issue-251.md).', '',
         'Dados integralmente sintéticos. Listas em ordem de posição (primeiro item = posição 1). '
         'FP indica resultado fora do julgamento de intenção; ∅ indica ausência. '
         'P12 é alias de P1 e permanece fora de todas as consultas de listagem.', '',
         '## Catálogo', '', '| ID | Tipo | Nome | Código | Unidade |', '|---|---|---|---|---|']
for x in d['registros']:
    lines.append(f"| {x['label']} | {x['tipo']} | {x['nome']} | {x.get('codigo','—')} | {x['departamento']} |")
lines += ['', '## Casos e ordenação', '',
          'Meilisearch: não executado em todos os casos (bloqueio pelo Controle de Aplicativo do Windows). '
          'Não há resultados nem tempos atribuídos a esse motor. '
          'O caso 12 foi chamado diretamente na camada SQL; a interface vigente o impede.', '',
          '| Caso | Cenário / termo | Relevantes | Atual | Literal experimental | pg_trgm experimental (0,3) |',
          '|---|---|---|---|---|---|']
for x in r['casos']:
    lines.append(f"| {x['id']} | {x['cenario']}: `{x['termo']}` | {', '.join(x['relevantes']) or '∅'} | "
                 + ' | '.join(ids(x[k]['resultados'], x['relevantes']) for k in ['atual','literal','trgm']) + ' |')
lines += ['', '## Falsos negativos', '', '| Caso | Atual | Literal | pg_trgm 0,3 |', '|---|---|---|---|']
for x in r['casos']:
    missing = [', '.join(t for t in x['relevantes'] if t not in [z['label'] for z in x[k]['resultados']]) or '—'
               for k in ['atual','literal','trgm']]
    lines.append(f"| {x['id']} | " + ' | '.join(missing) + ' |')
lines += ['', '## Tempos por consulta', '',
          'Milissegundos, p50 / p95 de 30 repetições após aquecimento. Incluem ponte JavaScript/WASM e '
          'tratamento local, sem rede, FastAPI, React ou partidas a frio. Atual de disciplina inclui '
          'duas consultas sequenciais na conexão embarcada e ordenação local; o navegador faz a dupla em paralelo. '
          'Não servem para comparar latência HTTP de produção. No caso 12, a variante literal retorna sem SQL.', '',
          '| Caso | Atual p50 / p95 | Literal p50 / p95 | pg_trgm p50 / p95 |', '|---|---|---|---|']
for x in r['casos']:
    lines.append(f"| {x['id']} | " + ' | '.join(num(x[k]['tempo']['p50_ms'])+' / '+num(x[k]['tempo']['p95_ms'])
                                               for k in ['atual','literal','trgm']) + ' |')
lines += ['', '## Métricas lexicais', '',
          '24 consultas: excluídos 12 (UI bloqueia) e 22 (sonda de curingas), apresentados separadamente acima. '
          '45 pares consulta/registro relevantes, 22 consultas positivas e duas negativas. '
          'TP/FP/FN são contados por par; MRR usa a posição do primeiro relevante e zero quando ausente.', '',
          '| Variante | TP / FP / FN | Precisão | Cobertura | MRR | Consultas positivas com acerto |', '|---|---|---|---|---|---|']
for k in ['atual','literal','trgm']:
    x=r['metricas']['lexicais'][k]
    lines.append(f"| {k} | {x['tp']} / {x['fp']} / {x['fn']} | {pct(x['precision'])} | {pct(x['recall'])} | {num(x['mrr'])} | {x['consultas_com_acerto']}/22 |")
lines += ['', '## Varredura de limiar', '',
          'Conjunto completo de 26 consultas, inclusive as duas sondas de controle. '
          'Os oito retornos indevidos da consulta de uma letra são contabilizados aqui; '
          'não confundir esta precisão com a métrica lexical. Os casos 11 e 24 permanecem ausentes em todos os limiares '
          'porque aproximação em código foi desativada deliberadamente.', '',
          '| Limiar inclusivo do menor word_similarity por termo | TP / FP / FN | Precisão | Cobertura | MRR |',
          '|---|---|---|---|---|']
for t in ['0.3','0.4','0.5','0.6']:
    x=r['metricas']['trgm_'+t]
    lines.append(f"| {t.replace('.',',')} | {x['tp']} / {x['fp']} / {x['fn']} | {pct(x['precision'])} | {pct(x['recall'])} | {num(x['mrr'])} |")
lines += ['', '## Índices no ensaio auxiliar', '',
          '12.000 linhas artificiais; consulta `nome % \'maria emlia santos\'`, limiar padrão de `%` (0,3). '
          'Este é outro SQL, destinado a verificar planos e armazenamento: não comprova indexação da consulta por mínimo de '
          '`word_similarity` usada no corpus. GiST usa assinatura padrão. Os índices foram criados um por vez.', '',
          '| Índice | p50 / p95 (ms) | Tabela (bytes) | Índices (bytes) | Plano |', '|---|---|---|---|---|']
for k in ['sem_indice','gin','gist']:
    x=r['planos'][k]; size=x['tamanho'][0]
    plan=x['plano'][0]['QUERY PLAN'][0]['Plan']['Node Type']
    lines.append(f"| {k} | {num(x['tempo']['p50_ms'])} / {num(x['tempo']['p95_ms'])} | {size['tabela_bytes']} | {size['indices_bytes']} | {plan} |")
lines += ['', 'Planos completos, buffers, amostras individuais, pontuações e versões: '
          '[resultados.json](resultados.json). SQL do repository, parâmetros e judgments: [dataset.json](dataset.json). '
          'Comandos e limitações: [reprodução](reproducao.md).', '']
(HERE / 'resultados.md').write_text('\n'.join(lines), encoding='utf8')
print('Tabelas geradas a partir de resultados.json.')
