import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { SEKCIA_IDS } from './data/sekcie';

const clanky = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './content/clanky' }),
  schema: z.object({
    title: z.string().min(10).max(110),
    perex: z.string().min(40).max(320),
    sekcia: z.enum(SEKCIA_IDS),
    tagy: z.array(z.string()).default([]),
    publikovane: z.coerce.date(),
    aktualizovane: z.coerce.date().optional(),
    // Popisok, kredit aj licencia sú povinné: bez nich build zlyhá.
    obrazok: z.object({
      src: z.string(),
      alt: z.string().min(5),
      popisok: z.string().min(5),
      kredit: z.string().min(2),
      licencia: z.string().min(2),
      ai: z.boolean().default(false),
    }),
    // ID redaktorov zo src/data/redakcia.ts. Vzorové články ich nemajú.
    redaktori: z
      .object({
        autor: z.string(),
        factcheck: z.string(),
        korektura: z.string(),
        // Dopĺňa sa až pri zverejnení v redakčnom rozhraní.
        schvalil: z.string().optional(),
      })
      .optional(),
    zdroje: z.array(z.object({ nazov: z.string(), url: z.string() })).min(1),
    trace: z.string().optional(),
    vzorovy: z.boolean().default(false),
    opravy: z.array(z.object({ datum: z.coerce.date(), text: z.string() })).default([]),
  }),
});

export const collections = { clanky };
