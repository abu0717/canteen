-- Add worker_request table for approval-based worker assignment
CREATE TABLE IF NOT EXISTS worker_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    cafe_id UUID NOT NULL REFERENCES cafe(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, cafe_id)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_worker_request_cafe_status ON worker_request(cafe_id, status);
CREATE INDEX IF NOT EXISTS idx_worker_request_user ON worker_request(user_id);
