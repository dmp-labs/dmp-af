# Release Process

This project uses [Python Semantic Release](https://python-semantic-release.readthedocs.io/) to automate versioning, changelog generation, git tagging, and publishing to PyPI.

## Overview

The release process is **triggered manually** via GitHub Actions, but everything else is automated:

- ✅ Version number calculation (from commit messages)
- ✅ Version bumping in `dmp_af/__init__.py` and `pyproject.toml`
- ✅ Changelog generation from commits
- ✅ Git tag creation
- ✅ GitHub release creation
- ✅ PyPI publishing

## Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types and Version Bumps

- `feat:` - New feature → **MINOR** version bump (0.14.0 → 0.15.0)
- `fix:` - Bug fix → **PATCH** version bump (0.14.0 → 0.14.1)
- `perf:` - Performance improvement → **PATCH** version bump
- `docs:` - Documentation changes → No version bump
- `style:` - Code style changes → No version bump
- `refactor:` - Code refactoring → No version bump
- `test:` - Test changes → No version bump
- `build:` - Build system changes → No version bump
- `ci:` - CI/CD changes → No version bump
- `chore:` - Other changes → No version bump

### Breaking Changes

To trigger a **MAJOR** version bump (0.14.0 → 1.0.0), include `BREAKING CHANGE:` in the commit footer:

```
feat: add support for Airflow 3.0

BREAKING CHANGE: Drop support for Airflow 2.6 and Python 3.9
```

Or use the `!` shorthand:

```
feat!: redesign configuration API
```

### Examples

```bash
# Patch release (0.14.6 → 0.14.7)
git commit -m "fix: correct snapshot task generation for new dbt format"

# Minor release (0.14.6 → 0.15.0)
git commit -m "feat: add support for dbt Cloud metadata export"

# With scope
git commit -m "feat(operators): add new Python venv operator"

# With body and footer
git commit -m "fix(sensors): timeout handling in external sensor

Previously the sensor would hang indefinitely when the upstream
task failed. Now it respects the timeout parameter.

Fixes #123"

# Major release (0.14.6 → 1.0.0)
git commit -m "feat: redesign DAG configuration API

BREAKING CHANGE: The DmpAfConfig class now requires explicit
domain specification. The old automatic domain detection has been
removed."
```

## Triggering a Release

### Option 1: Automatic Version Detection (Recommended)

Let semantic-release analyze commits and determine the version bump:

1. Go to **Actions** tab in GitHub
2. Select **Semantic Release** workflow
3. Click **Run workflow**
4. Leave all inputs empty
5. Click **Run workflow**

The workflow will:
- Analyze commits since last release
- Determine version bump (patch/minor/major)
- Skip release if no relevant commits found

### Option 2: Force Specific Version Bump

Override automatic detection:

1. Go to **Actions** tab in GitHub
2. Select **Semantic Release** workflow
3. Click **Run workflow**
4. Select force level: `patch`, `minor`, or `major`
5. Click **Run workflow**

### Option 3: Prerelease

Create a prerelease version (e.g., 0.15.0-rc.1):

1. Go to **Actions** tab in GitHub
2. Select **Semantic Release** workflow
3. Click **Run workflow**
4. Check **Create a prerelease version**
5. Click **Run workflow**

## What Happens During Release

1. **Verify Tests**: Waits for integration tests to pass on main branch
2. **Version Calculation**: Analyzes commits to determine next version
3. **Update Files**: Updates `__version__` in code and pyproject.toml
4. **Generate Changelog**: Adds new release section to CHANGELOG.md
5. **Create Commit**: Commits changes with message `chore(release): X.Y.Z`
6. **Create Tag**: Creates git tag `vX.Y.Z`
7. **Push Changes**: Pushes commit and tag to main branch
8. **GitHub Release**: Creates GitHub release with changelog
9. **Build Package**: Builds wheel and source distribution
10. **Publish to PyPI**: Uploads to PyPI with trusted publishing

## Validating Commits Locally

To ensure your commits follow the convention, install pre-commit hooks:

```bash
# Install pre-commit hook
uv run pre-commit install --hook-type commit-msg

# Test your commit message
uv run pre-commit run conventional-pre-commit \
  --hook-stage commit-msg \
  --commit-msg-filename <(printf 'feat: my new feature\n')

# If your shell does not support process substitution, write the message to a file instead:
printf 'feat: my new feature\n' > /tmp/commit-msg.txt
uv run pre-commit run conventional-pre-commit \
  --hook-stage commit-msg \
  --commit-msg-filename /tmp/commit-msg.txt
```

The hook will validate commit messages and reject invalid ones:

```bash
# ✅ Valid
git commit -m "feat: add new sensor type"

# ❌ Invalid (will be rejected)
git commit -m "added new sensor"
git commit -m "WIP: testing something"
```

## Previewing Next Version

To see what version will be released without actually releasing:

```bash
# Install semantic-release
uv sync --group release

# Preview next version
uvx --from python-semantic-release semantic-release version --print

# Show what would change
uvx --from python-semantic-release semantic-release version --print-tag
uvx --from python-semantic-release semantic-release version --print-last-released
uvx --from python-semantic-release semantic-release changelog --unreleased
```

## Troubleshooting

### No Release Created

**Problem**: Workflow runs but doesn't create a release.

**Causes**:
- No commits with `feat:`, `fix:`, or breaking changes since last release
- Only commits with `docs:`, `chore:`, `style:`, etc.

**Solution**: Ensure you have commits that warrant a version bump.

### Version Conflict

**Problem**: PyPI rejects the upload because version already exists.

**Solution**: Version conflicts should not happen with semantic-release. If they do:
1. Check the last git tag: `git describe --tags --abbrev=0`
2. Check PyPI version: https://pypi.org/project/dmp-af/
3. Manually tag if needed: `git tag vX.Y.Z && git push origin vX.Y.Z`

### Tests Failing

**Problem**: Release workflow fails at test verification step.

**Solution**: Fix the tests on main branch first. The release cannot proceed if integration tests are failing.

### Commit Hook Rejection

**Problem**: Cannot commit because message is rejected.

**Solutions**:
```bash
# Bypass the hook (not recommended)
git commit --no-verify -m "your message"

# Or fix the message format
git commit -m "feat: your feature description"
```

## Migration from Manual Releases

### First Release with Semantic Release

If migrating from manual releases:

1. Ensure `dmp_af/__init__.py` has correct current version
2. Create a git tag for the current version: `git tag v0.14.6`
3. Push the tag: `git push origin v0.14.6`
4. Make commits following conventional format
5. Trigger first semantic release

### Converting Old Commits

Old commits without conventional format won't affect new releases. Semantic-release only looks at commits since the last tagged release.

## Best Practices

1. **Write meaningful commit messages**: They become your changelog
2. **Use scopes**: `feat(operators):`, `fix(sensors):` for better organization
3. **Include issue references**: `Fixes #123`, `Closes #456`
4. **Group related changes**: Make logical, atomic commits
5. **Test before merging**: Only merge to main when tests pass
6. **Review changelog**: Check the generated changelog in the release PR

## Configuration

Configuration is in `pyproject.toml` under `[tool.semantic_release]`. Key settings:

- `branch = "main"`: Release from main branch
- `version_variables`: Where to update version in code
- `changelog_file`: Path to changelog
- `major_on_zero = false`: Allow 0.x.y versions without forcing 1.0.0
- `commit_parser_options`: Define which commit types trigger releases

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Semantic Release Docs](https://python-semantic-release.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
