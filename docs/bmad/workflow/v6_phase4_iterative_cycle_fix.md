# BMAD v6 Phase 4 Iterative Review-Fix Cycle - Bug Fix Documentation

**Date:** 2025-10-12  
**Version:** 6.0.0-alpha.0  
**Status:** FIXED  
**Severity:** CRITICAL - Broke core v6 workflow functionality

---

## Executive Summary

Fixed a critical bug in BMAD v6 Phase 4 Implementation workflow that prevented the iterative review-fix-review cycle from functioning. The DEV agent's hard-coded `Status == Approved` constraint conflicted with the v6 workflow design where stories transition to `Status == InProgress` after failed reviews.

**Impact:** Without this fix, developers had to manually override story status after each review, breaking workflow automation and violating the v6 methodology's "resumable after review" design principle.

---

## The Bug

### Root Cause

**File:** `bmad/bmm/agents/dev.md` line 15  
**Original Code:**
```xml
<step n="4">DO NOT start implementation until a story is loaded and Status == Approved</step>
```

**Problem:** This hard-coded constraint prevented the DEV agent from resuming work when `Status == InProgress`, which is the correct status after a failed review according to the v6 workflow guide.

### Secondary Issue

**File:** `bmad/bmm/workflows/4-implementation/review-story/workflow.yaml` line 53  
**Original Configuration:**
```yaml
update_status_on_result: false
```

**Problem:** The review workflow was not automatically updating story status based on review outcomes, requiring manual status management and breaking workflow automation.

---

## The v6 Intended Design

According to `/docs/bmad/workflow/v6_workflow_guide.md` (lines 196-206), the Story Flow States should be:

```
Draft (create-story)
  → Approved (SM approval)
    → In Progress (dev-story)
      → Ready for Review (dev complete)
        → Done (review passed)
        OR
        → In Progress (review failed, back to dev)
```

**Key Innovation (line 192):** `dev-story` workflow is "Resumable after review"

### The Iterative Cycle

```
┌─────────────────────────────────────────┐
│            SM: create-story             │
│   (Generate next story from epics.md)   │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│           SM: story-context             │
│  (Generate expertise injection XML)     │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│            DEV: dev-story               │
│  (Implement with context injection)     │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│         SR/DEV: review-story            │
│     (Validate against criteria)         │
└─────────────────────┬───────────────────┘
                      ↓
            ┌─────────┴─────────┐
            │    Issues Found?   │
            └─────────┬─────────┘
                ┌─────┴─────┐
                ↓           ↓
        [No: Next Story]  [Yes: Back to dev-story] ← THIS WAS BROKEN
                              ↓
                      [Loop until Done]
```

---

## The Fix

### Change 1: DEV Agent Activation Rule

**File:** `bmad/bmm/agents/dev.md` lines 14-21  
**Status:** ✅ FIXED

**New Code:**
```xml
<step n="4">Story Status Validation:
  - ALLOWED statuses for implementation: "Approved" OR "InProgress" (when resuming after review)
  - When Status == "InProgress": Verify that unchecked tasks exist in the story (particularly in "Review Follow-ups (AI)" or "Tasks / Subtasks" sections)
  - If Status == "InProgress" AND no unchecked tasks exist: HALT with message "Story is InProgress but has no unchecked tasks. Please verify story state or set Status to 'Approved' if starting fresh implementation."
  - If Status is neither "Approved" nor "InProgress": HALT with message "Story Status must be 'Approved' (for initial implementation) or 'InProgress' (for resuming after review). Current status: {status}"
  - RATIONALE: This enables the v6 iterative review-fix-review cycle where Status transitions: Approved → InProgress (dev) → Ready for Review → InProgress (review failed) → Ready for Review (fixes applied) → Done (review passed)</step>
```

**Why This Works:**
1. **Allows two valid statuses:** "Approved" (initial implementation) and "InProgress" (resuming after review)
2. **Validates work exists:** When status is "InProgress", verifies unchecked tasks exist
3. **Provides clear error messages:** Helps developers understand what's wrong if status is invalid
4. **Documents the rationale:** Explains the v6 iterative cycle directly in the agent definition

### Change 2: Review Workflow Auto-Status Update

**File:** `bmad/bmm/workflows/4-implementation/review-story/workflow.yaml` line 53  
**Status:** ✅ FIXED

**New Configuration:**
```yaml
update_status_on_result: true # CRITICAL: Must be true to enable v6 iterative review-fix cycle
status_on_approve: "Done"
status_on_changes_requested: "InProgress"
```

**Why This Works:**
1. **Automates status transitions:** Review workflow now automatically updates status based on outcome
2. **Eliminates manual intervention:** No need for developers to manually change status
3. **Aligns with v6 design:** Status automatically reflects review outcome

---

## How the Complete Cycle Now Works

### Scenario: Story with Review Issues

**Initial State:**
- Story file: `story-1.4-1-http-helper-with-retry-logic.md`
- Status: "Approved"
- All original tasks: `[x]` (checked)

**Step 1: Initial Implementation**
```bash
@dev
*develop
```
- DEV agent sees Status == "Approved" ✅
- Implements all tasks
- Updates Status to "Ready for Review"
- All tasks marked `[x]`

**Step 2: First Review**
```bash
@dev (or @sr)
*review
```
- Review workflow runs
- Finds 2 High-priority issues
- Appends "Senior Developer Review (AI)" section
- Adds unchecked tasks to "Review Follow-ups (AI)" section:
  ```markdown
  ### Review Follow-ups (AI)
  - [ ] [AI-Review][High] Fix cancel_order_api tuple unpacking
  - [ ] [AI-Review][High] Update .env.example to match new credentials
  ```
- **Automatically updates Status to "InProgress"** ✅ (NEW!)

**Step 3: Fix Issues (Resume Implementation)**
```bash
@dev
*develop
```
- DEV agent sees Status == "InProgress" ✅ (NOW ALLOWED!)
- Detects 2 unchecked tasks in "Review Follow-ups (AI)" section
- Implements fixes for both tasks
- Marks tasks as `[x]`
- Updates Status to "Ready for Review"

**Step 4: Second Review**
```bash
@dev (or @sr)
*review
```
- Review workflow runs again
- Verifies fixes are correct
- All issues resolved
- Appends second "Senior Developer Review (AI)" section
- **Automatically updates Status to "Done"** ✅

**Final State:**
- Status: "Done"
- All tasks: `[x]` (including review follow-ups)
- Two review sections in story file (showing iteration history)

---

## Verification Checklist

### ✅ DEV Agent Behavior
- [x] Accepts Status == "Approved" for initial implementation
- [x] Accepts Status == "InProgress" when unchecked tasks exist
- [x] Rejects Status == "InProgress" when no unchecked tasks exist
- [x] Provides clear error messages for invalid states
- [x] Can resume work multiple times on the same story

### ✅ Review Workflow Behavior
- [x] Appends review section to story file
- [x] Adds unchecked tasks to "Review Follow-ups (AI)" section
- [x] Automatically updates Status to "InProgress" when changes requested
- [x] Automatically updates Status to "Done" when approved
- [x] Can be run multiple times on the same story (appends new sections)

### ✅ Dev-Story Workflow Behavior
- [x] Detects unchecked tasks (including review follow-ups)
- [x] Resumes from first unchecked task
- [x] Updates Status to "Ready for Review" when all tasks complete
- [x] Works correctly whether starting fresh or resuming after review

### ✅ Complete Iterative Cycle
- [x] Approved → InProgress (dev) → Ready for Review → InProgress (review failed) → Ready for Review (fixes) → Done (review passed)
- [x] No manual status overrides required
- [x] Multiple review-fix iterations supported
- [x] Status transitions align with v6 workflow guide

---

## Testing the Fix

### Test Case 1: Fresh Story Implementation
```bash
# Story Status: Approved
@dev
*develop
# Expected: Implements all tasks, Status → "Ready for Review"
```

### Test Case 2: Review Finds Issues
```bash
# Story Status: Ready for Review
@dev
*review
# Expected: Appends review, adds unchecked tasks, Status → "InProgress"
```

### Test Case 3: Resume After Review
```bash
# Story Status: InProgress (with unchecked review tasks)
@dev
*develop
# Expected: Fixes issues, marks tasks [x], Status → "Ready for Review"
```

### Test Case 4: Review Approves
```bash
# Story Status: Ready for Review (after fixes)
@dev
*review
# Expected: Appends approval review, Status → "Done"
```

### Test Case 5: Multiple Iterations
```bash
# Repeat Test Cases 2-3 multiple times
# Expected: Each iteration adds new review section, cycle continues until approved
```

---

## Impact Analysis

### Before Fix
- ❌ Manual status override required after each review
- ❌ Workflow automation broken
- ❌ v6 "resumable after review" design non-functional
- ❌ Developer friction and confusion
- ❌ Inconsistent with v6 workflow documentation

### After Fix
- ✅ Fully automated status transitions
- ✅ True iterative review-fix-review cycle
- ✅ Aligns with v6 workflow guide
- ✅ No manual intervention required
- ✅ Clear error messages guide developers
- ✅ Multiple review iterations supported

---

## Related Files Modified

1. **`bmad/bmm/agents/dev.md`** - DEV agent activation rule (lines 14-21)
2. **`bmad/bmm/workflows/4-implementation/review-story/workflow.yaml`** - Auto-status update config (line 53)

## Related Files Verified (No Changes Needed)

1. **`bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml`** - Already supports iterative execution
2. **`bmad/bmm/workflows/4-implementation/dev-story/instructions.md`** - Already detects unchecked tasks correctly
3. **`bmad/bmm/workflows/4-implementation/review-story/instructions.md`** - Already adds review follow-up tasks correctly

---

## Lessons Learned

### Design Principle Violated
**"Agent constraints must align with workflow design"**

The DEV agent's hard-coded status check violated the workflow's "resumable after review" design. Agent-level constraints should support, not block, workflow-level behavior.

### Configuration vs. Code
The `update_status_on_result: false` default was overly conservative. For core workflow functionality (like the iterative review cycle), automation should be the default, with manual override as the option.

### Documentation Importance
The v6 workflow guide clearly documented the intended behavior, but the implementation didn't match. This highlights the importance of:
1. Implementation reviews against design docs
2. End-to-end workflow testing
3. Clear rationale comments in code

---

## Future Improvements

### Potential Enhancements
1. **Status validation in workflow.xml:** Add central status validation logic that all workflows can reference
2. **Story state machine:** Formalize valid status transitions in a state machine definition
3. **Automated testing:** Create integration tests that verify the complete iterative cycle
4. **Status history:** Track status transition history in story metadata

### Monitoring
- Track how many review iterations stories typically require
- Identify patterns in review failures to improve story-context generation
- Monitor for stories stuck in "InProgress" state

---

## Conclusion

This fix restores the BMAD v6 Phase 4 Implementation workflow to its intended design, enabling the revolutionary iterative review-fix-review cycle that makes v6 methodology powerful. The DEV agent can now seamlessly resume work after reviews, and status transitions are fully automated, eliminating manual intervention and developer friction.

**The v6 workflow now works as designed.** ✅

