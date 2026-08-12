-- ===========================================================================
-- MedExtract AI - Schema complet de la base de donnees  (DEV 1)
-- Execute automatiquement par PostgreSQL au premier demarrage du conteneur.
-- Contient les tables de TOUS les services (base partagee).
-- ===========================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- pour gen_random_uuid()

-- --------------------------------------------------------------------------
-- DEV 1 : Utilisateurs
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    username        VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    role            VARCHAR(20)  NOT NULL DEFAULT 'PATIENT'
                    CHECK (role IN ('PATIENT','DOCTOR','ADMIN')),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- --------------------------------------------------------------------------
-- DEV 2 : Documents
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename      VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path     TEXT         NOT NULL,
    file_size     BIGINT       NOT NULL,
    mime_type     VARCHAR(100) NOT NULL,
    doc_type      VARCHAR(20)  NOT NULL DEFAULT 'UNKNOWN'
                  CHECK (doc_type IN ('BLOOD_TEST','RADIOLOGY','PRESCRIPTION','REPORT','UNKNOWN')),
    status        VARCHAR(20)  NOT NULL DEFAULT 'PENDING'
                  CHECK (status IN ('PENDING','OCR_DONE','AI_DONE','ERROR')),
    ocr_text      TEXT,
    notes         TEXT,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);

-- --------------------------------------------------------------------------
-- DEV 2 : Resultats OCR
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ocr_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text        TEXT,
    words           JSONB,           -- [{"word","confidence","bbox":[x1,y1,x2,y2],"page"}]
    page_count      INTEGER DEFAULT 1,
    ocr_engine      VARCHAR(50) DEFAULT 'PaddleOCR',
    processing_time FLOAT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ocr_document ON ocr_results(document_id);

-- --------------------------------------------------------------------------
-- DEV 3 : Resultats medicaux (une ligne par document analyse)
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doc_type        VARCHAR(20),
    patient_name    VARCHAR(255),
    doctor_name     VARCHAR(255),
    lab_name        VARCHAR(255),
    model_version   VARCHAR(100),
    processing_time FLOAT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_medical_user ON medical_results(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_document ON medical_results(document_id);

-- --------------------------------------------------------------------------
-- DEV 3 : Analyses (plusieurs lignes par medical_result)
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analyses (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medical_result_id UUID NOT NULL REFERENCES medical_results(id) ON DELETE CASCADE,
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    analysis_name     VARCHAR(255) NOT NULL,
    value             FLOAT,
    unit              VARCHAR(50),
    ref_min           FLOAT,
    ref_max           FLOAT,
    status            VARCHAR(20) DEFAULT 'UNKNOWN'
                      CHECK (status IN ('NORMAL','HIGH','LOW','UNKNOWN')),
    confidence        FLOAT,
    bbox              JSONB,
    analysis_date     DATE,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_name ON analyses(user_id, analysis_name);

-- --------------------------------------------------------------------------
-- DEV 3 : Historique du chatbot
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id  UUID NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(user_id, session_id);

-- --------------------------------------------------------------------------
-- Pas de compte cree en dur (le hash bcrypt doit etre genere par l'application).
-- Creez votre premier compte via POST /api/auth/register, par exemple :
--   {"email":"admin@medextract.ai","username":"admin",
--    "password":"Admin1234","full_name":"Admin","role":"ADMIN"}
-- --------------------------------------------------------------------------
