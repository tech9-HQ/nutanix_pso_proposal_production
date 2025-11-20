// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

const app = express();
app.use(cors());
app.use(express.json());

// Read from .env
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
const PORT = process.env.PORT || 3000;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.error('Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Basic endpoints

// GET /api/catalog -> { categories: [...], services: [{category_name, service_name, ...}] }
app.get('/api/catalog', async (req, res) => {
  try {
    // Adjust table name/columns as per your schema (example: "proposals" table)
    const table = process.env.SUPABASE_TABLE || 'proposals';
    const { data, error } = await supabase
      .from(table)
      .select('category_name,service_name,positioning,description,price_man_day,duration_days,default_days')
      .order('category_name', { ascending: true });

    if (error) {
      console.error('Supabase catalog error', error);
      return res.status(500).json({ error: 'Supabase error' });
    }

    const categories = Array.from(new Set((data || []).map(d => d.category_name).filter(Boolean)));
    const services = (data || []).map(d => ({
      category_name: d.category_name || '',
      service_name: d.service_name || '',
      positioning: d.positioning || null,
      description: d.description || null,
      price_man_day: d.price_man_day || null,
      duration_days: d.duration_days || null,
      default_days: d.default_days || null
    }));
    res.json({ categories, services });
  } catch (err) {
    console.error('catalog exception', err);
    res.status(500).json({ error: 'Internal error' });
  }
});

// GET /api/categories -> { categories: [...] }
app.get('/api/categories', async (req, res) => {
  try {
    const table = process.env.SUPABASE_TABLE || 'proposals';
    const { data, error } = await supabase
      .from(table)
      .select('category_name')
      .not('category_name', 'is', null);

    if (error) { console.error(error); return res.status(500).json({ error: 'Supabase error' }); }
    const categories = Array.from(new Set((data || []).map(d => d.category_name).filter(Boolean)));
    res.json({ categories });
  } catch (err) {
    console.error('categories exception', err);
    res.status(500).json({ error: 'Internal error' });
  }
});

// GET /api/services?category=... -> { services: [service_name,...] }
app.get('/api/services', async (req, res) => {
  try {
    const category = req.query.category || '';
    const table = process.env.SUPABASE_TABLE || 'proposals';
    let query = supabase.from(table).select('service_name,category_name').not('service_name','is',null);
    if (category) query = query.eq('category_name', category);
    const { data, error } = await query;
    if (error) { console.error(error); return res.status(500).json({ error: 'Supabase error' }); }
    const services = Array.from(new Set((data || []).map(d => d.service_name).filter(Boolean)));
    res.json({ services });
  } catch (err) {
    console.error('services exception', err);
    res.status(500).json({ error: 'Internal error' });
  }
});

// GET /api/service_details?service_name=... -> returns first matched row with details
app.get('/api/service_details', async (req, res) => {
  try {
    const svc = req.query.service_name;
    if (!svc) return res.status(400).json({ error: 'service_name required' });
    const table = process.env.SUPABASE_TABLE || 'proposals';
    const { data, error } = await supabase
      .from(table)
      .select('*')
      .ilike('service_name', svc)
      .limit(1);

    if (error) { console.error('service_details error', error); return res.status(500).json({ error: 'Supabase error' }); }
    if (!data || !data.length) return res.json(null);
    res.json(data[0]);
  } catch (err) {
    console.error('service_details exception', err);
    res.status(500).json({ error: 'Internal error' });
  }
});

/**
 * NOTE:
 * - The following generate_proposal endpoint is a placeholder that forwards payload to your
 *   existing generation backend. If you already have a generator at another backend port (e.g. 8000),
 *   either proxy it or implement generation here. To keep this example minimal we will proxy
 *   through to env.GENERATE_URL if present.
 */
app.post('/api/generate_proposal', async (req, res) => {
  try {
    const GENERATE_URL = process.env.GENERATE_URL || null;
    if (!GENERATE_URL) return res.status(501).json({ error: 'No generate endpoint configured on server (set GENERATE_URL in .env)' });

    // forward request to GENERATE_URL
    const fetch = require('node-fetch');
    const r = await fetch(GENERATE_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req.body) });
    const buffer = await r.buffer();
    res.set('Content-Type', r.headers.get('content-type') || 'application/octet-stream');
    const cd = r.headers.get('content-disposition');
    if (cd) res.set('Content-Disposition', cd);
    res.status(r.status).send(buffer);
  } catch (err) {
    console.error('generate_proposal proxy error', err);
    res.status(500).json({ error: 'Failed to generate proposal' });
  }
});

// Optional proxy for suggest_services_ai_v2 if you already have a backend endpoint
app.post('/api/suggest_services_ai_v2', async (req, res) => {
  try {
    const SUGGEST_URL = process.env.SUGGEST_URL || null;
    if (!SUGGEST_URL) return res.status(501).json({ error: 'No suggest endpoint configured (set SUGGEST_URL)' });

    const fetch = require('node-fetch');
    // Forward original request body (multipart/form-data or JSON). We will proxy body raw.
    // If original client sends multipart, it's more complex. For now assume client posts FormData from browser
    // We'll forward by piping request to SUGGEST_URL
    const proxied = await fetch(SUGGEST_URL, { method: 'POST', body: req.body, headers: req.headers });
    const j = await proxied.json().catch(()=>null);
    res.status(proxied.status).json(j);
  } catch (err) {
    console.error('suggest proxy error', err);
    res.status(500).json({ error: 'Suggest proxy failed' });
  }
});

// Serve static files from 'public' (index.html + script.js)
app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
