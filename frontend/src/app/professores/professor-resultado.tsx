"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import DisciplinasProfessor from "@/components/disciplinas-professor";
import { listarDisciplinasDoProfessor } from "@/lib/services/professores";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "@/lib/types/institucional";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";

type ConsultaDisciplinas =
  | { estado: "carregando" }
  | { estado: "sucesso"; disciplinas: DisciplinaDetalhe[] }
  | { estado: "erro" };

// O resultado é montado com key=professor.id, inclusive para nomes iguais.
export default function ProfessorResultado({ professor, contexto = null }: { professor: ProfessorDetalhe; contexto?: ContextoBusca | null }) {
  const [consulta, setConsulta] = useState<ConsultaDisciplinas>({ estado: "carregando" });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let cancelado = false;
    listarDisciplinasDoProfessor(professor.id)
      .then((disciplinas) => {
        if (!cancelado) setConsulta({ estado: "sucesso", disciplinas });
      })
      .catch(() => {
        if (!cancelado) setConsulta({ estado: "erro" });
      });
    return () => { cancelado = true; };
  }, [professor.id, tentativa]);

  function tentarNovamente() {
    setConsulta({ estado: "carregando" });
    setTentativa((valor) => valor + 1);
  }

  const iniciais = professor.nome.split(/\s+/).filter(Boolean).slice(0, 2).map((parte) => parte[0]).join("");

  return (
    <li className="min-w-0 rounded-2xl border border-(--border) bg-(--panel) p-5 break-words sm:p-6">
      <div className="flex items-start gap-4">
        <span aria-hidden="true" className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-(--primary)/20 text-sm font-bold text-accent">{iniciais}</span>
        <div className="min-w-0">
          <h2 className="text-xl font-semibold">
            <Link href={comContextoBusca(`/professores/${professor.id}`, contexto)} className="hover:text-accent">
              {professor.nome}
            </Link>
          </h2>
          <p className="mt-2 text-sm text-(--muted)">Unidade acadêmica: {professor.departamento}</p>
        </div>
      </div>
      <h3 className="mt-6 text-xs font-medium tracking-wide text-(--muted) uppercase">Disciplinas lecionadas</h3>
      {consulta.estado === "carregando" && <p role="status" className="mt-2 text-sm text-(--muted)">Carregando disciplinas…</p>}
      {consulta.estado === "erro" && (
        <div className="mt-3 flex flex-col items-start gap-3">
          <p className="text-sm" role="alert">Não foi possível carregar as disciplinas deste professor.</p>
          <button type="button" onClick={tentarNovamente} className="button" aria-label={`Tentar novamente disciplinas de ${professor.nome}`}>Tentar novamente</button>
        </div>
      )}
      {consulta.estado === "sucesso" && <DisciplinasProfessor professorId={professor.id} disciplinas={consulta.disciplinas} contexto={contexto} />}
    </li>
  );
}
