#!/bin/bash

# MarvelQuant to MarvelQuant Branding Re-application Script
# Story 2.1 - Phase 1 Upstream Merge Support
#
# This script re-applies MarvelQuant branding after merging upstream changes
# from the original MarvelQuant repository. It intelligently handles conflicts
# and preserves MarvelQuant customizations.

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
VERBOSE=false
INTERACTIVE=false
BACKUP_DIR="backups/reapply-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="logs/reapply-branding-$(date +%Y%m%d-%H%M%S).log"

# Print functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Re-apply MarvelQuant branding after upstream merge.

OPTIONS:
    --dry-run       Preview changes without modifying files
    --verbose       Show detailed output
    --interactive   Prompt before each file modification
    --help          Show this help message

EXAMPLES:
    $0 --dry-run                    # Preview re-application
    $0                              # Re-apply branding
    $0 --interactive                # Re-apply with prompts

WORKFLOW:
    1. Detect files modified by upstream merge
    2. Identify MarvelQuant references in modified files
    3. Re-apply MarvelQuant branding
    4. Verify logo files are intact
    5. Generate report

TYPICAL USAGE AFTER UPSTREAM MERGE:
    git fetch upstream
    git merge upstream/main
    # Resolve any conflicts manually
    ./scripts/reapply-branding.sh --dry-run
    ./scripts/reapply-branding.sh
    ./scripts/verify-branding.sh

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Create log directory
mkdir -p logs

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Initialize
print_header "MarvelQuant Branding Re-application"
if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN MODE - No files will be modified"
fi
echo ""

log "Script started - Dry run: $DRY_RUN, Interactive: $INTERACTIVE"

# Create backup directory if not dry run
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$BACKUP_DIR"
    print_info "Backup directory: $BACKUP_DIR"
    log "Backup directory created: $BACKUP_DIR"
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    log "ERROR: Not in a git repository"
    exit 1
fi

# Detect recently modified files (last merge)
print_info "Detecting files modified by recent merge..."
MODIFIED_FILES=$(git diff --name-only HEAD@{1} HEAD 2>/dev/null || echo "")

if [ -z "$MODIFIED_FILES" ]; then
    print_warning "No recently merged files detected"
    print_info "Scanning all files for MarvelQuant references instead..."
    log "No recent merge detected, scanning all files"
    
    # Fall back to scanning all files
    MODIFIED_FILES=$(find . -type f \( -name "*.py" -o -name "*.html" -o -name "*.js" -o -name "*.css" -o -name "*.md" \) \
        -not -path "*/.git/*" \
        -not -path "*/.venv/*" \
        -not -path "*/venv/*" \
        -not -path "*/node_modules/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/backups/*" \
        -not -path "*/logs/*" \
        -not -path "*/docs/bmad/*")
fi

FILE_COUNT=$(echo "$MODIFIED_FILES" | wc -l | tr -d ' ')
print_success "Found $FILE_COUNT files to check"
log "Found $FILE_COUNT files to check"
echo ""

# Counters
TOTAL_FILES=0
MODIFIED_FILES_COUNT=0
TOTAL_REPLACEMENTS=0

# Replacement function
replace_in_file() {
    local file=$1
    local search=$2
    local replace=$3
    local description=$4
    
    # Check if file contains the search pattern
    if grep -q "$search" "$file" 2>/dev/null; then
        local count=$(grep -o "$search" "$file" | wc -l | tr -d ' ')
        
        if [ "$VERBOSE" = true ]; then
            print_info "  $description: $count occurrence(s) in $file"
        fi
        
        # Interactive mode
        if [ "$INTERACTIVE" = true ] && [ "$DRY_RUN" = false ]; then
            echo ""
            print_warning "Found $count occurrence(s) of '$search' in $file"
            read -p "Replace with '$replace'? (y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Skipped: $file"
                return 1
            fi
        fi
        
        if [ "$DRY_RUN" = false ]; then
            # Create backup
            cp "$file" "$BACKUP_DIR/$(basename $file).bak"
            
            # Perform replacement (macOS compatible)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s|$search|$replace|g" "$file"
            else
                sed -i "s|$search|$replace|g" "$file"
            fi
        fi
        
        TOTAL_REPLACEMENTS=$((TOTAL_REPLACEMENTS + count))
        return 0
    fi
    return 1
}

# Process files
print_header "Re-applying MarvelQuant Branding"

for file in $MODIFIED_FILES; do
    # Skip if file doesn't exist
    if [ ! -f "$file" ]; then
        continue
    fi
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    file_modified=false
    
    # Skip binary files
    if file "$file" | grep -q "text"; then
        
        # REPLACEMENT ORDER (same as replace-branding.sh):
        
        # 1. URLs
        if replace_in_file "$file" "marvelquant\.in" "marvelquant.com" "URL"; then
            file_modified=true
        fi
        if replace_in_file "$file" "www\.marvelquant\.in" "www.marvelquant.com" "URL (www)"; then
            file_modified=true
        fi
        if replace_in_file "$file" "https://marvelquant\.in" "https://marvelquant.com" "URL (https)"; then
            file_modified=true
        fi
        if replace_in_file "$file" "http://marvelquant\.in" "http://marvelquant.com" "URL (http)"; then
            file_modified=true
        fi
        
        # 2. Social media
        if replace_in_file "$file" "@marvelquant" "@marvelquant" "Social media"; then
            file_modified=true
        fi
        
        # 3. Possessive
        if replace_in_file "$file" "MarvelQuant's" "MarvelQuant's" "Possessive"; then
            file_modified=true
        fi
        if replace_in_file "$file" "marvelquant's" "marvelquant's" "Possessive (lowercase)"; then
            file_modified=true
        fi
        
        # 4. Package names
        if replace_in_file "$file" "marvelquant" "marvelquant" "Package name"; then
            file_modified=true
        fi
        
        # 5. Standard text
        if replace_in_file "$file" "MarvelQuant" "MarvelQuant" "Standard"; then
            file_modified=true
        fi
        
        if [ "$file_modified" = true ]; then
            MODIFIED_FILES_COUNT=$((MODIFIED_FILES_COUNT + 1))
            if [ "$VERBOSE" = false ]; then
                print_success "Modified: $file"
            fi
        fi
    fi
done

echo ""
print_header "Logo Files Verification"

# Verify logo files are intact
LOGO_FILES=(
    "static/favicon/logo.png"
    "static/favicon/apple-touch-icon.png"
    "static/favicon/android-chrome-192x192.png"
    "static/favicon/mstile-150x150.png"
    "static/favicon/favicon-32x32.png"
    "static/favicon/favicon-16x16.png"
    "static/favicon/favicon.ico"
    "static/favicon/safari-pinned-tab.svg"
)

LOGO_ISSUES=0
for logo in "${LOGO_FILES[@]}"; do
    if [ -f "$logo" ]; then
        print_success "Verified: $logo"
    else
        print_warning "Missing: $logo (may need to re-run logo conversion)"
        LOGO_ISSUES=$((LOGO_ISSUES + 1))
    fi
done

echo ""
print_header "Summary"
echo -e "Total files checked:    ${BLUE}$TOTAL_FILES${NC}"
echo -e "Files modified:         ${GREEN}$MODIFIED_FILES_COUNT${NC}"
echo -e "Total replacements:     ${GREEN}$TOTAL_REPLACEMENTS${NC}"
echo -e "Logo files missing:     ${YELLOW}$LOGO_ISSUES${NC}"

if [ "$DRY_RUN" = true ]; then
    echo ""
    print_warning "DRY RUN COMPLETE - No files were actually modified"
    print_info "Run without --dry-run to apply changes"
else
    echo ""
    print_success "Branding re-application complete!"
    print_info "Backup location: $BACKUP_DIR"
    print_info "Log file: $LOG_FILE"
    
    if [ $LOGO_ISSUES -gt 0 ]; then
        echo ""
        print_warning "Some logo files are missing"
        print_info "Run: ./scripts/convert-logos.sh to regenerate logos"
    fi
    
    echo ""
    print_info "Next steps:"
    print_info "  1. Run: ./scripts/verify-branding.sh"
    print_info "  2. Test the application"
    print_info "  3. Commit changes: git add . && git commit -m 'Re-apply MarvelQuant branding after upstream merge'"
fi

log "Script completed - Modified files: $MODIFIED_FILES_COUNT, Total replacements: $TOTAL_REPLACEMENTS"

