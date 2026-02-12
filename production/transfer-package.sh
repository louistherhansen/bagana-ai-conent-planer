#!/bin/bash

###############################################################################
# Bagana AI - Package Transfer Script
# 
# Script untuk transfer Docker images package ke VPS Hostinger
# 
# Usage:
#   chmod +x transfer-package.sh
#   ./transfer-package.sh [vps_user@vps_ip] [package_file]
#
# Example:
#   ./transfer-package.sh root@192.168.1.100
#   ./transfer-package.sh root@192.168.1.100 bagana-ai-docker-images-20250213.tar.gz
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
PACKAGE_DIR="$SCRIPT_DIR/packages"
VPS_TARGET="${1:-}"
PACKAGE_FILE="${2:-}"

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

# Check if package-docker.sh has been run
check_package_exists() {
    if [ -z "$PACKAGE_FILE" ]; then
        # Find latest package file
        PACKAGE_FILE=$(find "$PACKAGE_DIR" -name "bagana-ai-docker-images-*.tar.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        
        if [ -z "$PACKAGE_FILE" ]; then
            print_error "Package file tidak ditemukan!"
            print_info "Jalankan package-docker.sh terlebih dahulu untuk membuat package"
            exit 1
        fi
    fi
    
    if [ ! -f "$PACKAGE_FILE" ]; then
        print_error "File tidak ditemukan: $PACKAGE_FILE"
        exit 1
    fi
    
    print_success "Package file: $PACKAGE_FILE"
    
    # Check file size
    FILE_SIZE=$(du -h "$PACKAGE_FILE" | cut -f1)
    FILE_BYTES=$(stat -f%z "$PACKAGE_FILE" 2>/dev/null || stat -c%s "$PACKAGE_FILE" 2>/dev/null)
    print_info "File size: ${FILE_SIZE}"
    
    # Estimate transfer time (assuming 1MB/s average)
    if [ -n "$FILE_BYTES" ]; then
        EST_SECONDS=$((FILE_BYTES / 1048576))
        EST_MINUTES=$((EST_SECONDS / 60))
        if [ $EST_MINUTES -gt 0 ]; then
            print_info "Estimated transfer time: ~${EST_MINUTES} minutes"
        else
            print_info "Estimated transfer time: ~${EST_SECONDS} seconds"
        fi
    fi
}

# Get VPS target
get_vps_target() {
    if [ -z "$VPS_TARGET" ]; then
        print_info "Masukkan VPS target (format: user@ip atau user@domain):"
        read -p "VPS Target: " VPS_TARGET
        
        if [ -z "$VPS_TARGET" ]; then
            print_error "VPS target harus diisi!"
            exit 1
        fi
    fi
    
    # Validate format
    if [[ ! "$VPS_TARGET" =~ ^[^@]+@[^@]+$ ]]; then
        print_error "Format VPS target salah! Gunakan: user@ip atau user@domain"
        exit 1
    fi
    
    print_success "VPS Target: $VPS_TARGET"
}

# Check SSH connection
check_ssh_connection() {
    print_header "Checking SSH Connection"
    
    print_info "Testing SSH connection to $VPS_TARGET..."
    
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$VPS_TARGET" exit 2>/dev/null; then
        print_success "SSH connection OK"
    else
        print_warning "SSH connection test failed"
        print_info "Pastikan:"
        echo "  - SSH key sudah di-setup atau password tersedia"
        echo "  - VPS IP/domain benar"
        echo "  - Firewall mengizinkan SSH (port 22)"
        
        read -p "Lanjutkan transfer? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check remote directory
check_remote_directory() {
    print_info "Checking remote directory..."
    
    REMOTE_DIR="/tmp/bagana-ai-packages"
    
    ssh "$VPS_TARGET" "mkdir -p $REMOTE_DIR" 2>/dev/null || true
    
    print_success "Remote directory: $REMOTE_DIR"
}

# Transfer package
transfer_package() {
    print_header "Transferring Package"
    
    REMOTE_DIR="/tmp/bagana-ai-packages"
    REMOTE_FILE="$REMOTE_DIR/$(basename "$PACKAGE_FILE")"
    
    print_info "Transferring $PACKAGE_FILE to $VPS_TARGET:$REMOTE_FILE..."
    print_warning "Proses ini mungkin memakan waktu beberapa menit..."
    
    # Transfer with progress bar if available
    if command -v pv &> /dev/null; then
        pv "$PACKAGE_FILE" | ssh "$VPS_TARGET" "cat > $REMOTE_FILE"
    else
        scp "$PACKAGE_FILE" "$VPS_TARGET:$REMOTE_FILE"
    fi
    
    print_success "Transfer completed"
    
    # Verify file on remote
    print_info "Verifying file on remote..."
    REMOTE_SIZE=$(ssh "$VPS_TARGET" "du -h $REMOTE_FILE | cut -f1" 2>/dev/null)
    print_success "File verified on remote: ${REMOTE_SIZE}"
}

# Show next steps
show_next_steps() {
    print_header "Next Steps on VPS"
    
    REMOTE_DIR="/tmp/bagana-ai-packages"
    REMOTE_FILE="$REMOTE_DIR/$(basename "$PACKAGE_FILE")"
    
    echo ""
    print_info "Package sudah ditransfer ke VPS. Langkah selanjutnya:"
    echo ""
    echo "  1. SSH ke VPS:"
    echo "     ssh $VPS_TARGET"
    echo ""
    echo "  2. Load Docker images:"
    echo "     cd /var/www/bagana-ai/production"
    echo "     ./load-docker.sh $REMOTE_FILE"
    echo ""
    echo "  3. Atau manual:"
    echo "     gunzip $REMOTE_FILE"
    echo "     docker load -i ${REMOTE_FILE%.gz}"
    echo ""
    echo "  4. Migrasi Database (jika diperlukan):"
    echo "     # Di local machine, backup database:"
    echo "     ./migrate-database.sh backup"
    echo ""
    echo "     # Transfer backup ke VPS:"
    echo "     ./migrate-database.sh transfer $VPS_TARGET"
    echo ""
    echo "     # Di VPS, restore database:"
    echo "     ./migrate-database.sh restore /tmp/bagana-ai-database/backup_*.sql"
    echo ""
    echo "  5. Deploy aplikasi:"
    echo "     ./deploy.sh"
    echo ""
    print_info "Untuk panduan migrasi lengkap, lihat MIGRATION.md"
}

# Main execution
main() {
    print_header "Bagana AI - Package Transfer to VPS"
    
    check_package_exists
    get_vps_target
    check_ssh_connection
    check_remote_directory
    transfer_package
    show_next_steps
    
    echo ""
    print_success "Transfer selesai! 🎉"
}

# Run main function
main "$@"
