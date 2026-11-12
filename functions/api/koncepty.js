import { GitHub } from '../../functions-lib/github.js';

// Zoznam otvorených konceptov.
export async function onRequestGet({ env }) {
  return Response.json({ koncepty: await new GitHub(env).koncepty() });
}
