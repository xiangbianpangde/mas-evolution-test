---
name: documentation
description: 'Documentation management skill for archivist agents. Use when: (1) maintaining knowledge bases, (2) writing technical documentation, (3) updating README files, (4) organizing project documentation, (5) creating changelogs and commit logs, (6) managing GitHub documentation sync. This skill helps preserve experiment history, update documentation after changes, and maintain clear project records.'
metadata:
  {
    "openclaw":
      {
        "emoji": "📚",
        "requires": { "anyBins": ["git"] },
        "primaryEnv": "GITHUB_TOKEN",
      },
  }
---

# Documentation Skill

This skill provides guidance for archivist agents on how to maintain project documentation, knowledge bases, and GitHub synchronization.

## Core Capabilities

### 1. README Management
- Update main README.md with current project status
- Add new sections for features/changes
- Maintain consistent formatting

### 2. Changelog Generation
```bash
# Generate changelog from git commits
git log --oneline --decorate --graph --all > CHANGELOG.md
```

### 3. Knowledge Base Maintenance
- Maintain `knowledge/` directory structure
- Log experiments with full RCA
- Update pattern files after discoveries

### 4. GitHub Sync Protocol
1. After experiment round: commit results
2. After champion change: commit + tag
3. After architecture change: detailed changelog commit
4. Ensure repo is always deployable

### 5. Documentation Templates

#### Experiment Log Template
```markdown
# Experiment Round {N}

## Date: {timestamp}
## Version: {version_id}
## Score: {score}

### Changes Made
- {list of modifications}

### Results
- {detailed results}

### Lessons Learned
- {insights gained}

### Next Steps
- {action items}
```

#### RCA Template
```markdown
# Root Cause Analysis: {experiment_id}

## Problem
{description}

## Analysis
{investigation details}

## Root Cause
{identified cause}

## Resolution
{how it was fixed}

## Prevention
{how to avoid in future}
```

## File Organization

```
knowledge/
├── learning/
│   ├── experiments/     # Per-experiment analysis
│   ├── patterns/        # Detected patterns
│   └── trends/          # Industry trends
├── lessons/            # Failed experiment logs
└── snapshots/          # Successful harness copies
```

## Best Practices

1. **Commit Early, Commit Often** - Don't wait for perfect commits
2. **Descriptive Messages** - Explain what and why, not just what
3. **Preserve Context** - Include RCA in every significant commit
4. **Tag Champions** - Use git tags for version milestones
5. **Update README** - Keep it current after every champion change

## GitHub Workflow

```bash
# 1. Stage changes
git add .

# 2. Commit with description
git commit -m "feat: {description}

- Added {feature}
- Fixed {issue}
- Score: {new_score}"

# 3. Push to remote
git push origin main

# 4. Create tag for milestones
git tag -a v{version} -m "Champion: {version} with score {score}"
git push origin v{version}
```

## Snapshot Strategy

- **Champions**: Copy to `src/native/harness/harness_v{n}.py`
- **Failed experiments**: Log to `knowledge/lessons/`
- **Best practices**: Update `knowledge/trends/Known_Trends.md`

## Quality Checklist

- [ ] README reflects current state
- [ ] All experiments documented
- [ ] RCA complete for failures
- [ ] Git tags for milestones
- [ ] Knowledge base up to date
