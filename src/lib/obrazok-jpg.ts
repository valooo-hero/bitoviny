import { jeJpeg } from '../../functions-lib/jpeg.js';

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
  if (jpg.size > maxBajtov) throw new Error('Obrázok je po prevode väčší než 6 MB.');
  return new Promise<string>((ok, zle) => {
    const citac = new FileReader();
    citac.onload = () => {
      const dataUrl = String(citac.result);
      ok(dataUrl.slice(dataUrl.indexOf(',') + 1));
    };
    citac.onerror = () => zle(new Error('Súbor sa nepodarilo prečítať.'));
    citac.readAsDataURL(jpg);
  });
}
