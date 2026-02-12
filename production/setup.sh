#!/bin/bash

###############################################################################
# Bagana AI - Hostinger VPS Setup Script
# 
# Script untuk setup awal server Hostinger VPS
# Install Docker, Docker Compose, dan dependencies yang diperlukan
# 
# Usage:
#   chmod +x setup.sh
#   sudo ./setup.sh
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Script harus dijalankan dengan sudo atau sebagai root"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Tidak dapat mendeteksi OS"
        exit 1
    fi
    print_info "OS detected: $OS $VER"
}

# Update system
update_system() {
    print_header "Update sistem"
    apt-get update
    apt-get upgrade -y
    print_success "Sistem updated"
}

# Install basic dependencies
install_basic_deps() {
    print_header "Install basic dependencies"
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        ufw \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    print_success "Basic dependencies installed"
}

# Install Docker
install_docker() {
    print_header "Install Docker"
    
    if command -v docker &> /dev/null; then
        print_info "Docker sudah terinstall: $(docker --version)"
        return
    fi
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "Docker installed: $(docker --version)"
}

# Install Docker Compose (standalone)
install_docker_compose() {
    print_header "Install Docker Compose"
    
    if docker compose version &> /dev/null || command -v docker-compose &> /dev/null; then
        print_info "Docker Compose sudah terinstall"
        return
    fi
    
    # Docker Compose sudah termasuk dalam docker-compose-plugin
    # Install standalone jika diperlukan
    DOCKER_COMPOSE_VERSION="v2.24.0"
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed: $(docker-compose --version)"
}

# Setup firewall
setup_firewall() {
    print_header "Setup firewall"
    
    # Allow SSH
    ufw allow 22/tcp
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow application ports
    ufw allow 3000/tcp  # Frontend
    ufw allow 8000/tcp  # Backend
    ufw allow 5432/tcp  # PostgreSQL (optional, bisa di-disable untuk security)
    
    # Enable firewall
    echo "y" | ufw enable
    
    print_success "Firewall configured"
}

# Create application directory
create_app_directory() {
    print_header "Create application directory"
    
    APP_DIR="/var/www/bagana-ai"
    mkdir -p $APP_DIR
    chown -R $SUDO_USER:$SUDO_USER $APP_DIR 2>/dev/null || true
    
    print_success "Directory created: $APP_DIR"
}

# Install Nginx (optional)
install_nginx() {
    print_header "Install Nginx (optional)"
    
    read -p "Install Nginx untuk reverse proxy? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apt-get install -y nginx
        systemctl start nginx
        systemctl enable nginx
        print_success "Nginx installed"
    else
        print_info "Nginx skipped"
    fi
}

# Setup Docker group (optional)
setup_docker_group() {
    print_header "Setup Docker group"
    
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker $SUDO_USER
        print_success "User $SUDO_USER added to docker group"
        print_warning "Logout dan login kembali untuk menggunakan Docker tanpa sudo"
    fi
}

# Show summary
show_summary() {
    print_header "Setup Summary"
    
    echo ""
    print_info "Installed components:"
    echo "  - Docker: $(docker --version)"
    echo "  - Docker Compose: $(docker-compose --version 2>/dev/null || docker compose version)"
    echo "  - Firewall: $(ufw status | head -n 1)"
    
    echo ""
    print_info "Next steps:"
    echo "  1. Clone repository: git clone <repo-url> /var/www/bagana-ai"
    echo "  2. Copy env.example to .env dan edit sesuai kebutuhan"
    echo "  3. Run deployment: cd production && sudo ./deploy.sh"
    
    echo ""
    print_success "Setup selesai! 🎉"
}

# Main execution
main() {
    print_header "Bagana AI - Hostinger VPS Setup"
    
    check_root
    detect_os
    
    update_system
    install_basic_deps
    install_docker
    install_docker_compose
    setup_firewall
    create_app_directory
    install_nginx
    setup_docker_group
    show_summary
}

# Run main function
main "$@"
