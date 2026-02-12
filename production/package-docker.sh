#!/bin/bash

###############################################################################
# Bagana AI - Docker Images Package Script
# 
# Script untuk membuat package Docker images yang bisa ditransfer ke VPS
# 
# Usage:
#   chmod +x package-docker.sh
#   ./package-docker.sh
#
# Output:
#   - bagana-ai-docker-images.tar.gz (package semua images)
#   - bagana-ai-docker-images.tar (package tanpa kompresi)
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
PACKAGE_DIR="$SCRIPT_DIR/packages"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="bagana-ai-docker-images-${TIMESTAMP}"
PACKAGE_TAR="${PACKAGE_NAME}.tar"
PACKAGE_GZ="${PACKAGE_NAME}.tar.gz"

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

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker tidak terinstall!"
        exit 1
    fi
    print_success "Docker terinstall: $(docker --version)"
}

# Check Docker Compose installation
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose tidak terinstall!"
        exit 1
    fi
    print_success "Docker Compose terinstall"
}

# Build Docker images
build_images() {
    print_header "Building Docker Images"
    
    cd "$PROJECT_DIR"
    
    print_info "Building backend image..."
    docker build -f Dockerfile.backend -t bagana-ai-backend:latest .
    print_success "Backend image built"
    
    print_info "Building frontend image..."
    docker build -f Dockerfile.frontend -t bagana-ai-frontend:latest .
    print_success "Frontend image built"
    
    # List images
    print_info "Docker images yang akan di-package:"
    docker images | grep -E "bagana-ai|REPOSITORY" || true
}

# Get image names from docker-compose
get_image_names() {
    cd "$SCRIPT_DIR"
    
    # Get images from docker-compose
    IMAGES=()
    
    # Backend image (built)
    if docker images | grep -q "bagana-ai-backend"; then
        IMAGES+=("bagana-ai-backend:latest")
    fi
    
    # Frontend image (built)
    if docker images | grep -q "bagana-ai-frontend"; then
        IMAGES+=("bagana-ai-frontend:latest")
    fi
    
    # PostgreSQL image (from docker hub)
    IMAGES+=("postgres:14-alpine")
    
    # Nginx image (from docker hub)
    IMAGES+=("nginx:alpine")
    
    echo "${IMAGES[@]}"
}

# Save Docker images to tar file
save_images() {
    print_header "Saving Docker Images"
    
    # Create packages directory
    mkdir -p "$PACKAGE_DIR"
    
    # Get image names
    IMAGES=($(get_image_names))
    
    if [ ${#IMAGES[@]} -eq 0 ]; then
        print_error "Tidak ada images yang ditemukan!"
        print_info "Jalankan build terlebih dahulu atau pastikan images sudah ada"
        exit 1
    fi
    
    print_info "Images yang akan di-save:"
    for img in "${IMAGES[@]}"; do
        echo "  - $img"
    done
    
    # Pull images if not exists locally
    print_info "Memastikan semua images tersedia..."
    for img in "${IMAGES[@]}"; do
        if [[ "$img" == *"bagana-ai"* ]]; then
            print_info "Skipping pull for local image: $img"
        else
            print_info "Pulling $img..."
            docker pull "$img" || print_warning "Failed to pull $img, menggunakan local jika ada"
        fi
    done
    
    # Save images to tar file
    print_info "Saving images to ${PACKAGE_TAR}..."
    docker save "${IMAGES[@]}" -o "$PACKAGE_DIR/$PACKAGE_TAR"
    
    # Check file size
    FILE_SIZE=$(du -h "$PACKAGE_DIR/$PACKAGE_TAR" | cut -f1)
    print_success "Images saved: $PACKAGE_DIR/$PACKAGE_TAR (${FILE_SIZE})"
}

# Compress tar file
compress_package() {
    print_header "Compressing Package"
    
    print_info "Compressing ${PACKAGE_TAR}..."
    cd "$PACKAGE_DIR"
    gzip -c "$PACKAGE_TAR" > "$PACKAGE_GZ"
    
    # Check file sizes
    TAR_SIZE=$(du -h "$PACKAGE_TAR" | cut -f1)
    GZ_SIZE=$(du -h "$PACKAGE_GZ" | cut -f1)
    
    print_success "Package compressed:"
    echo "  - Uncompressed: $PACKAGE_TAR (${TAR_SIZE})"
    echo "  - Compressed:   $PACKAGE_GZ (${GZ_SIZE})"
    
    # Calculate compression ratio
    TAR_BYTES=$(stat -f%z "$PACKAGE_TAR" 2>/dev/null || stat -c%s "$PACKAGE_TAR" 2>/dev/null)
    GZ_BYTES=$(stat -f%z "$PACKAGE_GZ" 2>/dev/null || stat -c%s "$PACKAGE_GZ" 2>/dev/null)
    if [ -n "$TAR_BYTES" ] && [ -n "$GZ_BYTES" ] && [ "$TAR_BYTES" -gt 0 ]; then
        RATIO=$(echo "scale=1; (1 - $GZ_BYTES / $TAR_BYTES) * 100" | bc)
        print_info "Compression ratio: ${RATIO}%"
    fi
}

# Create package info file
create_package_info() {
    print_header "Creating Package Info"
    
    INFO_FILE="$PACKAGE_DIR/${PACKAGE_NAME}.info"
    
    cat > "$INFO_FILE" <<EOF
# Bagana AI Docker Images Package
# Created: $(date)
# Package: ${PACKAGE_NAME}

## Images Included:
$(for img in $(get_image_names); do echo "- $img"; done)

## File Sizes:
- ${PACKAGE_TAR}: $(du -h "$PACKAGE_DIR/$PACKAGE_TAR" | cut -f1)
- ${PACKAGE_GZ}: $(du -h "$PACKAGE_DIR/$PACKAGE_GZ" | cut -f1)

## Instructions:
1. Transfer ${PACKAGE_GZ} ke VPS
2. Extract: gunzip ${PACKAGE_GZ}
3. Load images: docker load -i ${PACKAGE_TAR}
4. Or use load-docker.sh script

## Docker Images List:
$(docker images | grep -E "bagana-ai|postgres|nginx|REPOSITORY" || echo "No images found")

EOF
    
    print_success "Package info created: $INFO_FILE"
}

# Show summary
show_summary() {
    print_header "Package Summary"
    
    echo ""
    print_info "Package files created in: $PACKAGE_DIR"
    echo ""
    ls -lh "$PACKAGE_DIR" | grep -E "${PACKAGE_NAME}|total" || true
    
    echo ""
    print_info "Next steps:"
    echo "  1. Transfer ${PACKAGE_GZ} ke VPS:"
    echo "     scp $PACKAGE_DIR/${PACKAGE_GZ} user@vps:/tmp/"
    echo ""
    echo "  2. Atau gunakan transfer-package.sh script"
    echo ""
    echo "  3. Di VPS, load images:"
    echo "     gunzip ${PACKAGE_GZ}"
    echo "     docker load -i ${PACKAGE_TAR}"
    echo ""
    echo "  4. Atau gunakan load-docker.sh script di VPS"
}

# Cleanup old packages (optional)
cleanup_old_packages() {
    read -p "Hapus package lama? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up old packages..."
        find "$PACKAGE_DIR" -name "bagana-ai-docker-images-*.tar*" -mtime +7 -delete 2>/dev/null || true
        print_success "Old packages cleaned"
    fi
}

# Main execution
main() {
    print_header "Bagana AI - Docker Images Packaging"
    
    check_docker
    check_docker_compose
    
    # Ask if should build first
    read -p "Build images terlebih dahulu? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_images
    else
        print_info "Skipping build, menggunakan images yang sudah ada"
    fi
    
    save_images
    compress_package
    create_package_info
    show_summary
    cleanup_old_packages
    
    echo ""
    print_success "Packaging selesai! 🎉"
}

# Run main function
main "$@"
