# BMAD v6 Phase 4 Iterative Cycle - Quick Reference

**Last Updated:** 2025-10-12  
**Version:** 6.0.0-alpha.0

---

## Valid Story Status Values

| Status | Meaning | Who Sets It | Next Action |
|--------|---------|-------------|-------------|
| **Draft** | Story created, not yet approved | SM (create-story) | SM reviews and approves |
| **Approved** | Ready for implementation | SM (manual) | DEV runs *develop |
| **InProgress** | Being implemented OR needs fixes after review | DEV (dev-story) OR SR/DEV (review-story) | DEV runs *develop |
| **Ready for Review** | Implementation complete, awaiting review | DEV (dev-story) | SR/DEV runs *review |
| **Done** | Review passed, story complete | SR/DEV (review-story) | Move to next story |

---

## The Iterative Cycle Commands

### 1️⃣ Initial Implementation
```bash
# Story Status: Approved
@dev
*develop
# Result: Status → "Ready for Review"
```

### 2️⃣ First Review
```bash
# Story Status: Ready for Review
@dev  # or @sr
*review
# Result: 
#   - If approved: Status → "Done" ✅
#   - If issues found: Status → "InProgress", adds unchecked tasks
```

### 3️⃣ Fix Issues (Resume)
```bash
# Story Status: InProgress (with unchecked review tasks)
@dev
*develop
# Result: Fixes issues, Status → "Ready for Review"
```

### 4️⃣ Second Review
```bash
# Story Status: Ready for Review
@dev  # or @sr
*review
# Result:
#   - If approved: Status → "Done" ✅
#   - If more issues: Status → "InProgress", adds more tasks
```

### 🔁 Repeat Steps 3-4 Until Done

---

## Status Transition Diagram

```
Draft
  ↓ (SM approves)
Approved
  ↓ (DEV *develop)
InProgress
  ↓ (DEV completes all tasks)
Ready for Review
  ↓ (SR/DEV *review)
  ├─→ Done (if approved) ✅
  └─→ InProgress (if issues found)
        ↓ (DEV *develop - fixes issues)
      Ready for Review
        ↓ (SR/DEV *review)
        ├─→ Done (if approved) ✅
        └─→ InProgress (if more issues)
              ↓ (repeat until Done)
```

---

## DEV Agent Status Rules

### ✅ ALLOWED: Status == "Approved"
- **When:** Starting fresh implementation
- **Action:** DEV implements all tasks from scratch

### ✅ ALLOWED: Status == "InProgress" (with unchecked tasks)
- **When:** Resuming after review found issues
- **Action:** DEV continues from first unchecked task

### ❌ BLOCKED: Status == "InProgress" (no unchecked tasks)
- **Error:** "Story is InProgress but has no unchecked tasks"
- **Fix:** Verify story state or set Status to "Approved"

### ❌ BLOCKED: Status == "Ready for Review"
- **Error:** "Story Status must be 'Approved' or 'InProgress'"
- **Fix:** Run *review first, or manually set to "Approved"

### ❌ BLOCKED: Status == "Done"
- **Error:** "Story Status must be 'Approved' or 'InProgress'"
- **Fix:** Story is complete, move to next story

---

## Review Workflow Behavior

### Automatic Status Updates (NEW!)
- **Enabled by default:** `update_status_on_result: true`
- **On Approve:** Status → "Done"
- **On Changes Requested:** Status → "InProgress"

### Review Follow-up Tasks
Review workflow automatically adds unchecked tasks:

```markdown
### Review Follow-ups (AI)
- [ ] [AI-Review][High] Fix cancel_order_api tuple unpacking
- [ ] [AI-Review][Med] Add error handling for edge case X
- [ ] [AI-Review][Low] Improve logging in module Y
```

DEV agent will detect and implement these tasks when resuming.

---

## Common Scenarios

### Scenario 1: Review Finds Critical Bug
```
Status: Ready for Review
↓ *review
Status: InProgress (adds 1 High-priority task)
↓ *develop
Status: Ready for Review (bug fixed)
↓ *review
Status: Done ✅
```

### Scenario 2: Multiple Review Iterations
```
Status: Ready for Review
↓ *review (finds 3 issues)
Status: InProgress
↓ *develop (fixes 3 issues)
Status: Ready for Review
↓ *review (finds 2 more issues)
Status: InProgress
↓ *develop (fixes 2 issues)
Status: Ready for Review
↓ *review (all good)
Status: Done ✅
```

### Scenario 3: Review Approves First Time
```
Status: Ready for Review
↓ *review (no issues found)
Status: Done ✅
```

---

## Troubleshooting

### Problem: DEV refuses to run with Status="InProgress"
**Cause:** Old version of DEV agent (before fix)  
**Solution:** Verify `bmad/bmm/agents/dev.md` line 15 allows "InProgress" status

### Problem: Review doesn't update status automatically
**Cause:** `update_status_on_result: false` in workflow config  
**Solution:** Verify `bmad/bmm/workflows/4-implementation/review-story/workflow.yaml` line 53 is `true`

### Problem: DEV says "no unchecked tasks" but Status="InProgress"
**Cause:** All review tasks were manually marked complete, or status was manually changed  
**Solution:** Either add unchecked tasks or change Status to "Approved"

### Problem: Story stuck in "InProgress" forever
**Cause:** Review tasks not being completed  
**Solution:** Run `*develop` to complete unchecked tasks, then `*review` to verify

---

## File Locations

### Agent Definition
- **DEV Agent:** `bmad/bmm/agents/dev.md`
- **Status validation:** Lines 15-20

### Workflows
- **dev-story:** `bmad/bmm/workflows/4-implementation/dev-story/`
- **review-story:** `bmad/bmm/workflows/4-implementation/review-story/`

### Configuration
- **Review auto-status:** `bmad/bmm/workflows/4-implementation/review-story/workflow.yaml` line 53

### Documentation
- **v6 Workflow Guide:** `docs/bmad/workflow/v6_workflow_guide.md`
- **Fix Documentation:** `docs/bmad/workflow/v6_phase4_iterative_cycle_fix.md`

---

## Key Takeaways

1. ✅ **DEV agent now accepts both "Approved" and "InProgress" status**
2. ✅ **Review workflow automatically updates status based on outcome**
3. ✅ **Multiple review-fix iterations are fully supported**
4. ✅ **No manual status overrides required**
5. ✅ **The v6 iterative cycle works as designed**

---

## Quick Commands Cheat Sheet

```bash
# Start implementation
@dev → *develop

# Review implementation
@dev → *review  # or @sr → *review

# Resume after review (if issues found)
@dev → *develop

# Check story status
# (Open story file and look at ## Status section)

# Complete epic (after all stories Done)
@sm → *retrospective
```

---

**Remember:** The workflow is now fully automated. Just run `*develop` and `*review` in sequence, and the status will transition automatically based on outcomes. No manual intervention needed! 🚀

