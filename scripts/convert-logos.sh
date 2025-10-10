#!/usr/bin/env bash

################################################################################
# MarvelQuant Logo Conversion Script
# Converts SVG source logo to all required formats and sizes
#
# Source: docs/bmad/Logo-Main.svg (Vector SVG)
# Output: static/favicon/ (8 logo files)
#
# Requirements:
#   - rsvg-convert (preferred) OR ImageMagick (fallback)
#   - optipng (optional, for optimization)
#
# Usage: ./scripts/convert-logos.sh
################################################################################

set -e  # Exit on error

# Ensure we're using bash 4+ for associative arrays, or use workaround
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "Warning: Bash 4+ recommended. Using compatibility mode."
    USE_COMPAT=true
else
    USE_COMPAT=false
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOURCE_SVG_FULL="docs/bmad/Logo-Main-Fixed.svg"
SOURCE_SVG_SYMBOL="docs/bmad/Logo-Symbol.svg"
OUTPUT_DIR="static/favicon"
BACKUP_DIR="static/favicon-backup-$(date +%Y%m%d-%H%M%S)"

# Logo strategy: ALL files use SYMBOL ONLY (no text)
# Rationale: Text is unreadable at small sizes; symbol-only is standard for favicons
USE_SYMBOL_FOR_ALL=true

# Use Logo-Main-Fixed.svg for conversion (gradient with proper opacity)
# We'll crop the symbol portion from the full logo
USE_CROP_METHOD=true

# Logo sizes to generate (filename:size pairs)
LOGO_FILES=(
    "logo.png:512"
    "apple-touch-icon.png:180"
    "android-chrome-192x192.png:192"
    "favicon-32x32.png:32"
    "favicon-16x16.png:16"
    "mstile-150x150.png:150"
)

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

################################################################################
# Pre-flight Checks
################################################################################

print_header "MarvelQuant Logo Conversion - Pre-flight Checks"

# Check if source SVG files exist
if [ ! -f "$SOURCE_SVG_SYMBOL" ]; then
    print_error "Symbol SVG not found: $SOURCE_SVG_SYMBOL"
    print_info "Creating symbol-only SVG from main logo..."

    # Extract symbol from main SVG (viewBox 0 0 310 296)
    if [ ! -f "$SOURCE_SVG_FULL" ]; then
        print_error "Main SVG not found: $SOURCE_SVG_FULL"
        exit 1
    fi

    # Create symbol SVG by extracting the symbol path
    cat > "$SOURCE_SVG_SYMBOL" << 'SYMBOLSVG'
<svg width="310" height="296" viewBox="0 0 310 296" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M0.350586 1.69245C0.350586 0.757733 1.10832 0 2.04303 0H233.062C233.996 0 234.754 0.75773 234.754 1.69244V196.126C234.754 196.553 234.916 196.964 235.206 197.277L307.614 275.309C308.619 276.392 307.851 278.152 306.373 278.152H235.521C235.04 278.152 234.583 277.948 234.262 277.591L195.961 234.965C195.64 234.608 195.182 234.404 194.702 234.404H2.04303C1.10832 234.404 0.350586 233.646 0.350586 232.711V1.69245ZM49.1497 42.3113C48.215 42.3113 47.4572 43.0691 47.4572 44.0038V185.182C47.4572 186.117 48.215 186.874 49.1497 186.874H71.7174H79.1408H109.299H128.675H147.289H164.939H187.507C188.442 186.874 189.199 186.117 189.199 185.182V44.0038C189.199 43.0691 188.442 42.3113 187.507 42.3113H164.774C164.306 42.3113 163.859 42.5048 163.539 42.8458L119.672 89.6028C119.004 90.3142 117.875 90.3156 117.206 89.6059L73.117 42.8428C72.7972 42.5036 72.3517 42.3113 71.8855 42.3113H49.1497Z" fill="url(#paint0_linear_23_1431)"/>
<defs>
<linearGradient id="paint0_linear_23_1431" x1="288" y1="-162.5" x2="486.554" y2="314.484" gradientUnits="userSpaceOnUse">
<stop stop-color="#08102E"/>
<stop offset="0.316401" stop-color="#1A2B6B"/>
<stop offset="0.657544" stop-color="#0D58C6"/>
<stop offset="0.938369" stop-color="white" stop-opacity="0"/>
</linearGradient>
</defs>
</svg>
SYMBOLSVG

    print_success "Symbol SVG created: $SOURCE_SVG_SYMBOL"
fi

print_success "Symbol SVG found: $SOURCE_SVG_SYMBOL ($(du -h "$SOURCE_SVG_SYMBOL" | cut -f1))"

# Check for conversion tools
CONVERTER=""
if check_command "rsvg-convert"; then
    CONVERTER="rsvg"
    print_success "Using rsvg-convert (optimal quality)"
elif check_command "convert"; then
    CONVERTER="imagemagick"
    print_success "Using ImageMagick convert (fallback)"
else
    print_error "No SVG conversion tool found!"
    echo ""
    print_info "Please install one of the following:"
    echo "  macOS:   brew install librsvg    (for rsvg-convert)"
    echo "           brew install imagemagick (for convert)"
    echo "  Linux:   apt-get install librsvg2-bin"
    echo "           apt-get install imagemagick"
    exit 1
fi

# Check for optimization tools (optional)
OPTIMIZE=false
if check_command "optipng"; then
    OPTIMIZE=true
    print_success "PNG optimization available (optipng)"
else
    print_warning "optipng not found - PNGs will not be optimized (optional)"
fi

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    print_error "Output directory not found: $OUTPUT_DIR"
    exit 1
fi
print_success "Output directory found: $OUTPUT_DIR"

echo ""

################################################################################
# Backup Existing Logos
################################################################################

print_header "Backing Up Existing Logos"

mkdir -p "$BACKUP_DIR"
cp -r "$OUTPUT_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
print_success "Backup created: $BACKUP_DIR"

echo ""

################################################################################
# SVG to PNG Conversion
################################################################################

print_header "Converting SVG to PNG (6 sizes)"

convert_svg_to_png() {
    local output_file="$1"
    local size="$2"
    local output_path="$OUTPUT_DIR/$output_file"

    print_info "Generating $output_file (${size}x${size}px) from symbol..."

    # WORKAROUND for rsvg-convert gradient opacity bug:
    # 1. Render full logo at high resolution with WHITE background
    # 2. Crop to symbol portion (left 38.75% of width)
    # 3. Remove white background (make transparent)
    # 4. Resize to target size with high-quality filtering
    # 5. Add sharpening for small sizes

    # Calculate high-res dimensions
    # Use higher multipliers for smaller sizes to reduce artifacts
    local multiplier=3
    if [ "$size" -le 16 ]; then
        multiplier=8  # 8x for 16x16 (128px source)
    elif [ "$size" -le 32 ]; then
        multiplier=6  # 6x for 32x32 (192px source)
    elif [ "$size" -le 48 ]; then
        multiplier=5  # 5x for 48x48 (240px source)
    fi

    local hires_size=$((size * multiplier))
    local full_width=$((hires_size * 800 / 310))  # Scale to full logo width
    local full_height=$((full_width * 296 / 800))  # Maintain aspect ratio
    local crop_width=$((full_width * 310 / 800))   # Symbol is 310/800 of full width

    # Step 1: Render full logo at high resolution with white background
    if ! command -v rsvg-convert &> /dev/null; then
        print_error "rsvg-convert not found! Please install: brew install librsvg"
        return 1
    fi

    rsvg-convert \
        -w "$full_width" \
        -h "$full_height" \
        --background-color=white \
        "$SOURCE_SVG_FULL" \
        -o "/tmp/logo_hires_white.png"

    # Step 2-5: Crop, remove white background, resize, sharpen
    if command -v magick &> /dev/null; then
        # Determine sharpening based on size
        # Stronger sharpening for smaller sizes to prevent pixelation
        local sharpen_args=""
        if [ "$size" -le 16 ]; then
            sharpen_args="-unsharp 1x1"  # Strong sharpening for 16x16
        elif [ "$size" -le 32 ]; then
            sharpen_args="-unsharp 0x1.5"  # Medium sharpening for 32x32
        elif [ "$size" -le 48 ]; then
            sharpen_args="-unsharp 0x1"  # Light sharpening for 48x48
        fi

        # FINAL APPROACH: Crop, resize, then make white transparent
        # This preserves the gradient colors while removing white background
        # Use higher fuzz tolerance for small sizes to catch all white artifacts
        local fuzz_tolerance="10%"
        if [ "$size" -le 48 ]; then
            fuzz_tolerance="25%"  # Higher tolerance for small sizes to remove all white
        fi

        magick "/tmp/logo_hires_white.png" \
            -crop "${crop_width}x${full_height}+0+0" \
            +repage \
            -filter Lanczos \
            -resize "${size}x${size}" \
            -fuzz "$fuzz_tolerance" \
            -transparent white \
            $sharpen_args \
            -background none \
            -gravity center \
            -extent "${size}x${size}" \
            -fuzz "$fuzz_tolerance" \
            -transparent white \
            -fuzz 35% \
            -transparent white \
            "$output_path"

        # Additional cleanup for small sizes: remove very light pixels (anti-aliasing artifacts)
        # Target light gray pixels that appear near-white (e.g., #DCDCDC and lighter)
        if [ "$size" -le 48 ]; then
            magick "$output_path" \
                -fuzz 50% \
                -transparent "rgb(220,220,220)" \
                "$output_path"
        fi
    else
        print_error "ImageMagick not found! Please install: brew install imagemagick"
        return 1
    fi

    # Cleanup
    rm -f "/tmp/logo_hires_white.png"

    if [ $? -eq 0 ]; then
        print_success "$output_file created ($(du -h "$output_path" | cut -f1))"
    else
        print_error "Failed to create $output_file"
        return 1
    fi
}

# Generate all PNG sizes
for entry in "${LOGO_FILES[@]}"; do
    file="${entry%:*}"
    size="${entry#*:}"
    convert_svg_to_png "$file" "$size"
done

echo ""

################################################################################
# Generate Multi-Resolution ICO
################################################################################

print_header "Generating Multi-Resolution favicon.ico"

if check_command "magick"; then
    print_info "Creating favicon.ico with multiple resolutions (16x16, 32x32, 48x48)..."

    # Use the already-generated PNGs to create multi-resolution ICO
    # This ensures consistency with the other logo files
    magick \
        "$OUTPUT_DIR/favicon-16x16.png" \
        "$OUTPUT_DIR/favicon-32x32.png" \
        "$OUTPUT_DIR/logo.png" -resize 48x48 \
        "$OUTPUT_DIR/favicon.ico"

    if [ $? -eq 0 ]; then
        print_success "favicon.ico created ($(du -h "$OUTPUT_DIR/favicon.ico" | cut -f1))"
    else
        print_error "Failed to create favicon.ico"
    fi
else
    print_warning "ImageMagick not available - cannot create multi-resolution ICO"
    print_info "Using 32x32 PNG as fallback..."
    cp "$OUTPUT_DIR/favicon-32x32.png" "$OUTPUT_DIR/favicon.ico"
fi

echo ""

################################################################################
# Safari Pinned Tab SVG
################################################################################

print_header "Generating Safari Pinned Tab SVG"

print_info "Copying symbol SVG for safari-pinned-tab.svg..."

# Use symbol-only SVG for Safari pinned tab
cp "$SOURCE_SVG_SYMBOL" "$OUTPUT_DIR/safari-pinned-tab.svg"

# Option 2: Optimize SVG (if svgo is available)
if check_command "svgo"; then
    print_info "Optimizing SVG with svgo..."
    svgo "$OUTPUT_DIR/safari-pinned-tab.svg" -o "$OUTPUT_DIR/safari-pinned-tab.svg" --quiet
    print_success "safari-pinned-tab.svg optimized"
else
    print_success "safari-pinned-tab.svg created (unoptimized)"
    print_warning "Install svgo for SVG optimization: npm install -g svgo"
fi

echo ""

################################################################################
# PNG Optimization
################################################################################

if [ "$OPTIMIZE" = true ]; then
    print_header "Optimizing PNG Files"

    for entry in "${LOGO_FILES[@]}"; do
        file="${entry%:*}"
        print_info "Optimizing $file..."
        optipng -quiet -o2 "$OUTPUT_DIR/$file"
        print_success "$file optimized ($(du -h "$OUTPUT_DIR/$file" | cut -f1))"
    done

    echo ""
fi

################################################################################
# Verification
################################################################################

print_header "Verification"

echo ""
print_info "Generated files:"
echo ""

for entry in "${LOGO_FILES[@]}"; do
    file="${entry%:*}"
    if [ -f "$OUTPUT_DIR/$file" ]; then
        size=$(du -h "$OUTPUT_DIR/$file" | cut -f1)
        dimensions=$(sips -g pixelWidth -g pixelHeight "$OUTPUT_DIR/$file" 2>/dev/null | grep -E "pixelWidth|pixelHeight" | awk '{print $2}' | tr '\n' 'x' | sed 's/x$//')
        print_success "$file - ${dimensions}px - $size"
    else
        print_error "$file - MISSING"
    fi
done

# Check ICO
if [ -f "$OUTPUT_DIR/favicon.ico" ]; then
    size=$(du -h "$OUTPUT_DIR/favicon.ico" | cut -f1)
    print_success "favicon.ico - Multi-res - $size"
else
    print_error "favicon.ico - MISSING"
fi

# Check SVG
if [ -f "$OUTPUT_DIR/safari-pinned-tab.svg" ]; then
    size=$(du -h "$OUTPUT_DIR/safari-pinned-tab.svg" | cut -f1)
    print_success "safari-pinned-tab.svg - Vector - $size"
else
    print_error "safari-pinned-tab.svg - MISSING"
fi

echo ""

################################################################################
# Summary
################################################################################

print_header "Conversion Complete!"

echo ""
print_success "All logo files generated successfully!"
print_info "Output directory: $OUTPUT_DIR"
print_info "Backup directory: $BACKUP_DIR"
echo ""
print_info "Next steps:"
echo "  1. Visually inspect logos in $OUTPUT_DIR"
echo "  2. Test logos in browser (especially 16x16 and 32x32)"
echo "  3. Commit changes: git add $OUTPUT_DIR && git commit -m 'Branding: Replace logos with MarvelQuant branding'"
echo ""

