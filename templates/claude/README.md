# Optional hardened Claude Code settings

This is a deny-only starting point for projects that copy these agents and skills. Review every rule before use and merge it with the project's existing settings; do not overwrite project-specific permissions blindly.

To enable it for a repository:

```bash
mkdir -p .claude
cp templates/claude/settings.json .claude/settings.json
```

The template blocks common credential and signing files, including Gradle and keystore property files that often hold signing passwords, plus destructive Git state changes, remote mutation, direct push or merge, release, publishing, signing, notarization, and store or test-distribution commands. Agents rarely need `local.properties`; Gradle still reads it. Agent prose is not a command sandbox, and plugin subagents cannot enforce command-specific hooks, so project settings are the enforcement layer. Command matching is textual and cannot cover every equivalent command, wrapper, alias, script, MCP tool, or external process. Keep branch protection, credential isolation, sandboxing, and human review in place.

If a denied operation is genuinely required, perform it outside the agent session or change the project policy deliberately. Do not weaken the shared policy merely to bypass a failed task.

Official sources:

- Claude Code settings: https://docs.anthropic.com/en/docs/claude-code/settings
- Claude Code permissions: https://docs.anthropic.com/en/docs/claude-code/permissions
- Claude Code security: https://docs.anthropic.com/en/docs/claude-code/security
