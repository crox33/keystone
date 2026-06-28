# Requiring 1 reviewer on pull requests

Goal: nobody can merge to the default branch (`master`) without **at least one
other person approving** the PR. Set this once, after migration, on
`github.com/crox33/keystone`.

## Option A — GitHub UI (simplest)
1. Repo → **Settings** → **Branches** → **Add branch ruleset** (or *Add rule*).
2. Target the default branch (`master`).
3. Enable **Require a pull request before merging**, then set
   **Required approvals = 1**.
4. (Recommended) also tick **Dismiss stale approvals on new commits** and
   **Require status checks to pass** (select the CI check once it exists).
5. (Recommended) **Do not allow bypassing the above settings** so admins are held
   to the same rule.
6. Save.

> "1 *other* reviewer" is inherent: GitHub never counts the PR author's own
> approval. A solo repo therefore needs a second collaborator to actually merge —
> add one under Settings → Collaborators.

## Option B — one command (`gh`)
Requires admin on the repo. Creates a ruleset requiring 1 approval:

```bash
gh api --method POST repos/crox33/keystone/rulesets \
  -H "Accept: application/vnd.github+json" \
  --input - <<'JSON'
{
  "name": "default-branch-protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      } },
    { "type": "non_fast_forward" }
  ]
}
JSON
```

To also require CI to pass, add a `required_status_checks` rule once the workflow
exists. Verify with:
```bash
gh api repos/crox33/keystone/rulesets
```
