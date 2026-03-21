/**
 * manifest.ts — custom tools for reading and writing feature.yaml
 *
 * All manifest operations are delegated to manifest_tool.py, which uses
 * PyYAML to parse and serialise safely. Agents must use these tools instead
 * of writing raw YAML — LLM-generated YAML produces duplicate keys,
 * indentation bugs, and structural drift.
 *
 * Tool names exposed to agents:
 *   manifest_read           — read the full manifest as JSON
 *   manifest_write_section  — write or replace a top-level section
 *   manifest_set            — set a single field by dot-path
 *   manifest_append         — append an item to a list
 *   manifest_validate       — validate structure after any write
 */

import { tool } from "@opencode-ai/plugin";
import path from "path";
import { execFileSync } from "child_process";

// ---------------------------------------------------------------------------
// Internal: call manifest_tool.py with argv-style args
// ---------------------------------------------------------------------------
const SCRIPT = (worktree: string) =>
  path.join(worktree, ".opencode/tools/manifest_tool.py");

const run = (worktree: string, ...args: string[]): string => {
  try {
    const output = execFileSync("uv run python", [SCRIPT(worktree), ...args], {
      encoding: "utf8",
      timeout: 15000,
    });
    return output.trim();
  } catch (e: any) {
    // execFileSync throws on non-zero exit; stdout is still in e.stdout
    const stdout = (e.stdout ?? "").trim();
    if (stdout) return stdout;
    return JSON.stringify({ ok: false, error: e.message ?? String(e) });
  }
};

const manifestPath = (worktree: string, slug: string) =>
  path.join(worktree, "workflow", slug, "feature.yaml");

// ---------------------------------------------------------------------------
// manifest_read
// ---------------------------------------------------------------------------
export const read = tool({
  description:
    "Read workflow/<slug>/feature.yaml and return the full parsed manifest as a JSON object. " +
    "Always call this before any write operation to get the current state. " +
    "Never read the file as raw text — this tool validates YAML and returns structured data.",
  args: {
    slug: tool.schema.string().describe("Feature slug, e.g. passwordless-login"),
  },
  async execute(args, context) {
    return run(context.worktree, "read", manifestPath(context.worktree, args.slug));
  },
});

// ---------------------------------------------------------------------------
// manifest_write_section
// ---------------------------------------------------------------------------
export const write_section = tool({
  description:
    "Write or replace a complete top-level section of feature.yaml " +
    "(meta, feature, problem, design, plan, execution, or review). " +
    "Pass the section content as a JSON string. " +
    "The tool handles YAML serialisation — never write raw YAML manually. " +
    "Use manifest_set for targeted single-field updates; use this only when " +
    "writing a new section for the first time (e.g. adding 'design' at shape stage).",
  args: {
    slug: tool.schema.string().describe("Feature slug"),
    section: tool.schema
      .enum(["meta", "feature", "problem", "design", "plan", "execution", "review"])
      .describe("Top-level section name to write"),
    data: tool.schema
      .string()
      .describe(
        "Section content as a JSON string — a valid JSON object matching the manifest-writer schema for this section."
      ),
  },
  async execute(args, context) {
    return run(
      context.worktree,
      "write",
      manifestPath(context.worktree, args.slug),
      args.section,
      args.data
    );
  },
});

// ---------------------------------------------------------------------------
// manifest_set
// ---------------------------------------------------------------------------
export const set = tool({
  description:
    "Set a single field in feature.yaml using a dot-separated path. " +
    "Use this for targeted updates: status transitions, timestamps, phase changes, " +
    "and any single-field update. Far safer than rewriting a whole section. " +
    "Dot-path examples: " +
    "'feature.status' | " +
    "'feature.commands.next' | " +
    "'execution.waves.0.status' | " +
    "'plan.dag.auth-token.tasks.0.phase' | " +
    "'execution.slice_commits.auth-token' | " +
    "'review.verdict'. " +
    "Value must be JSON-encoded: strings as '\"building\"', numbers as '42', " +
    "booleans as 'true', null as 'null', objects as '{\"key\": \"val\"}'.",
  args: {
    slug: tool.schema.string().describe("Feature slug"),
    dot_path: tool.schema
      .string()
      .describe(
        "Dot-separated path to the field. Use numeric indices for list items: 'execution.waves.0.status'. " +
        "Hyphenated keys work as-is: 'plan.dag.auth-token.tasks.0.phase'."
      ),
    value: tool.schema
      .string()
      .describe(
        "New value as a JSON-encoded string. " +
        "String: '\"building\"' | Number: '42' | Boolean: 'true' | Null: 'null' | Object: '{\"k\": \"v\"}'."
      ),
  },
  async execute(args, context) {
    return run(
      context.worktree,
      "set",
      manifestPath(context.worktree, args.slug),
      args.dot_path,
      args.value
    );
  },
});

// ---------------------------------------------------------------------------
// manifest_append
// ---------------------------------------------------------------------------
export const append = tool({
  description:
    "Append a new item to a list in feature.yaml using a dot-separated path. " +
    "Use this for: adding entries to execution.run_history, review.findings, " +
    "execution.blockers, problem.open_questions, execution.waves, plan.dag.<slice>.tasks. " +
    "Never use this to overwrite existing entries — use manifest_set for that. " +
    "If the list does not yet exist at the path, it is created automatically.",
  args: {
    slug: tool.schema.string().describe("Feature slug"),
    dot_path: tool.schema
      .string()
      .describe(
        "Dot-separated path to the list. " +
        "Examples: 'execution.run_history' | 'review.findings' | " +
        "'execution.blockers' | 'problem.open_questions' | 'execution.waves'."
      ),
    item: tool.schema
      .string()
      .describe(
        "Item to append as a JSON-encoded string. " +
        "Must be a valid JSON object or value matching the manifest-writer schema for this list."
      ),
  },
  async execute(args, context) {
    return run(
      context.worktree,
      "append",
      manifestPath(context.worktree, args.slug),
      args.dot_path,
      args.item
    );
  },
});

// ---------------------------------------------------------------------------
// manifest_validate
// ---------------------------------------------------------------------------
export const validate = tool({
  description:
    "Validate the structure of feature.yaml and return any errors found. " +
    "Checks: required sections present for the current status, " +
    "plan.dag has no orphaned dependencies or self-references, " +
    "execution.waves are well-formed, review.verdict is a valid value. " +
    "Always call this after manifest_write_section and after any sequence of " +
    "manifest_set calls that changes feature.status. Fix all errors before proceeding.",
  args: {
    slug: tool.schema.string().describe("Feature slug"),
  },
  async execute(args, context) {
    return run(context.worktree, "validate", manifestPath(context.worktree, args.slug));
  },
});
