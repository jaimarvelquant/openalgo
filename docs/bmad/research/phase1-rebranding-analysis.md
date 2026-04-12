# COMPREHENSIVE PHASE 1 REBRANDING ANALYSIS & IMPLEMENTATION PLAN

**Project:** OpenAlgo → MarvelQuant Rebranding  
**Phase:** Phase 1 (LOW RISK) - Logo Replacement & Documentation Updates  
**Status:** ANALYSIS ONLY - NO CHANGES MADE  
**Date:** October 7, 2025

---

## TABLE OF CONTENTS

1. [Logo Conversion Strategy](#1-logo-conversion-strategy)
2. [Text Replacement Analysis](#2-text-replacement-analysis)
3. [Git Workflow for Upstream Sync](#3-git-workflow-for-upstream-sync)
4. [Automation Strategy](#4-automation-strategy)
5. [Risk Assessment](#5-risk-assessment)
6. [Implementation Checklist](#6-implementation-checklist)

---

## EXECUTIVE SUMMARY

This document provides a comprehensive analysis and implementation plan for Phase 1 of the OpenAlgo → MarvelQuant rebranding effort. Phase 1 focuses on LOW RISK changes:

- **Logo Replacement:** 8 files in `static/favicon/`
- **Text Replacement:** 35 HTML files + 104 Markdown files
- **Total Occurrences:** 1,006+ text replacements needed

**Key Findings:**
- Source logo: 1920x1080px PNG at `/Users/maruth/projects/openalgo/docs/bmad/Logo-view.png`
- Requires conversion to 8 different formats (square icons, favicons, SVG)
- 130+ occurrences in HTML templates
- 876+ occurrences in Markdown documentation
- Zero occurrences of typo variant "openlago"

**Risk Level:** LOW - No code execution changes, only visual and documentation updates

**Estimated Effort:** 10-20 hours for complete Phase 1 implementation

---

## 1. LOGO CONVERSION STRATEGY

### 1.1 Source Logo Analysis

**Source File:** `/Users/maruth/projects/openalgo/docs/bmad/Logo-view.png`
- **Dimensions:** 1920x1080px (16:9 aspect ratio)
- **Format:** PNG RGBA (with transparency support)
- **Size:** 52,685 bytes (~51 KB)
- **Color Mode:** 8-bit/color RGBA

**Challenge:** The source logo has a 16:9 aspect ratio, but most target formats require square dimensions (1:1 aspect ratio).

### 1.2 Target Files Required

**Location:** `/Users/maruth/projects/openalgo/static/favicon/`

| File | Size | Purpose | Notes |
|------|------|---------|-------|
| `logo.png` | 512x512px | Main UI logo (navbar) | Use center crop or padding |
| `apple-touch-icon.png` | 180x180px | iOS home screen | Requires opaque background |
| `android-chrome-192x192.png` | 192x192px | Android app icon | Supports transparency |
| `favicon-16x16.png` | 16x16px | Small browser favicon | May need simplification |
| `favicon-32x32.png` | 32x32px | Medium browser favicon | Standard size |
| `mstile-150x150.png` | 150x150px | Windows tile | Solid background recommended |
| `favicon.ico` | Multi-res | Browser favicon | Contains 16x16, 32x32, 48x48 |
| `safari-pinned-tab.svg` | Vector | Safari pinned tab | Monochrome SVG required |

### 1.3 Aspect Ratio Handling Strategy

**Three Approaches:**

**Option A: Center Crop (Recommended for Icons)**
- Crop to center square (1080x1080px) from source
- Best for: favicon, app icons, tiles
- Pros: No distortion, maintains logo integrity
- Cons: May lose horizontal content

**Option B: Contain with Padding**
- Scale to fit within square, add transparent padding
- Best for: logo.png (navbar usage)
- Pros: Shows full logo
- Cons: Logo appears smaller

**Option C: Contain with Background**
- Scale to fit within square, add colored background
- Best for: opaque formats (favicon.ico)
- Pros: Shows full logo with context
- Cons: Requires background color choice

**Recommendation:** Use Option A (center crop) for all square icons, Option B for logo.png

### 1.4 Prerequisites Installation

```bash
# macOS (using Homebrew)
brew install imagemagick
brew install librsvg  # For SVG conversion
brew install potrace  # For bitmap to vector conversion

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install imagemagick librsvg2-bin potrace

# Verify installation
convert --version
rsvg-convert --version
potrace --version
```

### 1.5 Step-by-Step Conversion Commands

#### Step 1: Create Center-Cropped Square Base

```bash
# Navigate to logo directory
cd /Users/maruth/projects/openalgo/docs/bmad

# Create a center-cropped 1080x1080 square version
# This will be our base for all square icons
convert Logo-view.png \
  -gravity center \
  -crop 1080x1080+0+0 \
  +repage \
  Logo-square-1080.png

# Alternative: If you want to preserve full logo with padding
convert Logo-view.png \
  -resize 1080x1080 \
  -background none \
  -gravity center \
  -extent 1080x1080 \
  Logo-square-padded-1080.png
```

#### Step 2: Generate All Required Formats

**2.1 logo.png (512x512px - Main UI Logo)**

```bash
# Option A: From center-cropped square (recommended)
convert Logo-square-1080.png \
  -resize 512x512 \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/logo.png

# Option B: From original with padding (shows full logo)
convert Logo-view.png \
  -resize 512x512 \
  -background none \
  -gravity center \
  -extent 512x512 \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/logo.png

# Optimize file size
optipng -o7 /Users/maruth/projects/openalgo/static/favicon/logo.png
```

**2.2 apple-touch-icon.png (180x180px - iOS Home Screen)**

```bash
# iOS requires opaque background (no transparency)
# Use white or brand color background

# With white background
convert Logo-square-1080.png \
  -resize 180x180 \
  -background white \
  -alpha remove \
  -alpha off \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/apple-touch-icon.png

# With custom background color (example: #1a1a1a for dark)
convert Logo-square-1080.png \
  -resize 180x180 \
  -background "#1a1a1a" \
  -alpha remove \
  -alpha off \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/apple-touch-icon.png

# Optimize
optipng -o7 /Users/maruth/projects/openalgo/static/favicon/apple-touch-icon.png
```

**2.3 android-chrome-192x192.png (192x192px - Android App Icon)**

```bash
# Android supports transparency
convert Logo-square-1080.png \
  -resize 192x192 \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/android-chrome-192x192.png

# Optimize
optipng -o7 /Users/maruth/projects/openalgo/static/favicon/android-chrome-192x192.png
```

**2.4 favicon-16x16.png (16x16px - Small Browser Favicon)**

```bash
# For very small sizes, may need to simplify logo
# Use Lanczos filter for best quality at small sizes
convert Logo-square-1080.png \
  -resize 16x16 \
  -filter Lanczos \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/favicon-16x16.png

# Optimize
optipng -o7 /Users/maruth/projects/openalgo/static/favicon/favicon-16x16.png
```

**2.5 favicon-32x32.png (32x32px - Medium Browser Favicon)**

```bash
convert Logo-square-1080.png \
  -resize 32x32 \
  -filter Lanczos \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/favicon-32x32.png

# Optimize
optipng -o7 /Users/maruth/projects/openalgo/static/favicon/favicon-32x32.png
```

**2.6 mstile-150x150.png (150x150px - Windows Tile)**

```bash
# Windows tiles typically use solid background
# Use brand color or white
convert Logo-square-1080.png \
  -resize 150x150 \
  -background white \
  -alpha remove \
  -alpha off \
  -quality 95 \
  /Users/maruth/projects/openalgo/static/favicon/mstile-150x150.png

# Optimize
optipng -o7 /Users/maruth/projects/openalgo/static/favicon/mstile-150x150.png
```

**2.7 favicon.ico (Multi-resolution ICO - 16x16, 32x32, 48x48)**

```bash
# First, create individual PNG files for each size
convert Logo-square-1080.png \
  -resize 16x16 \
  -filter Lanczos \
  -background white \
  -alpha remove \
  -alpha off \
  favicon-16.png

convert Logo-square-1080.png \
  -resize 32x32 \
  -filter Lanczos \
  -background white \
  -alpha remove \
  -alpha off \
  favicon-32.png

convert Logo-square-1080.png \
  -resize 48x48 \
  -filter Lanczos \
  -background white \
  -alpha remove \
  -alpha off \
  favicon-48.png

# Combine into multi-resolution ICO file
convert favicon-16.png favicon-32.png favicon-48.png \
  /Users/maruth/projects/openalgo/static/favicon/favicon.ico

# Clean up temporary files
rm favicon-16.png favicon-32.png favicon-48.png
```

**2.8 safari-pinned-tab.svg (Monochrome SVG - Safari Pinned Tab)**

This is the most complex conversion as it requires:
1. Converting PNG to monochrome bitmap
2. Tracing bitmap to vector (SVG)
3. Simplifying paths

```bash
# Step 1: Convert to monochrome bitmap (black on transparent)
convert Logo-square-1080.png \
  -alpha extract \
  -threshold 50% \
  -negate \
  logo-mono.pbm

# Step 2: Trace to SVG using potrace
potrace logo-mono.pbm \
  --svg \
  --output logo-traced.svg \
  --turdsize 2 \
  --alphamax 1.0

# Step 3: Optimize SVG (manual or using svgo)
# Install svgo: npm install -g svgo
svgo logo-traced.svg \
  --output /Users/maruth/projects/openalgo/static/favicon/safari-pinned-tab.svg \
  --multipass \
  --pretty

# Clean up
rm logo-mono.pbm logo-traced.svg

# Note: You may need to manually edit the SVG to:
# 1. Set viewBox="0 0 16 16" or similar
# 2. Ensure single color (black) paths
# 3. Remove any unnecessary attributes
```

### 1.6 Complete Batch Conversion Script

See full script in Section 4.1 - `scripts/convert-logos.sh`

### 1.7 Quality Verification Checklist

After conversion, verify each file:

**Visual Quality Checks:**
- [ ] `logo.png` - Clear and recognizable at 32px height (navbar size)
- [ ] `apple-touch-icon.png` - No transparency artifacts, clean edges
- [ ] `android-chrome-192x192.png` - Sharp at full size
- [ ] `favicon-16x16.png` - Recognizable despite tiny size
- [ ] `favicon-32x32.png` - Clear and sharp
- [ ] `mstile-150x150.png` - Clean background, no artifacts
- [ ] `favicon.ico` - Displays correctly in browser tab
- [ ] `safari-pinned-tab.svg` - Clean monochrome silhouette

**Technical Checks:**
```bash
# Check file sizes (should be reasonable)
ls -lh /Users/maruth/projects/openalgo/static/favicon/

# Check image dimensions
identify /Users/maruth/projects/openalgo/static/favicon/*.png

# Check ICO contains multiple resolutions
identify /Users/maruth/projects/openalgo/static/favicon/favicon.ico

# Check SVG is valid
xmllint --noout /Users/maruth/projects/openalgo/static/favicon/safari-pinned-tab.svg
```

**Browser Testing:**
- [ ] Chrome/Edge - favicon displays correctly
- [ ] Firefox - favicon displays correctly
- [ ] Safari - pinned tab icon displays correctly
- [ ] iOS Safari - home screen icon displays correctly
- [ ] Android Chrome - home screen icon displays correctly
- [ ] Windows - tile icon displays correctly

### 1.8 Rollback Plan

**Before making changes, backup existing logos:**

```bash
# Create backup directory
mkdir -p /Users/maruth/projects/openalgo/static/favicon-backup-$(date +%Y%m%d)

# Backup all existing logo files
cp /Users/maruth/projects/openalgo/static/favicon/*.png \
   /Users/maruth/projects/openalgo/static/favicon/*.ico \
   /Users/maruth/projects/openalgo/static/favicon/*.svg \
   /Users/maruth/projects/openalgo/static/favicon-backup-$(date +%Y%m%d)/

# Or use git to track changes
cd /Users/maruth/projects/openalgo
git add static/favicon/
git commit -m "Backup: Original OpenAlgo logos before rebranding"
```

**To rollback:**
```bash
# Restore from backup
cp /Users/maruth/projects/openalgo/static/favicon-backup-YYYYMMDD/* \
   /Users/maruth/projects/openalgo/static/favicon/

# Or use git
git checkout HEAD~1 -- static/favicon/
```

---

## 2. TEXT REPLACEMENT ANALYSIS

### 2.1 Replacement Patterns

**Case-Sensitive Mapping:**

| Original | Replacement | Usage Context |
|----------|-------------|---------------|
| `OpenAlgo` | `MarvelQuant` | Title case - UI labels, page titles, documentation headings |
| `openalgo` | `marvelquant` | Lowercase - URLs, file paths, code identifiers |
| `OPENALGO` | `MARVELQUANT` | Uppercase - Constants, environment variables |
| `openalgoUI` | `marvelquantUI` | Mixed case - Package names |
| `openalgoHQ` | `marvelquantHQ` | Mixed case - Social media handles |
| `OpenAlgo's` | `MarvelQuant's` | Possessive form |

**URL Replacements:**

| Original URL | Replacement | Notes |
|--------------|-------------|-------|
| `https://openalgo.in` | `https://marvelquant.com` | Main website |
| `https://docs.openalgo.in` | `https://docs.marvelquant.com` | Documentation |
| `https://www.openalgo.in` | `https://www.marvelquant.com` | WWW variant |
| `github.com/marketcalls/openalgo` | `github.com/jaimarvelquant/openalgo` | Current repo (already correct) |
| `@openalgoHQ` | `@marvelquantHQ` | Twitter/X handle |
| `@openalgo` | `@marvelquant` | YouTube handle |

### 2.2 HTML Template Files Summary

**Total HTML Files:** 35 files  
**Total Occurrences:** 130+

**File Categories:**

1. **Error Pages (2 files):** 404.html, 500.html
2. **Broker Auth Pages (20+ files):** 5paisa.html, aliceblue.html, angel.html, etc.
3. **Base Templates (5 files):** base.html, layout.html, navbar.html, public_navbar.html, footer.html
4. **Main Pages (5 files):** login.html, dashboard.html, index.html, setup.html, download.html
5. **FAQ Page (1 file):** faq.html (25+ occurrences - highest concentration)
6. **Feature Pages (3 files):** pnltracker.html, tradingview.html

**Common Patterns in HTML Files:**
- Page titles: `{% block title %}... - OpenAlgo{% endblock %}`
- Logo alt text: `alt="OpenAlgo"`
- Brand names in text: `OpenAlgo` in paragraphs
- Documentation links: `https://docs.openalgo.in`
- Social media links: `@openalgoHQ`, `@openalgo`

### 2.3 Markdown Documentation Files Summary

**Total Markdown Files:** 104 files  
**Total Occurrences:** 876+

**File Categories:**

1. **Root Documentation (5 files):** README.md (50+ occurrences), INSTALL.md, CONTRIBUTING.md, SECURITY.md, AGENTS.md
2. **Design Documentation (15 files):** design/*.md - Architecture, API, broker integration, etc.
3. **Feature Documentation (40+ files):** docs/*.md - Various features and guides
4. **Sandbox Documentation (7 files):** docs/sandbox/*.md
5. **Python Strategies (5 files):** docs/python_strategies/*.md
6. **WebSocket Documentation (3 files):** docs/websockets/*.md
7. **Installation/Upgrade (3 files):** install/README.md, upgrade/README.md, download/README.md
8. **Story/Epic Documentation (15+ files):** docs/bmad/stories/*.md
9. **Prompt Documentation (5 files):** docs/prompt/*.md

**High-Frequency Files:**
- `README.md` - 50+ occurrences (main project description)
- `install/README.md` - 30+ occurrences (installation instructions)
- `design/03_broker_integration.md` - 30+ occurrences (integration docs)
- `docs/ENHANCED_PRODUCT_DOCUMENT.md` - Comprehensive product docs

### 2.4 Detailed File Listing

**HTML Templates with Line Numbers:**

See complete listing in the comprehensive report. Key files:
- `templates/faq.html` - Lines 3, 8, 12, 27, 37, 42, 75, 84, 87, 103, 168, 171, 193, 213, 216, 239, 247, 251, 292, 308, 321, 340, 356, 372, 388, 392, 401, 404
- `templates/base.html` - Lines 21, 23, 133, 134, 235
- `templates/layout.html` - Lines 15, 16, 102, 103, 124, 130, 136
- `templates/navbar.html` - Lines 10, 11, 270
- `templates/public_navbar.html` - Lines 10, 11, 20, 21, 22
- `templates/footer.html` - Lines 8, 12, 26, 47, 58
- All broker auth pages follow similar pattern (3-4 occurrences each)

**Markdown Files by Category:**

1. **Root Docs:** README.md, INSTALL.md, CONTRIBUTING.md, SECURITY.md, AGENTS.md
2. **Design Docs:** design/01_architecture.md through design/14_sandbox_architecture.md, design/README.md
3. **Feature Docs:** 40+ files in docs/ directory
4. **Installation:** install/README.md, upgrade/README.md
5. **Stories:** 15+ files in docs/bmad/stories/

---

## 3. GIT WORKFLOW FOR UPSTREAM SYNC

### 3.1 Fork Architecture & Strategy

**Current Repository Structure:**
```
Upstream (Original):
  github.com/marketcalls/openalgo (main branch)
  ↓
Fork (Your Branded Version):
  github.com/jaimarvelquant/openalgo (main branch)
  ↓
Local Clone:
  /Users/maruth/projects/openalgo
```

**Branching Strategy:**

```
main (production-ready, branded)
  ├── upstream-sync (temporary branch for merging upstream changes)
  ├── branding (permanent branch with branding-only changes)
  └── feature/* (feature branches)
```

### 3.2 Initial Setup

**Step 1: Configure Remotes**

```bash
cd /Users/maruth/projects/openalgo

# Verify current remote (should be your fork)
git remote -v
# origin  https://github.com/jaimarvelquant/openalgo.git (fetch)
# origin  https://github.com/jaimarvelquant/openalgo.git (push)

# Add upstream remote (original OpenAlgo repository)
git remote add upstream https://github.com/marketcalls/openalgo.git

# Verify remotes
git remote -v
# origin    https://github.com/jaimarvelquant/openalgo.git (fetch)
# origin    https://github.com/jaimarvelquant/openalgo.git (push)
# upstream  https://github.com/marketcalls/openalgo.git (fetch)
# upstream  https://github.com/marketcalls/openalgo.git (push)

# Fetch upstream branches
git fetch upstream
```

**Step 2: Create Branding Branch**

```bash
# Create a branch that contains ONLY branding changes
# This will be used to reapply branding after upstream merges
git checkout -b branding

# Apply all branding changes (logos + text replacements)
# ... (run logo conversion and text replacement scripts)

# Commit branding changes
git add static/favicon/
git commit -m "Branding: Replace logos with MarvelQuant branding"

git add templates/ README.md INSTALL.md CONTRIBUTING.md design/ docs/ install/ upgrade/
git commit -m "Branding: Replace OpenAlgo text with MarvelQuant"

# Push branding branch
git push origin branding

# Return to main
git checkout main

# Merge branding into main
git merge branding
git push origin main
```

### 3.3 Upstream Sync Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  UPSTREAM SYNC WORKFLOW                                      │
└─────────────────────────────────────────────────────────────┘

1. Fetch Upstream Changes
   ┌──────────────┐
   │   upstream   │ (marketcalls/openalgo)
   │     main     │
   └──────┬───────┘
          │ git fetch upstream
          ↓
   ┌──────────────┐
   │    local     │
   │ upstream/main│
   └──────────────┘

2. Create Sync Branch
   ┌──────────────┐
   │     main     │ (your branded version)
   └──────┬───────┘
          │ git checkout -b upstream-sync
          ↓
   ┌──────────────┐
   │upstream-sync │
   └──────────────┘

3. Merge Upstream
   ┌──────────────┐     ┌──────────────┐
   │upstream-sync │ ←── │upstream/main │
   └──────┬───────┘     └──────────────┘
          │ git merge upstream/main
          ↓
   ┌──────────────┐
   │ Resolve      │
   │ Conflicts    │
   └──────┬───────┘
          │
          ↓
   ┌──────────────┐
   │ Reapply      │
   │ Branding     │
   └──────┬───────┘
          │
          ↓
   ┌──────────────┐
   │   Test &     │
   │   Verify     │
   └──────┬───────┘
          │
          ↓
4. Merge to Main
   ┌──────────────┐
   │     main     │ ←── upstream-sync
   └──────┬───────┘
          │ git merge upstream-sync
          ↓
   ┌──────────────┐
   │    origin    │
   │     main     │
   └──────────────┘
```

### 3.4 Step-by-Step Sync Commands

```bash
# Step 1: Fetch latest upstream changes
git fetch upstream

# Step 2: Create sync branch from your main
git checkout main
git checkout -b upstream-sync

# Step 3: Merge upstream changes
git merge upstream/main

# If there are conflicts, resolve them
# Priority: Keep your branding, accept upstream functionality

# Step 4: Reapply branding (automated)
./scripts/reapply-branding.sh

# Step 5: Test thoroughly
# - Run application
# - Check all pages
# - Verify branding is intact
# - Test new upstream features

# Step 6: Commit any additional changes
git add .
git commit -m "Merge upstream changes and reapply branding"

# Step 7: Merge back to main
git checkout main
git merge upstream-sync

# Step 8: Push to your fork
git push origin main

# Step 9: Clean up sync branch
git branch -d upstream-sync
```

### 3.5 Conflict Resolution Strategy

**Files Most Likely to Conflict:**

1. **Logo Files** (LOW conflict risk - binary files)
   - `static/favicon/*.png`, `*.ico`, `*.svg`
   - **Strategy:** Always keep your version (use `git checkout --ours`)

2. **HTML Templates** (MEDIUM conflict risk)
   - `templates/*.html`
   - **Strategy:** Accept upstream structure, reapply branding text

3. **Documentation** (HIGH conflict risk)
   - `README.md`, `INSTALL.md`, `CONTRIBUTING.md`, `docs/**/*.md`
   - **Strategy:** Accept upstream content, reapply branding text

4. **Configuration Files** (LOW conflict risk)
   - `package.json`, `pyproject.toml`
   - **Strategy:** Manual review, keep branding in name/description

**Conflict Resolution Commands:**

```bash
# For logo files - always keep yours
git checkout --ours static/favicon/logo.png
git checkout --ours static/favicon/*.png
git add static/favicon/

# For text files - use merge tool
git mergetool templates/base.html

# Or manually edit and reapply branding
# After resolving conflicts:
git add <resolved-file>
git commit
```

### 3.6 Git Attributes Configuration

**File: `.gitattributes`**

Create this file to define merge strategies for specific files:

```gitattributes
# .gitattributes - Custom merge strategies for MarvelQuant fork

# Logo files - always keep ours during merge
static/favicon/logo.png merge=ours
static/favicon/apple-touch-icon.png merge=ours
static/favicon/android-chrome-192x192.png merge=ours
static/favicon/favicon.ico merge=ours
static/favicon/favicon-16x16.png merge=ours
static/favicon/favicon-32x32.png merge=ours
static/favicon/mstile-150x150.png merge=ours
static/favicon/safari-pinned-tab.svg merge=ours

# Branding-specific documentation - use custom merge driver
README.md merge=branding-merge
INSTALL.md merge=branding-merge
CONTRIBUTING.md merge=branding-merge

# Binary files
*.png binary
*.ico binary
*.jpg binary
*.jpeg binary
```

**Configure Custom Merge Driver:**

```bash
# Add to .git/config or ~/.gitconfig
git config merge.ours.driver true
git config merge.ours.name "Always keep our version"

# For branding merge driver (requires custom script)
git config merge.branding-merge.driver "./scripts/branding-merge-driver.sh %O %A %B %P"
git config merge.branding-merge.name "Merge and reapply branding"
```

### 3.7 Files Most Likely to Conflict

**High Conflict Risk:**
- `README.md` - Frequently updated with new features
- `INSTALL.md` - Installation instructions may change
- `docs/**/*.md` - Documentation updates
- `templates/base.html` - Core template structure
- `templates/navbar.html` - Navigation changes

**Medium Conflict Risk:**
- `templates/*.html` - UI updates
- `package.json` - Dependency updates
- `pyproject.toml` - Python dependencies
- `design/**/*.md` - Architecture documentation

**Low Conflict Risk:**
- `static/favicon/*` - Binary files (use --ours)
- `broker/**/*.py` - Broker-specific code
- `services/**/*.py` - Service layer code

### 3.8 Maintenance Checklist

**Monthly Upstream Sync Checklist:**

```markdown
## Upstream Sync Checklist

### Pre-Sync
- [ ] Backup current state: `git tag backup-$(date +%Y%m%d)`
- [ ] Ensure working directory is clean: `git status`
- [ ] Fetch upstream: `git fetch upstream`
- [ ] Review upstream changes: `git log upstream/main --oneline --since="1 month ago"`

### Sync Process
- [ ] Create sync branch: `git checkout -b upstream-sync`
- [ ] Merge upstream: `git merge upstream/main`
- [ ] Resolve conflicts (if any)
- [ ] Reapply branding: `./scripts/reapply-branding.sh`
- [ ] Verify branding: `./scripts/verify-branding.sh`

### Testing
- [ ] Application starts without errors
- [ ] All pages load correctly
- [ ] Branding is correct on all pages
- [ ] New upstream features work
- [ ] No broken links
- [ ] Run test suite (if available)

### Finalize
- [ ] Commit changes: `git commit -m "Merge upstream and reapply branding"`
- [ ] Merge to main: `git checkout main && git merge upstream-sync`
- [ ] Push to origin: `git push origin main`
- [ ] Clean up: `git branch -d upstream-sync`
- [ ] Tag release: `git tag v$(date +%Y.%m.%d)`
- [ ] Update changelog

### Post-Sync
- [ ] Monitor for issues
- [ ] Update documentation if needed
- [ ] Notify team of changes
```

---

## 4. AUTOMATION STRATEGY

### 4.1 Complete Logo Conversion Script

**Script: `scripts/convert-logos.sh`**

```bash
#!/bin/bash

# Logo Conversion Script for MarvelQuant Rebranding
# Usage: ./convert-logos.sh

set -e  # Exit on error

# Configuration
SOURCE_LOGO="/Users/maruth/projects/openalgo/docs/bmad/Logo-view.png"
OUTPUT_DIR="/Users/maruth/projects/openalgo/static/favicon"
TEMP_DIR="/tmp/logo-conversion"
BACKGROUND_COLOR="white"  # Change to brand color if needed

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MarvelQuant Logo Conversion Script ===${NC}"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v convert >/dev/null 2>&1 || { echo -e "${RED}Error: ImageMagick not installed${NC}"; exit 1; }
command -v optipng >/dev/null 2>&1 || echo -e "${YELLOW}Warning: optipng not installed (optional)${NC}"
command -v potrace >/dev/null 2>&1 || echo -e "${YELLOW}Warning: potrace not installed (needed for SVG)${NC}"

# Create temp directory
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo -e "${GREEN}Step 1: Creating center-cropped square base${NC}"
convert "$SOURCE_LOGO" \
  -gravity center \
  -crop 1080x1080+0+0 \
  +repage \
  logo-square-1080.png

echo -e "${GREEN}Step 2: Generating logo.png (512x512)${NC}"
convert logo-square-1080.png \
  -resize 512x512 \
  -quality 95 \
  "$OUTPUT_DIR/logo.png"
[ -x "$(command -v optipng)" ] && optipng -o7 -quiet "$OUTPUT_DIR/logo.png"

echo -e "${GREEN}Step 3: Generating apple-touch-icon.png (180x180)${NC}"
convert logo-square-1080.png \
  -resize 180x180 \
  -background "$BACKGROUND_COLOR" \
  -alpha remove \
  -alpha off \
  -quality 95 \
  "$OUTPUT_DIR/apple-touch-icon.png"
[ -x "$(command -v optipng)" ] && optipng -o7 -quiet "$OUTPUT_DIR/apple-touch-icon.png"

echo -e "${GREEN}Step 4: Generating android-chrome-192x192.png (192x192)${NC}"
convert logo-square-1080.png \
  -resize 192x192 \
  -quality 95 \
  "$OUTPUT_DIR/android-chrome-192x192.png"
[ -x "$(command -v optipng)" ] && optipng -o7 -quiet "$OUTPUT_DIR/android-chrome-192x192.png"

echo -e "${GREEN}Step 5: Generating favicon-16x16.png (16x16)${NC}"
convert logo-square-1080.png \
  -resize 16x16 \
  -filter Lanczos \
  -quality 95 \
  "$OUTPUT_DIR/favicon-16x16.png"
[ -x "$(command -v optipng)" ] && optipng -o7 -quiet "$OUTPUT_DIR/favicon-16x16.png"

echo -e "${GREEN}Step 6: Generating favicon-32x32.png (32x32)${NC}"
convert logo-square-1080.png \
  -resize 32x32 \
  -filter Lanczos \
  -quality 95 \
  "$OUTPUT_DIR/favicon-32x32.png"
[ -x "$(command -v optipng)" ] && optipng -o7 -quiet "$OUTPUT_DIR/favicon-32x32.png"

echo -e "${GREEN}Step 7: Generating mstile-150x150.png (150x150)${NC}"
convert logo-square-1080.png \
  -resize 150x150 \
  -background "$BACKGROUND_COLOR" \
  -alpha remove \
  -alpha off \
  -quality 95 \
  "$OUTPUT_DIR/mstile-150x150.png"
[ -x "$(command -v optipng)" ] && optipng -o7 -quiet "$OUTPUT_DIR/mstile-150x150.png"

echo -e "${GREEN}Step 8: Generating favicon.ico (multi-resolution)${NC}"
convert logo-square-1080.png -resize 16x16 -filter Lanczos -background "$BACKGROUND_COLOR" -alpha remove -alpha off favicon-16.png
convert logo-square-1080.png -resize 32x32 -filter Lanczos -background "$BACKGROUND_COLOR" -alpha remove -alpha off favicon-32.png
convert logo-square-1080.png -resize 48x48 -filter Lanczos -background "$BACKGROUND_COLOR" -alpha remove -alpha off favicon-48.png
convert favicon-16.png favicon-32.png favicon-48.png "$OUTPUT_DIR/favicon.ico"

echo -e "${GREEN}Step 9: Generating safari-pinned-tab.svg${NC}"
if command -v potrace >/dev/null 2>&1; then
  convert logo-square-1080.png \
    -alpha extract \
    -threshold 50% \
    -negate \
    logo-mono.pbm

  potrace logo-mono.pbm \
    --svg \
    --output "$OUTPUT_DIR/safari-pinned-tab.svg" \
    --turdsize 2 \
    --alphamax 1.0

  echo -e "${YELLOW}Note: You may need to manually edit safari-pinned-tab.svg${NC}"
else
  echo -e "${YELLOW}Skipping SVG generation (potrace not installed)${NC}"
  echo -e "${YELLOW}Please generate safari-pinned-tab.svg manually${NC}"
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}=== Conversion Complete ===${NC}"
echo ""
echo "Generated files in: $OUTPUT_DIR"
echo ""
echo "File sizes:"
ls -lh "$OUTPUT_DIR"/*.png "$OUTPUT_DIR"/*.ico "$OUTPUT_DIR"/*.svg 2>/dev/null | awk '{print $9, $5}'
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review all generated images for quality"
echo "2. Test logo.png in the navbar (should be clear at 32px height)"
echo "3. Test favicons in different browsers"
echo "4. Manually review/edit safari-pinned-tab.svg if needed"
echo "5. Commit changes to git"
```

### 4.2 Text Replacement Script

**Script: `scripts/replace-branding.sh`**

```bash
#!/bin/bash

# Branding Replacement Script for MarvelQuant Rebranding
# Phase 1: HTML and Markdown files only (LOW RISK)
# Usage: ./replace-branding.sh [--dry-run]

set -e

# Configuration
PROJECT_ROOT="/Users/maruth/projects/openalgo"
BACKUP_DIR="$PROJECT_ROOT/branding-backup-$(date +%Y%m%d-%H%M%S)"
DRY_RUN=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}=== DRY RUN MODE - No changes will be made ===${NC}"
fi

echo -e "${GREEN}=== MarvelQuant Branding Replacement Script ===${NC}"
echo -e "${GREEN}=== Phase 1: HTML & Markdown Files ===${NC}"
echo ""

# Function to create backup
create_backup() {
    echo -e "${BLUE}Creating backup...${NC}"
    mkdir -p "$BACKUP_DIR"

    # Backup HTML files
    find "$PROJECT_ROOT/templates" -name "*.html" -exec cp --parents {} "$BACKUP_DIR" \; 2>/dev/null || \
    find "$PROJECT_ROOT/templates" -name "*.html" -exec sh -c 'mkdir -p "$1/$(dirname "$2")" && cp "$2" "$1/$2"' _ "$BACKUP_DIR" {} \;

    # Backup Markdown files
    find "$PROJECT_ROOT" -name "*.md" ! -path "*/.venv/*" ! -path "*/.git/*" -exec sh -c 'mkdir -p "$1/$(dirname "$2")" && cp "$2" "$1/$2"' _ "$BACKUP_DIR" {} \; 2>/dev/null

    echo -e "${GREEN}Backup created at: $BACKUP_DIR${NC}"
    echo ""
}

# Function to perform replacements
perform_replacements() {
    local file_pattern=$1
    local description=$2

    echo -e "${BLUE}Processing $description...${NC}"

    # Find all matching files
    local files
    if [[ "$file_pattern" == "*.html" ]]; then
        files=$(find "$PROJECT_ROOT/templates" -name "$file_pattern")
    else
        files=$(find "$PROJECT_ROOT" -name "$file_pattern" ! -path "*/.venv/*" ! -path "*/.git/*" ! -path "*/node_modules/*")
    fi

    local count=0
    for file in $files; do
        if [[ -f "$file" ]]; then
            # Count occurrences before replacement
            local before=$(grep -i -o "openalgo" "$file" 2>/dev/null | wc -l)

            if [[ $before -gt 0 ]]; then
                if [[ "$DRY_RUN" == false ]]; then
                    # Perform replacements (case-sensitive, in order)
                    # 1. URLs first (to avoid double replacement)
                    sed -i.bak 's|https://openalgo\.in|https://marvelquant.com|g' "$file"
                    sed -i.bak 's|https://docs\.openalgo\.in|https://docs.marvelquant.com|g' "$file"
                    sed -i.bak 's|https://www\.openalgo\.in|https://www.marvelquant.com|g' "$file"
                    sed -i.bak 's|http://openalgo\.in|http://marvelquant.com|g' "$file"
                    sed -i.bak 's|docs\.openalgo\.in|docs.marvelquant.com|g' "$file"
                    sed -i.bak 's|www\.openalgo\.in|www.marvelquant.com|g' "$file"

                    # 2. Social media handles
                    sed -i.bak 's|@openalgoHQ|@marvelquantHQ|g' "$file"
                    sed -i.bak 's|@openalgo|@marvelquant|g' "$file"
                    sed -i.bak 's|/openalgoHQ|/marvelquantHQ|g' "$file"

                    # 3. Text replacements (order matters!)
                    # Possessive forms first
                    sed -i.bak 's/OpenAlgo'\''s/MarvelQuant'\''s/g' "$file"
                    sed -i.bak 's/openalgo'\''s/marvelquant'\''s/g' "$file"

                    # Package names
                    sed -i.bak 's/openalgoUI/marvelquantUI/g' "$file"
                    sed -i.bak 's/openalgoHQ/marvelquantHQ/g' "$file"

                    # Standard replacements
                    sed -i.bak 's/OpenAlgo/MarvelQuant/g' "$file"
                    sed -i.bak 's/openalgo/marvelquant/g' "$file"
                    sed -i.bak 's/OPENALGO/MARVELQUANT/g' "$file"

                    # Remove backup files
                    rm -f "$file.bak"

                    # Count after
                    local after=$(grep -i -o "openalgo" "$file" 2>/dev/null | wc -l)
                    echo -e "  ${GREEN}✓${NC} $file (replaced $before occurrences, $after remaining)"
                    ((count++))
                else
                    echo -e "  ${YELLOW}[DRY RUN]${NC} Would replace $before occurrences in: $file"
                    ((count++))
                fi
            fi
        fi
    done

    echo -e "${GREEN}Processed $count files${NC}"
    echo ""
}

# Main execution
if [[ "$DRY_RUN" == false ]]; then
    create_backup
fi

# Process HTML files
perform_replacements "*.html" "HTML templates"

# Process Markdown files
perform_replacements "*.md" "Markdown documentation"

# Summary
echo -e "${GREEN}=== Replacement Complete ===${NC}"
echo ""

if [[ "$DRY_RUN" == false ]]; then
    echo -e "${GREEN}Backup location: $BACKUP_DIR${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review changes: git diff"
    echo "2. Test the application thoroughly"
    echo "3. Check all pages for correct branding"
    echo "4. Verify all links work correctly"
    echo "5. Commit changes: git add . && git commit -m 'Rebrand: OpenAlgo → MarvelQuant'"
    echo ""
    echo -e "${YELLOW}To rollback:${NC}"
    echo "cp -r $BACKUP_DIR/* $PROJECT_ROOT/"
else
    echo -e "${YELLOW}This was a dry run. No changes were made.${NC}"
    echo "Run without --dry-run to perform actual replacements."
fi
```

### 4.3 Verification Script

**Script: `scripts/verify-branding.sh`**

```bash
#!/bin/bash

# Branding Verification Script
# Checks for any remaining "openalgo" references after replacement

PROJECT_ROOT="/Users/maruth/projects/openalgo"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Branding Verification Report ===${NC}"
echo ""

# Check HTML files
echo -e "${YELLOW}Checking HTML files...${NC}"
html_count=$(grep -r -i "openalgo" "$PROJECT_ROOT/templates" --include="*.html" 2>/dev/null | wc -l)
if [[ $html_count -eq 0 ]]; then
    echo -e "${GREEN}✓ No 'openalgo' found in HTML files${NC}"
else
    echo -e "${RED}✗ Found $html_count occurrences in HTML files:${NC}"
    grep -r -n -i "openalgo" "$PROJECT_ROOT/templates" --include="*.html" 2>/dev/null
fi
echo ""

# Check Markdown files
echo -e "${YELLOW}Checking Markdown files...${NC}"
md_count=$(grep -r -i "openalgo" "$PROJECT_ROOT" --include="*.md" ! -path "*/.venv/*" ! -path "*/.git/*" 2>/dev/null | wc -l)
if [[ $md_count -eq 0 ]]; then
    echo -e "${GREEN}✓ No 'openalgo' found in Markdown files${NC}"
else
    echo -e "${RED}✗ Found $md_count occurrences in Markdown files${NC}"
    echo -e "${YELLOW}(Showing first 20 occurrences)${NC}"
    grep -r -n -i "openalgo" "$PROJECT_ROOT" --include="*.md" ! -path "*/.venv/*" ! -path "*/.git/*" 2>/dev/null | head -20
fi
echo ""

# Check for MarvelQuant
echo -e "${YELLOW}Verifying MarvelQuant branding...${NC}"
marvelquant_count=$(grep -r -i "marvelquant" "$PROJECT_ROOT/templates" --include="*.html" 2>/dev/null | wc -l)
echo -e "${GREEN}Found $marvelquant_count occurrences of 'MarvelQuant' in HTML files${NC}"
echo ""

# Summary
echo -e "${GREEN}=== Summary ===${NC}"
if [[ $html_count -eq 0 ]] && [[ $md_count -eq 0 ]]; then
    echo -e "${GREEN}✓ All branding replacements complete!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some 'openalgo' references remain${NC}"
    echo -e "${YELLOW}Review the output above and run replacements again if needed${NC}"
    exit 1
fi
```

### 4.4 Reapply Branding Script (for upstream merges)

**Script: `scripts/reapply-branding.sh`**

```bash
#!/bin/bash

# Reapply Branding Script
# Automatically reapplies MarvelQuant branding after upstream merge
# Usage: ./scripts/reapply-branding.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Reapplying MarvelQuant Branding ===${NC}"
echo ""

# Step 1: Ensure logo files are correct
echo -e "${YELLOW}Step 1: Verifying logo files...${NC}"
if [[ -f "docs/bmad/Logo-view.png" ]]; then
    # Check if logos need to be regenerated
    if [[ ! -f "static/favicon/logo.png" ]] || \
       [[ "docs/bmad/Logo-view.png" -nt "static/favicon/logo.png" ]]; then
        echo "Regenerating logo files..."
        ./scripts/convert-logos.sh
    else
        echo "Logo files are up to date"
    fi
else
    echo -e "${YELLOW}Warning: Source logo not found at docs/bmad/Logo-view.png${NC}"
fi

# Step 2: Reapply text branding
echo -e "${YELLOW}Step 2: Reapplying text branding...${NC}"

# Function to replace branding in a file
replace_branding() {
    local file=$1

    if [[ -f "$file" ]]; then
        # URLs
        sed -i.bak 's|https://openalgo\.in|https://marvelquant.com|g' "$file"
        sed -i.bak 's|https://docs\.openalgo\.in|https://docs.marvelquant.com|g' "$file"
        sed -i.bak 's|https://www\.openalgo\.in|https://www.marvelquant.com|g' "$file"
        sed -i.bak 's|docs\.openalgo\.in|docs.marvelquant.com|g' "$file"
        sed -i.bak 's|www\.openalgo\.in|www.marvelquant.com|g' "$file"

        # Social media
        sed -i.bak 's|@openalgoHQ|@marvelquantHQ|g' "$file"
        sed -i.bak 's|@openalgo|@marvelquant|g' "$file"

        # Text
        sed -i.bak 's/OpenAlgo'\''s/MarvelQuant'\''s/g' "$file"
        sed -i.bak 's/openalgoUI/marvelquantUI/g' "$file"
        sed -i.bak 's/openalgoHQ/marvelquantHQ/g' "$file"
        sed -i.bak 's/OpenAlgo/MarvelQuant/g' "$file"
        sed -i.bak 's/openalgo/marvelquant/g' "$file"
        sed -i.bak 's/OPENALGO/MARVELQUANT/g' "$file"

        rm -f "$file.bak"
    fi
}

# Process HTML files
echo "Processing HTML templates..."
find templates -name "*.html" -type f | while read file; do
    replace_branding "$file"
done

# Process Markdown files
echo "Processing Markdown documentation..."
find . -name "*.md" -type f ! -path "*/.venv/*" ! -path "*/.git/*" ! -path "*/node_modules/*" | while read file; do
    replace_branding "$file"
done

# Step 3: Verify branding
echo -e "${YELLOW}Step 3: Verifying branding...${NC}"
./scripts/verify-branding.sh

echo ""
echo -e "${GREEN}=== Branding Reapplied Successfully ===${NC}"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Test the application"
echo "3. Commit changes: git add . && git commit -m 'Reapply branding after upstream merge'"
```

### 4.5 GitHub Actions Workflow

**File: `.github/workflows/verify-branding.yml`**

```yaml
name: Verify Branding

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  verify-branding:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Check for OpenAlgo branding in HTML
        run: |
          if grep -r -i "openalgo" templates/ --include="*.html"; then
            echo "::error::Found 'OpenAlgo' branding in HTML files"
            exit 1
          fi
          echo "✓ No OpenAlgo branding found in HTML files"

      - name: Check for OpenAlgo branding in Markdown
        run: |
          count=$(grep -r -i "openalgo" . --include="*.md" ! -path "*/.venv/*" ! -path "*/.git/*" | wc -l)
          if [[ $count -gt 0 ]]; then
            echo "::warning::Found $count occurrences of 'OpenAlgo' in Markdown files"
            grep -r -n -i "openalgo" . --include="*.md" ! -path "*/.venv/*" ! -path "*/.git/*" | head -20
          else
            echo "✓ No OpenAlgo branding found in Markdown files"
          fi

      - name: Verify MarvelQuant branding
        run: |
          count=$(grep -r -i "marvelquant" templates/ --include="*.html" | wc -l)
          if [[ $count -eq 0 ]]; then
            echo "::error::No MarvelQuant branding found"
            exit 1
          fi
          echo "✓ Found $count occurrences of MarvelQuant branding"

      - name: Check logo files
        run: |
          required_files=(
            "static/favicon/logo.png"
            "static/favicon/apple-touch-icon.png"
            "static/favicon/android-chrome-192x192.png"
            "static/favicon/favicon.ico"
            "static/favicon/favicon-16x16.png"
            "static/favicon/favicon-32x32.png"
            "static/favicon/mstile-150x150.png"
            "static/favicon/safari-pinned-tab.svg"
          )

          for file in "${required_files[@]}"; do
            if [[ ! -f "$file" ]]; then
              echo "::error::Missing logo file: $file"
              exit 1
            fi
          done
          echo "✓ All logo files present"
```

---

## 5. RISK ASSESSMENT

### 5.1 Risk Matrix

| Risk Category | Probability | Impact | Mitigation Strategy |
|---------------|-------------|--------|---------------------|
| **Logo Conversion Quality** | LOW | MEDIUM | Test on multiple devices, use high-quality source |
| **Text Replacement Errors** | LOW | LOW | Use automated scripts, verify with grep |
| **Upstream Merge Conflicts** | MEDIUM | MEDIUM | Use .gitattributes, automated conflict resolution |
| **Broken Links After Rebranding** | LOW | MEDIUM | Verify all URLs, set up redirects |
| **SEO Impact** | MEDIUM | HIGH | Set up 301 redirects, update sitemap |
| **User Confusion** | LOW | LOW | Clear communication, update documentation |
| **Git History Pollution** | LOW | LOW | Use feature branches, squash commits |
| **Automated Script Failures** | LOW | MEDIUM | Test scripts thoroughly, have manual fallback |

### 5.2 Potential Issues & Mitigation

#### **Issue 1: Logo Quality at Small Sizes**

**Problem:** Logo may not be recognizable at 16x16px or 32x32px

**Mitigation:**
- Test logo at all sizes before deployment
- Consider creating simplified version for small sizes
- Use vector-based logo if possible
- Test on multiple devices and browsers

**Rollback:** Keep backup of original logos

#### **Issue 2: Upstream Merge Conflicts**

**Problem:** Frequent conflicts in branded files when merging upstream

**Mitigation:**
- Use `.gitattributes` to define merge strategies
- Automate branding reapplication
- Keep branding changes in separate commits
- Document conflict resolution procedures

**Rollback:** Use `git merge --abort` and resolve manually

#### **Issue 3: Broken External Links**

**Problem:** Links to openalgo.in domains will break

**Mitigation:**
- Set up 301 redirects from old domains
- Update all internal links
- Verify all external links
- Monitor for 404 errors

**Rollback:** Keep list of all URL changes

#### **Issue 4: Search Engine Indexing**

**Problem:** Loss of SEO rankings due to rebranding

**Mitigation:**
- Set up 301 redirects
- Update Google Search Console
- Submit new sitemap
- Update social media profiles
- Announce rebrand publicly

**Rollback:** Revert domain changes if needed

### 5.3 Testing Strategy

**Pre-Deployment Testing Checklist:**

```markdown
## Branding Testing Checklist

### Visual Testing
- [ ] Logo displays correctly on all pages
- [ ] Logo is clear at all sizes (16px to 512px)
- [ ] Favicon appears in browser tabs
- [ ] iOS home screen icon looks good
- [ ] Android app icon looks good
- [ ] Windows tile icon looks good
- [ ] Safari pinned tab icon is recognizable

### Text Verification
- [ ] No "OpenAlgo" text in HTML templates
- [ ] No "OpenAlgo" text in visible documentation
- [ ] All URLs updated to new domain
- [ ] Social media handles updated
- [ ] Page titles show "MarvelQuant"
- [ ] Meta descriptions updated

### Functional Testing
- [ ] Application starts without errors
- [ ] All pages load correctly
- [ ] Navigation works properly
- [ ] Authentication works
- [ ] API endpoints function correctly
- [ ] Broker integrations work
- [ ] WebSocket connections work

### Link Testing
- [ ] All internal links work
- [ ] All external links work
- [ ] Documentation links work
- [ ] Social media links work
- [ ] GitHub links work

### Cross-Browser Testing
- [ ] Chrome/Edge - all features work
- [ ] Firefox - all features work
- [ ] Safari - all features work
- [ ] Mobile browsers - all features work

### Device Testing
- [ ] Desktop - Windows
- [ ] Desktop - macOS
- [ ] Desktop - Linux
- [ ] Mobile - iOS
- [ ] Mobile - Android
- [ ] Tablet - iPad
- [ ] Tablet - Android
```

---

## 6. IMPLEMENTATION CHECKLIST

### 6.1 Phase 1 Implementation Steps

**Step 1: Preparation (1-2 hours)**
- [ ] Read this entire document
- [ ] Install required tools (ImageMagick, optipng, potrace)
- [ ] Create backup of current state: `git tag backup-$(date +%Y%m%d)`
- [ ] Ensure working directory is clean: `git status`
- [ ] Create scripts directory: `mkdir -p scripts`
- [ ] Copy all scripts from this document to `scripts/` directory
- [ ] Make scripts executable: `chmod +x scripts/*.sh`

**Step 2: Logo Conversion (2-3 hours)**
- [ ] Verify source logo exists: `ls -lh docs/bmad/Logo-view.png`
- [ ] Review logo at full size to understand content
- [ ] Decide on aspect ratio strategy (center crop vs padding)
- [ ] Run logo conversion script: `./scripts/convert-logos.sh`
- [ ] Verify all 8 logo files were created
- [ ] Check file sizes are reasonable
- [ ] Test logo.png in browser at different sizes
- [ ] Test all favicons in different browsers
- [ ] Manually review/edit safari-pinned-tab.svg if needed
- [ ] Commit logo changes: `git add static/favicon/ && git commit -m "Branding: Replace logos with MarvelQuant branding"`

**Step 3: Text Replacement - Dry Run (1 hour)**
- [ ] Run replacement script in dry-run mode: `./scripts/replace-branding.sh --dry-run`
- [ ] Review the output to understand what will be changed
- [ ] Check for any unexpected replacements
- [ ] Verify file counts match expectations (35 HTML, 104 MD)

**Step 4: Text Replacement - Actual (2-3 hours)**
- [ ] Run replacement script: `./scripts/replace-branding.sh`
- [ ] Review backup location printed by script
- [ ] Check git diff to review changes: `git diff`
- [ ] Spot-check several files manually
- [ ] Run verification script: `./scripts/verify-branding.sh`
- [ ] Fix any remaining issues manually
- [ ] Commit text changes: `git add . && git commit -m "Branding: Replace OpenAlgo text with MarvelQuant"`

**Step 5: Testing (3-4 hours)**
- [ ] Start the application
- [ ] Test all pages load correctly
- [ ] Check navbar logo displays correctly
- [ ] Check favicon in browser tab
- [ ] Test on mobile device
- [ ] Verify all links work
- [ ] Check documentation pages
- [ ] Test broker authentication pages
- [ ] Verify FAQ page content
- [ ] Check footer links
- [ ] Test in different browsers (Chrome, Firefox, Safari)

**Step 6: Git Configuration (1 hour)**
- [ ] Create `.gitattributes` file with merge strategies
- [ ] Configure git merge drivers
- [ ] Test git configuration
- [ ] Commit git configuration: `git add .gitattributes && git commit -m "Git: Configure merge strategies for branding"`

**Step 7: Finalization (1 hour)**
- [ ] Push changes to origin: `git push origin main`
- [ ] Tag release: `git tag v$(date +%Y.%m.%d) && git push --tags`
- [ ] Update changelog (if exists)
- [ ] Document any issues encountered
- [ ] Create list of remaining tasks (if any)

### 6.2 Post-Implementation Tasks

**Immediate (within 24 hours):**
- [ ] Monitor application for any issues
- [ ] Check error logs
- [ ] Verify user feedback
- [ ] Test on production environment (if different from dev)

**Short-term (within 1 week):**
- [ ] Set up domain redirects (if domains are changing)
- [ ] Update Google Search Console
- [ ] Update social media profiles
- [ ] Announce rebranding to users
- [ ] Update any external documentation

**Long-term (within 1 month):**
- [ ] Monitor SEO impact
- [ ] Gather user feedback
- [ ] Plan Phase 2 (Python code changes)
- [ ] Document lessons learned

### 6.3 Rollback Procedure

If issues are discovered after implementation:

```bash
# Option 1: Restore from backup tag
git reset --hard backup-YYYYMMDD
git push origin main --force

# Option 2: Restore from backup directory
cp -r branding-backup-YYYYMMDD-HHMMSS/* /Users/maruth/projects/openalgo/

# Option 3: Revert specific commits
git log --oneline  # Find commit hashes
git revert <commit-hash>
git push origin main
```

---

## 7. SUMMARY & NEXT STEPS

### 7.1 Phase 1 Summary

**What Phase 1 Accomplishes:**
- ✅ Complete logo replacement (8 files)
- ✅ Text branding in all HTML templates (35 files)
- ✅ Text branding in all documentation (104 files)
- ✅ Git workflow for upstream synchronization
- ✅ Automated scripts for maintenance
- ✅ CI/CD verification

**What Phase 1 Does NOT Include:**
- ❌ Python code changes (214 files)
- ❌ JSON configuration files (31 files)
- ❌ JavaScript/CSS files (4 files)
- ❌ Database schema changes
- ❌ Installation scripts
- ❌ External service updates

**Risk Level:** LOW - No code execution changes

**Estimated Effort:** 10-20 hours total

**Success Criteria:**
- All logos display correctly
- No "OpenAlgo" text visible in UI
- No "OpenAlgo" text in user-facing documentation
- All links work correctly
- Application functions normally
- Branding verification script passes

### 7.2 Next Steps After Phase 1

**Phase 2: Configuration & Build Files (Medium Risk)**
- Update `package.json`
- Update `pyproject.toml`
- Update `docker-compose.yaml`
- Update API collection files
- Estimated effort: 4-8 hours

**Phase 3: Python Code Changes (Medium-High Risk)**
- Update 214 Python files
- Update broker plugin files
- Update service layer files
- Extensive testing required
- Estimated effort: 16-24 hours

**Phase 4: Database & Critical Files (HIGH Risk)**
- Database schema changes
- Authentication salt values
- Installation scripts
- Requires migration strategy
- Estimated effort: 16-24 hours

**Phase 5: External Services (Ongoing)**
- Domain registration
- DNS configuration
- Social media updates
- SEO management
- Varies by external factors

### 7.3 Key Takeaways

1. **Start with Low Risk:** Phase 1 provides immediate visual impact with minimal risk
2. **Automate Everything:** Scripts ensure consistency and repeatability
3. **Test Thoroughly:** Visual changes are easy to verify
4. **Plan for Upstream:** Git workflow ensures smooth updates from original repository
5. **Document Everything:** This analysis serves as implementation guide and reference

### 7.4 Support & Resources

**Scripts Location:** `/Users/maruth/projects/openalgo/scripts/`
- `convert-logos.sh` - Logo conversion
- `replace-branding.sh` - Text replacement
- `verify-branding.sh` - Verification
- `reapply-branding.sh` - Reapply after merge

**Documentation:** This file serves as complete reference

**Backup Strategy:** Always create backups before changes

**Testing:** Use provided checklists for comprehensive testing

---

## APPENDIX

### A. Quick Reference Commands

```bash
# Logo conversion
./scripts/convert-logos.sh

# Text replacement (dry run)
./scripts/replace-branding.sh --dry-run

# Text replacement (actual)
./scripts/replace-branding.sh

# Verify branding
./scripts/verify-branding.sh

# Upstream sync
git fetch upstream
git checkout -b upstream-sync
git merge upstream/main
./scripts/reapply-branding.sh
git checkout main && git merge upstream-sync

# Rollback
git reset --hard backup-YYYYMMDD
```

### B. File Counts Summary

| Category | Files | Occurrences |
|----------|-------|-------------|
| HTML Templates | 35 | 130+ |
| Markdown Docs | 104 | 876+ |
| **Phase 1 Total** | **139** | **1,006+** |
| Logo Files | 8 | N/A |

### C. Contact & Support

For questions or issues during implementation:
1. Review this document thoroughly
2. Check script output for error messages
3. Use `--dry-run` mode to preview changes
4. Keep backups of all changes
5. Test incrementally

---

**END OF PHASE 1 REBRANDING ANALYSIS**

**Document Version:** 1.0
**Last Updated:** October 7, 2025
**Status:** ANALYSIS COMPLETE - READY FOR IMPLEMENTATION


