-- create_tables.sql
-- Run this if you prefer to create the table manually using mysql client.
-- Make sure the database 'scam_detector' (or your chosen DB_NAME) exists.

CREATE TABLE IF NOT EXISTS analyses (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  job_description LONGTEXT NOT NULL,
  risk_score INT NOT NULL,
  risk_level VARCHAR(10) NOT NULL,
  reasons JSON NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
