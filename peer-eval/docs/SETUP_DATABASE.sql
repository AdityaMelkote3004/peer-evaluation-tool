-- ============================================
-- PEER EVALUATION SYSTEM - DATABASE SETUP
-- ============================================
-- Run this SQL in your Supabase SQL Editor
-- Dashboard -> SQL Editor -> New Query -> Paste & Run
-- ============================================

-- ============================================
-- CLEAN UP: DROP ALL EXISTING TABLES
-- ============================================
DROP TABLE IF EXISTS evaluation_scores CASCADE;
DROP TABLE IF EXISTS evaluations CASCADE;
DROP TABLE IF EXISTS form_criteria CASCADE;
DROP TABLE IF EXISTS evaluation_forms CASCADE;
DROP TABLE IF EXISTS team_members CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- CREATE TABLES
-- ============================================

-- 1. CREATE USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 2. CREATE PROJECTS TABLE
CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructor_id BIGINT NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_instructor ON projects(instructor_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Add foreign key constraint after users are inserted
-- This will be added later in the script

-- 3. CREATE TEAMS TABLE
CREATE TABLE IF NOT EXISTS teams (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_teams_project ON teams(project_id);

-- 4. CREATE TEAM_MEMBERS TABLE (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id);

-- 5. CREATE EVALUATION_FORMS TABLE
CREATE TABLE IF NOT EXISTS evaluation_forms (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    max_score INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_forms_project ON evaluation_forms(project_id);

-- 6. CREATE FORM_CRITERIA TABLE
CREATE TABLE IF NOT EXISTS form_criteria (
    id BIGSERIAL PRIMARY KEY,
    form_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    max_points INTEGER NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_form_criteria_form ON form_criteria(form_id);

-- 7. CREATE EVALUATIONS TABLE
CREATE TABLE IF NOT EXISTS evaluations (
    id BIGSERIAL PRIMARY KEY,
    form_id BIGINT NOT NULL,
    evaluator_id BIGINT NOT NULL,
    evaluatee_id BIGINT NOT NULL,
    team_id BIGINT NOT NULL,
    total_score INTEGER,
    comments TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(form_id, evaluator_id, evaluatee_id)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_form ON evaluations(form_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_evaluator ON evaluations(evaluator_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_evaluatee ON evaluations(evaluatee_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_team ON evaluations(team_id);

-- 8. CREATE EVALUATION_SCORES TABLE
CREATE TABLE IF NOT EXISTS evaluation_scores (
    id BIGSERIAL PRIMARY KEY,
    evaluation_id BIGINT NOT NULL,
    criterion_id BIGINT NOT NULL,
    score INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(evaluation_id, criterion_id)
);

CREATE INDEX IF NOT EXISTS idx_evaluation_scores_evaluation ON evaluation_scores(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_scores_criterion ON evaluation_scores(criterion_id);

-- ============================================
-- INSERT SAMPLE DATA
-- ============================================

-- Insert a default instructor
INSERT INTO users (email, name, role, password_hash) 
VALUES ('instructor@test.com', 'Dr. Smith', 'instructor', 'temp_password')
ON CONFLICT (email) DO NOTHING;

-- Insert sample students
INSERT INTO users (email, name, role, password_hash) 
VALUES 
    ('alice@test.com', 'Alice Johnson', 'student', 'temp_password'),
    ('bob@test.com', 'Bob Williams', 'student', 'temp_password'),
    ('charlie@test.com', 'Charlie Brown', 'student', 'temp_password'),
    ('diana@test.com', 'Diana Prince', 'student', 'temp_password')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- ADD FOREIGN KEY CONSTRAINTS (After data is inserted)
-- ============================================

-- Add foreign key constraints now that data exists
DO $$ 
BEGIN
    -- Projects
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_projects_instructor') THEN
        ALTER TABLE projects ADD CONSTRAINT fk_projects_instructor 
        FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;

    -- Teams
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_teams_project') THEN
        ALTER TABLE teams ADD CONSTRAINT fk_teams_project 
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
    END IF;

    -- Team Members
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_team_members_team') THEN
        ALTER TABLE team_members ADD CONSTRAINT fk_team_members_team 
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_team_members_user') THEN
        ALTER TABLE team_members ADD CONSTRAINT fk_team_members_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;

    -- Evaluation Forms
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluation_forms_project') THEN
        ALTER TABLE evaluation_forms ADD CONSTRAINT fk_evaluation_forms_project 
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
    END IF;

    -- Form Criteria
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_form_criteria_form') THEN
        ALTER TABLE form_criteria ADD CONSTRAINT fk_form_criteria_form 
        FOREIGN KEY (form_id) REFERENCES evaluation_forms(id) ON DELETE CASCADE;
    END IF;

    -- Evaluations
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluations_form') THEN
        ALTER TABLE evaluations ADD CONSTRAINT fk_evaluations_form 
        FOREIGN KEY (form_id) REFERENCES evaluation_forms(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluations_evaluator') THEN
        ALTER TABLE evaluations ADD CONSTRAINT fk_evaluations_evaluator 
        FOREIGN KEY (evaluator_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluations_evaluatee') THEN
        ALTER TABLE evaluations ADD CONSTRAINT fk_evaluations_evaluatee 
        FOREIGN KEY (evaluatee_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluations_team') THEN
        ALTER TABLE evaluations ADD CONSTRAINT fk_evaluations_team 
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE;
    END IF;

    -- Evaluation Scores
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluation_scores_evaluation') THEN
        ALTER TABLE evaluation_scores ADD CONSTRAINT fk_evaluation_scores_evaluation 
        FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_evaluation_scores_criterion') THEN
        ALTER TABLE evaluation_scores ADD CONSTRAINT fk_evaluation_scores_criterion 
        FOREIGN KEY (criterion_id) REFERENCES form_criteria(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================
-- ENABLE ROW LEVEL SECURITY (Optional)
-- ============================================
-- Uncomment these if you want to enable RLS

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE evaluation_forms ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE form_criteria ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE evaluation_scores ENABLE ROW LEVEL SECURITY;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these to verify everything was created:

-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check users
SELECT id, email, name, role, created_at FROM users;

-- ============================================
-- SUCCESS! 🎉
-- ============================================
-- All tables created. You can now use the API!
