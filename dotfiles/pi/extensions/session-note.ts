/**
 * Session Note Extension
 *
 * Surfaces ./ai/session-note.md on session start / /new without auto-running it.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export interface SessionNoteSummary {
	notePath: string;
	goal: string;
	mtime: string;
}

/** Extract the first meaningful line under `## Goal` (or the first body line). */
export function extractGoal(text: string): string {
	const lines = text.split(/\r?\n/);
	let inGoal = false;

	for (const raw of lines) {
		const line = raw.trim();
		if (line.toLowerCase().startsWith("## goal")) {
			inGoal = true;
			continue;
		}
		if (inGoal) {
			if (line.startsWith("#")) break;
			if (line) return line.slice(0, 140);
		}
	}

	for (const raw of lines) {
		const line = raw.trim();
		if (line && !line.startsWith("#")) return line.slice(0, 140);
	}

	return "Saved session handoff";
}

function formatLocalTimestamp(ms: number): string {
	const d = new Date(ms);
	const pad = (n: number) => String(n).padStart(2, "0");
	return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** Locate and summarize `<cwd>/ai/session-note.md` if present and non-empty. */
export function findSessionNoteSummary(cwd: string): SessionNoteSummary | null {
	const notePath = path.join(cwd, "ai", "session-note.md");
	let stat: fs.Stats;
	try {
		stat = fs.statSync(notePath);
	} catch {
		return null;
	}
	if (!stat.isFile() || stat.size === 0) return null;

	try {
		const content = fs.readFileSync(notePath, "utf-8");
		return {
			notePath,
			goal: extractGoal(content),
			mtime: formatLocalTimestamp(stat.mtimeMs),
		};
	} catch {
		return null;
	}
}

export default function (pi: ExtensionAPI) {
	let pendingGuideline: string | null = null;

	pi.on("session_start", async (_event, ctx) => {
		const summary = findSessionNoteSummary(ctx.cwd);
		if (!summary) {
			pendingGuideline = null;
			return;
		}

		pendingGuideline =
			`A session handoff note exists at ${summary.notePath} (saved ${summary.mtime}). ` +
			`Summary: ${summary.goal}. Do NOT read or execute it unless the user asks to resume/continue or references the session note.`;

		if (ctx.hasUI) {
			ctx.ui.notify(`Session note found (ai/session-note.md, ${summary.mtime}): ${summary.goal}`, "info");
		}
	});

	pi.on("before_agent_start", async (event) => {
		if (!pendingGuideline || event.messageType !== "user") return;
		event.systemPromptOptions.promptGuidelines.push(pendingGuideline);
		pendingGuideline = null;
	});
}
