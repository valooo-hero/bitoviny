import assert from 'node:assert/strict';
import { test } from 'node:test';

import { zloz } from '../functions-lib/clanok.js';
import { GitHub } from '../functions-lib/github.js';
import { onRequestPost } from '../functions/api/koncept/[pr]/zverejnit.js';

test('zoznam konceptov nasleduje GitHub Link aj pri stránke zadanej ID repozitára', async (t) => {
  const gh = new GitHub({ GITHUB_REPO: 'test/bitoviny' }, 'test-token');
  t.mock.method(globalThis, 'fetch', async (adresa) => {
    if (adresa.includes('/repos/test/bitoviny/pulls?')) {
      return Response.json([], { headers: { Link: '<https://api.github.com/repositories/7/pulls?page=2>; rel="next"' } });
    }
    assert.equal(adresa, 'https://api.github.com/repositories/7/pulls?page=2');
    return Response.json([{
      number: 42, title: 'Koncept: Starý koncept', created_at: '2025-11-12T00:00:00Z',
      head: { ref: 'koncept/stary', repo: { full_name: 'test/bitoviny' } },
    }]);
  });
  assert.equal((await gh.koncepty())[0].pr, 42);
});

test('ručné zverejnenie duplicitného konceptu vráti 409 pred zápisom alebo zlúčením', async (t) => {
  const hlavicka = {
    title: 'Nový nadpis tej istej technologickej správy',
    perex: 'Dostatočne dlhý perex správy s podrobnejším vysvetlením.',
    obrazok: { src: '/obrazky/test.webp', kredit: 'Redakcia', licencia: 'CC0', popisok: 'Ilustrácia' },
    zdroje: [{ url: 'https://www.test.sk/sprava/?utm_source=rss&id=3' }],
  };
  const text = 'Veta v článku. '.repeat(20);
  const zapis = [];
  t.mock.method(globalThis, 'fetch', async (adresa, { method, body }) => {
    zapis.push([adresa, method]);
    if (adresa.endsWith('/pulls/42')) {
      return Response.json({ number: 42, state: 'open', head: { ref: 'koncept/test', repo: { full_name: 'test/bitoviny' } } });
    }
    if (adresa.includes('/pulls/42/files')) {
      return Response.json([{ filename: 'content/clanky/novy.md' }]);
    }
    if (adresa.includes('/contents/content/clanky/novy.md')) {
      return Response.json({ content: Buffer.from(zloz(hlavicka, text)).toString('base64'), sha: 'koncept-sha' });
    }
    if (adresa.endsWith('/git/trees/main?recursive=1')) {
      return Response.json({ truncated: false, tree: [{ path: 'content/clanky/povodny.md', type: 'blob', sha: 'main-sha' }] });
    }
    assert.equal(adresa, 'https://api.github.com/graphql');
    assert.equal(method, 'POST');
    assert.equal(JSON.parse(body).variables.sha0, 'main-sha');
    const stare = {
      ...hlavicka, title: 'Pôvodný článok', publikovane: new Date(Date.now() - 60_000).toISOString(),
      zdroje: [{ url: 'http://test.sk/sprava?id=3#fragment' }],
    };
    return Response.json({ data: { repository: { clanok0: { text: zloz(stare, text), isTruncated: false } } } });
  });
  const response = await onRequestPost({
    env: { GITHUB_REPO: 'test/bitoviny' }, data: { token: 'test-token' }, params: { pr: 42 },
    request: new Request('https://redakcia.example', { method: 'POST', body: JSON.stringify({ potvrdenie: true }) }),
  });
  assert.equal(response.status, 409);
  assert.match(JSON.stringify(await response.json()), /povodny/);
  assert.equal(zapis.length, 5);
  assert.ok(zapis.filter(([, method]) => method === 'POST').every(([adresa]) => adresa.endsWith('/graphql')));
});
