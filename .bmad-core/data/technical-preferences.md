<!-- Powered by BMAD™ Core -->

# User-Defined Preferred Patterns and Preferences

## Development Methodology

### Parallel Development Standards
- **Naming Convention**: `story-{epic_num}-{set_num}-{story_num}[Feature-Name]`
- **Branch Pattern**: `feature/story-{epic}-{set}-{num}-{feature-slug}`
- **Worktree Path**: `../worktree-story-{epic}-{set}-{num}`
- **Parallel-Safe Priority**: Maximize concurrent development opportunities

### Story Organization
- **Parallel Sets**: Group independent stories for simultaneous development
- **Sequential Stories**: Number as `story-{epic}-{next}` after parallel sets
- **Dependency Tracking**: Explicit dependency mapping for merge planning
- **Module Isolation**: Assign stories to conflict-free system modules

### Quality Assurance for Parallel Development
- **Independent Testing**: Each story maintains full test coverage
- **Integration Gates**: Cross-story testing before final merges
- **Code Review**: Parallel peer reviews with dependency awareness
- **Merge Strategy**: Feature flags for gradual rollouts

## File Naming Standards

### Stories
- **Format**: `story-{epic}.{story}[{feature-slug}].md`
- **Examples**:
  - `story-1.1[user-auth].md`
  - `story-1-1-2[payment-flow].md`
  - `story-2[integration-testing].md`

### Branches
- **Feature Branches**: `feature/story-{id}-{feature-slug}`
- **Bugfix Branches**: `fix/story-{id}-{issue-slug}`
- **Hotfix Branches**: `hotfix/{issue-slug}`

### Worktrees
- **Path Pattern**: `../worktree-story-{id}`
- **Naming**: Match branch name for clarity

## Development Acceleration Preferences

### Parallel Processing
- **Preferred**: Git worktrees for parallel story development
- **Capacity**: 3-4 simultaneous stories per epic set
- **Synchronization**: Daily alignment meetings
- **Integration**: Automated testing for cross-story conflicts

### Automation Priority
- **High**: Test automation for parallel validation
- **Medium**: Code generation for boilerplate
- **Low**: Manual documentation tasks

### Quality Gates
- **Pre-Parallel**: Architecture review and dependency analysis
- **During Parallel**: Independent story validation
- **Post-Parallel**: Integration testing and final QA
