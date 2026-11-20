import { test } from 'node:test';
import assert from 'node:assert/strict';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
const carregar = arquivo => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const { consultarMinhasAvaliacoes } = await carregar('services/minhas-avaliacoes.js');
const { listarDestaques } = await carregar('services/destaques.js');
const { reenviarConfirmacao } = await carregar('services/auth.js');
const uuid = '11111111-1111-4111-8111-111111111111';
const item = {id:uuid,professor_id:uuid,disciplina_id:uuid,professor:{nome:'Docente'},disciplina:{nome:'Disciplina',codigo:'CIC'},didatica:4,dificuldade:'MEDIO',chamada:false,disponibiliza_material:false,qualidade_material:null,recomenda:true,updated_at:'2026-11-18T00:00:00Z'};

test('minhas avaliações usa credenciais, no-store, paginação e cancelamento', async t => {
 const c = new AbortController();
 t.mock.method(globalThis,'fetch',async(url,opcoes)=>{
  assert.match(url,/\/api\/avaliacoes\/minhas\?pagina=2$/);assert.equal(opcoes.credentials,'include');assert.equal(opcoes.cache,'no-store');assert.equal(opcoes.signal,c.signal);
  return Response.json({itens:[item],total:11,pagina:2,tamanho:10});
 });
 assert.equal((await consultarMinhasAvaliacoes(2,c.signal)).itens[0].didatica,4);
});
test('minhas avaliações rejeita contrato incompatível sem simular lista vazia', async t => {
 for(const resposta of [{},{itens:[],total:-1,pagina:1,tamanho:10},{itens:[{...item,didatica:9}],total:1,pagina:1,tamanho:10},{itens:[{...item,disponibiliza_material:true}],total:1,pagina:1,tamanho:10},{itens:[{...item,updated_at:'inválido'}],total:1,pagina:1,tamanho:10}]){
  const mock=t.mock.method(globalThis,'fetch',async()=>Response.json(resposta));
  await assert.rejects(consultarMinhasAvaliacoes(1));mock.mock.restore();
 }
});
test('página inválida não dispara requisição', async t=>{
 const mock=t.mock.method(globalThis,'fetch',()=>{throw Error('não deveria requisitar');});
 for(const pagina of [0,-1,1.1,NaN,100001])await assert.rejects(consultarMinhasAvaliacoes(pagina));
 assert.equal(mock.mock.callCount(),0);
});
test('reenvio envia somente e-mail e retorno opcional pelo contrato existente', async t=>{
 const corpos=[];t.mock.method(globalThis,'fetch',async(url,opcoes)=>{assert.match(url,/\/api\/auth\/reenviar-confirmacao$/);assert.equal(opcoes.credentials,'include');corpos.push(JSON.parse(opcoes.body));return Response.json({message:'Resposta neutra'},{status:202});});
 await reenviarConfirmacao('teste@aluno.unb.br',null);await reenviarConfirmacao('teste@aluno.unb.br','/destino-validado-pela-pagina');
 assert.deepEqual(corpos,[{email:'teste@aluno.unb.br'},{email:'teste@aluno.unb.br',return_to:'/destino-validado-pela-pagina'}]);
});
test('destaques consultam somente uma rota e preservam código e unidade', async t=>{
 const mock=t.mock.method(globalThis,'fetch',async(url)=>{assert.match(url,/\/api\/disciplinas\/destaques$/);return Response.json([{id:uuid,codigo:'CIC',nome:'Disciplina',departamento:'CIC',departamento_nome:'Computação',total_avaliacoes:2}]);});
 assert.equal((await listarDestaques())[0].departamentoNome,'Computação');assert.equal(mock.mock.callCount(),1);
});
test('destaques rejeitam resposta malformada ou contagem inexistente', async t=>{
 for(const resposta of [{},[{id:uuid,codigo:'CIC',nome:'Disciplina',departamento:'CIC',total_avaliacoes:0}]]){
  const mock=t.mock.method(globalThis,'fetch',async()=>Response.json(resposta));await assert.rejects(listarDestaques());mock.mock.restore();
 }
});
