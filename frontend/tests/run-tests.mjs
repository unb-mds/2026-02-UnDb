import { mkdtempSync, rmSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const frontend = fileURLToPath(new URL("../", import.meta.url));
const medirCobertura = process.argv.includes("--coverage");

function executarNode(args, env = process.env) {
  const resultado = spawnSync(process.execPath, args, { cwd: frontend, stdio: "inherit", env });
  if (resultado.error) throw resultado.error;
  return resultado.status ?? 1;
}

function executarTestes() {
  const tipos = executarNode(["node_modules/next/dist/bin/next", "typegen"]);
  if (tipos !== 0) return tipos;

  const destino = mkdtempSync(join(frontend, ".test-build-"));
  const fontesCompiladas = join(destino, "src");
  try {
    const compilacao = executarNode([
      "node_modules/typescript/bin/tsc", "--project", "tests/tsconfig.json", "--outDir", fontesCompiladas,
    ]);
    if (compilacao !== 0) return compilacao;

    // c8 lê o JS e os sourcemaps antes que o finally remova a compilação.
    const comando = medirCobertura ? [
      "node_modules/c8/bin/c8.js", "--src", fontesCompiladas,
      "--temp-directory", join(destino, "v8"), process.execPath,
    ] : [];
    return executarNode([
      ...comando,
      "--test",
      "tests/avaliacao.test.mjs",
      "tests/busca.test.mjs",
      "tests/comentarios.test.mjs",
      "tests/moderacao.test.mjs",
      "tests/denuncia.test.mjs",
      "tests/browser-navigation.test.mjs",
    ], { ...process.env, AVALIACAO_TEST_BUILD: join(fontesCompiladas, "lib") });
  } finally {
    rmSync(destino, { recursive: true, force: true });
  }
}

process.exitCode = executarTestes();
