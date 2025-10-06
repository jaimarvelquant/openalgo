# QA Review Rounds Template

## QA Results

### Round 1: {timestamp} - Initial Review
- **Reviewer:** {qa-agent-name}
- **Decision:** {PASS/CONCERNS/FAIL}
- **Overall Assessment:** {brief summary}

#### Findings
- **Issue 1:** {description}
  - **Severity:** {high/medium/low}
  - **Impact:** {description}
  - **Recommendation:** {action required}
- **Issue 2:** {description}
  - **Severity:** {high/medium/low}
  - **Impact:** {description}
  - **Recommendation:** {action required}

#### Test Results
- **Unit Tests:** {passed}/{total}
- **Integration Tests:** {passed}/{total}
- **Coverage:** {percentage}%
- **Performance:** {benchmark results}

#### Gate Status
Gate: {status} → docs/qa/gates/{epic}.{story}-{slug}.yml

---

### Round 2: {timestamp} - After Fixes
- **Reviewer:** {qa-agent-name}
- **Decision:** {PASS/CONCERNS/FAIL}
- **Previous Decision:** {Round 1 decision}
- **Changes Addressed:** {summary of fixes}

#### Validation of Fixes
- **Issue 1:** ✅ RESOLVED - {how it was fixed}
- **Issue 2:** ✅ RESOLVED - {how it was fixed}

#### New Findings
- {None identified or list any new issues}

#### Updated Test Results
- **Unit Tests:** {passed}/{total}
- **Integration Tests:** {passed}/{total}
- **Coverage:** {percentage}%
- **Performance:** {benchmark results}

#### Gate Status
Gate: {status} → docs/qa/gates/{epic}.{story}-{slug}.yml

---

### Round 3: {timestamp} - Final Review
- **Reviewer:** {qa-agent-name}
- **Decision:** {PASS/WAIVED}
- **Previous Decision:** {Round 2 decision}
- **Final Assessment:** {summary}

#### Final Validation
- **All Issues Resolved:** ✅
- **Quality Gates Met:** ✅
- **Regression Testing:** ✅ PASSED
- **Performance Requirements:** ✅ MET

#### Gate Status
Gate: PASS → docs/qa/gates/{epic}.{story}-{slug}.yml

### Recommended Status
[✓ Ready for Done] - All QA requirements satisfied

---

## QA Review Summary

| Round | Date | Decision | Issues Found | Issues Resolved | Gate Status |
|-------|------|----------|--------------|-----------------|-------------|
| 1 | {date1} | {decision1} | {count1} | 0 | {gate1} |
| 2 | {date2} | {decision2} | {count2} | {resolved2} | {gate2} |
| 3 | {date3} | {decision3} | 0 | {resolved3} | PASS |

**Total Review Cycles:** {total_rounds}
**Total Time in Review:** {total_days} days
**Final Outcome:** {PASS/WAIVED}

### Quality Metrics
- **Initial Defect Density:** {defects}/{loc} defects per line
- **Fix Effectiveness:** {percentage}% of issues resolved in first fix attempt
- **Review Efficiency:** {hours} hours total review time
- **Code Quality Score:** {score}/100

### Lessons Learned
- {Key insights from review process}
- {Improvements for future development}
- {Best practices identified}

### Sign-off
**QA Reviewer:** {qa-agent-name}
**Date:** {final-date}
**Approval:** ✅ Quality gates met, story ready for production
