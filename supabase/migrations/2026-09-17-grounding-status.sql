-- Migration: Add grounding_status to messages and drop grounded

-- Add new column
ALTER TABLE messages ADD COLUMN grounding_status TEXT;

-- Migrate existing data
UPDATE messages
SET grounding_status = CASE
    WHEN grounded = TRUE THEN 'FACTUAL_PLACEMENT'
    WHEN grounded = FALSE THEN 'CONTRADICTORY_CLAIM'
    ELSE NULL
END;

-- We can drop the grounded column safely because the backend API and frontend types have been fully migrated
ALTER TABLE messages DROP COLUMN grounded;
