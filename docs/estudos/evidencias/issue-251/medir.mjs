// Artefato de estudo: PostgreSQL WASM em memória; Meilisearch local opcional.
// Não importa configuração, conexão, pacote ou serviço da aplicação.
import { readFile, writeFile, mkdtemp } from 'node:fs/promises';
import { createWriteStream } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { tmpdir } from 'node:os';
import { spawn } from 'node:child_process';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(await readFile(join(here, 'dataset.json'), 'utf8'));
if (!process.env.PGLITE_PACKAGE) throw Error('Defina PGLITE_PACKAGE para o pacote isolado, fora dos manifests do projeto.');
const { PGlite } = await import(pathToFileURL(join(process.env.PGLITE_PACKAGE, 'dist/index.js')));
const { pg_trgm } = await import(pathToFileURL(join(process.env.PGLITE_PACKAGE, 'dist/contrib/pg_trgm.js')));
const pg = new PGlite({ extensions: { pg_trgm } });
const byId = new Map(data.registros.map(r => [r.id, r]));
const collator = new Intl.Collator('pt-BR', { sensitivity: 'base' });
const compare = (a, b) => collator.compare(a.nome, b.nome) || collator.compare(a.departamento, b.departamento) || a.id.localeCompare(b.id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const percentile = (a, p) => [...a].sort((x,y) => x-y)[Math.ceil(a.length*p)-1];
const stats = a => ({ p50_ms: percentile(a, .5), p95_ms: percentile(a, .95), amostras_ms: a });
const project = rows => rows.map(r => ({ label: byId.get(r.id)?.label, id: r.id,
  score: r.score === undefined ? null : Number(r.score), faixa: r.faixa ?? null }));
async function timed(fn) {
  const start = performance.now(); const value = await fn();
  return { value, ms: performance.now()-start };
}
async function baseline(c) {
  const union = new Map();
  for (const q of c.queries_atual) {
    for (const r of (await pg.query(q.sql, q.params)).rows) union.set(r.id, byId.get(r.id));
  }
  return [...union.values()].sort(compare);
}
async function literal(c) {
  if(c.termo.trim().length<2) return [];
  const table=c.tipo==='professores'?'professores':'disciplinas';
  const filter=c.tipo==='professores'?'AND id NOT IN (SELECT origem_id FROM professor_correspondencias)':'';
  // Política experimental explícita: apóstrofos removidos, hífens viram espaços.
  const q=c.normalizado.replace(/['’]/g,'').replace(/[-–—]/g,' ').trim().split(/\s+/).join(' ');
  const name="regexp_replace(replace(replace(nome_normalizado,chr(39),''),'’',''),'[-–—]',' ','g')";
  const code=c.tipo==='disciplinas'?'OR strpos(lower(codigo),lower($2))>0':'';
  const rows=(await pg.query(`SELECT id FROM ${table} WHERE
    ((SELECT bool_and(strpos(${name},t)>0) FROM unnest(string_to_array($1,' ')) t) ${code}) ${filter}`,
    c.tipo==='disciplinas'?[q,c.termo.trim()]:[q])).rows;
  return rows.map(r=>byId.get(r.id)).sort(compare);
}
// Faixas experimentais: exato, prefixo, todos os termos literais, aproximado.
// Código não recebe aproximação nesta variante conservadora.
function fuzzyQuery(c, threshold = .3) {
  const table = c.tipo === 'professores' ? 'professores' : 'disciplinas';
  const filter = c.tipo === 'professores' ? 'AND id NOT IN (SELECT origem_id FROM professor_correspondencias)' : '';
  const code = c.tipo === 'disciplinas' && /^[a-z]+\d+$/i.test(c.termo.trim());
  const sql = code ? `SELECT id, 1.0 AS score, CASE WHEN lower(codigo)=$1 THEN 0 ELSE 1 END AS faixa
      FROM disciplinas WHERE strpos(lower(codigo),$1)>0 ORDER BY faixa,codigo,id LIMIT 8` : `
    WITH candidatos AS (
      SELECT id,nome,nome_normalizado,
        (SELECT min(word_similarity(t,nome_normalizado)) FROM unnest(string_to_array($1,' ')) t) AS score,
        CASE WHEN nome_normalizado=$1 THEN 0
          WHEN starts_with(nome_normalizado,$1) THEN 1
          WHEN (SELECT bool_and(strpos(nome_normalizado,t)>0) FROM unnest(string_to_array($1,' ')) t) THEN 2
          ELSE 3 END AS faixa
      FROM ${table} WHERE true ${filter}
    ) SELECT id,score,faixa FROM candidatos
      WHERE $1<>'' AND (faixa<3 OR (length($1)>=3 AND score >= $2))
      ORDER BY faixa,score DESC,nome,id LIMIT 8`;
  return { sql, params: code ? [c.termo.trim().toLowerCase()] : [c.normalizado, threshold] };
}
async function fuzzy(c, threshold) {
  const q = fuzzyQuery(c, threshold); return (await pg.query(q.sql, q.params)).rows;
}
function metrics(cases, key) {
  let tp=0,fp=0,fn=0,mrr=0,positive=0,queryHit=0,negative=0,negativeHit=0;
  for (const c of cases) {
    const ids=c[key].resultados.map(r => r.label), rel=c.relevantes;
    tp+=ids.filter(x=>rel.includes(x)).length;
    fp+=ids.filter(x=>!rel.includes(x)).length;
    fn+=rel.filter(x=>!ids.includes(x)).length;
    if (rel.length) { positive++; const rank=ids.findIndex(x=>rel.includes(x)); if(rank>=0){mrr+=1/(rank+1);queryHit++;} }
    else { negative++; if(ids.length)negativeHit++; }
  }
  return {tp,fp,fn,precision:tp/(tp+fp)||0,recall:tp/(tp+fn)||0,mrr:mrr/positive,
    consultas_positivas:positive,consultas_com_acerto:queryHit,consultas_negativas:negative,negativas_com_resultados:negativeHit};
}

let child, log;
try {
  await pg.exec('CREATE EXTENSION pg_trgm;');
  for (const ddl of data.ddl) await pg.exec(ddl);
  for(const u of data.unidades) await pg.query('INSERT INTO unidades (id,fonte,codigo,nome) VALUES ($1,\'SIGAA\',$2,$3)', [u.id,u.codigo,u.nome]);
  for(const r of data.registros) {
    if(r.tipo==='professores') await pg.query('INSERT INTO professores(id,nome,nome_normalizado,departamento,identidade_confirmada) VALUES($1,$2,$3,$4,false)',[r.id,r.nome,r.nome_normalizado,r.departamento]);
    else await pg.query('INSERT INTO disciplinas(id,codigo,nome,nome_normalizado,departamento) VALUES($1,$2,$3,$4,$5)',[r.id,r.codigo,r.nome,r.nome_normalizado,r.departamento]);
  }
  await pg.query('INSERT INTO professor_correspondencias(origem_id,destino_id,evidencia) VALUES($1,$2,$3)',
    [data.registros.find(r=>r.label==='P12').id,data.registros.find(r=>r.label==='P1').id,'alias sintético']);
  const metadata={ data_utc:new Date().toISOString(), commit:data.commit,node:process.version,python:data.python,
    sqlalchemy:data.sqlalchemy,pglite:'0.5.16',postgres:(await pg.query('SELECT version()')).rows,
    pg_trgm:(await pg.query("SELECT extversion FROM pg_extension WHERE extname='pg_trgm'")).rows,
    locale:(await pg.query('SELECT datcollate,datctype FROM pg_database WHERE datname=current_database()')).rows, repeticoes:30, warmup_por_consulta:1,
    escopo:'SQL PostgreSQL em WASM; latência inclui ponte JS. Se Meili for executado, inclui HTTP localhost. Não comparar como benchmark de produção.'};
  const cases=[];
  for(const c of data.casos) {
    const base=await baseline(c);
    assert.deepEqual(base.map(r=>r.label).sort(), [...c.sqlite_ids].sort(), `Paridade SQLite/PostgreSQL caso ${c.id}`);
    const row={id:c.id,termo:c.termo,tipo:c.tipo,cenario:c.cenario,relevantes:c.relevantes,
      ui_consultaria:c.termo.trim().length>=2,atual:{resultados:project(base)},literal:{resultados:project(await literal(c))},trgm:{resultados:project(await fuzzy(c,.3))},sweep:{}};
    for(const t of [.3,.4,.5,.6]) row.sweep[t]=project(await fuzzy(c,t));
    const baseTimes=[],trgmTimes=[],literalTimes=[];
    for(let i=0;i<30;i++) {
      baseTimes.push((await timed(()=>baseline(c))).ms);
      trgmTimes.push((await timed(()=>fuzzy(c,.3))).ms);
      literalTimes.push((await timed(()=>literal(c))).ms);
    }
    row.atual.tempo=stats(baseTimes); row.trgm.tempo=stats(trgmTimes);
    row.literal.tempo=stats(literalTimes);
    cases.push(row);
  }
  const probes=(await pg.query(`SELECT similarity('emliia','maria emilia dos santos') AS global_emliia,
    word_similarity('emliia','maria emilia dos santos') AS palavra_emliia,
    similarity('cic004','cic0004') AS codigo_omitido,
    similarity('cic0400','cic0004') AS codigo_trocado,
    similarity('emília','emilia') AS acento_cru,
    similarity('emilia','emilia') AS acento_normalizado,
    similarity('joao-pedro','joao pedro') AS pontuacao`)).rows;

  // Ensaio de planos isolado e artificial, separado do corpus de relevância.
  await pg.exec(`CREATE TABLE carga AS SELECT g AS id,
    CASE WHEN g%100=0 THEN 'maria emilia santos '||g ELSE 'docente sintetico '||g END AS nome
    FROM generate_series(1,12000) g; ANALYZE carga;`);
  const plans={};
  async function plan(label) {
    const q="SELECT id FROM carga WHERE nome % 'maria emlia santos'";
    await pg.query(q); const times=[];for(let i=0;i<30;i++)times.push((await timed(()=>pg.query(q))).ms);
    plans[label]={tempo:stats(times),plano:(await pg.query('EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) '+q)).rows,
      tamanho:(await pg.query("SELECT pg_table_size('carga') AS tabela_bytes,pg_indexes_size('carga') AS indices_bytes")).rows};
  }
  await plan('sem_indice');
  await pg.exec('CREATE INDEX carga_gin ON carga USING gin (nome gin_trgm_ops); ANALYZE carga;');await plan('gin');
  await pg.exec('DROP INDEX carga_gin; CREATE INDEX carga_gist ON carga USING gist (nome gist_trgm_ops); ANALYZE carga;');await plan('gist');
  plans.knn=(await pg.query("EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) SELECT id FROM carga ORDER BY nome <-> 'maria emlia santos' LIMIT 8")).rows;

  if(process.env.MEILI_BINARY) {
    const dir=await mkdtemp(join(tmpdir(),'undb-251-meili-'));
    metadata.meili_diretorio_temporario=dir;
    log=createWriteStream(join(dir,'ensaio.log'));
    child=spawn(process.env.MEILI_BINARY,['--http-addr','127.0.0.1:17700','--db-path',join(dir,'dados'),'--no-analytics'],
      {windowsHide:true,env:{...process.env,MEILI_ENV:'production',MEILI_MASTER_KEY:'chave-sintetica-local-issue-251'}});
    child.stdout.pipe(log,{end:false});child.stderr.pipe(log,{end:false});
    const base='http://127.0.0.1:17700';
    const api=async(path,method='GET',body)=> {
      const res=await fetch(base+path,{method,signal:AbortSignal.timeout(10000),
        headers:{Authorization:'Bearer chave-sintetica-local-issue-251','Content-Type':'application/json'},
        ...(body?{body:JSON.stringify(body)}:{})});
      const json=await res.json();if(!res.ok)throw Error(JSON.stringify(json));return json;
    };
    for(let i=0;;i++){try{await api('/health');break;}catch(e){if(i>=120||child.exitCode!==null)throw e;await sleep(250);}}
    metadata.meilisearch=await api('/version');
    const task=async t=>{for(let i=0;i<240;i++){const r=await api('/tasks/'+t.taskUid);if(r.status==='succeeded')return r;if(r.status==='failed')throw Error(JSON.stringify(r));await sleep(100);}throw Error('Timeout da tarefa de indexação');};
    const settings={searchableAttributes:['codigo','nome'],displayedAttributes:['id','nome','codigo','departamento','departamento_nome'],
      typoTolerance:{enabled:true,minWordSizeForTypos:{oneTypo:5,twoTypos:9},disableOnAttributes:['codigo']}};
    metadata.meili_settings_enviadas=settings;metadata.meili_tasks=[];
    for(const tipo of ['professores','disciplinas']) {
      metadata.meili_tasks.push(await task(await api('/indexes','POST',{uid:tipo,primaryKey:'id'})));
      metadata.meili_tasks.push(await task(await api(`/indexes/${tipo}/settings`,'PATCH',settings)));
      const docs=data.registros.filter(r=>r.tipo===tipo&&!r.alias).map(({id,nome,codigo,departamento,departamento_nome})=>({id,nome,codigo,departamento,departamento_nome}));
      metadata.meili_tasks.push(await task(await api(`/indexes/${tipo}/documents`,'POST',docs)));
    }
    metadata.meili_settings_efetivas=await api('/indexes/professores/settings');
    for(const c of cases) {
      const search=(matchingStrategy='last')=>api(`/indexes/${c.tipo}/search`,'POST',{q:c.termo,limit:8,showRankingScore:true,matchingStrategy});
      const first=await search(); const all=await search('all'); const times=[];
      for(let i=0;i<30;i++)times.push((await timed(search)).ms);
      c.meili={resultados:first.hits.map(r=>({label:byId.get(r.id).label,id:r.id,score:r._rankingScore})),
        tempo:stats(times),processingTimeMs:first.processingTimeMs,
        estrategia_all:all.hits.map(r=>({label:byId.get(r.id).label,id:r.id,score:r._rankingScore}))};
    }
    metadata.meili_stats=await api('/stats');
  }
  const summary={atual:metrics(cases,'atual'),literal:metrics(cases,'literal'),trgm:metrics(cases,'trgm')};
  const lexical=cases.filter(c=>!['12','22'].includes(c.id));
  summary.lexicais={casos:lexical.map(c=>c.id),atual:metrics(lexical,'atual'),literal:metrics(lexical,'literal'),trgm:metrics(lexical,'trgm')};
  if(!process.env.MEILI_BINARY) metadata.meilisearch_nao_executado=process.env.MEILI_BLOCK_REASON || 'Executável não fornecido';
  for(const t of [.3,.4,.5,.6]) summary['trgm_'+t]=metrics(cases.map(c=>({...c,temp:{resultados:c.sweep[t]}})),'temp');
  if(cases[0].meili) {summary.meili=metrics(cases,'meili');summary.meili_all=metrics(cases.map(c=>({...c,temp:{resultados:c.meili.estrategia_all}})),'temp');}
  const report={metadata,probes,planos:plans,metricas:summary,casos:cases};
  await writeFile(join(here,'resultados.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({metadata,metricas:summary},null,2));
} finally {
  if(child&&child.exitCode===null){child.kill();await new Promise(r=>child.once('exit',r));}
  log?.end();await pg.close();
}
