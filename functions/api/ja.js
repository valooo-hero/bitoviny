// Kto je prihlásený. Slúži rozhraniu na zistenie, či treba ukázať prihlásenie.
export async function onRequestGet({ data }) {
  return Response.json({ login: data.login });
}
