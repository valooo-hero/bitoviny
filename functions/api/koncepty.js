import { GitHub } from '../../functions-lib/github.js';

// Zoznam otvorených konceptov.
export async function onRequestGet({ env, data }) {
  return Response.json({ koncepty: await new GitHub(env, data.token).koncepty() });
}
