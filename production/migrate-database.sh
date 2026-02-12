#!/bin/bash

###############################################################################
# Bagana AI - Database Migration Script
# 
# Script untuk backup, transfer, dan restore database dari local ke VPS
# 
# Usage:
#   chmod +x migrate-database.sh
#   ./migrate-database.sh backup                    # Backup database lokal
#   ./migrate-database.sh transfer [vps] [file]     # Transfer backup ke VPS
#   ./migrate-database.sh restore [file]            # Restore di VPS
#
# Example:
#   ./migrate-database.sh backup
#   ./migrate-database.sh transfer root@192.168.1.100 backup_20250213.sql
#   ./migrate-database.sh restore backup_20250213.sql
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
BACKUP_DIR="$SCRIPT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ACTION="${1:-}"

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

# Check Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose tidak terinstall!"
        exit 1
    fi
    print_success "Docker Compose terinstall"
}

# Backup database
backup_database() {
    print_header "Backing Up Database"
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Check if docker-compose is running
    cd "$SCRIPT_DIR"
    if ! docker-compose ps postgres &> /dev/null | grep -q "Up"; then
        print_error "PostgreSQL container tidak berjalan!"
        print_info "Jalankan: docker-compose up -d postgres"
        exit 1
    fi
    
    BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql"
    
    print_info "Backing up database..."
    print_info "Target file: $BACKUP_FILE"
    
    # Backup database
    docker-compose exec -T postgres pg_dump -U bagana_user bagana_ai > "$BACKUP_FILE"
    
    # Check file size
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    print_success "Backup completed: $BACKUP_FILE (${FILE_SIZE})"
    
    # Verify backup
    print_info "Verifying backup file..."
    if [ -s "$BACKUP_FILE" ]; then
        LINE_COUNT=$(wc -l < "$BACKUP_FILE")
        print_success "Backup verified: ${LINE_COUNT} lines"
    else
        print_error "Backup file kosong atau tidak valid!"
        exit 1
    fi
    
    # Show backup info
    echo ""
    print_info "Backup file location: $BACKUP_FILE"
    print_info "To transfer to VPS:"
    echo "  scp $BACKUP_FILE root@YOUR_VPS_IP:/tmp/bagana-ai-database/"
    echo ""
    echo "  Or use: ./migrate-database.sh transfer root@YOUR_VPS_IP $BACKUP_FILE"
}

# Transfer backup to VPS
transfer_backup() {
    print_header "Transferring Database Backup to VPS"
    
    VPS_TARGET="${2:-}"
    BACKUP_FILE="${3:-}"
    
    if [ -z "$VPS_TARGET" ]; then
        print_info "Masukkan VPS target (format: user@ip atau user@domain):"
        read -p "VPS Target: " VPS_TARGET
        
        if [ -z "$VPS_TARGET" ]; then
            print_error "VPS target harus diisi!"
            exit 1
        fi
    fi
    
    if [ -z "$BACKUP_FILE" ]; then
        # Find latest backup file
        BACKUP_FILE=$(find "$BACKUP_DIR" -name "backup_*.sql" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        
        if [ -z "$BACKUP_FILE" ]; then
            print_error "Backup file tidak ditemukan!"
            print_info "Jalankan backup terlebih dahulu: ./migrate-database.sh backup"
            exit 1
        fi
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "File tidak ditemukan: $BACKUP_FILE"
        exit 1
    fi
    
    print_success "VPS Target: $VPS_TARGET"
    print_success "Backup File: $BACKUP_FILE"
    
    # Check SSH connection
    print_info "Testing SSH connection..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$VPS_TARGET" exit 2>/dev/null; then
        print_success "SSH connection OK"
    else
        print_warning "SSH connection test failed"
        print_info "Pastikan SSH key sudah di-setup atau password tersedia"
        read -p "Lanjutkan transfer? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Create remote directory
    REMOTE_DIR="/tmp/bagana-ai-database"
    print_info "Creating remote directory..."
    ssh "$VPS_TARGET" "mkdir -p $REMOTE_DIR" 2>/dev/null || true
    
    # Transfer file
    REMOTE_FILE="$REMOTE_DIR/$(basename "$BACKUP_FILE")"
    print_info "Transferring $BACKUP_FILE to $VPS_TARGET:$REMOTE_FILE..."
    
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    print_info "File size: ${FILE_SIZE}"
    
    # Transfer with progress if available
    if command -v pv &> /dev/null; then
        pv "$BACKUP_FILE" | ssh "$VPS_TARGET" "cat > $REMOTE_FILE"
    else
        scp "$BACKUP_FILE" "$VPS_TARGET:$REMOTE_FILE"
    fi
    
    print_success "Transfer completed"
    
    # Verify file on remote
    print_info "Verifying file on remote..."
    REMOTE_SIZE=$(ssh "$VPS_TARGET" "du -h $REMOTE_FILE | cut -f1" 2>/dev/null)
    print_success "File verified on remote: ${REMOTE_SIZE}"
    
    echo ""
    print_info "Next steps on VPS:"
    echo "  1. SSH ke VPS:"
    echo "     ssh $VPS_TARGET"
    echo ""
    echo "  2. Restore database:"
    echo "     cd /var/www/bagana-ai/production"
    echo "     ./migrate-database.sh restore $REMOTE_FILE"
}

# Restore database
restore_database() {
    print_header "Restoring Database"
    
    BACKUP_FILE="${2:-}"
    
    if [ -z "$BACKUP_FILE" ]; then
        # Find latest backup file in common locations
        BACKUP_FILE=$(find . /tmp/bagana-ai-database ~ -name "backup_*.sql" -type f 2>/dev/null | head -n 1)
        
        if [ -z "$BACKUP_FILE" ]; then
            print_error "Backup file tidak ditemukan!"
            print_info "Specify file: ./migrate-database.sh restore /path/to/backup.sql"
            exit 1
        fi
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "File tidak ditemukan: $BACKUP_FILE"
        exit 1
    fi
    
    print_success "Backup File: $BACKUP_FILE"
    
    # Check file size
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    print_info "File size: ${FILE_SIZE}"
    
    # Check if docker-compose is running
    cd "$SCRIPT_DIR"
    if ! docker-compose ps postgres &> /dev/null | grep -q "Up"; then
        print_error "PostgreSQL container tidak berjalan!"
        print_info "Starting PostgreSQL..."
        docker-compose up -d postgres
        
        # Wait for PostgreSQL to be ready
        print_info "Waiting for PostgreSQL to be ready..."
        timeout=60
        counter=0
        while ! docker-compose exec -T postgres pg_isready -U bagana_user &> /dev/null; do
            sleep 2
            counter=$((counter + 2))
            if [ $counter -ge $timeout ]; then
                print_error "PostgreSQL tidak siap setelah $timeout detik"
                exit 1
            fi
        done
        print_success "PostgreSQL ready"
    fi
    
    # Confirm restore
    print_warning "PERINGATAN: Restore akan mengganti data yang ada di database!"
    read -p "Lanjutkan restore? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Restore dibatalkan"
        exit 0
    fi
    
    # Check if database has existing data
    EXISTING_TABLES=$(docker-compose exec -T postgres psql -U bagana_user -d bagana_ai -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ -n "$EXISTING_TABLES" ] && [ "$EXISTING_TABLES" -gt 0 ]; then
        print_warning "Database sudah memiliki ${EXISTING_TABLES} tabel"
        read -p "Hapus data yang ada sebelum restore? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Dropping existing schema..."
            docker-compose exec -T postgres psql -U bagana_user -d bagana_ai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" 2>/dev/null || true
            print_success "Schema dropped"
        fi
    fi
    
    # Restore database
    print_info "Restoring database..."
    print_warning "Proses ini mungkin memakan waktu beberapa menit..."
    
    cat "$BACKUP_FILE" | docker-compose exec -T postgres psql -U bagana_user -d bagana_ai
    
    print_success "Database restored"
    
    # Verify restore
    print_info "Verifying restore..."
    TABLE_COUNT=$(docker-compose exec -T postgres psql -U bagana_user -d bagana_ai -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
        print_success "Restore verified: ${TABLE_COUNT} tables created"
        
        # Show sample data counts
        echo ""
        print_info "Sample data counts:"
        docker-compose exec -T postgres psql -U bagana_user -d bagana_ai -c "SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL SELECT 'content_plans', COUNT(*) FROM content_plans UNION ALL SELECT 'chat_history', COUNT(*) FROM chat_history;" 2>/dev/null || true
    else
        print_warning "Tidak ada tabel yang ditemukan setelah restore"
    fi
    
    echo ""
    print_info "Next steps:"
    echo "  1. Restart application containers:"
    echo "     docker-compose restart backend frontend"
    echo ""
    echo "  2. Verify application:"
    echo "     docker-compose logs -f backend"
    echo "     curl http://localhost:8000/health"
}

# Show usage
show_usage() {
    echo "Usage: $0 {backup|transfer|restore} [options]"
    echo ""
    echo "Commands:"
    echo "  backup                    Backup database lokal"
    echo "  transfer [vps] [file]     Transfer backup ke VPS"
    echo "  restore [file]            Restore database di VPS"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 transfer root@192.168.1.100 backup_20250213.sql"
    echo "  $0 restore backup_20250213.sql"
}

# Main execution
main() {
    check_docker_compose
    
    case "$ACTION" in
        backup)
            backup_database
            ;;
        transfer)
            transfer_backup "$@"
            ;;
        restore)
            restore_database "$@"
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Operation completed! 🎉"
}

# Run main function
main "$@"
