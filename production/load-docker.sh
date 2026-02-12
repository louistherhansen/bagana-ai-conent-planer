#!/bin/bash

###############################################################################
# Bagana AI - Docker Images Load Script (for VPS)
# 
# Script untuk load Docker images dari package file di VPS
# 
# Usage:
#   chmod +x load-docker.sh
#   ./load-docker.sh [package-file.tar.gz]
#
# Example:
#   ./load-docker.sh bagana-ai-docker-images-20250213_120000.tar.gz
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
PACKAGE_FILE="${1:-}"

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
        print_warning "Script perlu dijalankan dengan sudo untuk load images"
        print_info "Mencoba dengan sudo..."
        if sudo -n true 2>/dev/null; then
            SUDO_CMD="sudo"
        else
            print_error "Perlu sudo access untuk load images"
            exit 1
        fi
    else
        SUDO_CMD=""
    fi
}

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker tidak terinstall!"
        print_info "Install Docker terlebih dahulu atau jalankan setup.sh"
        exit 1
    fi
    print_success "Docker terinstall: $(docker --version)"
}

# Find package file
find_package_file() {
    if [ -n "$PACKAGE_FILE" ]; then
        if [ ! -f "$PACKAGE_FILE" ]; then
            print_error "File tidak ditemukan: $PACKAGE_FILE"
            exit 1
        fi
        PACKAGE_PATH="$PACKAGE_FILE"
    else
        # Look for package files in current directory and common locations
        PACKAGE_PATH=$(find . /tmp ~ -name "bagana-ai-docker-images-*.tar.gz" -type f 2>/dev/null | head -n 1)
        
        if [ -z "$PACKAGE_PATH" ]; then
            print_error "Package file tidak ditemukan!"
            print_info "Cari file dengan pattern: bagana-ai-docker-images-*.tar.gz"
            print_info "Atau specify file: ./load-docker.sh /path/to/package.tar.gz"
            exit 1
        fi
    fi
    
    print_success "Package file ditemukan: $PACKAGE_PATH"
    
    # Check file size
    FILE_SIZE=$(du -h "$PACKAGE_PATH" | cut -f1)
    print_info "File size: ${FILE_SIZE}"
}

# Extract package if compressed
extract_package() {
    if [[ "$PACKAGE_PATH" == *.gz ]]; then
        print_header "Extracting Package"
        
        TAR_FILE="${PACKAGE_PATH%.gz}"
        
        if [ -f "$TAR_FILE" ]; then
            print_info "File .tar sudah ada, menggunakan yang sudah ada"
            PACKAGE_TAR="$TAR_FILE"
        else
            print_info "Extracting ${PACKAGE_PATH}..."
            gunzip -k "$PACKAGE_PATH"
            PACKAGE_TAR="$TAR_FILE"
            print_success "Extracted: $PACKAGE_TAR"
        fi
    else
        PACKAGE_TAR="$PACKAGE_PATH"
    fi
}

# Load Docker images
load_images() {
    print_header "Loading Docker Images"
    
    print_info "Loading images from ${PACKAGE_TAR}..."
    print_warning "Proses ini mungkin memakan waktu beberapa menit..."
    
    # Load images
    $SUDO_CMD docker load -i "$PACKAGE_TAR"
    
    print_success "Images loaded successfully"
}

# Verify loaded images
verify_images() {
    print_header "Verifying Loaded Images"
    
    print_info "Loaded Docker images:"
    docker images | grep -E "bagana-ai|postgres|nginx|REPOSITORY" || true
    
    # Check for required images
    REQUIRED_IMAGES=("bagana-ai-backend" "bagana-ai-frontend" "postgres:14-alpine" "nginx:alpine")
    MISSING_IMAGES=()
    
    for img in "${REQUIRED_IMAGES[@]}"; do
        if ! docker images | grep -q "$img"; then
            MISSING_IMAGES+=("$img")
        fi
    done
    
    if [ ${#MISSING_IMAGES[@]} -gt 0 ]; then
        print_warning "Beberapa images tidak ditemukan:"
        for img in "${MISSING_IMAGES[@]}"; do
            echo "  - $img"
        done
    else
        print_success "Semua required images tersedia"
    fi
}

# Show next steps
show_next_steps() {
    print_header "Next Steps"
    
    echo ""
    print_info "Images sudah di-load. Langkah selanjutnya:"
    echo ""
    echo "  1. Pastikan file .env sudah dikonfigurasi:"
    echo "     cp env.example .env"
    echo "     nano .env"
    echo ""
    echo "  2. Deploy aplikasi:"
    echo "     ./deploy.sh"
    echo ""
    echo "  3. Atau start dengan docker-compose:"
    echo "     docker-compose up -d"
    echo ""
    echo "  4. Check status:"
    echo "     docker-compose ps"
    echo "     docker-compose logs -f"
}

# Cleanup extracted file (optional)
cleanup_extracted() {
    if [[ "$PACKAGE_PATH" == *.gz ]] && [ -f "$PACKAGE_TAR" ]; then
        read -p "Hapus file .tar yang sudah di-extract? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$PACKAGE_TAR"
            print_success "File .tar dihapus"
        fi
    fi
}

# Main execution
main() {
    print_header "Bagana AI - Docker Images Loader"
    
    check_permissions
    check_docker
    find_package_file
    extract_package
    load_images
    verify_images
    show_next_steps
    cleanup_extracted
    
    echo ""
    print_success "Loading selesai! 🎉"
}

# Run main function
main "$@"
