import { spawn } from "node:child_process";
import { cp, mkdir, stat } from "node:fs/promises";
import { resolve } from "node:path";

const projectRoot = process.cwd();
const standaloneRoot = resolve(projectRoot, ".next", "standalone");
const standaloneServer = resolve(standaloneRoot, "server.js");
const staticSource = resolve(projectRoot, ".next", "static");
const staticDestination = resolve(standaloneRoot, ".next", "static");
const publicSource = resolve(projectRoot, "public");
const publicDestination = resolve(standaloneRoot, "public");

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

if (!(await exists(standaloneServer))) {
  throw new Error("A standalone production build is required. Run `corepack pnpm build` first.");
}

await mkdir(resolve(standaloneRoot, ".next"), { recursive: true });
await cp(staticSource, staticDestination, { force: true, recursive: true });
if (await exists(publicSource)) {
  await cp(publicSource, publicDestination, { force: true, recursive: true });
}

const server = spawn(process.execPath, [standaloneServer], {
  cwd: standaloneRoot,
  env: process.env,
  stdio: "inherit",
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => server.kill(signal));
}

server.on("exit", (code, signal) => {
  if (signal !== null) process.exitCode = 1;
  else process.exitCode = code ?? 1;
});
