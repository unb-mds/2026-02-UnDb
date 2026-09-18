"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { listarProfessores } from "@/lib/services/professores";
import type { ProfessorDetalhe } from "@/lib/types/institucional";

const TAMANHO_MINIMO_BUSCA = 2;

export default function BuscaProfessoresPage() {
  const [termo, setTermo] = useState("");
  const termoBuscado = useDebouncedValue(termo.trim(), 300);

  const [resultados, setResultados] = useState<ProfessorDetalhe[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const buscaValida = termoBuscado.length >= TAMANHO_MINIMO_BUSCA;

  useEffect(() => {
    if (!buscaValida) return;

    let cancelado = false;
    /* eslint-disable-next-line react-hooks/set-state-in-effect --
       busca com debounce: sem lib de data-fetching no projeto ainda,
       este é o padrão de fetch-on-effect, não um loop de estado. */
    setCarregando(true);
    setErro(null);

    listarProfessores(termoBuscado)
      .then((professores) => {
        if (!cancelado) setResultados(professores);
      })
      .catch(() => {
        if (!cancelado) {
          setResultados([]);
          setErro("Não foi possível buscar professores agora. Tente novamente em instantes.");
        }
      })
      .finally(() => {
        if (!cancelado) setCarregando(false);
      });

    return () => {
      cancelado = true;
    };
  }, [termoBuscado, buscaValida]);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold">Buscar professor</h1>
        <p className="mt-1 text-sm text-foreground/70">
          Digite o nome, completo ou parcial — acentos e maiúsculas não importam.
        </p>
      </div>

      <label className="flex flex-col gap-2">
        <span className="sr-only">Nome do professor</span>
        <input
          type="search"
          value={termo}
          onChange={(evento) => setTermo(evento.target.value)}
          placeholder="Ex.: maria emilia"
          autoFocus
          className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base outline-none focus:border-foreground/50"
        />
      </label>

      <div aria-live="polite">
        {termo.trim().length === 0 && (
          <p className="text-sm text-foreground/60">Digite ao menos {TAMANHO_MINIMO_BUSCA} letras para começar.</p>
        )}

        {termo.trim().length > 0 && termo.trim().length < TAMANHO_MINIMO_BUSCA && (
          <p className="text-sm text-foreground/60">Continue digitando…</p>
        )}

        {buscaValida && carregando && <p className="text-sm text-foreground/60">Buscando…</p>}

        {buscaValida && erro && <p className="text-sm text-red-600 dark:text-red-400">{erro}</p>}

        {buscaValida && !carregando && !erro && resultados.length === 0 && (
          <p className="text-sm text-foreground/60">
            Nenhum professor encontrado para &quot;{termoBuscado}&quot;. Confira a grafia ou tente um nome mais
            curto.
          </p>
        )}

        {buscaValida && !carregando && !erro && resultados.length > 0 && (
          <ul className="flex flex-col gap-2">
            {resultados.map((professor) => (
              <li key={professor.id}>
                <Link
                  href={`/professores/${professor.id}`}
                  className="block rounded-lg border border-foreground/10 px-4 py-3 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
                >
                  <span className="font-medium">{professor.nome}</span>
                  <span className="block text-sm text-foreground/60">{professor.departamento}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
