#!/bin/bash

###############################################################################
# Bagana AI - Hostinger VPS Deployment Script
# 
# Script otomatis untuk deploy Bagana AI ke Hostinger VPS menggunakan Docker Compose
# 
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Requirements:
#   - Ubuntu 22.04+ atau Debian 11+
#   - Docker & Docker Compose sudah terinstall
#   - File .env sudah dikonfigurasi
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root or with sudo
check_permissions() {
    if [ "$EUID" -ne 0 ]; then 
        print_warning "Script perlu dijalankan dengan sudo"
        exit 1
    fi
}

# Check if .env file exists
check_env_file() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_error "File .env tidak ditemukan!"
        print_info "Copy dari env.example dan edit sesuai kebutuhan:"
        print_info "  cp env.example .env"
        print_info "  nano .env"
        exit 1
    fi
    print_success "File .env ditemukan"
}

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker tidak terinstall!"
        print_info "Jalankan setup.sh terlebih dahulu"
        exit 1
    fi
    print_success "Docker terinstall: $(docker --version)"
}

# Check Docker Compose installation
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose tidak terinstall!"
        print_info "Jalankan setup.sh terlebih dahulu"
        exit 1
    fi
    print_success "Docker Compose terinstall"
}

# Load environment variables
load_env() {
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
    print_success "Environment variables loaded"
}

# Stop existing containers
stop_containers() {
    print_header "Menghentikan containers yang berjalan"
    cd "$SCRIPT_DIR"
    docker-compose down 2>/dev/null || true
    print_success "Containers dihentikan"
}

# Build Docker images
build_images() {
    print_header "Building Docker images"
    cd "$SCRIPT_DIR"
    docker-compose build --no-cache
    print_success "Docker images berhasil dibuild"
}

# Start services
start_services() {
    print_header "Starting services"
    cd "$SCRIPT_DIR"
    docker-compose up -d
    print_success "Services started"
}

# Wait for services to be healthy
wait_for_services() {
    print_header "Menunggu services siap"
    
    print_info "Menunggu PostgreSQL..."
    timeout=60
    counter=0
    while ! docker-compose exec -T postgres pg_isready -U ${DB_USER:-bagana_user} &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "PostgreSQL tidak siap setelah $timeout detik"
            exit 1
        fi
    done
    print_success "PostgreSQL siap"
    
    print_info "Menunggu Backend..."
    timeout=120
    counter=0
    while ! curl -f http://localhost:${BACKEND_PORT:-8000}/health &> /dev/null; do
        sleep 3
        counter=$((counter + 3))
        if [ $counter -ge $timeout ]; then
            print_warning "Backend mungkin belum siap, check logs: docker-compose logs backend"
            break
        fi
    done
    print_success "Backend siap"
    
    print_info "Menunggu Frontend..."
    timeout=120
    counter=0
    while ! curl -f http://localhost:${FRONTEND_PORT:-3000} &> /dev/null; do
        sleep 3
        counter=$((counter + 3))
        if [ $counter -ge $timeout ]; then
            print_warning "Frontend mungkin belum siap, check logs: docker-compose logs frontend"
            break
        fi
    done
    print_success "Frontend siap"
}

# Initialize database
init_database() {
    print_header "Menginisialisasi database"
    
    # Wait a bit more for PostgreSQL to be fully ready
    sleep 5
    
    # Check if database already initialized
    if docker-compose exec -T postgres psql -U ${DB_USER:-bagana_user} -d ${DB_NAME:-bagana_ai} -c "\dt" | grep -q "users"; then
        print_info "Database sudah terinisialisasi, skip..."
        return
    fi
    
    # Run init script
    if [ -f "$SCRIPT_DIR/init-database.sql" ]; then
        docker-compose exec -T postgres psql -U ${DB_USER:-bagana_user} -d ${DB_NAME:-bagana_ai} < "$SCRIPT_DIR/init-database.sql"
        print_success "Database initialized"
    else
        print_warning "init-database.sql tidak ditemukan, skip initialization"
    fi
}

# Show status
show_status() {
    print_header "Status Deployment"
    
    echo ""
    print_info "Container Status:"
    docker-compose ps
    
    echo ""
    print_info "Service URLs:"
    echo "  Frontend: http://localhost:${FRONTEND_PORT:-3000}"
    echo "  Backend:  http://localhost:${BACKEND_PORT:-8000}"
    echo "  Database: localhost:${DB_PORT:-5432}"
    
    echo ""
    print_info "Useful commands:"
    echo "  View logs:     docker-compose logs -f"
    echo "  Stop:          docker-compose down"
    echo "  Restart:       docker-compose restart"
    echo "  Status:        docker-compose ps"
}

# Main execution
main() {
    print_header "Bagana AI - Hostinger VPS Deployment"
    
    check_permissions
    check_env_file
    check_docker
    check_docker_compose
    load_env
    
    stop_containers
    build_images
    start_services
    wait_for_services
    init_database
    show_status
    
    echo ""
    print_success "Deployment selesai! 🎉"
    print_info "Akses aplikasi di: http://localhost:${FRONTEND_PORT:-3000}"
}

# Run main function
main "$@"
