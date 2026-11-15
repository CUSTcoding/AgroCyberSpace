# Conventional Commits Specification & Guide

All commits, pull request titles, and branch contributions in this repository follow the **[Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)** specification.

---

## 1. Commit Message Structure

Every commit message must follow this exact format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Example:
```
feat(game): add 12 chapter seeds and content validator

Implements verified pedagogical seeds for Mozambique study regions
and validates schema consistency across all lessons.

Closes #42
```

---

## 2. Commit Types

| Type | Description | Release Bump | Example |
|---|---|---|---|
| **`feat`** | A new user-facing feature or API endpoint | Minor (`0.X.0`) | `feat(api): add /regions/{id}/map-config endpoint` |
| **`fix`** | A bug fix in existing behavior | Patch (`0.0.X`) | `fix(auth): handle expired refresh token gracefully` |
| **`docs`** | Documentation changes only | None | `docs(readme): add docker deployment instructions` |
| **`style`** | Code style changes (formatting, whitespace, semi-colons) | None | `style(frontend): format JSX components with Prettier` |
| **`refactor`** | Code refactoring that neither fixes a bug nor adds a feature | None | `refactor(db): streamline session pooling in database.py` |
| **`perf`** | Performance improvements | Patch (`0.0.X`) | `perf(geo): add GIST index on district polygon geometry` |
| **`test`** | Adding or correcting automated tests | None | `test(auth): add integration tests for JWT rotation` |
| **`build`** | Changes affecting build tooling or external dependencies | None | `build(uv): bump fastapi from 0.114.0 to 0.115.0` |
| **`ci`** | Changes to CI/CD workflows and automation scripts | None | `ci(github): add conventional commit linting workflow` |
| **`chore`** | Routine repository maintenance tasks | None | `chore(gitignore): ignore local COG raster storage` |
| **`revert`** | Reverts a previous commit | Varies | `revert: feat(game): rollback chapter 10 seed change` |

---

## 3. Allowed Scopes

Scopes provide contextual clarity regarding the subsystem being altered:

| Scope | Subsystem / Area |
|---|---|
| `auth` | Authentication, JWT, Argon2id hashing, user roles |
| `users` | User profile endpoints and models |
| `regions` | Study regions (Gaza, Tete, Zambézia), districts, and communities |
| `game` | Chapters, lessons, missions, scoring, progress, achievements |
| `eo` | Earth Observation, NASA POWER, timeseries, dataset metadata |
| `ai` | Deterministic template explanations and hint providers |
| `db` | PostgreSQL, PostGIS, Alembic migrations, database engine |
| `frontend` | Web UI, React components, scene rendering, speech audio |
| `infra` | Docker, Compose stacks, Nginx reverse proxy |
| `ci` | GitHub Actions workflows and automation |
| `docs` | Repository documentation, guides, and ADRs |

---

## 4. Breaking Changes

Breaking changes must be clearly flagged in one of two ways:
1. Append an exclamation mark (`!`) immediately preceding the colon:
   ```
   feat(auth)!: require email confirmation before login
   ```
2. Include a `BREAKING CHANGE:` footer with explanation:
   ```
   refactor(api): change user identifier from integer to UUIDv4

   BREAKING CHANGE: The /users endpoints now expect UUIDv4 paths.
   ```

---

## 5. Automated CI Validation

The pull request title and commit messages are checked in CI using the `.github/workflows/conventional-commits.yml` action. Pull requests with non-compliant titles cannot be merged.
