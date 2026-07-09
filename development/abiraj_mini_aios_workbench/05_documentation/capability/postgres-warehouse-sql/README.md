# Capability: `postgres-warehouse-sql` (Claude Code skill)

**Version-controlled SOURCE** of the reusable Claude Code skill for querying the company
PostgreSQL warehouse (`order_management_copy`) through the connected Postgres MCP. Applies to
**any** project that touches that database.

- `SKILL.md` — the skill (router + rules + trigger description).
- `references/` — 3 query-pattern guides (`pattern_single_table.md`, `pattern_multi_table.md`,
  `pattern_ppc_stock_lookup.md`) + 17 `TABLE_*.md` per-table schema references.

## Why it lives here
Claude Code only auto-loads skills from a `.claude/skills/` folder — but `**/.claude/` is
**git-ignored** in this repo, so a skill placed there is not backed up. This folder is the
**tracked, backed-up source of truth**; a working copy is installed into the user's global
skills dir to actually load it.

## Install / activate (loads for every project on the machine)
Copy this folder into the global skills directory, then start a new Claude session:

```bash
# Windows (Git Bash)
cp -r "development/abiraj_mini_aios_workbench/05_documentation/capability/postgres-warehouse-sql" \
      "$HOME/.claude/skills/"
```

After a re-clone of this repo on a new machine, run the same copy once to reinstall the skill.

## Update flow
Edit the files **here** (tracked), commit, then re-run the copy above to refresh the active
copy in `~/.claude/skills/`. Keep the two in sync; this folder is canonical.

## Add a new table
Drop a `TABLE_<name>.md` into `references/` and add a line to the table index in `SKILL.md`.
