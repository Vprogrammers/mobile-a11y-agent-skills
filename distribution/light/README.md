# Mobile A11y Agent Skills Lite

Minimal, copy-ready distribution of accessibility agents and skills for Android, iOS, and Kotlin Multiplatform.

This repository is generated from [`Vprogrammers/mobile-a11y-agent-skills`](https://github.com/Vprogrammers/mobile-a11y-agent-skills). Development, validation, evals, samples, issues, and pull requests belong in the canonical repository.

## Install

Copy the agents and skills into the `.claude/` directory at the root of your project:

```bash
mkdir -p /path/to/your-project/.claude
cp -R .claude/agents .claude/skills /path/to/your-project/.claude/
```

This installs the specialized agents, the accessibility skills, and their references.

Then add the consumer instructions from `.claude/CLAUDE.md`. If your project has no `.claude/CLAUDE.md`, copy the file. Otherwise, merge its sections into your existing file instead of overwriting it.

## Contents

```text
.claude/
├── CLAUDE.md
├── agents/
└── skills/
```

The generated `.source.json` records the canonical source repository and commit.

## Source and support

- Documentation: <https://github.com/Vprogrammers/mobile-a11y-agent-skills>
- Issues: <https://github.com/Vprogrammers/mobile-a11y-agent-skills/issues>
- Contributing: <https://github.com/Vprogrammers/mobile-a11y-agent-skills/blob/main/CONTRIBUTING.md>

Do not submit content changes to this generated mirror.
