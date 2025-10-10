#!/bin/bash

# MarvelQuant to MarvelQuant Branding Verification Script
# Story 2.1 - Phase 1 Verification Automation
#
# This script verifies that all branding replacements have been completed
# correctly and identifies any remaining MarvelQuant references.

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERBOSE=false
REPORT_FILE="logs/verify-branding-$(date +%Y%m%d-%H%M%S).log"

# Counters
TOTAL_FILES=0
FILES_WITH_ISSUES=0
TOTAL_ISSUES=0

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

Verify MarvelQuant to MarvelQuant branding replacement.

OPTIONS:
    --verbose       Show detailed output
    --help          Show this help message

EXAMPLES:
    $0                      # Run verification
    $0 --verbose            # Run with detailed output

CHECKS:
    1. Remaining "MarvelQuant" references
    2. Remaining "marvelquant" references
    3. Remaining "marvelquant.com" URLs
    4. Remaining "@marvelquant" social handles
    5. Logo files verification
    6. Acceptance criteria validation

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$REPORT_FILE"
}

# Initialize
print_header "MarvelQuant Branding Verification"
echo ""

log "Verification started"

# Define file patterns to include (excluding *.py as Python imports are internal code)
INCLUDE_PATTERNS=(
    "*.html"
    "*.js"
    "*.css"
    "*.md"
    "*.txt"
    "*.yaml"
    "*.yml"
    "*.json"
)

# Define directories to exclude
EXCLUDE_DIRS=(
    ".git"
    ".venv"
    "venv"
    "node_modules"
    "__pycache__"
    "*.pyc"
    ".pytest_cache"
    "backups"
    "logs"
    "docs"
    "scripts"
)

# Build find command
FIND_CMD="find . -type f \("
for i in "${!INCLUDE_PATTERNS[@]}"; do
    if [ $i -eq 0 ]; then
        FIND_CMD="$FIND_CMD -name '${INCLUDE_PATTERNS[$i]}'"
    else
        FIND_CMD="$FIND_CMD -o -name '${INCLUDE_PATTERNS[$i]}'"
    fi
done
FIND_CMD="$FIND_CMD \)"

for dir in "${EXCLUDE_DIRS[@]}"; do
    FIND_CMD="$FIND_CMD -not -path '*/$dir/*'"
done

# Get list of files
print_info "Scanning for files to verify..."
FILES=$(eval $FIND_CMD)
TOTAL_FILES=$(echo "$FILES" | wc -l | tr -d ' ')
print_success "Found $TOTAL_FILES files to verify"
log "Found $TOTAL_FILES files to verify"
echo ""

# Verification function
check_pattern() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        local count=$(grep -o "$pattern" "$file" | wc -l | tr -d ' ')
        local lines=$(grep -n "$pattern" "$file" | cut -d: -f1 | tr '\n' ',' | sed 's/,$//')
        
        print_warning "$description found in $file (lines: $lines)"
        log "ISSUE: $description in $file (count: $count, lines: $lines)"
        
        if [ "$VERBOSE" = true ]; then
            echo "  Occurrences:"
            grep -n "$pattern" "$file" | head -5
            echo ""
        fi
        
        TOTAL_ISSUES=$((TOTAL_ISSUES + count))
        return 0
    fi
    return 1
}

# Process files
print_header "Checking for Remaining OpenAlgo References"

for file in $FILES; do
    file_has_issues=false

    # Skip binary files
    if file "$file" | grep -q "text"; then

        # Check for various OpenAlgo patterns (OLD branding that should be replaced)
        if check_pattern "$file" "OpenAlgo" "OpenAlgo (title case)"; then
            file_has_issues=true
        fi

        if check_pattern "$file" "openalgo" "openalgo (lowercase)"; then
            file_has_issues=true
        fi

        if check_pattern "$file" "openalgo\.in" "openalgo.in (URL)"; then
            file_has_issues=true
        fi

        if check_pattern "$file" "@openalgo" "@openalgo (social)"; then
            file_has_issues=true
        fi

        if [ "$file_has_issues" = true ]; then
            FILES_WITH_ISSUES=$((FILES_WITH_ISSUES + 1))
        fi
    fi
done

echo ""
print_header "Logo Files Verification"

# Check logo files
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
        print_success "Found: $logo"
        log "Logo file exists: $logo"
    else
        print_error "Missing: $logo"
        log "ERROR: Logo file missing: $logo"
        LOGO_ISSUES=$((LOGO_ISSUES + 1))
    fi
done

echo ""
print_header "Acceptance Criteria Validation"

# AC #1: Logo Replacement
if [ $LOGO_ISSUES -eq 0 ]; then
    print_success "AC #1: Logo Replacement - PASS (all 8 logo files present)"
    log "AC #1: PASS"
else
    print_error "AC #1: Logo Replacement - FAIL ($LOGO_ISSUES missing logo files)"
    log "AC #1: FAIL"
fi

# AC #2: Domain Migration
DOMAIN_ISSUES=$(grep -r "openalgo\.in" --include="*.py" --include="*.html" --include="*.js" --exclude-dir=".git" --exclude-dir="backups" --exclude-dir="logs" --exclude-dir="docs" --exclude-dir="scripts" --exclude-dir=".venv" --exclude-dir="venv" . 2>/dev/null | wc -l | tr -d ' ')
if [ $DOMAIN_ISSUES -eq 0 ]; then
    print_success "AC #2: Domain Migration - PASS (no openalgo.in references)"
    log "AC #2: PASS"
else
    print_error "AC #2: Domain Migration - FAIL ($DOMAIN_ISSUES openalgo.in references remain)"
    log "AC #2: FAIL"
fi

# AC #3: Text Branding (excluding Python imports which are internal code)
TEXT_ISSUES=$(grep -r "OpenAlgo\|openalgo" --include="*.html" --include="*.js" --include="*.md" --exclude-dir=".git" --exclude-dir="backups" --exclude-dir="logs" --exclude-dir="docs" --exclude-dir="scripts" --exclude-dir=".venv" --exclude-dir="venv" . 2>/dev/null | wc -l | tr -d ' ')
if [ $TEXT_ISSUES -eq 0 ]; then
    print_success "AC #3: Text Branding - PASS (no OpenAlgo text references in user-facing files)"
    log "AC #3: PASS"
else
    print_error "AC #3: Text Branding - FAIL ($TEXT_ISSUES OpenAlgo text references remain in user-facing files)"
    log "AC #3: FAIL"
fi

echo ""
print_header "Summary"
echo -e "Total files scanned:        ${BLUE}$TOTAL_FILES${NC}"
echo -e "Files with issues:          ${YELLOW}$FILES_WITH_ISSUES${NC}"
echo -e "Total issues found:         ${YELLOW}$TOTAL_ISSUES${NC}"
echo -e "Logo files missing:         ${YELLOW}$LOGO_ISSUES${NC}"

echo ""
if [ $TOTAL_ISSUES -eq 0 ] && [ $LOGO_ISSUES -eq 0 ]; then
    print_success "✓ VERIFICATION PASSED - All branding replacements complete!"
    log "Verification PASSED"
    exit 0
else
    print_warning "⚠ VERIFICATION INCOMPLETE - Issues found"
    print_info "Review the issues above and re-run replacement script if needed"
    print_info "Report file: $REPORT_FILE"
    log "Verification FAILED - Issues: $TOTAL_ISSUES, Logo issues: $LOGO_ISSUES"
    exit 1
fi

