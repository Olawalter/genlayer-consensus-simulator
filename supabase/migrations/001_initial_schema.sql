-- GenLayer Consensus Simulator: Initial Schema
-- Migration 001

CREATE TABLE profiles (
  id           UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username     TEXT UNIQUE NOT NULL,
  role         TEXT NOT NULL DEFAULT 'learner',
  xp           INTEGER NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE claims (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID REFERENCES profiles(id) ON DELETE SET NULL,
  content      TEXT NOT NULL,
  category     TEXT NOT NULL,
  metadata     JSONB,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE simulations (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id           UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  user_id            UUID REFERENCES profiles(id) ON DELETE SET NULL,
  status             TEXT NOT NULL DEFAULT 'pending',
  validator_count    INTEGER NOT NULL DEFAULT 5,
  consensus_reached  BOOLEAN,
  final_verdict      TEXT,
  contract_address   TEXT,
  tx_hash            TEXT,
  chain_data         JSONB,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at       TIMESTAMPTZ
);

CREATE TABLE validators (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  model        TEXT NOT NULL,
  persona      TEXT NOT NULL,
  bias_profile JSONB,
  is_active    BOOLEAN NOT NULL DEFAULT true,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE validator_votes (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id     UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  validator_id      UUID NOT NULL REFERENCES validators(id),
  role              TEXT NOT NULL DEFAULT 'validator',
  vote              TEXT NOT NULL,
  confidence        NUMERIC(4,3),
  reasoning         TEXT,
  raw_llm_output    TEXT,
  equivalence_score NUMERIC(4,3),
  voted_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE consensus_results (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id     UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  round             INTEGER NOT NULL DEFAULT 1,
  accept_count      INTEGER NOT NULL DEFAULT 0,
  reject_count      INTEGER NOT NULL DEFAULT 0,
  uncertain_count   INTEGER NOT NULL DEFAULT 0,
  consensus_type    TEXT,
  equivalence_pass  BOOLEAN,
  outcome           TEXT,
  computed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE appeals (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id         UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  initiated_by          UUID REFERENCES profiles(id) ON DELETE SET NULL,
  reason                TEXT NOT NULL,
  status                TEXT NOT NULL DEFAULT 'open',
  additional_validators INTEGER NOT NULL DEFAULT 3,
  original_outcome      TEXT NOT NULL,
  final_outcome         TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at           TIMESTAMPTZ
);

CREATE TABLE appeal_rounds (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appeal_id   UUID NOT NULL REFERENCES appeals(id) ON DELETE CASCADE,
  round       INTEGER NOT NULL,
  outcome     TEXT,
  votes_data  JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE analytics_events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES profiles(id) ON DELETE SET NULL,
  event_type  TEXT NOT NULL,
  payload     JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES profiles(id) ON DELETE SET NULL,
  action      TEXT NOT NULL,
  table_name  TEXT,
  record_id   UUID,
  diff        JSONB,
  ip_address  INET,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_simulations_user_id   ON simulations(user_id);
CREATE INDEX idx_simulations_status    ON simulations(status);
CREATE INDEX idx_validator_votes_sim   ON validator_votes(simulation_id);
CREATE INDEX idx_claims_user_id        ON claims(user_id);
CREATE INDEX idx_appeals_simulation_id ON appeals(simulation_id);
CREATE INDEX idx_analytics_user_event  ON analytics_events(user_id, event_type);
CREATE INDEX idx_audit_logs_user_id    ON audit_logs(user_id);

-- Row Level Security
ALTER TABLE profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims             ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations        ENABLE ROW LEVEL SECURITY;
ALTER TABLE validator_votes    ENABLE ROW LEVEL SECURITY;
ALTER TABLE consensus_results  ENABLE ROW LEVEL SECURITY;
ALTER TABLE appeals            ENABLE ROW LEVEL SECURITY;
ALTER TABLE appeal_rounds      ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events   ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs         ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_own"         ON profiles         FOR ALL    USING (auth.uid() = id);
CREATE POLICY "claims_own_insert"    ON claims           FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "claims_own_select"    ON claims           FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "simulations_own"      ON simulations      FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "votes_auth_read"      ON validator_votes  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "consensus_auth_read"  ON consensus_results FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "appeals_auth_read"    ON appeals          FOR SELECT USING (auth.role() = 'authenticated');
