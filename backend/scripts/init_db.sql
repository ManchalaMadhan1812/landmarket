-- Initialize LandMarket Database with PostGIS
-- This script runs automatically when the PostgreSQL container starts

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Create custom types for the application
DO $$
BEGIN
    -- User role enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role_enum') THEN
        CREATE TYPE user_role_enum AS ENUM (
            'buyer', 
            'vendor', 
            'broker', 
            'admin', 
            'verification_officer', 
            'finance_manager', 
            'super_admin'
        );
    END IF;

    -- Property type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'property_type_enum') THEN
        CREATE TYPE property_type_enum AS ENUM (
            'residential', 
            'commercial', 
            'agricultural', 
            'industrial', 
            'plot', 
            'apartment', 
            'house'
        );
    END IF;

    -- Property purpose enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'purpose_enum') THEN
        CREATE TYPE purpose_enum AS ENUM ('sale', 'rent', 'lease');
    END IF;

    -- Property status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'property_status_enum') THEN
        CREATE TYPE property_status_enum AS ENUM (
            'draft', 
            'pending', 
            'active', 
            'reserved', 
            'sold', 
            'rejected', 
            'archived'
        );
    END IF;

    -- Area unit enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'area_unit_enum') THEN
        CREATE TYPE area_unit_enum AS ENUM (
            'sqft', 
            'cent', 
            'ground', 
            'acre', 
            'hectare'
        );
    END IF;

    -- Document type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'document_type_enum') THEN
        CREATE TYPE document_type_enum AS ENUM (
            'patta', 
            'chitta', 
            'ec', 
            'sale_deed', 
            'title_deed', 
            'survey_sketch', 
            'rera'
        );
    END IF;

    -- Message type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_type_enum') THEN
        CREATE TYPE message_type_enum AS ENUM (
            'text', 
            'image', 
            'document', 
            'system'
        );
    END IF;

    -- Enquiry status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enquiry_status_enum') THEN
        CREATE TYPE enquiry_status_enum AS ENUM (
            'new', 
            'contacted', 
            'site_visit_scheduled', 
            'negotiating', 
            'closed_won', 
            'closed_lost'
        );
    END IF;

    -- Site visit status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'site_visit_status_enum') THEN
        CREATE TYPE site_visit_status_enum AS ENUM (
            'requested', 
            'confirmed', 
            'rescheduled', 
            'completed', 
            'cancelled'
        );
    END IF;

    -- Verification status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'verification_status_enum') THEN
        CREATE TYPE verification_status_enum AS ENUM (
            'pending', 
            'verified', 
            'rejected'
        );
    END IF;

    -- Verification type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'verification_type_enum') THEN
        CREATE TYPE verification_type_enum AS ENUM (
            'location', 
            'documents', 
            'seller', 
            'broker', 
            'boundary'
        );
    END IF;

    -- Notification type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notification_type_enum') THEN
        CREATE TYPE notification_type_enum AS ENUM (
            'enquiry', 
            'message', 
            'site_visit', 
            'property_approved', 
            'subscription'
        );
    END IF;

    -- Payment status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status_enum') THEN
        CREATE TYPE payment_status_enum AS ENUM (
            'pending', 
            'completed', 
            'failed', 
            'refunded'
        );
    END IF;

    -- Subscription plan type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plan_type_enum') THEN
        CREATE TYPE plan_type_enum AS ENUM (
            'featured_listing', 
            'premium_seller'
        );
    END IF;

    -- Subscription status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscription_status_enum') THEN
        CREATE TYPE subscription_status_enum AS ENUM (
            'active', 
            'cancelled', 
            'expired'
        );
    END IF;

    -- Audit action enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'audit_action_enum') THEN
        CREATE TYPE audit_action_enum AS ENUM (
            'create', 
            'update', 
            'delete', 
            'approve', 
            'reject'
        );
    END IF;

    -- Requirement status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'requirement_status_enum') THEN
        CREATE TYPE requirement_status_enum AS ENUM (
            'active', 
            'fulfilled', 
            'expired'
        );
    END IF;

    -- Requirement response status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'requirement_response_status_enum') THEN
        CREATE TYPE requirement_response_status_enum AS ENUM (
            'sent', 
            'viewed', 
            'interested', 
            'rejected'
        );
    END IF;
END $$;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create function to calculate distance between two points
CREATE OR REPLACE FUNCTION calculate_distance(lat1 FLOAT, lon1 FLOAT, lat2 FLOAT, lon2 FLOAT)
RETURNS FLOAT AS $$
BEGIN
    RETURN ST_Distance(
        ST_GeogFromText('POINT(' || lon1 || ' ' || lat1 || ')'),
        ST_GeogFromText('POINT(' || lon2 || ' ' || lat2 || ')')
    ) / 1000.0; -- Return distance in kilometers
END;
$$ LANGUAGE plpgsql;

-- Create function for area unit conversions
CREATE OR REPLACE FUNCTION convert_area(
    area_value DECIMAL,
    from_unit area_unit_enum,
    to_unit area_unit_enum
) RETURNS DECIMAL AS $$
DECLARE
    sqft_value DECIMAL;
BEGIN
    -- Convert to square feet first
    CASE from_unit
        WHEN 'sqft' THEN sqft_value := area_value;
        WHEN 'cent' THEN sqft_value := area_value * 435.6;  -- 1 cent = 435.6 sqft
        WHEN 'ground' THEN sqft_value := area_value * 2400; -- 1 ground = 2400 sqft
        WHEN 'acre' THEN sqft_value := area_value * 43560;  -- 1 acre = 43560 sqft
        WHEN 'hectare' THEN sqft_value := area_value * 107639; -- 1 hectare = 107639 sqft
    END CASE;
    
    -- Convert from square feet to target unit
    CASE to_unit
        WHEN 'sqft' THEN RETURN sqft_value;
        WHEN 'cent' THEN RETURN sqft_value / 435.6;
        WHEN 'ground' THEN RETURN sqft_value / 2400;
        WHEN 'acre' THEN RETURN sqft_value / 43560;
        WHEN 'hectare' THEN RETURN sqft_value / 107639;
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Insert initial Indian states and cities data
CREATE TABLE IF NOT EXISTS temp_indian_locations (
    state VARCHAR(100),
    district VARCHAR(100),
    city VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

-- Sample Indian location data (focusing on South India as mentioned in requirements)
INSERT INTO temp_indian_locations (state, district, city, latitude, longitude) VALUES
('Tamil Nadu', 'Chennai', 'Chennai', 13.0827, 80.2707),
('Tamil Nadu', 'Chennai', 'Tambaram', 12.9249, 80.1000),
('Tamil Nadu', 'Coimbatore', 'Coimbatore', 11.0168, 76.9558),
('Tamil Nadu', 'Salem', 'Salem', 11.6643, 78.1460),
('Tamil Nadu', 'Madurai', 'Madurai', 9.9252, 78.1198),
('Tamil Nadu', 'Tiruchirappalli', 'Tiruchirappalli', 10.7905, 78.7047),
('Karnataka', 'Bangalore Urban', 'Bangalore', 12.9716, 77.5946),
('Karnataka', 'Mysore', 'Mysore', 12.2958, 76.6394),
('Karnataka', 'Mangalore', 'Mangalore', 12.9141, 74.8560),
('Kerala', 'Ernakulam', 'Kochi', 9.9312, 76.2673),
('Kerala', 'Thiruvananthapuram', 'Thiruvananthapuram', 8.5241, 76.9366),
('Kerala', 'Kozhikode', 'Kozhikode', 11.2588, 75.7804),
('Andhra Pradesh', 'Hyderabad', 'Hyderabad', 17.3850, 78.4867),
('Andhra Pradesh', 'Visakhapatnam', 'Visakhapatnam', 17.6868, 83.2185),
('Telangana', 'Hyderabad', 'Secunderabad', 17.4399, 78.4983);

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO landmarket_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO landmarket_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO landmarket_user;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'LandMarket database initialized successfully with PostGIS extensions and custom types';
END $$;