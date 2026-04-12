# OpenAlgo → MarvelQuant Rebranding Checklist

**Status:** In Progress  
**Story:** 2.1 - OpenAlgo to MarvelQuant Rebranding  
**Date:** 2025-10-11

---

## ✅ Already Completed

Based on the backup directory `backups/branding-20251010-111055/`, the following have been rebranded:

- ✅ HTML templates (`templates/`)
- ✅ Most Markdown documentation (`docs/`)
- ✅ README.md and main documentation
- ✅ Docker configuration (`docker-compose.yaml`)
- ✅ MCP server configurations (most files)
- ✅ Core Python constants (`utils/constants.py`)
- ✅ BMAD core config (`bmad/core/config.yaml`) - **JUST FIXED**

---

## ⚠️ Remaining Items to Update

### **1. Package Configuration Files**

#### `package.json` (Line 2)
```json
{
  "name": "openalgo",  // ← Change to "marvelquant"
  "version": "1.0.0",
  ...
}
```

**Action:** Change `"name": "openalgo"` to `"name": "marvelquant"`

---

### **2. MCP Configuration Files (Development)**

#### `mcp/mcp_config_codex.json`
```json
{
  "mcpServers": {
    "openalgo": {  // ← Change to "marvelquant"
      "command": "/Users/maruth/projects/openalgo/.venv/bin/python3",  // ← Update path
      "args": [
        "/Users/maruth/projects/openalgo/mcp/mcpserver.py",  // ← Update path
        ...
      ]
    }
  }
}
```

**Actions:**
1. Change server name from `"openalgo"` to `"marvelquant"`
2. **DECISION NEEDED:** Update paths from `/Users/maruth/projects/openalgo/` to `/Users/maruth/projects/marvelquant/` OR keep as-is?

#### `mcp/mcp_config_claude.json`
Same changes as above.

---

### **3. API Collection Files**

#### `collections/openalgo/bruno.json`
```json
{
  "version": "1",
  "name": "openalgo",  // ← Change to "marvelquant"
  "type": "collection",
  ...
}
```

**Action:** Change `"name": "openalgo"` to `"name": "marvelquant"`

#### `collections/openalgo_bruno.json` (Line 489)
```json
{
  "brunoConfig": {
    "version": "1",
    "name": "openalgo",  // ← Change to "marvelquant"
    ...
  }
}
```

**Action:** Change `"name": "openalgo"` to `"name": "marvelquant"`

#### `collections/postman/openalgo.postman_environment.json`
```json
{
  "id": "7f3a1196-6606-4bf1-a4ce-45e756b062a9",
  "name": "openalgo",  // ← Change to "marvelquant"
  "values": [
    {
      "key": "apiKey",
      "value": "your-openAlgo-Api-key",  // ← Change to "your-marvelquant-api-key"
      ...
    }
  ]
}
```

**Actions:**
1. Change `"name": "openalgo"` to `"name": "marvelquant"`
2. Change `"your-openAlgo-Api-key"` to `"your-marvelquant-api-key"`

---

### **4. Directory Names (Optional)**

#### `collections/openalgo/`
**Decision:** Rename to `collections/marvelquant/` or keep as-is?

**Recommendation:** Rename for consistency

---

### **5. Code References (Technical Debt)**

#### `docs/bmad/research/ib_vnpy_adaptation_plan.md`
Contains function names like:
- `openalgo_to_vn()` (Line 331)
- `vn_to_openalgo()` (Line 362)

**Decision:** These are **internal function names** in a research document. Options:
1. **Keep as-is** (historical reference, not production code)
2. **Update to** `marvelquant_to_vn()` and `vn_to_marvelquant()` for consistency
3. **Use generic names** like `platform_to_vn()` and `vn_to_platform()`

**Recommendation:** Keep as-is (research document, not production code)

---

## 🎯 Critical Decision: Directory Path Strategy

### **Option A: Keep Directory Name as `openalgo`** ✅ **RECOMMENDED**

**Pros:**
- No need to update absolute paths in MCP configs
- Existing git history preserved
- Simpler migration
- Internal paths don't affect users

**Cons:**
- Directory name doesn't match branding

**What to update:**
- Only user-facing names (package.json, API collections, documentation)
- Keep all file paths as `/Users/maruth/projects/openalgo/`

---

### **Option B: Rename Directory to `marvelquant`**

**Pros:**
- Complete consistency
- Cleaner for new developers

**Cons:**
- Must update ALL absolute paths in:
  - MCP configuration files (6+ files)
  - Git remote URL (if applicable)
  - Virtual environment paths
  - IDE configurations
  - Backup scripts
- Risk of breaking existing integrations

**What to update:**
- Everything (directory + all references)

---

## 📝 Recommended Action Plan

### **Phase 1: User-Facing Rebranding** (Recommended Now)

1. ✅ Update `package.json` name
2. ✅ Update API collection names (Bruno, Postman)
3. ✅ Rename `collections/openalgo/` to `collections/marvelquant/`
4. ⚠️ **SKIP** MCP config path updates (keep `/Users/maruth/projects/openalgo/`)
5. ⚠️ **SKIP** directory rename

**Result:** All user-facing elements say "MarvelQuant", internal paths stay stable

---

### **Phase 2: Complete Path Migration** (Optional Future)

Only if you decide to rename the directory:

1. Rename `/Users/maruth/projects/openalgo/` → `/Users/maruth/projects/marvelquant/`
2. Update all MCP configs with new paths
3. Update git remote (if needed)
4. Recreate virtual environment or update paths
5. Update IDE workspace settings

---

## 🔍 Verification Commands

### Check for remaining "openalgo" references:
```bash
# Check configuration files
grep -r "openalgo" package.json collections/ mcp/*.json

# Check for absolute paths
grep -r "/Users/maruth/projects/openalgo" mcp/ collections/

# Verify branding in user-facing files
grep -ri "openalgo" templates/ static/ README.md
```

### Run existing verification script:
```bash
bash scripts/verify-branding.sh
```

---

## 📊 Summary

| Category | Files | Status | Priority |
|----------|-------|--------|----------|
| HTML Templates | ~50 files | ✅ Done | High |
| Documentation | ~100 files | ✅ Done | High |
| Docker Config | 1 file | ✅ Done | High |
| BMAD Config | 1 file | ✅ Done | High |
| Package Config | 1 file | ⚠️ TODO | High |
| API Collections | 3 files | ⚠️ TODO | Medium |
| MCP Configs | 2 files | ⚠️ Optional | Low |
| Directory Name | 1 directory | ⚠️ Optional | Low |
| Research Docs | 1 file | ⚠️ Optional | Low |

---

## 🎯 Next Steps

**Immediate (Story 2.1 Completion):**
1. Update `package.json` name field
2. Update API collection names (Bruno, Postman)
3. Optionally rename `collections/openalgo/` directory
4. Run verification script
5. Mark Story 2.1 as complete

**Future (Optional):**
- Decide on directory rename strategy
- Update MCP configs if directory renamed
- Update research document function names

---

## 📌 Notes

- **Git Repository:** Currently at `https://github.com/jaimarvelquant/openalgo.git`
  - **Decision needed:** Rename repo or keep URL?
- **Workspace Path:** `/Users/maruth/projects/openalgo/`
  - **Recommendation:** Keep as-is for stability
- **BMAD Framework:** Now correctly uses `{project-root}` placeholders (fixed)

