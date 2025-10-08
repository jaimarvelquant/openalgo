# OpenAlgo Research & Implementation Plans

This directory contains comprehensive analysis and implementation plans for OpenAlgo development projects.

## Documents

### 1. Phase 1 Rebranding Analysis
**File:** `phase1-rebranding-analysis.md`
**Size:** 52 KB (1,710 lines)
**Status:** Complete - Ready for Implementation
**Project:** OpenAlgo → MarvelQuant Rebranding

**Contents:**
- Complete logo conversion strategy with step-by-step commands
- Detailed text replacement analysis for 139 files (35 HTML + 104 Markdown)
- Git workflow for maintaining branded fork while syncing with upstream
- Complete automation scripts (logo conversion, text replacement, verification)
- Risk assessment and mitigation strategies
- Implementation checklist with time estimates
- Testing procedures and rollback plans

**Key Statistics:**
- **Logo Files:** 8 files to replace in `static/favicon/`
- **HTML Templates:** 35 files, 130+ occurrences
- **Markdown Docs:** 104 files, 876+ occurrences
- **Total Phase 1:** 139 files, 1,006+ text replacements
- **Risk Level:** LOW (no code execution changes)
- **Estimated Effort:** 10-20 hours

### 2. Jainam Prop Implementation Plan
**File:** `jainam-prop-implementation-plan.md`
**Size:** 37 KB (1,357 lines)
**Status:** Complete - Ready for Execution
**Project:** Jainam Prop Broker Integration Enhancement

**Contents:**
- Comprehensive gap analysis between fivepaisaxts (reference) and jainam_prop
- 4-phase implementation plan with detailed tasks
- Phase 1: Critical missing features (market depth, OI, date chunking)
- Phase 2: Robustness improvements (retry logic, token refresh)
- Phase 3: Code quality & structure (class-based, WebSocket enhancements)
- Phase 4: Testing & validation (unit, integration, performance)
- Complete code examples and implementation details
- Risk assessment and success criteria

**Key Statistics:**
- **Total Effort:** 100-130 hours over 13-19 days
- **New Code:** ~2,130 lines to add
- **Files to Modify:** 8 existing files
- **New Files:** 3 new API files + 7 new test files
- **Priority:** Phase 1 (CRITICAL), Phase 2 (HIGH), Phase 4 (HIGH), Phase 3 (MEDIUM)

**Critical Gaps to Fix:**
- ❌ No market depth function
- ❌ No Open Interest support
- ❌ No date chunking for historical data
- ❌ Limited timeframe support (5 vs 10)
- ❌ No retry logic or token refresh
- ❌ Missing WebSocket handlers

---

## Quick Start - Rebranding

### Prerequisites
```bash
# macOS
brew install imagemagick optipng potrace

# Ubuntu/Debian
sudo apt-get install imagemagick optipng potrace
```

### Implementation Steps

1. **Read the Analysis**
   ```bash
   cat docs/bmad/research/phase1-rebranding-analysis.md
   ```

2. **Create Scripts Directory**
   ```bash
   mkdir -p scripts
   # Copy scripts from the analysis document to scripts/ directory
   chmod +x scripts/*.sh
   ```

3. **Convert Logos**
   ```bash
   ./scripts/convert-logos.sh
   ```

4. **Replace Text (Dry Run First)**
   ```bash
   ./scripts/replace-branding.sh --dry-run
   ./scripts/replace-branding.sh
   ```

5. **Verify Changes**
   ```bash
   ./scripts/verify-branding.sh
   ```

6. **Test Thoroughly**
   - Start application
   - Check all pages
   - Verify logos and text
   - Test in multiple browsers

7. **Commit Changes**
   ```bash
   git add .
   git commit -m "Phase 1: OpenAlgo → MarvelQuant rebranding"
   git push origin main
   ```

## Automation Scripts

All scripts are documented in the Phase 1 analysis. Copy them to the `scripts/` directory:

1. **`scripts/convert-logos.sh`** - Converts source logo to all required formats
2. **`scripts/replace-branding.sh`** - Replaces text in HTML and Markdown files
3. **`scripts/verify-branding.sh`** - Verifies all replacements are complete
4. **`scripts/reapply-branding.sh`** - Reapplies branding after upstream merges

## Git Workflow

### Initial Setup
```bash
# Add upstream remote
git remote add upstream https://github.com/marketcalls/openalgo.git
git fetch upstream

# Create branding branch
git checkout -b branding
# ... apply branding changes ...
git commit -m "Branding: MarvelQuant"
git checkout main
git merge branding
```

### Syncing with Upstream
```bash
# Fetch upstream changes
git fetch upstream

# Create sync branch
git checkout -b upstream-sync
git merge upstream/main

# Reapply branding
./scripts/reapply-branding.sh

# Merge to main
git checkout main
git merge upstream-sync
git push origin main
```

## File Structure

```
docs/bmad/research/
├── README.md                              # This file
├── phase1-rebranding-analysis.md          # Rebranding Phase 1 analysis
├── jainam-prop-implementation-plan.md     # Jainam Prop enhancement plan
└── [future analysis documents]

docs/bmad/
├── Logo-view.png                       # Source logo (1920x1080)
└── [other bmad documents]

scripts/                                # Create this directory
├── convert-logos.sh                    # Logo conversion
├── replace-branding.sh                 # Text replacement
├── verify-branding.sh                  # Verification
└── reapply-branding.sh                 # Reapply after merge

static/favicon/                         # Target logo directory
├── logo.png                            # Main UI logo (512x512)
├── apple-touch-icon.png                # iOS icon (180x180)
├── android-chrome-192x192.png          # Android icon (192x192)
├── favicon-16x16.png                   # Small favicon
├── favicon-32x32.png                   # Medium favicon
├── mstile-150x150.png                  # Windows tile
├── favicon.ico                         # Multi-res ICO
└── safari-pinned-tab.svg               # Safari pinned tab
```

## Replacement Mapping

| Original | Replacement | Context |
|----------|-------------|---------|
| `OpenAlgo` | `MarvelQuant` | Title case |
| `openalgo` | `marvelquant` | Lowercase |
| `OPENALGO` | `MARVELQUANT` | Uppercase |
| `openalgoUI` | `marvelquantUI` | Package name |
| `openalgoHQ` | `marvelquantHQ` | Social media |
| `https://openalgo.in` | `https://marvelquant.com` | Main site |
| `https://docs.openalgo.in` | `https://docs.marvelquant.com` | Docs site |
| `@openalgoHQ` | `@marvelquantHQ` | Twitter/X |
| `@openalgo` | `@marvelquant` | YouTube |

## Testing Checklist

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
- [ ] All links work correctly

### Cross-Browser Testing
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Logo quality at small sizes | LOW | MEDIUM | Test thoroughly before deployment |
| Text replacement errors | LOW | LOW | Use automated scripts, verify |
| Upstream merge conflicts | MEDIUM | MEDIUM | Use .gitattributes, automation |
| Broken links | LOW | MEDIUM | Verify all URLs, set up redirects |

## Rollback Plan

```bash
# Option 1: Restore from backup tag
git reset --hard backup-YYYYMMDD
git push origin main --force

# Option 2: Restore from backup directory
cp -r branding-backup-YYYYMMDD-HHMMSS/* /Users/maruth/projects/openalgo/

# Option 3: Revert specific commits
git log --oneline
git revert <commit-hash>
git push origin main
```

## Next Phases

### Phase 2: Configuration & Build Files (Medium Risk)
- Update `package.json`, `pyproject.toml`
- Update `docker-compose.yaml`
- Update API collection files
- Estimated: 4-8 hours

### Phase 3: Python Code Changes (Medium-High Risk)
- Update 214 Python files
- Update broker plugins
- Update service layer
- Estimated: 16-24 hours

### Phase 4: Database & Critical Files (HIGH Risk)
- Database schema changes
- Authentication changes
- Installation scripts
- Estimated: 16-24 hours

### Phase 5: External Services (Ongoing)
- Domain registration
- DNS configuration
- Social media updates
- SEO management

## Support

For detailed information on any aspect of Phase 1 implementation, refer to:
- **`phase1-rebranding-analysis.md`** - Complete analysis with all details

For questions during implementation:
1. Review the analysis document thoroughly
2. Check script output for error messages
3. Use `--dry-run` mode to preview changes
4. Keep backups of all changes
5. Test incrementally

## Status

### Rebranding Project
- [x] Phase 1 Analysis Complete
- [ ] Phase 1 Implementation
- [ ] Phase 2 Analysis
- [ ] Phase 2 Implementation
- [ ] Phase 3 Analysis
- [ ] Phase 3 Implementation
- [ ] Phase 4 Analysis
- [ ] Phase 4 Implementation
- [ ] Phase 5 Planning

### Jainam Prop Enhancement
- [x] Contextual Analysis Complete
- [x] Implementation Plan Complete
- [ ] Phase 1: Critical Features (5-7 days)
- [ ] Phase 2: Robustness (3-5 days)
- [ ] Phase 3: Code Quality (3-4 days)
- [ ] Phase 4: Testing (2-3 days)

---

**Last Updated:** October 8, 2025
**Document Version:** 1.1
**Status:** Multiple Projects - Ready for Implementation

