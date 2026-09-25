import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

// Usa TypeScript já instalado e o runner nativo do Node, sem novo framework.
const frontend = fileURLToPath(new URL("../", import.meta.url));
const destino = mkdtempSync(join(tmpdir(), "undb-formulario-test-"));
try {
  const compilacao = spawnSync(process.execPath, [
    "node_modules/typescript/bin/tsc", "--outDir", destino,
    "--target", "ES2022", "--module", "commonjs", "--moduleResolution", "node",
    "--strict", "--skipLibCheck", "--esModuleInterop",
    "src/lib/avaliacao-formulario.ts", "src/lib/services/avaliacoes.ts", "src/lib/services/auth.ts",
  ], { cwd: frontend, stdio: "inherit" });
  if (compilacao.error) throw compilacao.error;
  if (compilacao.status !== 0) {
    process.exitCode = compilacao.status ?? 1;
  } else {
    const testes = spawnSync(process.execPath, ["--test", "tests/avaliacao.test.mjs"], {
      cwd: frontend,
      stdio: "inherit",
      env: { ...process.env, AVALIACAO_TEST_BUILD: destino },
    });
    if (testes.error) throw testes.error;
    process.exitCode = testes.status ?? 1;
  }
} finally {
  rmSync(destino, { recursive: true, force: true });
}
