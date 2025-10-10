# Story 2.1: OpenAlgo to MarvelQuant Rebranding - Phase 1 (Logo & Documentation)

Status: ContextReadyDraft

## Story

As a **product owner**,
I want **to rebrand the OpenAlgo application to MarvelQuant by replacing all logos, updating domain references, and changing text references in HTML templates and documentation**,
so that **the application reflects the new MarvelQuant brand identity consistently across all user-facing elements while maintaining full functionality**.

## Acceptance Criteria

1. **Logo Replacement Complete**
   - All 8 logo files in `static/favicon/` are replaced with MarvelQuant branding
   - Logo files include: logo.png (512x512), apple-touch-icon.png (180x180), android-chrome-192x192.png (192x192), favicon-16x16.png, favicon-32x32.png, mstile-150x150.png, favicon.ico (multi-res), safari-pinned-tab.svg
   - All logos are properly sized and optimized
   - Logos display correctly across all browsers and devices

2. **Domain Migration Complete**
   - All references to `openalgo.in` are updated to `marvelquant.com`
   - All references to `docs.openalgo.in` are updated to `docs.marvelquant.com`
   - All references to `www.openalgo.in` are updated to `www.marvelquant.com`
   - Social media handles updated: `@openalgoHQ` → `@marvelquantHQ`, `@openalgo` → `@marvelquant`

3. **Text Branding Updated**
   - All 35 HTML template files updated with MarvelQuant branding
   - All 104 Markdown documentation files updated with MarvelQuant branding
   - Naming conventions preserved (e.g., `OpenAlgo` → `MarvelQuant`, `openalgo` → `marvelquant`, `OPENALGO` → `MARVELQUANT`)
   - Possessive forms handled correctly (`OpenAlgo's` → `MarvelQuant's`)
   - Package names updated (`openalgoUI` → `marvelquantUI`, `openalgoHQ` → `marvelquantHQ`)

4. **Quality Verification**
   - Verification script confirms zero remaining "openalgo" references in HTML files
   - Verification script confirms zero remaining "openalgo" references in Markdown files
   - All pages load without errors
   - All links function correctly
   - Branding is consistent across all pages

5. **Git Workflow Configured**
   - `.gitattributes` file created with merge strategies for logo files
   - Backup of original branding created before changes
   - All changes committed with clear commit messages
   - Rebranding scripts are executable and functional

6. **User-Facing Python Strings Updated**
   - Telegram bot test messages updated to "MarvelQuant" (2 occurrences in `blueprints/telegram.py`)
   - 2FA issuer name updated to "MarvelQuant" (1 occurrence in `database/user_db.py`)
   - Migration script output messages updated (5 occurrences across 3 files in `upgrade/`)
   - Telegram bot test message displays "MarvelQuant" branding
   - 2FA authenticator apps display "MarvelQuant" as issuer name
   - Internal Python code (function names, variables, comments, logs) intentionally NOT changed (zero user-facing impact)

## Tasks / Subtasks

- [ ] **Task 1: Environment Setup & Prerequisites** (AC: #5)
  - [ ] 1.1: Install ImageMagick for logo conversion (`brew install imagemagick` on macOS)
  - [ ] 1.2: Install optipng for logo optimization (`brew install optipng`)
  - [ ] 1.3: Install potrace for SVG conversion (`brew install potrace`)
  - [ ] 1.4: Verify all tools are installed correctly
  - [ ] 1.5: Create `scripts/` directory in project root
  - [ ] 1.6: Create backup tag: `git tag backup-$(date +%Y%m%d)`

- [ ] **Task 2: Create Automation Scripts** (AC: #5)
  - [ ] 2.1: Create `scripts/convert-logos.sh` from phase1-rebranding-analysis.md Section 4.1
  - [ ] 2.2: Create `scripts/replace-branding.sh` from phase1-rebranding-analysis.md Section 4.2
  - [ ] 2.3: Create `scripts/verify-branding.sh` from phase1-rebranding-analysis.md Section 4.3
  - [ ] 2.4: Create `scripts/reapply-branding.sh` from phase1-rebranding-analysis.md Section 4.4
  - [ ] 2.5: Make all scripts executable: `chmod +x scripts/*.sh`
  - [ ] 2.6: Review scripts for macOS compatibility (sed syntax)

- [ ] **Task 3: Logo Conversion & Replacement** (AC: #1)
  - [ ] 3.1: Verify source logo exists at `/Users/maruth/projects/openalgo/docs/bmad/Logo-Main.svg`
  - [ ] 3.2: Verify SVG source logo is valid and renders correctly
  - [ ] 3.3: Run logo conversion script: `./scripts/convert-logos.sh`
  - [ ] 3.4: Verify all 8 logo files created in `static/favicon/`
  - [ ] 3.5: Check logo file sizes are reasonable (< 100KB each)
  - [ ] 3.6: Test logo.png displays correctly in navbar at 32px height
  - [ ] 3.7: Test favicons in Chrome, Firefox, Safari
  - [ ] 3.8: Test apple-touch-icon on iOS device
  - [ ] 3.9: Test android-chrome icon on Android device
  - [ ] 3.10: Manually review safari-pinned-tab.svg for quality (can use source SVG directly if suitable)
  - [ ] 3.11: Commit logo changes: `git add static/favicon/ && git commit -m "Branding: Replace logos with MarvelQuant branding"`

- [ ] **Task 4: Text Replacement - Dry Run & Validation** (AC: #2, #3)
  - [ ] 4.1: Run replacement script in dry-run mode: `./scripts/replace-branding.sh --dry-run`
  - [ ] 4.2: Review dry-run output for expected file counts (35 HTML, 104 MD)
  - [ ] 4.3: Verify replacement patterns are correct
  - [ ] 4.4: Check for any unexpected replacements
  - [ ] 4.5: Confirm backup strategy is in place

- [ ] **Task 5: Text Replacement - Execution** (AC: #2, #3)
  - [ ] 5.1: Run replacement script: `./scripts/replace-branding.sh`
  - [ ] 5.2: Note backup directory location from script output
  - [ ] 5.3: Review git diff for HTML files: `git diff templates/`
  - [ ] 5.4: Review git diff for Markdown files: `git diff *.md docs/`
  - [ ] 5.5: Spot-check 5-10 files manually for correct replacements
  - [ ] 5.6: Verify URL replacements are correct
  - [ ] 5.7: Verify social media handle replacements
  - [ ] 5.8: Verify possessive forms handled correctly
  - [ ] 5.9: Commit text changes: `git add . && git commit -m "Branding: Replace OpenAlgo text with MarvelQuant"`

- [ ] **Task 6: Verification & Quality Assurance** (AC: #4)
  - [ ] 6.1: Run verification script: `./scripts/verify-branding.sh`
  - [ ] 6.2: Confirm zero "openalgo" references in HTML files
  - [ ] 6.3: Confirm zero "openalgo" references in Markdown files
  - [ ] 6.4: Verify MarvelQuant branding count is as expected (130+ in HTML)
  - [ ] 6.5: Fix any remaining issues manually if needed
  - [ ] 6.6: Re-run verification script to confirm all issues resolved

- [ ] **Task 7: Application Testing** (AC: #4)
  - [ ] 7.1: Start the application locally
  - [ ] 7.2: Verify application starts without errors
  - [ ] 7.3: Test homepage displays MarvelQuant branding
  - [ ] 7.4: Test navbar logo displays correctly
  - [ ] 7.5: Test favicon appears in browser tab
  - [ ] 7.6: Test all broker authentication pages (20+ pages)
  - [ ] 7.7: Test FAQ page (highest concentration of changes - 25+ occurrences)
  - [ ] 7.8: Test dashboard page
  - [ ] 7.9: Test login page
  - [ ] 7.10: Test setup page
  - [ ] 7.11: Test download page
  - [ ] 7.12: Verify all navigation links work
  - [ ] 7.13: Verify all footer links work
  - [ ] 7.14: Check browser console for any errors

- [ ] **Task 8: Cross-Browser & Device Testing** (AC: #1, #4)
  - [ ] 8.1: Test in Chrome/Edge - verify logo and branding
  - [ ] 8.2: Test in Firefox - verify logo and branding
  - [ ] 8.3: Test in Safari - verify logo and branding
  - [ ] 8.4: Test on iOS Safari - verify home screen icon
  - [ ] 8.5: Test on Android Chrome - verify app icon
  - [ ] 8.6: Test responsive design on mobile devices
  - [ ] 8.7: Verify Windows tile icon (if accessible)

- [ ] **Task 9: Git Workflow Configuration** (AC: #5)
  - [ ] 9.1: Create `.gitattributes` file with merge strategies from phase1-rebranding-analysis.md Section 3.6
  - [ ] 9.2: Configure git merge drivers: `git config merge.ours.driver true`
  - [ ] 9.3: Test git configuration
  - [ ] 9.4: Commit git configuration: `git add .gitattributes && git commit -m "Git: Configure merge strategies for branding"`
  - [ ] 9.5: Document upstream sync workflow for future use

- [ ] **Task 10: Update User-Facing Python Strings** (AC: #3, #6)
  - [ ] 10.1: Update Telegram bot test messages in `blueprints/telegram.py` (2 occurrences: "Test Message from OpenAlgo")
  - [ ] 10.2: Update 2FA issuer name in `database/user_db.py` (1 occurrence: issuer_name="OpenAlgo")
  - [ ] 10.3: Update migration script messages in `upgrade/migrate_smtp_simple.py` (2 occurrences)
  - [ ] 10.4: Update migration script messages in `upgrade/migrate_security_columns.py` (2 occurrences)
  - [ ] 10.5: Update migration script messages in `upgrade/migrate_telegram_bot.py` (1 occurrence)
  - [ ] 10.6: Test Telegram bot integration - send test message and verify "MarvelQuant" branding
  - [ ] 10.7: Test 2FA setup flow - verify authenticator app displays "MarvelQuant" as issuer
  - [ ] 10.8: Run verification to confirm all user-facing Python strings updated
  - [ ] 10.9: Commit Python string changes: `git add . && git commit -m "Branding: Update user-facing Python strings"`

- [ ] **Task 11: Documentation & Finalization** (AC: #5)
  - [ ] 11.1: Update changelog (if exists) with rebranding changes
  - [ ] 11.2: Document any issues encountered during implementation
  - [ ] 11.3: Note that internal Python code (function names, variables, comments, logs) intentionally NOT changed
  - [ ] 11.4: Push all changes to origin: `git push origin main`
  - [ ] 11.5: Tag release: `git tag phase1-rebranding-$(date +%Y%m%d) && git push --tags`
  - [ ] 11.6: Verify GitHub repository shows correct branding

## Dev Notes

### Architecture Patterns & Constraints

**Risk Level:** LOW - Phase 1 focuses on visual, documentation, and user-facing string changes with no code execution logic modifications.

**Key Constraints:**
- Preserve all existing naming conventions and patterns (kebab-case, snake_case, PascalCase)
- Maintain exact file structure - no file renames in Phase 1
- Python changes LIMITED to user-facing string literals only (8 occurrences across 5 files)
- NO changes to: function names, variable names, class names, comments, log messages, or internal code structure
- NO changes to JSON configuration or JavaScript files in Phase 1
- All changes must be reversible via git

**Replacement Order (Critical):**
1. URLs first (to avoid double replacement)
2. Social media handles
3. Possessive forms
4. Package names
5. Standard text replacements (case-sensitive)

**Automation Strategy:**
- All scripts use bash for macOS compatibility
- Scripts include dry-run mode for safety
- Automatic backup creation before changes
- Verification scripts for quality assurance

### Project Structure Notes

**Files Modified:**
- `static/favicon/` - 8 logo files (binary replacements)
- `templates/` - 35 HTML files (text replacements)
- Root and subdirectories - 104 Markdown files (text replacements)
- `blueprints/telegram.py` - 2 user-facing string literals (Telegram test messages)
- `database/user_db.py` - 1 user-facing string literal (2FA issuer name)
- `upgrade/migrate_smtp_simple.py` - 2 user-facing string literals (migration output)
- `upgrade/migrate_security_columns.py` - 2 user-facing string literals (migration output)
- `upgrade/migrate_telegram_bot.py` - 1 user-facing string literal (migration output)

**Files Created:**
- `scripts/convert-logos.sh` - Logo conversion automation
- `scripts/replace-branding.sh` - Text replacement automation
- `scripts/verify-branding.sh` - Verification automation
- `scripts/reapply-branding.sh` - Upstream merge support
- `.gitattributes` - Git merge strategies

**Files NOT Modified (Phase 1):**
- Python files (209 files) - Internal code (function names, variables, comments, logs) intentionally NOT changed
- JSON configuration files (31 files) - deferred to future phases if needed
- JavaScript/CSS files (4 files) - deferred to future phases if needed
- Database schemas - no changes needed for rebranding
- Installation scripts - no changes needed for rebranding

### References

**Primary Source:**
- [Source: docs/bmad/research/phase1-rebranding-analysis.md] - Comprehensive Phase 1 analysis with all implementation details

**Logo Source:**
- [Source: docs/bmad/Logo-Main.svg] - MarvelQuant logo (Vector SVG format - scalable to any size without quality loss)

**Key Sections Referenced:**
- Section 1: Logo Conversion Strategy - Detailed conversion commands and quality checks
- Section 2: Text Replacement Analysis - Complete file listing and replacement patterns
- Section 3: Git Workflow - Upstream sync strategy and conflict resolution
- Section 4: Automation Strategy - Complete script implementations
- Section 5: Risk Assessment - Mitigation strategies and testing approach
- Section 6: Implementation Checklist - Step-by-step execution plan

**Testing Standards:**
- Visual quality checks for all logo sizes (16px to 512px)
- Cross-browser testing (Chrome, Firefox, Safari)
- Cross-device testing (Desktop, iOS, Android)
- Functional testing (all pages load, all links work)
- Verification script must pass with zero "openalgo" references

**Rollback Strategy:**
- Git tag backup before changes: `backup-YYYYMMDD`
- Automated backup directory: `branding-backup-YYYYMMDD-HHMMSS`
- Git revert capability for all commits
- Original logo files preserved in backup

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-09 | 1.0 | Initial story creation with comprehensive task breakdown and context | Bob (Scrum Master) |
| 2025-10-09 | 1.1 | Added Task 11 for user-facing Python strings (8 occurrences), AC #6, clarified internal code NOT changed | Bob (Scrum Master) |
| 2025-10-09 | 1.2 | Updated logo source to SVG vector format (Logo-Main.svg), removed aspect ratio cropping concerns, superior quality at all sizes | Bob (Scrum Master) |

## Dev Agent Record

### Context Reference

- [Story Context XML](../../bmad/docs/story-context-2.1.xml) - Generated 2025-10-09

### Agent Model Used

Claude Sonnet 4.5 (Augment Agent)

### Debug Log References

<!-- To be added during implementation -->

### Completion Notes List

<!-- To be added during implementation -->

### File List

<!-- To be added during implementation -->

