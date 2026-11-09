"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { ordenarResultados, ordemBusca, urlBusca, type TipoBusca } from "@/lib/contexto-busca";
import { listarProfessores } from "@/lib/services/professores";
import { buscarDisciplinas } from "@/lib/services/disciplinas";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "@/lib/types/institucional";
import ProfessorResultado from "@/app/professores/professor-resultado";
import Caminho from "@/components/caminho";
import DisciplinaCatalogo from "./disciplina-catalogo";

type Resultado = ProfessorDetalhe | DisciplinaDetalhe;
type Consulta = { tipo: TipoBusca; termo: string; tentativa: number } & (
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
  const atual = termo.trim() === termoBuscado && consulta?.tipo === tipo && consulta.termo === termoBuscado && consulta.tentativa === tentativa;
  const carregando = buscaValida && !atual;
  const erro = atual && consulta.estado === "erro";
  const resultados = atual && consulta.estado === "sucesso" ? ordenarResultados(consulta.resultados, ordem) : [];

  useEffect(() => {
    if (termoBuscado.length < 2) return;
    let cancelado = false;
    const buscar = tipo === "professores" ? listarProfessores : buscarDisciplinas;
    buscar(termoBuscado)
      .then((resultados) => {
        if (!cancelado) setConsulta({ tipo, termo: termoBuscado, tentativa, estado: "sucesso", resultados });
      })
      .catch(() => {
        if (!cancelado) setConsulta({ tipo, termo: termoBuscado, tentativa, estado: "erro" });
      });
    return () => { cancelado = true; };
  }, [termoBuscado, tentativa, tipo]);

  return (
    <main className="container flex flex-1 flex-col gap-8 py-8 sm:py-12">
      <Caminho itens={[{ nome: "Início", href: "/" }, { nome: professor ? "Professores" : "Disciplinas" }]} />
      <div className="flex w-full flex-col gap-6">
        <div>
          <h1 className="text-3xl font-semibold">{buscaValida ? `Resultados para “${termo}”` : `Buscar ${professor ? "professor" : "disciplina"}`}</h1>
          <p className="mt-3 text-sm text-(--muted)">
            {professor ? "Digite o nome, completo ou parcial — acentos e maiúsculas não importam." : "Digite o nome ou o código — ex.: algoritmos ou CIC0004."}
            {" "}A consulta é pública e abrange todas as unidades acadêmicas.
          </p>
        </div>

        <label className="flex max-w-2xl flex-col gap-2">
          <span className="text-sm font-medium">{professor ? "Nome do professor" : "Nome ou código da disciplina"}</span>
          <input
            type="search"
            value={termo}
            onChange={(evento) => window.history.replaceState(null, "", urlBusca({ ...contexto, termo: evento.target.value }))}
            placeholder={professor ? "Ex.: maria emilia" : "Ex.: fundamentos"}
            className="min-w-0 rounded-xl border border-(--border) bg-(--raised) px-4 py-3 text-base"
          />
        </label>
      </div>

      <section aria-label="Resultados da busca" className="flex flex-col gap-4">
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-(--border) pb-4">
          <nav aria-label="Tipo de busca" className="flex flex-wrap gap-2 text-sm text-(--muted)">
            <Link href={urlBusca({ ...contexto, tipo: "professores" })} aria-current={professor ? "page" : undefined} className="border-b-2 border-transparent px-3 py-3 hover:text-foreground aria-[current=page]:border-accent aria-[current=page]:text-foreground">Professores</Link>
            <Link href={urlBusca({ ...contexto, tipo: "disciplinas" })} aria-current={!professor ? "page" : undefined} className="border-b-2 border-transparent px-3 py-3 hover:text-foreground aria-[current=page]:border-accent aria-[current=page]:text-foreground">Disciplinas</Link>
          </nav>
        <label className="flex w-full min-w-0 flex-col gap-2 sm:w-auto">
          <span className="text-sm font-medium">Ordenar resultados</span>
          <select
            value={ordem}
            aria-describedby="unidade-ajuda"
            onChange={(evento) => window.history.pushState(null, "", urlBusca({ ...contexto, ordem: ordemBusca(evento.target.value) }))}
            className="w-full min-w-0 rounded-lg border border-(--border) bg-(--raised) px-3 py-3 text-sm"
          >
            <option value="nome">Nome do professor/da disciplina (A–Z)</option>
            <option value="unidade">Unidade acadêmica (A–Z)</option>
          </select>
        </label>
        </div>
        <p id="unidade-ajuda" className="text-sm text-(--muted)">
          Unidade acadêmica pode ser departamento, instituto ou faculdade, conforme o cadastro institucional.
        </p>
        <div aria-live="polite" aria-atomic="true" aria-busy={carregando}>
          {!buscaValida && <p className="text-sm text-foreground/70">{termo.trim() ? "Continue digitando…" : "Digite ao menos 2 letras para começar."}</p>}
          {carregando && <p className="text-sm text-foreground/70">Buscando…</p>}
          {buscaValida && erro && (
            <div className="flex flex-col items-start gap-3 rounded-2xl border border-(--border) bg-(--panel) p-6">
              <p role="alert" className="text-sm">Não foi possível buscar {tipo} agora. Verifique sua conexão e tente novamente.</p>
              <button type="button" onClick={() => setTentativa((valor) => valor + 1)} className="button">Tentar novamente</button>
            </div>
          )}
          {buscaValida && atual && !erro && (
            <p className="text-sm text-foreground/70">
              {resultados.length ? `${resultados.length} resultado(s) para “${termoBuscado}”.` : `Nenhum resultado para “${termoBuscado}”. Confira ${professor ? "a grafia ou tente um nome mais curto" : "o nome ou o código"}.`}
            </p>
          )}
        </div>
        {buscaValida && atual && !erro && resultados.length > 0 && (
          <>
            <p className="text-sm text-foreground/70">{professor ? "As disciplinas estão agrupadas por professor. Confira a unidade acadêmica antes de escolher." : "Escolha uma disciplina para comparar professores ou chegar à avaliação."}</p>
            <ul className={`grid gap-4 ${professor ? "" : "sm:grid-cols-2 lg:grid-cols-3"}`} aria-label="Lista de resultados">
              {resultados.map((resultado) => (
                "codigo" in resultado ? <DisciplinaCatalogo key={resultado.id} disciplina={resultado} contexto={contexto} />
                  : <ProfessorResultado key={resultado.id} professor={resultado} contexto={contexto} />
              ))}
            </ul>
          </>
        )}
      </section>
    </main>
  );
}
