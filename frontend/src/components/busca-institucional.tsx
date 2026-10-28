"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { comContextoBusca, ordenarResultados, ordemBusca, urlBusca, type TipoBusca } from "@/lib/contexto-busca";
import { listarProfessores } from "@/lib/services/professores";
import { buscarDisciplinas } from "@/lib/services/disciplinas";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "@/lib/types/institucional";
import ProfessorResultado from "@/app/professores/professor-resultado";

type Resultado = ProfessorDetalhe | DisciplinaDetalhe;
type Consulta = { termo: string; tentativa: number } & (
  | { estado: "sucesso"; resultados: Resultado[] }
  | { estado: "erro" }
);

export default function BuscaInstitucional({ tipo }: { tipo: TipoBusca }) {
  const parametros = useSearchParams();
  const termo = parametros.get("q") ?? "";
  const ordem = ordemBusca(parametros.get("ordem"));
  const contexto = { tipo, termo, ordem };
  const termoBuscado = useDebouncedValue(termo.trim(), 300);
  const [tentativa, setTentativa] = useState(0);
  const [consulta, setConsulta] = useState<Consulta | null>(null);
  const professor = tipo === "professores";
  const buscaValida = termo.trim().length >= 2;
  const atual = termo.trim() === termoBuscado && consulta?.termo === termoBuscado && consulta.tentativa === tentativa;
  const carregando = buscaValida && !atual;
  const erro = atual && consulta.estado === "erro";
  const resultados = atual && consulta.estado === "sucesso" ? ordenarResultados(consulta.resultados, ordem) : [];

  useEffect(() => {
    if (termoBuscado.length < 2) return;
    let cancelado = false;
    const buscar = tipo === "professores" ? listarProfessores : buscarDisciplinas;
    buscar(termoBuscado)
      .then((resultados) => {
        if (!cancelado) setConsulta({ termo: termoBuscado, tentativa, estado: "sucesso", resultados });
      })
      .catch(() => {
        if (!cancelado) setConsulta({ termo: termoBuscado, tentativa, estado: "erro" });
      });
    return () => { cancelado = true; };
  }, [termoBuscado, tentativa, tipo]);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold">Buscar {professor ? "professor" : "disciplina"}</h1>
        <p className="mt-1 text-sm text-foreground/70">
          {professor ? "Digite o nome, completo ou parcial — acentos e maiúsculas não importam." : "Digite o nome ou o código — ex.: algoritmos ou CIC0004."}
          {" "}A consulta é pública e abrange todas as unidades acadêmicas.
        </p>
      </div>

      <nav aria-label="Tipo de busca" className="flex flex-wrap gap-4 text-sm text-accent">
        <Link href="/professores" aria-current={professor ? "page" : undefined}>Por professor</Link>
        <Link href="/disciplinas" aria-current={!professor ? "page" : undefined}>Por disciplina</Link>
      </nav>

      <label className="flex flex-col gap-2">
        <span className="text-sm font-medium">{professor ? "Nome do professor" : "Nome ou código da disciplina"}</span>
        <input
          type="search"
          value={termo}
          onChange={(evento) => window.history.replaceState(null, "", urlBusca({ ...contexto, termo: evento.target.value }))}
          placeholder={professor ? "Ex.: maria emilia" : "Ex.: fundamentos"}
          className="min-w-0 rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base outline-none focus:border-foreground/50"
        />
      </label>

      <section aria-label="Resultados da busca" className="flex flex-col gap-4">
        <label className="flex min-w-0 flex-col gap-2">
          <span className="text-sm font-medium">Ordenar resultados</span>
          <select
            value={ordem}
            aria-describedby="unidade-ajuda"
            onChange={(evento) => window.history.pushState(null, "", urlBusca({ ...contexto, ordem: ordemBusca(evento.target.value) }))}
            className="w-full min-w-0 rounded-lg border border-foreground/20 bg-background px-3 py-2.5 text-sm"
          >
            <option value="nome">Nome do professor/da disciplina (A–Z)</option>
            <option value="unidade">Unidade acadêmica (A–Z)</option>
          </select>
        </label>
        <p id="unidade-ajuda" className="text-sm text-foreground/70">
          Unidade acadêmica pode ser departamento, instituto ou faculdade, conforme o cadastro institucional.
        </p>
        <div aria-live="polite" aria-atomic="true" aria-busy={carregando}>
          {!buscaValida && <p className="text-sm text-foreground/70">{termo.trim() ? "Continue digitando…" : "Digite ao menos 2 letras para começar."}</p>}
          {carregando && <p className="text-sm text-foreground/70">Buscando…</p>}
          {buscaValida && erro && (
            <div className="flex flex-col items-start gap-3">
              <p role="alert" className="text-sm text-red-600 dark:text-red-400">Não foi possível buscar {tipo} agora. Verifique sua conexão e tente novamente.</p>
              <button type="button" onClick={() => setTentativa((valor) => valor + 1)} className="rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium">Tentar novamente</button>
            </div>
          )}
          {buscaValida && atual && !erro && (
            <p className="text-sm text-foreground/70">
              {resultados.length ? `${resultados.length} resultado(s) para “${termoBuscado}”.` : `Nenhum resultado para “${termoBuscado}”. Confira ${professor ? "a grafia ou tente um nome mais curto" : "o nome ou o código"}.`}
            </p>
          )}
        </div>
        {buscaValida && atual && !erro && resultados.length > 0 && (
          <ul className="flex flex-col gap-2">
            {resultados.map((resultado) => (
              "codigo" in resultado ? <li key={resultado.id}>
                <Link href={comContextoBusca(`/${tipo}/${resultado.id}`, contexto)} className="block break-words rounded-lg border border-foreground/10 px-4 py-3 transition hover:border-foreground/30 hover:bg-foreground/[0.03]">
                  <span className="block font-medium">{resultado.nome}</span>
                  <span className="block font-mono text-xs text-foreground/60">Código da disciplina: {resultado.codigo}</span>
                  <span className="block text-sm text-foreground/70">Unidade acadêmica: {resultado.departamento}</span>
                </Link>
              </li> : <ProfessorResultado key={resultado.id} professor={resultado} contexto={contexto} />
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
