import { cache } from "react";
import { notFound } from "next/navigation";
import { identificadorValido } from "./identificador";
import { ApiError } from "./services/http-error";
import { obterProfessor, listarProfessores } from "./services/professores";
import { obterDisciplina, listarDisciplinas } from "./services/disciplinas";
import { consultarAvaliacaoAgregada } from "./services/avaliacoes";

function verificarId(id: string) { if (!identificadorValido(id)) notFound(); }
function tratarErro(erro: unknown): never {
  if (erro instanceof ApiError && erro.naoEncontrado) notFound();
  throw erro;
}
// cache do React é por renderização: metadados e página compartilham a consulta,
// sem cache compartilhado de sessão ou de respostas de estudantes.
export const professorPublico = cache(async (id: string) => {
  verificarId(id); return obterProfessor(id).catch(tratarErro);
});
export const disciplinaPublica = cache(async (id: string) => {
  verificarId(id); return obterDisciplina(id).catch(tratarErro);
});
export const avaliacaoPublica = cache(async (id: string, disciplinaId: string) => {
  verificarId(id); verificarId(disciplinaId);
  return consultarAvaliacaoAgregada(id, disciplinaId).catch(tratarErro);
});
export const catalogoPublico = cache(async (tipo: "professores" | "disciplinas") => {
  const itens = tipo === "professores" ? await listarProfessores() : await listarDisciplinas();
  return itens.filter(item => identificadorValido(item.id)).sort((a, b) => a.id.localeCompare(b.id));
});
