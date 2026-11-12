import { GitHub } from '../../../../functions-lib/github.js';

// Zahodenie konceptu: zavrie pull request a zmaže jeho vetvu. Nič sa nezverejní.
export async function onRequestPost({ env, params, data }) {
  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(Number(params.pr));
  await gh.zavri(k.pr.number);
  await gh.zmazVetvu(k.vetva);
  return Response.json({ ok: true });
}
