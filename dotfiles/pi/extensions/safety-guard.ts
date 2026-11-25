/**
 * Safety Guard Extension
 *
 * Blocks secret writes, git force-push / ./ai/ staging, and edits to ~/.pi/agent
 * or ~/projects/desktopConfigs outside dedicated tuning sessions.
 */

import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const ALLOWED_ENV_EXAMPLES = new Set([".env.example", ".env.sample", ".env.template"]);
const SECRET_EXTENSIONS = [".pem", ".key", ".kdbx", ".pgp", ".gpg"];
const MUTATION_HINTS =
	/(?:^|\s|[;|&(])(?:>|>>|tee\b|rm\b|mv\b|cp\b|ln\b|sed\s+-i|chmod\b|chown\b|touch\b|mkdir\b)/;

function expandHome(rawPath: string, homeDir: string): string {
	if (rawPath === "~") return homeDir;
	if (rawPath.startsWith("~/")) return path.join(homeDir, rawPath.slice(2));
	return rawPath;
}

function realpathBestEffort(targetPath: string): string {
	const abs = path.resolve(targetPath);
	try {
		return fs.realpathSync(abs);
	} catch {
		const parent = path.dirname(abs);
		if (parent === abs) return abs;
		try {
			return path.join(fs.realpathSync(parent), path.basename(abs));
		} catch {
			return abs;
		}
	}
}

export function isInsideDir(candidate: string, dir: string): boolean {
	const normCand = path.resolve(candidate);
	const normDir = path.resolve(dir);
	return normCand === normDir || normCand.startsWith(normDir + path.sep);
}

/** Validate write/edit target paths against secret and config-drift rules. */
export function checkWriteTarget(
	rawPath: string,
	cwd: string,
	homeDir: string = os.homedir(),
): string | null {
	if (!rawPath) return null;

	const expanded = expandHome(rawPath, homeDir);
	const resolved = path.isAbsolute(expanded) ? path.resolve(expanded) : path.resolve(cwd, expanded);
	const realTarget = realpathBestEffort(resolved);
	const base = path.basename(resolved);

	if (/(?:^|\/)\.git(?:\/|$)/.test(resolved) || /(?:^|\/)\.git(?:\/|$)/.test(realTarget)) {
		return `Writes inside .git/ are blocked (${rawPath})`;
	}
	if ((base === ".env" || base.startsWith(".env.")) && !ALLOWED_ENV_EXAMPLES.has(base)) {
		return `Writes to secret env file "${base}" are blocked`;
	}
	if (SECRET_EXTENSIONS.some((ext) => base.endsWith(ext))) {
		return `Writes to credential/key file "${base}" are blocked`;
	}

	const piAgentDir = realpathBestEffort(path.join(homeDir, ".pi", "agent"));
	const piAuthFile = path.join(piAgentDir, "auth.json");
	if (realTarget === piAuthFile || resolved === path.join(homeDir, ".pi", "agent", "auth.json")) {
		return "Modifying ~/.pi/agent/auth.json is blocked; use `pi auth login`";
	}

	const desktopConfigsDir = realpathBestEffort(path.join(homeDir, "projects", "desktopConfigs"));
	const realCwd = realpathBestEffort(cwd);
	const inTuningRepo = isInsideDir(realCwd, desktopConfigsDir);

	if (!inTuningRepo) {
		if (isInsideDir(resolved, piAgentDir) || isInsideDir(realTarget, piAgentDir)) {
			return "Editing ~/.pi/agent/ is blocked outside projects/desktopConfigs";
		}
		if (isInsideDir(realTarget, desktopConfigsDir)) {
			return "Editing projects/desktopConfigs is blocked from non-config sessions";
		}
	}

	return null;
}

/** Validate bash commands against force-push, ./ai/ staging, destructive rm, and config drift. */
export function checkBashCommand(
	command: string,
	cwd: string,
	homeDir: string = os.homedir(),
): string | null {
	if (!command) return null;

	if (/\bgit\s+push\b[^\n]*(?:\s--force(?:-with-lease)?\b|\s-[a-zA-Z]*f\b)/.test(command)) {
		return "Force-push is blocked by safety-guard";
	}
	if (/\bgit\s+add\b[^\n]*(?:^|\s)(?:\.?\/)?ai(?:\/|\s|$)/.test(command)) {
		return "Staging ./ai/ is blocked; internal agent artifacts must never be committed";
	}
	if (/\bgit\s+add\b[^\n]*(?:^|\s)\.env(?:\.|\s|$)/.test(command)) {
		return "Staging .env files is blocked";
	}
	if (
		/\brm\s+-[a-zA-Z]*(?:r[a-zA-Z]*f|f[a-zA-Z]*r)\b[^\n]*\s+(?:\/(?:\*|\s|$)|~(?:\/|\s|$)|\$HOME|\$\{HOME\})/.test(
			command,
		)
	) {
		return "Destructive recursive delete on root or home directory is blocked";
	}

	const desktopConfigsDir = realpathBestEffort(path.join(homeDir, "projects", "desktopConfigs"));
	const inTuningRepo = isInsideDir(realpathBestEffort(cwd), desktopConfigsDir);
	if (
		!inTuningRepo &&
		/(?:\.pi\/agent|desktopConfigs)/.test(command) &&
		MUTATION_HINTS.test(command)
	) {
		return "Mutating ~/.pi/agent or desktopConfigs via shell is blocked outside projects/desktopConfigs";
	}

	return null;
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		let reason: string | null = null;

		if (event.toolName === "write" || event.toolName === "edit") {
			const targetPath = typeof event.input?.path === "string" ? event.input.path : "";
			reason = checkWriteTarget(targetPath, ctx.cwd);
		} else if (event.toolName === "bash") {
			const command = typeof event.input?.command === "string" ? event.input.command : "";
			reason = checkBashCommand(command, ctx.cwd);
		}

		if (reason) {
			if (ctx.hasUI) ctx.ui.notify(reason, "warning");
			return { block: true, reason };
		}
		return undefined;
	});
}
