#!/bin/bash

#############################################################################
# ERPNext Custom Templates Deployment Script
#############################################################################
# 
# This script copies custom Chart of Accounts templates from the local
# workspace to the ERPNext container's verified templates directory.
#
# Usage:
#   ./copy_templates_to_container.sh [CONTAINER_NAME] [--clear-cache]
#
# Arguments:
#   CONTAINER_NAME  (optional) Name of the ERPNext backend container
#                   Default: erpnext_backend
#   --clear-cache   (optional) Clear ERPNext cache and restart container
#
# Examples:
#   ./copy_templates_to_container.sh
#   ./copy_templates_to_container.sh my-erpnext-backend
#   ./copy_templates_to_container.sh erpnext-backend --clear-cache
#
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CONTAINER_NAME="${1:-erpnext_backend}"
CLEAR_CACHE=false
SITE_NAME="erpnext.example.com"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --clear-cache)
            CLEAR_CACHE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [CONTAINER_NAME] [--clear-cache]"
            echo ""
            echo "Copy custom templates to ERPNext container"
            echo ""
            echo "Options:"
            echo "  CONTAINER_NAME    Name of the ERPNext backend container (default: erpnext_backend)"
            echo "  --clear-cache     Clear ERPNext cache and restart container after copying"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
    esac
done

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEMPLATES_SOURCE="${PROJECT_ROOT}/templates/account"
CONTAINER_TARGET_DIR="/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ERPNext Custom Templates Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if container exists and is running
echo -e "${YELLOW}→${NC} Checking container status..."
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${RED}✗${NC} Container '${CONTAINER_NAME}' exists but is not running"
        echo -e "${YELLOW}  Run: docker start ${CONTAINER_NAME}${NC}"
        exit 1
    else
        echo -e "${RED}✗${NC} Container '${CONTAINER_NAME}' not found"
        echo -e "${YELLOW}  Available containers:${NC}"
        docker ps -a --format "  - {{.Names}}"
        exit 1
    fi
fi
echo -e "${GREEN}✓${NC} Container '${CONTAINER_NAME}' is running"
echo ""

# Check if templates directory exists
if [ ! -d "${TEMPLATES_SOURCE}" ]; then
    echo -e "${RED}✗${NC} Templates directory not found: ${TEMPLATES_SOURCE}"
    exit 1
fi

# Count template files
TEMPLATE_COUNT=0

# Function to copy templates for a country
copy_country_templates() {
    local country_code="$1"
    local country_dir="${TEMPLATES_SOURCE}/${country_code}"
    
    if [ ! -d "${country_dir}" ]; then
        return
    fi
    
    echo -e "${YELLOW}→${NC} Processing templates for country: ${country_code}"
    
    # Find all JSON files (excluding certain patterns)
    while IFS= read -r -d '' template_file; do
        local filename=$(basename "${template_file}")
        
        # Skip files that don't match the expected naming pattern
        # Expected: br_*.json (country_code prefix)
        if [[ ! "${filename}" =~ ^${country_code}_.*\.json$ ]]; then
            echo -e "  ${YELLOW}⊗${NC} Skipping: ${filename} (doesn't match ${country_code}_*.json pattern)"
            continue
        fi
        
        local target_file="${CONTAINER_TARGET_DIR}/${filename}"
        
        echo -e "  ${BLUE}→${NC} Copying: ${filename}"
        
        # Copy file to container
        if docker cp "${template_file}" "${CONTAINER_NAME}:${target_file}"; then
            # Set correct permissions
            docker exec --user root "${CONTAINER_NAME}" chown frappe:frappe "${target_file}"
            docker exec --user root "${CONTAINER_NAME}" chmod 644 "${target_file}"
            echo -e "  ${GREEN}✓${NC} Deployed: ${filename}"
            ((TEMPLATE_COUNT++))
        else
            echo -e "  ${RED}✗${NC} Failed to copy: ${filename}"
            exit 1
        fi
    done < <(find "${country_dir}" -maxdepth 1 -name "${country_code}_*.json" -type f -print0)
}

# Copy templates for each country directory
echo -e "${BLUE}──────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE} Chart of Accounts Templates${NC}"
echo -e "${BLUE}──────────────────────────────────────────────────────────${NC}"
echo ""

# Find all country directories (two-letter codes)
for country_dir in "${TEMPLATES_SOURCE}"/*; do
    if [ -d "${country_dir}" ]; then
        country_code=$(basename "${country_dir}")
        # Only process if it looks like a country code (2 letters)
        if [[ "${country_code}" =~ ^[a-z]{2}$ ]]; then
            copy_country_templates "${country_code}"
        fi
    fi
done

echo ""
echo -e "${BLUE}──────────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}✓${NC} Successfully deployed ${TEMPLATE_COUNT} template(s)"
echo -e "${BLUE}──────────────────────────────────────────────────────────${NC}"
echo ""

# Clear cache and restart if requested
if [ "${CLEAR_CACHE}" = true ]; then
    echo -e "${YELLOW}→${NC} Clearing ERPNext cache..."
    if docker exec --user frappe "${CONTAINER_NAME}" bash -c "cd /home/frappe/frappe-bench && bench --site ${SITE_NAME} clear-cache"; then
        echo -e "${GREEN}✓${NC} Cache cleared successfully"
    else
        echo -e "${RED}✗${NC} Failed to clear cache"
        exit 1
    fi
    
    echo -e "${YELLOW}→${NC} Restarting container..."
    if docker restart "${CONTAINER_NAME}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Container restarted successfully"
        echo -e "${YELLOW}  Waiting for container to be ready...${NC}"
        sleep 5
    else
        echo -e "${RED}✗${NC} Failed to restart container"
        exit 1
    fi
    echo ""
fi

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Templates are now available in ERPNext:"
echo -e "  ${BLUE}→${NC} Navigate to: ${YELLOW}Company creation form${NC}"
echo -e "  ${BLUE}→${NC} Field: ${YELLOW}Chart of Accounts Based On${NC}"
echo -e "  ${BLUE}→${NC} Your custom templates should appear in the dropdown"
echo ""

if [ "${CLEAR_CACHE}" = false ]; then
    echo -e "${YELLOW}Note:${NC} If templates don't appear, run with --clear-cache:"
    echo -e "  ${BLUE}$0 ${CONTAINER_NAME} --clear-cache${NC}"
    echo ""
fi
