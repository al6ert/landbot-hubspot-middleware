---
name: create-new-skill
description: Scaffolds a complete agent skill directory structure and generates a high-quality SKILL.md. Use this when the user wants to add a new capability or when you identify a repeatable task that should be encapsulated.
---

# create-new-skill

## Goal

To generate a complete, premium-grade agent skill structure. This includes creating the full directory scaffolding and a `SKILL.md` file designed for high router recall and precise execution.

## When to use

- When the user explicitly asks to "create a skill", "add a capability", or "teach you how to do X".
- When you identify a repeatable complex task. **Note**: If identifying a task automatically, suggest creating the skill first and proceed only after user confirmation.

## When NOT to use

- For one-off scripts or simple code snippets.
- For simple aliases or single-command tasks that don't require specific instructions or safety constraints.

## Inputs

- **User Request**: Natural language description of the skill's purpose.
- **Target Directory**: Defaults to `.agent/skills/` in the workspace root.

## Outputs

A new skill directory with the following structure:

- `SKILL.md`: The primary instruction file (must be uppercase).
- `scripts/`: For deterministic logic/tools.
- `references/`: For documentation or large context files.
- `examples/`: For golden examples and few-shot prompts.
- `assets/`: For static resources.
- `evals/`: For testing and regression prompts.

## Procedure

### Step 1: Analyze & Validate

- **Name**: Choose a concise `kebab-case` name.
- **Validation**: Avoid generic names like `test`, `tmp`, or `new-skill`.
- **Collision Check**: Verify if the directory already exists. If it does, ask for permission to update or choose a new name.
- **Description**: Draft a precise "router prompt" (Capability + Context + Examples).

### Step 2: Scaffold Structure

- Create the main folder: `.agent/skills/<skill-name>`.
- Create sub-directories: `scripts/`, `references/`, `examples/`, `assets/`, `evals/`.

### Step 3: Generate SKILL.md

- Create `.agent/skills/<skill-name>/SKILL.md` (exactly this casing).
- Use the **Premium Template** provided below.

#### Premium Template

```markdown
---
name: <skill-name>
description: <precise description for routing: capability + context + 2-3 intent examples>
---
# <skill-name>

## Goal
<Clear statement of what this skill achieves>

## When to use
- <Specific scenario 1>
- <Specific scenario 2>

## When NOT to use
- <Counter-example 1>
- <Counter-example 2>

## Inputs
- <Required information, files, or state>

## Outputs
- <What is produced: files, terminal output, modified state, etc.>

## Procedure
1.  <Step 1>
2.  <Step 2>
3.  ...

## Constraints / Safety
- <Safety rules, e.g., "Ask for confirmation before side effects">
- <Domain-specific constraints>

## Examples
**User:** <Example trigger prompt>
**Agent:** <Expected behavior/output showing logic and results>
```

### Step 4: Verification (Definition of Done)

- [ ] `SKILL.md` uses uppercase filename.
- [ ] `description` follows the "router prompt" pattern.
- [ ] `When NOT to use` is clearly defined.
- [ ] At least one "Golden Example" is included in the body.
- [ ] All scaffold folders (`scripts/`, etc.) exist.

### Step 5: Confirm

- Notify the user that the skill has been created and list the scaffolded files.

## Constraints / Safety

- **Strictly** use `SKILL.md` (uppercase) for the main file.
- **Sanitize** names to avoid invalid filesystem characters.
- **Do not** overwrite existing folders without explicit user consent.
