"use client";

import { useEffect, useState } from "react";
import { listarDisciplinas } from "../services/disciplinas";
import type { DisciplinaDetalhe } from "../types/institucional";

type ConsultaCatalogo = { tentativa: number } & (
  | { estado: "sucesso"; disciplinas: DisciplinaDetalhe[] }
  | { estado: "erro" }
);

/** Catálogo público com nova tentativa, sem manter respostas de uma montagem anterior. */
export function useCatalogo() {
  const [tentativa, setTentativa] = useState(0);
  const [consulta, setConsulta] = useState<ConsultaCatalogo | null>(null);
  useEffect(() => {
    let cancelado = false;
    listarDisciplinas()
      .then((disciplinas) => {
        if (!cancelado) setConsulta({ tentativa, estado: "sucesso", disciplinas });
      })
      .catch(() => {
        if (!cancelado) setConsulta({ tentativa, estado: "erro" });
      });
    return () => { cancelado = true; };
  }, [tentativa]);
  return {
    consulta: consulta?.tentativa === tentativa ? consulta : null,
    tentarNovamente: () => setTentativa((valor) => valor + 1),
  };
}
