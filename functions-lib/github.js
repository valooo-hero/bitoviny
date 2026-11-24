// Tenká vrstva nad GitHub REST API. Koncept je pull request z vetvy koncept/...

export const PREDPONA_VETVY = 'koncept/';
export const ZASTUPNY_OBRAZOK = '/obrazky/zastupny.jpg';

export function jeZastupnyObrazok(src) {
  return src === ZASTUPNY_OBRAZOK || src === '/obrazky/zastupny.svg';
}

export function naBase64(bajty) {
  let bin = '';
  for (let i = 0; i < bajty.length; i += 0x8000) bin += String.fromCharCode(...bajty.subarray(i, i + 0x8000));
  return btoa(bin);
}

export function zBase64NaText(b64) {
  const bin = atob(b64.replace(/\s/g, ''));
  return new TextDecoder().decode(Uint8Array.from(bin, (c) => c.charCodeAt(0)));
}

export class GitHub {
  /** token je oprávnenie prihláseného editora z relácie, nie trvalý token servera. */
  constructor(env, token) {
    if (!token) throw new Error('Chýba prístupový token.');
    this.repo = env.GITHUB_REPO || 'valooo-hero/bitoviny';
    this.token = token;
  }

  async api(metoda, cesta, telo, stranka = false) {
    const url = cesta.startsWith('https://api.github.com/') ? cesta : `https://api.github.com/repos/${this.repo}${cesta}`;
    const r = await fetch(url, {
      method: metoda,
      headers: {
        Authorization: `Bearer ${this.token}`,
        Accept: 'application/vnd.github+json',
        'User-Agent': 'bitoviny-admin',
        'X-GitHub-Api-Version': '2022-11-28',
      },
      body: telo ? JSON.stringify(telo) : undefined,
    });
    if (r.status === 204) return null;
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(`GitHub ${metoda} ${cesta}: ${r.status} ${data.message || ''}`);
    return stranka ? { data, link: r.headers.get('Link') } : data;
  }

  async vsetkyStrany(cesta) {
    const vysledok = [];
    const navstivene = new Set();
    while (cesta) {
      if (navstivene.has(cesta)) throw new Error('GitHub zopakoval adresu pri stránkovaní.');
      navstivene.add(cesta);
      const { data, link } = await this.api('GET', cesta, undefined, true);
      vysledok.push(...data);
      const dalsia = /<([^>]+)>;\s*rel="next"/.exec(link ?? '')?.[1];
      if (!dalsia) break;
      const url = new URL(dalsia);
      const predpona = '/repos/' + this.repo;
      const cestaRepozitara = url.pathname.startsWith(predpona + '/') || /^\/repositories\/\d+\//.test(url.pathname);
      if (url.origin !== 'https://api.github.com' || url.username || url.password || !cestaRepozitara) {
        throw new Error('GitHub vrátil neočakávanú adresu ďalšej strany.');
      }
      cesta = url.href;
    }
    return vysledok;
  }

  async suboryClankov() {
    const { tree, truncated } = await this.api('GET', '/git/trees/main?recursive=1');
    if (truncated) throw new Error('GitHub vrátil neúplný strom článkov.');
    return tree.filter((p) => p.type === 'blob' && p.path.startsWith('content/clanky/') && p.path.endsWith('.md'));
  }

  async *textyClankov(clanky) {
    const [owner, name] = this.repo.split('/');
    const davka = 24;
    for (let i = 0; i < clanky.length; i += davka) {
      const subory = clanky.slice(i, i + davka);
      const argumenty = subory.map((_, j) => '$sha' + j + ': GitObjectID!');
      const polia = subory.map((_, j) =>
        'clanok' + j + ': object(oid: $sha' + j + ') { ... on Blob { text isTruncated } }'
      );
      const query = 'query ($owner: String!, $name: String!, ' + argumenty.join(', ') + ') {' +
        ' repository(owner: $owner, name: $name) { ' + polia.join(' ') + ' } }';
      const variables = { owner, name, ...Object.fromEntries(subory.map((s, j) => ['sha' + j, s.sha])) };
      const odpoved = await fetch('https://api.github.com/graphql', {
        method: 'POST',
        headers: {
          Authorization: 'Bearer ' + this.token,
          'Content-Type': 'application/json',
          'User-Agent': 'bitoviny-admin',
        },
        body: JSON.stringify({ query, variables }),
      });
      const { data, errors } = await odpoved.json();
      if (!odpoved.ok || errors?.length || !data?.repository) {
        throw new Error('GitHub neposkytol archív na overenie duplicít.');
      }
      for (const [j, subor] of subory.entries()) {
        const blob = data.repository['clanok' + j];
        if (typeof blob?.text !== 'string' || blob.isTruncated) {
          throw new Error('GitHub vrátil neúplný článok z archívu.');
        }
        yield { path: subor.path, text: blob.text };
      }
    }
  }

  async koncepty() {
    const prs = await this.vsetkyStrany('/pulls?state=open&base=main&per_page=100&sort=created&direction=desc');
    return prs
      .filter((p) => p.head.ref.startsWith(PREDPONA_VETVY) && p.head.repo?.full_name === this.repo)
      .map((p) => ({
        pr: p.number,
        titulok: p.title.replace(/^Koncept:\s*/, ''),
        vetva: p.head.ref,
        vytvorene: p.created_at,
        url: p.html_url,
      }));
  }

  /** Pull request konceptu a cesty k jeho dvom súborom. Odmietne PR, ktorý nie je koncept. */
  async koncept(cislo) {
    const pr = await this.api('GET', `/pulls/${cislo}`);
    if (pr.state !== 'open') throw new Error('Pull request už nie je otvorený.');
    if (!pr.head.ref.startsWith(PREDPONA_VETVY) || pr.head.repo?.full_name !== this.repo) {
      throw new Error('Tento pull request nie je koncept z pipeline.');
    }
    const subory = await this.api('GET', `/pulls/${cislo}/files?per_page=100`);
    const clanok = subory.find((s) => /^content\/clanky\/[^/]+\.md$/.test(s.filename))?.filename;
    const sprava = subory.find((s) => /^redakcia\/spravy\/[^/]+\.json$/.test(s.filename))?.filename;
    if (!clanok) throw new Error('V pull requeste chýba článok.');
    return { pr, vetva: pr.head.ref, clanok, sprava, slug: clanok.split('/').pop().replace(/\.md$/, '') };
  }

  async subor(cesta, vetva) {
    const d = await this.api('GET', `/contents/${cesta.split('/').map(encodeURIComponent).join('/')}?ref=${encodeURIComponent(vetva)}`);
    return { text: zBase64NaText(d.content), sha: d.sha };
  }

  async zapis(cesta, vetva, obsahB64, sprava, sha) {
    return this.api('PUT', `/contents/${cesta.split('/').map(encodeURIComponent).join('/')}`, {
      message: sprava,
      branch: vetva,
      content: obsahB64,
      ...(sha ? { sha } : {}),
    });
  }

  async zapisText(cesta, vetva, text, sprava, sha) {
    return this.zapis(cesta, vetva, naBase64(new TextEncoder().encode(text)), sprava, sha);
  }

  /** Zmaže súbor vo vetve. Chýbajúci súbor nie je chyba. */
  async zmazSubor(cesta, vetva, sprava) {
    const sha = await this.shaSuboru(cesta, vetva);
    if (!sha) return;
    try {
      await this.api('DELETE', `/contents/${cesta}`, { message: sprava, branch: vetva, sha });
    } catch {
      // nepoužitý súbor vo vetve neškodí, zlyhanie mazania nesmie pokaziť hlavnú akciu
    }
  }

  async shaSuboru(cesta, vetva) {
    try {
      return (await this.api('GET', `/contents/${cesta}?ref=${encodeURIComponent(vetva)}`)).sha;
    } catch {
      return undefined;
    }
  }

  async zluc(cislo, titulok, sha) {
    // Tesne po zápise do vetvy GitHub ešte prepočítava, či sa dá zlúčiť, a zlúčenie
    // odmieta stavom 405 alebo 409. Preto sa pokus niekoľkokrát zopakuje. Parameter
    // sha zaručí, že sa zlúči presne tá verzia, ktorú editor schválil.
    let posledna;
    for (let pokus = 0; pokus < 10; pokus++) {
      try {
        return await this.api('PUT', `/pulls/${cislo}/merge`, { merge_method: 'squash', commit_title: titulok, ...(sha ? { sha } : {}) });
      } catch (e) {
        posledna = e;
        if (!/: 40[59] /.test(e.message)) throw e;
        await new Promise((r) => setTimeout(r, 1500));
      }
    }
    throw new Error(`Zlúčenie sa nepodarilo ani po opakovaní. ${posledna.message}`);
  }

  async zavri(cislo) {
    return this.api('PATCH', `/pulls/${cislo}`, { state: 'closed' });
  }

  async zmazVetvu(vetva) {
    try {
      await this.api('DELETE', `/git/refs/heads/${vetva}`);
    } catch {
      // vetva už neexistuje
    }
  }
}
