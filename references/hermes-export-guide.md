# Hermes Environment Export Guide

## When to Use

When the user asks to export/archive their Hermes environment (skills, wiki, memory) for backup, migration, or sharing.

## What to Export

### 1. Custom Skills

**Location:** `skills/`

**How to identify custom vs bundled:**
```bash
# List bundled skill names
cat skills/.bundled_manifest | awk '{print $1}'

# Compare against all skill dirs to find custom ones
comm -23 <(ls -d skills/*/ | xargs -I{} basename {} | sort) \
         <(cat skills/.bundled_manifest | awk '{print $1}' | sort)
```

**Export:** Copy the entire skill directory including all subdirectories (references/, scripts/, templates/, llm-wiki/):
```bash
cp -r skills/<skill-name> <export-dir>/skills/
```

**Important:** Some skills have embedded wikis (e.g., `model-router/llm-wiki/`). Include these — they contain session-specific knowledge that doesn't exist elsewhere.

### 2. LLM-Wiki

**Location:** `config/wiki/`

**Export:** Copy the entire wiki directory:
```bash
cp -r config/wiki/* <export-dir>/wiki/
```

### 3. Memory

**Locations:**
- `config/memory/user.md` — Hardware, software, environment facts
- `config/MEMORY.md` — Master memory index
- `config/memories/MEMORY.md` — Hermes internal memory store

**Export:**
```bash
cp config/memory/user.md <export-dir>/memory/user_profile.md
cp config/MEMORY.md <export-dir>/memory/MEMORY_INDEX.md
cp config/memories/MEMORY.md <export-dir>/memory/
```

## Export Structure

```
HERMES_FILES/
├── README.md
├── skills/
│   ├── <custom-skill>/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/
│   └── forward.md
├── memory/
│   ├── user_profile.md
│   ├── MEMORY_INDEX.md
│   └── memories_MEMORY.md
└── wiki/
    ├── SCHEMA.md
    ├── index.md
    ├── entities/
    ├── concepts/
    └── ...
```

## Verification

After export:
1. Count files: `find <export-dir> -type f | wc -l`
2. Check total size: `du -sh <export-dir>`
3. Verify key files exist
4. Run `sync` to ensure all writes are flushed
