#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const STORE_PATH = path.join(process.env.HOME || '', '.openclaw', 'memory', 'local-rag-smoke-store.json');
const DIM = 512;

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function tokenize(text) {
  return String(text)
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(Boolean);
}

function normalize(vec) {
  const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0)) || 1;
  return vec.map((v) => v / norm);
}

function embed(text) {
  const vec = new Array(DIM).fill(0);
  for (const token of tokenize(text)) {
    const digest = crypto.createHash('sha256').update(token).digest();
    const idx = digest.readUInt16BE(0) % DIM;
    const sign = (digest[2] & 1) === 0 ? 1 : -1;
    vec[idx] += sign * (1 + token.length / 10);
  }
  return normalize(vec);
}

function cosine(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}

function loadStore() {
  try {
    return JSON.parse(fs.readFileSync(STORE_PATH, 'utf8'));
  } catch {
    return { entries: [] };
  }
}

function saveStore(store) {
  ensureDir(STORE_PATH);
  fs.writeFileSync(STORE_PATH, JSON.stringify(store, null, 2));
}

function add(text, metadata = {}) {
  const store = loadStore();
  const entry = {
    id: crypto.randomUUID(),
    text,
    metadata,
    createdAt: new Date().toISOString(),
    vector: embed(text),
  };
  store.entries.push(entry);
  saveStore(store);
  return entry;
}

function search(query, limit = 5) {
  const store = loadStore();
  const qv = embed(query);
  return store.entries
    .map((entry) => ({
      id: entry.id,
      text: entry.text,
      metadata: entry.metadata,
      createdAt: entry.createdAt,
      score: cosine(qv, entry.vector),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

function usage() {
  console.log(`Usage:
  node scripts/local_rag_smoke.js add "text to store"
  node scripts/local_rag_smoke.js search "query" [limit]
  node scripts/local_rag_smoke.js reset
  node scripts/local_rag_smoke.js stats`);
}

const [, , cmd, ...args] = process.argv;

if (!cmd) {
  usage();
  process.exit(1);
}

if (cmd === 'add') {
  const text = args.join(' ').trim();
  if (!text) {
    console.error('add requires text');
    process.exit(1);
  }
  const entry = add(text);
  console.log(JSON.stringify({ ok: true, action: 'add', entry }, null, 2));
} else if (cmd === 'search') {
  const limitArg = args.length > 1 ? Number(args[args.length - 1]) : NaN;
  const hasLimit = Number.isFinite(limitArg);
  const query = (hasLimit ? args.slice(0, -1) : args).join(' ').trim();
  const limit = hasLimit ? limitArg : 5;
  if (!query) {
    console.error('search requires query');
    process.exit(1);
  }
  console.log(JSON.stringify({ ok: true, action: 'search', query, results: search(query, limit) }, null, 2));
} else if (cmd === 'reset') {
  ensureDir(STORE_PATH);
  saveStore({ entries: [] });
  console.log(JSON.stringify({ ok: true, action: 'reset', path: STORE_PATH }, null, 2));
} else if (cmd === 'stats') {
  const store = loadStore();
  console.log(JSON.stringify({ ok: true, action: 'stats', path: STORE_PATH, entries: store.entries.length }, null, 2));
} else {
  usage();
  process.exit(1);
}
