BEGIN;

CREATE TABLE IF NOT EXISTS sector_dependencies (
    dependency_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_sector TEXT NOT NULL,
    dependent_sector TEXT NOT NULL,
    dependency_type TEXT NOT NULL,
    evidence_reference TEXT,
    confidence TEXT CHECK (confidence IN ('documented', 'literature', 'assumption')),
    UNIQUE (source_sector, dependent_sector)
);

-- Seed with widely documented infrastructure dependencies
INSERT INTO sector_dependencies (source_sector, dependent_sector, dependency_type, evidence_reference, confidence)
VALUES 
    ('electricity', 'water', 'power for pumping', 'EU CER framework', 'documented'),
    ('electricity', 'healthcare', 'power for life support', 'EU CER framework', 'documented'),
    ('electricity', 'telecommunications', 'power for cell towers', 'EU CER framework', 'documented'),
    ('telecommunications', 'healthcare', 'connectivity for records', 'EU CER framework', 'documented'),
    ('water', 'healthcare', 'water for sanitation', 'EU CER framework', 'documented')
ON CONFLICT DO NOTHING;

COMMIT;
