---
name: create-new-subagent
description: Creates a new specialized OpenCode subagent following best practices. Use this when you need a dedicated assistant for a specific repeating task.
---

# create-new-subagent

## Goal

To automate the creation of high-quality, specialized OpenCode subagents. This skill ensures that subagents are correctly configured, have limited tool access for security/focus, and include clear handoff rules for delegation.

## When to use

- When you need a specialized agent to handle a specific part of a larger workflow (e.g., code review, documentation generation, UI component creation).
- When a task is complex enough that a dedicated persona and instruction set would improve accuracy.

## When NOT to use

- For simple tasks that the primary agent can handle directly.
- For creating another general-purpose agent.

## Inputs

- **Subagent Name**: A concise, descriptive name.
- **Purpose**: A clear description of what the subagent will do.
- **Model**: (Optional) Preferred model defaults to `anthropic/claude-3-5-sonnet-20240620`.
- **Tools**: (Optional) List of tools the subagent needs (defaults to none).

## Outputs

- A new markdown file in `.opencode/agents/` (or current directory if outside OpenCode environment).

## Procedure

1. **Analyze**: Understand the specific task the subagent will perform.
2. **Name & Describe**: Suggest a `kebab-case` filename and a detailed `description` for the yaml frontmatter (crucial for primary agent delegation).
3. **Configure**: Set `mode: subagent` and the specified model.
4. **Prompt Engineering**: Draft a clear persona and instructions based on the purpose.
5. **Set Tools**: Explicitly list tools, defaulting to `false` for everything except what is strictly necessary.
6. **Define Handoffs**: Specify exactly when and how the subagent should return control to the primary agent.
7. **Create File**: Write the resulting markdown to `.opencode/agents/<name>.md`.

## Constraints / Safety

- **Tool Access**: Always limit tool access to the bare minimum.
- **Directory**: Prefer `.opencode/agents/` for local agents.
- **Clarity**: The `description` in the frontmatter must be clear and action-oriented to ensure successful routing by the primary agent.

## Examples

**User:** Create a subagent to review my code for security vulnerabilities.
**Agent:** I will create a `security-reviewer` subagent. It will be configured with a focused security persona, no access to write/edit tools for safety, and clear instructions to return a prioritized list of vulnerabilities.
[File Created: .opencode/agents/security-reviewer.md]
