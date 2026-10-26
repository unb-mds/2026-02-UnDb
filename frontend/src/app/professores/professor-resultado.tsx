"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import DisciplinasProfessor from "@/components/disciplinas-professor";
import { listarDisciplinasDoProfessor } from "@/lib/services/professores";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "@/lib/types/institucional";

type ConsultaDisciplinas =
  | { estado: "carregando" }
  | { estado: "sucesso"; disciplinas: DisciplinaDetalhe[] }
  | { estado: "erro" };

// O resultado é montado com key=professor.id, inclusive para nomes iguais.
export default function ProfessorResultado({ professor }: { professor: ProfessorDetalhe }) {
  const [consulta, setConsulta] = useState<ConsultaDisciplinas>({ estado: "carregando" });

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
  }, [professor.id]);

  return (
    <li className="min-w-0 rounded-lg border border-foreground/10 p-4 break-words">
      <h2 className="font-semibold">
        <Link href={`/professores/${professor.id}`} className="text-accent underline underline-offset-2 hover:text-foreground">
          {professor.nome}
        </Link>
      </h2>
      <p className="mt-1 text-sm text-foreground/70">Unidade acadêmica: {professor.departamento}</p>
      <h3 className="mt-4 text-sm font-medium text-foreground/70">Disciplinas lecionadas</h3>
      {consulta.estado === "carregando" && <p className="mt-2 text-sm text-foreground/60">Carregando disciplinas…</p>}
      {consulta.estado === "erro" && (
        <p className="mt-2 text-sm text-foreground/70" role="status">
          Não foi possível carregar as disciplinas deste professor. Tente abrir o perfil novamente em instantes.
        </p>
      )}
      {consulta.estado === "sucesso" && <DisciplinasProfessor professorId={professor.id} disciplinas={consulta.disciplinas} />}
    </li>
  );
}
