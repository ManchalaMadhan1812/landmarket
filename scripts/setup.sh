#!/bin/bash

# LandMarket Project Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up LandMarket development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Create .env file from example if it doesn't exist
setup_env_file() {
    print_status "Setting up environment file..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example"
        print_warning "Please update the .env file with your actual configuration values"
        print_warning "Especially important: GOOGLE_MAPS_API_KEY, RAZORPAY keys"
    else
        print_success ".env file already exists"
    fi
}

# Build and start Docker containers
start_services() {
    print_status "Building and starting Docker containers..."
    
    # Build the containers
    docker-compose build
    
    # Start the services
    docker-compose up -d db redis elasticsearch
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are healthy
    if docker-compose ps | grep -q "unhealthy"; then
        print_error "Some services are unhealthy. Please check the logs:"
        docker-compose logs
        exit 1
    fi
    
    print_success "Core services are running"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for database to be fully ready
    sleep 5
    
    # Run migrations
    docker-compose exec -T backend python manage.py migrate
    
    print_success "Database migrations completed"
}

# Create superuser (interactive)
create_superuser() {
    print_status "Creating Django superuser..."
    print_warning "You will be prompted to create an admin user"
    
    docker-compose exec backend python manage.py createsuperuser
    
    print_success "Superuser created"
}

# Load initial data
load_initial_data() {
    print_status "Loading initial data..."
    
    # Create and load fixtures (if they exist)
    if [ -f "backend/fixtures/initial_data.json" ]; then
        docker-compose exec -T backend python manage.py loaddata initial_data.json
        print_success "Initial data loaded"
    else
        print_warning "No initial data fixtures found, skipping..."
    fi
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        if command -v npm &> /dev/null; then
            npm install
            print_success "Frontend dependencies installed"
        else
            print_warning "npm not found. Frontend dependencies will be installed in Docker container."
        fi
        
        cd ..
    fi
}

# Start all services
start_all_services() {
    print_status "Starting all services..."
    
    docker-compose up -d
    
    print_success "All services are now running!"
}

# Display access information
show_access_info() {
    print_success "🎉 LandMarket setup completed successfully!"
    echo ""
    echo "📍 Access Points:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000/api/"
    echo "  Admin Panel:  http://localhost:8000/admin/"
    echo "  API Docs:     http://localhost:8000/api/docs/"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Shell:        docker-compose exec backend python manage.py shell"
    echo ""
    echo "📖 Next Steps:"
    echo "  1. Update your .env file with real API keys"
    echo "  2. Access the admin panel to configure initial data"
    echo "  3. Start developing your features!"
    echo ""
}

# Error handling
handle_error() {
    print_error "Setup failed. Cleaning up..."
    docker-compose down
    exit 1
}

# Main setup process
main() {
    trap handle_error ERR
    
    echo "🏗️  LandMarket - India Real Estate Marketplace"
    echo "   Development Environment Setup"
    echo ""
    
    check_docker
    check_docker_compose
    setup_env_file
    start_services
    run_migrations
    
    # Ask if user wants to create superuser
    read -p "Do you want to create a Django superuser now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    load_initial_data
    setup_frontend
    start_all_services
    
    show_access_info
}

# Run main function
main "$@"