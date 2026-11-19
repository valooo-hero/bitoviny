export function jeJpeg(bajty) {
  return bajty[0] === 0xff && bajty[1] === 0xd8 && bajty[2] === 0xff;
}

export function jeWebp(bajty) {
  return bajty[0] === 0x52 && bajty[1] === 0x49 && bajty[2] === 0x46 && bajty[3] === 0x46 &&
    bajty[8] === 0x57 && bajty[9] === 0x45 && bajty[10] === 0x42 && bajty[11] === 0x50;
}

function spojBajty(casti) {
  const vysledok = new Uint8Array(casti.reduce((velkost, cast) => velkost + cast.length, 0));
  let pozicia = 0;
  for (const cast of casti) {
    vysledok.set(cast, pozicia);
    pozicia += cast.length;
  }
  return vysledok;
}

// Z WebP s jedným snímkom zachová iba bloky potrebné na dekódovanie.
export function webpBezMetadat(bajty) {
  if (!jeWebp(bajty)) return null;
  const data = new DataView(bajty.buffer, bajty.byteOffset, bajty.byteLength);
  const koniec = data.getUint32(4, true) + 8;
  if (koniec > bajty.length) return null;
  const casti = [bajty.slice(0, 12)];
  let maObrazok = false;
  for (let i = 12; i < koniec;) {
    if (i + 8 > koniec) return null;
    const znacka = String.fromCharCode(...bajty.subarray(i, i + 4));
    const velkost = data.getUint32(i + 4, true);
    const dalsi = i + 8 + velkost + (velkost % 2);
    if (dalsi > koniec || znacka === 'ANIM' || znacka === 'ANMF') return null;
    if (znacka === 'VP8X') {
      if (velkost !== 10 || (bajty[i + 8] & 0x02)) return null;
      const hlavicka = bajty.slice(i, dalsi);
      hlavicka[8] &= 0x10; // Ponechá príznak priehľadnosti.
      casti.push(hlavicka);
    } else if (['VP8 ', 'VP8L', 'ALPH'].includes(znacka)) {
      if (znacka !== 'ALPH') maObrazok = true;
      casti.push(bajty.subarray(i, dalsi));
    }
    i = dalsi;
  }
  if (!maObrazok) return null;
  const vysledok = spojBajty(casti);
  new DataView(vysledok.buffer).setUint32(4, vysledok.length - 8, true);
  return vysledok;
}

// Odstráni aplikačné značky a komentáre. Časti s pixelmi ostávajú bitovo rovnaké.
export function jpegBezMetadat(bajty) {
  if (!jeJpeg(bajty)) return null;
  const casti = [];
  let zaciatok = 0;
  let vSkene = false;
  let maSken = false;
  for (let i = 2; i < bajty.length;) {
    const znacka = vSkene ? bajty.indexOf(0xff, i) : i;
    if (znacka === -1 || bajty[znacka] !== 0xff) return null;
    i = znacka + 1;
    while (bajty[i] === 0xff) i++;
    const typ = bajty[i++];
    if (vSkene && (typ === 0 || (typ >= 0xd0 && typ <= 0xd7))) continue;
    if (typ === 0xd9) {
      if (!maSken) return null;
      casti.push(bajty.subarray(zaciatok, i));
      return spojBajty(casti);
    }
    if (typ === 0x01) continue;
    const velkost = (bajty[i] << 8) | bajty[i + 1];
    const koniec = i + velkost;
    if (velkost < 2 || koniec > bajty.length) return null;
    // Štandardný Adobe APP14 môže byť potrebný na správnu interpretáciu farieb.
    const adobe = typ === 0xee && velkost === 14 &&
      String.fromCharCode(...bajty.subarray(i + 2, i + 7)) === 'Adobe';
    if (typ === 0xfe || (typ >= 0xe0 && typ <= 0xef && !adobe)) {
      casti.push(bajty.subarray(zaciatok, znacka));
      zaciatok = koniec;
    }
    vSkene = typ === 0xda;
    maSken ||= vSkene;
    i = koniec;
  }
  return null;
}
