# Create Parallel Stories Task

## Purpose

Generate multiple stories that can be developed simultaneously using Git worktrees. This task analyzes epics and creates parallel-safe stories with clear dependencies, worktree branches, and conflict-free development paths.

## When to Use

Use this task when:
- Epic has independent features that can be developed in parallel
- Team has multiple developers available
- Want to accelerate development through concurrent work
- Stories have minimal interdependencies

## Task Execution

### 1. Analyze Epic for Parallel Opportunities

**Input Requirements:**
- Epic file (sharded or monolithic)
- Current development context
- Team capacity and developer availability

**Analysis Criteria:**
- **Independence**: Stories that don't depend on each other
- **Module Isolation**: Features in different system modules
- **API Stability**: Changes don't break shared interfaces
- **Data Independence**: No shared database schema changes

### 2. Generate Parallel Story Set

**Story Structure:**
```
story-{epic_num}-{set_num}-{story_num}[Feature-Name]
```

**Example:**
```
story-1-1-1[User-Auth] - Branch: feature/story-1-1-1-user-auth
story-1-1-2[Payment-Processing] - Branch: feature/story-1-1-2-payment-processing
story-1-1-3[Admin-Dashboard] - Branch: feature/story-1-1-3-admin-dashboard
```

### 3. Create Worktree Development Plan

**Branch Naming:** `feature/story-{epic}-{set}-{number}-{feature-slug}`

**Worktree Setup:**
```bash
# Create worktrees for parallel development
git worktree add ../worktree-story-1-1-1 feature/story-1-1-1-user-auth
git worktree add ../worktree-story-1-1-2 feature/story-1-1-2-payment-processing
git worktree add ../worktree-story-1-1-3 feature/story-1-1-3-admin-dashboard
```

### 4. Dependency Management

**Parallel-Safe Indicators:**
- ✅ **Parallel-Safe**: Can develop simultaneously
- ⚠️ **Sequential-Dependent**: Must complete before other stories
- ❌ **Conflict-Risk**: High risk of merge conflicts

**Dependency Mapping:**
```yaml
story-1-1-1-user-auth:
  parallel_safe: true
  depends_on: []
  conflicts_with: []

story-1-1-2-payment-processing:
  parallel_safe: true
  depends_on: []
  conflicts_with: []

story-1-1-3-admin-dashboard:
  parallel_safe: true
  depends_on: ["story-1-1-1-user-auth"]
  conflicts_with: []
```

### 5. Module Assignment

**Conflict Prevention:**
- **Frontend**: UI components, styling, user interactions
- **Backend**: API endpoints, business logic, services
- **Database**: Schema changes, migrations, data models
- **Infrastructure**: Configuration, deployment, monitoring

### 6. Development Workflow

**Parallel Execution:**
1. Create worktrees for each parallel story
2. Assign developers to different stories
3. Daily sync meetings for parallel story status
4. Independent testing and QA for each story
5. Merge conflict resolution planning

**Merge Strategy:**
```bash
# Individual story completion
cd ../worktree-story-1-1-1
git add .
git commit -m "feat: implement user auth (#story-1-1-1)"

# Merge back to main
git checkout main
git merge feature/story-1-1-1-user-auth
```

### 7. Quality Assurance

**Parallel Testing:**
- Unit tests run independently
- Integration tests for story-specific features
- Cross-story integration testing
- Parallel performance testing

### 8. Progress Tracking

**Parallel Dashboard:**
```
📊 Parallel Development Set 1-1 Status
├── ✅ story-1-1-1[User-Auth] - 95% complete
├── 🔄 story-1-1-2[Payment-Processing] - 60% complete
└── ⏳ story-1-1-3[Admin-Dashboard] - 20% complete

🎯 Next: Integration testing for completed stories
```

## Output Formats

### Story List Output
```
## Parallel Development Set {epic_num}-{set_num}

### Stories Ready for Parallel Development
- story-{epic}-{set}-{num}[Feature-Name] - Branch: feature/story-{epic}-{set}-{num}-{feature-slug}
- story-{epic}-{set}-{num}[Feature-Name] - Branch: feature/story-{epic}-{set}-{num}-{feature-slug}
- story-{epic}-{set}-{num}[Feature-Name] - Branch: feature/story-{epic}-{set}-{num}-{feature-slug}

### Sequential Dependencies (After Set Completion)
- story-{epic}-{next}[Integration-Testing] - Depends on: story-{epic}-{set}-*
```

### Worktree Setup Script
```bash
#!/bin/bash
# Parallel Development Setup Script

echo "🚀 Setting up parallel development worktrees..."

# Create worktrees
git worktree add ../worktree-story-1-1-1 feature/story-1-1-1-user-auth
git worktree add ../worktree-story-1-1-2 feature/story-1-1-2-payment-processing
git worktree add ../worktree-story-1-1-3 feature/story-1-1-3-admin-dashboard

echo "✅ Worktrees created successfully!"
echo "📝 Assign developers to worktrees and start development"
```

## Success Criteria

- **Parallel Safety**: Stories can be developed without merge conflicts
- **Clear Dependencies**: All inter-story dependencies documented
- **Fast Development**: 2-3x acceleration through parallel work
- **Quality Maintenance**: Independent testing doesn't compromise quality
- **Easy Merging**: Clean integration back to main branch

## Best Practices

### Story Sizing
- Keep parallel stories similar in size (3-5 days each)
- Ensure adequate test coverage for independent validation
- Include integration testing requirements

### Communication
- Daily standups for parallel story status
- Early identification of dependency issues
- Regular code reviews across parallel stories

### Conflict Prevention
- Clear module boundaries
- API contract agreements
- Database migration coordination
- Shared component freeze during parallel development
