import { test } from 'node:test';
import assert from 'node:assert/strict';
import { runInNewContext } from 'node:vm';
import { lerTextoPagina } from './browser-navigation.mjs';

test('documento sem body durante navegação é carregamento, não exceção', async () => {
  const documento = { body: null };
  const avaliar = async expression => runInNewContext(expression, { document: documento });
  assert.equal(await lerTextoPagina(avaliar), '');
  documento.body = { innerText: 'Comentários' };
  assert.equal(await lerTextoPagina(avaliar), 'Comentários');
});

test('troca de contexto CDP permite nova leitura no documento seguinte', async () => {
  let tentativa = 0;
  const avaliar = async () => {
    if (tentativa++ === 0) throw new Error('Cannot find context with specified id');
    return 'Página carregada';
  };
  assert.equal(await lerTextoPagina(avaliar), '');
  assert.equal(await lerTextoPagina(avaliar), 'Página carregada');
});

test('erro inesperado e asserção não são mascarados como carregamento', async () => {
  for (const erro of [new TypeError('falha do produto'), new Error('asserção rejeitada'), new Error('Timeout CDP Runtime.evaluate')]) {
    await assert.rejects(lerTextoPagina(async () => { throw erro; }), e => e === erro);
  }
});
