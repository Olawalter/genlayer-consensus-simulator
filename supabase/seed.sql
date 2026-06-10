-- Seed: default validator personalities
-- Run after migration 001

INSERT INTO validators (name, model, persona, bias_profile) VALUES
  ('Atlas',   'gpt-4o',          'analytical', '{"strictness": 0.8}'),
  ('Nova',    'claude-3-5-sonnet','creative',   '{"strictness": 0.4}'),
  ('Orion',   'llama-3',          'strict',     '{"strictness": 0.9}'),
  ('Lyra',    'mistral-large',    'lenient',    '{"strictness": 0.2}'),
  ('Zephyr',  'gemini-pro',       'balanced',   '{"strictness": 0.6}');
