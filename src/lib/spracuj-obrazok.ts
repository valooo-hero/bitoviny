import { jeJpeg } from '../../functions-lib/format-obrazka.js';
import { GPT_IMAGE } from '../../functions-lib/modely-obrazkov.js';

export async function obrazokAkoJpg(subor: Blob, maxBajtov: number): Promise<string> {
  let jpg = subor;
  const hlavicka = new Uint8Array(await subor.slice(0, 3).arrayBuffer());
  if (!jeJpeg(hlavicka)) {
    const bitmapa = await createImageBitmap(subor).catch(() => {
      throw new Error('Obrázok sa nepodarilo načítať.');
    });
    const platno = document.createElement('canvas');
    try {
      platno.width = bitmapa.width;
      platno.height = bitmapa.height;
      const kontext = platno.getContext('2d');
      if (!kontext) throw new Error('Prevod obrázka na JPG zlyhal.');
      kontext.fillStyle = '#fff';
      kontext.fillRect(0, 0, platno.width, platno.height);
      kontext.drawImage(bitmapa, 0, 0);
      jpg = await new Promise<Blob>((ok, zle) => {
        platno.toBlob((blob) => {
          if (blob?.type === 'image/jpeg') ok(blob);
          else zle(new Error('Prevod obrázka na JPG zlyhal.'));
        }, 'image/jpeg', 0.88);
      });
    } finally {
      bitmapa.close();
    }
  }
  return obrazokNaBase64(jpg, maxBajtov);
}

export async function vygenerovanyObrazokAkoWebp(subor: Blob, model: string, maxBajtov: number): Promise<string> {
  const bitmapa = await createImageBitmap(subor);
  try {
    const platno = model === GPT_IMAGE.id ? await zvacsiGptObrazok(bitmapa) : platnoZBitmapy(bitmapa);
    const webp = await new Promise<Blob>((ok, zle) => {
      platno.toBlob((blob) => {
        if (blob?.type === 'image/webp') ok(blob);
        else zle(new Error('Prehliadač nedokáže uložiť obrázok WebP.'));
      }, 'image/webp', 0.75);
    });
    return obrazokNaBase64(webp, maxBajtov);
  } finally {
    bitmapa.close();
  }
}

function platnoZBitmapy(bitmapa: ImageBitmap, vyska = bitmapa.height): HTMLCanvasElement {
  const platno = document.createElement('canvas');
  platno.width = bitmapa.width;
  platno.height = vyska;
  const kontext = platno.getContext('2d');
  if (!kontext) throw new Error('Obrázok sa nepodarilo pripraviť na uloženie.');
  const hornyOkraj = (bitmapa.height - vyska) / 2;
  kontext.drawImage(bitmapa, 0, -hornyOkraj);
  return platno;
}

async function zvacsiGptObrazok(bitmapa: ImageBitmap): Promise<HTMLCanvasElement> {
  const { vstupnaSirka, vstupnaVyska, generovanaVyska, vystupnaSirka, vystupnaVyska } = GPT_IMAGE;
  if (bitmapa.width !== vstupnaSirka || bitmapa.height !== generovanaVyska) {
    throw new Error(`ChatGPT Images 2.0 vrátil rozlíšenie ${bitmapa.width} × ${bitmapa.height}. Očakáva sa ${vstupnaSirka} × ${generovanaVyska}.`);
  }
  // fal.ai vyžaduje rozmery deliteľné 16. Zo stredu vyberieme presný formát 16 : 9.
  const vstup = platnoZBitmapy(bitmapa, vstupnaVyska);
  const platno = document.createElement('canvas');
  platno.width = vystupnaSirka;
  platno.height = vystupnaVyska;
  const { default: pica } = await import('pica');
  return pica({ features: ['js'] }).resize(vstup, platno, { filter: 'lanczos3' });
}

function obrazokNaBase64(subor: Blob, maxBajtov: number): Promise<string> {
  if (subor.size > maxBajtov) throw new Error('Obrázok je po prevode väčší než 6 MB.');
  return new Promise<string>((ok, zle) => {
    const citac = new FileReader();
    citac.onload = () => {
      const dataUrl = String(citac.result);
      ok(dataUrl.slice(dataUrl.indexOf(',') + 1));
    };
    citac.onerror = () => zle(new Error('Súbor sa nepodarilo prečítať.'));
    citac.readAsDataURL(subor);
  });
}
