"use client";

import { nomeUnidade } from "@/lib/unidade";

import Link from "next/link";
import { iniciaisProfessor } from "@/lib/iniciais";
import { useEffect, useState } from "react";
import Icone from "@/components/icone";
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


  return (
    <li className="destaque h-full min-w-0 break-words">
      <Link href={comContextoBusca(`/professores/${professor.id}`, contexto)} className="destaque-visual professor-visual" aria-label={`Ver perfil de ${professor.nome}`}>
        <span className="avatar-initials large rounded-2xl!" aria-hidden="true">{iniciaisProfessor(professor.nome)}</span>
        <span className="text-xs font-medium tracking-widest text-(--ink-soft) uppercase">Professor</span>
        <span className="destaque-notch" aria-hidden="true"><span className="destaque-arrow"><span className="inline-flex -rotate-45"><Icone nome="arrow-right" /></span></span></span>
      </Link>
      <div className="px-3">
        <h2 className="text-xl leading-tight font-semibold tracking-tight">
          <Link href={comContextoBusca(`/professores/${professor.id}`, contexto)} className="hover:text-accent">{professor.nome}</Link>
        </h2>
        <p className="mt-3 text-sm text-(--muted)">Unidade acadêmica: {nomeUnidade(professor)}</p>
      <h3 className="label-mono mt-6 normal-case!">Disciplinas lecionadas</h3>
      {consulta.estado === "carregando" && <p role="status" className="mt-2 text-sm text-(--muted)">Carregando disciplinas…</p>}
      {consulta.estado === "erro" && (
        <div className="mt-3 flex flex-col items-start gap-3">
          <p className="text-sm" role="alert">Não foi possível carregar as disciplinas deste professor.</p>
          <button type="button" onClick={tentarNovamente} className="button" aria-label={`Tentar novamente disciplinas de ${professor.nome}`}>Tentar novamente</button>
        </div>
      )}
      {consulta.estado === "sucesso" && <DisciplinasProfessor professorId={professor.id} disciplinas={consulta.disciplinas} contexto={contexto} compacta />}
      </div>
    </li>
  );
}
