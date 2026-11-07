import { ApiError } from "./services/http-error";
import type { AvaliacaoInput } from "./types/avaliacao";

export const criteriosAvaliacao = [
  { nome: "didatica", rotulo: "Didática", opcoes: [["1", "1"], ["2", "2"], ["3", "3"], ["4", "4"], ["5", "5"]] },
  { nome: "dificuldade", rotulo: "Dificuldade", opcoes: [["FACIL", "Fácil"], ["MEDIO", "Médio"], ["DIFICIL", "Difícil"]] },
  { nome: "chamada", rotulo: "Chamada", opcoes: [["true", "Sim"], ["false", "Não"]] },
  { nome: "material", rotulo: "Material", opcoes: [["NAO_DISPONIBILIZA", "Não disponibiliza"], ["RUIM", "Ruim"], ["MEDIO", "Médio"], ["BOM", "Bom"]] },
  { nome: "recomenda", rotulo: "Recomenda a matéria", opcoes: [["true", "Sim"], ["false", "Não"]] },
] as const;

export function criarEntradaAvaliacao(
  formulario: FormData,
  professorId: string,
  disciplinaId: string,
): AvaliacaoInput {
  for (const criterio of criteriosAvaliacao) {
    if (!criterio.opcoes.some(([valor]) => valor === formulario.get(criterio.nome))) {
      throw new Error(`Selecione uma opção válida para ${criterio.rotulo}.`);
    }
  }

  // Os valores foram verificados contra as escalas acima, inclusive false explícito.
  const material = formulario.get("material") as "NAO_DISPONIBILIZA" | "RUIM" | "MEDIO" | "BOM";
  return {
    professor_id: professorId,
    disciplina_id: disciplinaId,
    didatica: Number(formulario.get("didatica")),
    dificuldade: formulario.get("dificuldade") as AvaliacaoInput["dificuldade"],
    chamada: formulario.get("chamada") === "true",
    recomenda: formulario.get("recomenda") === "true",
    ...(material === "NAO_DISPONIBILIZA"
      ? { disponibiliza_material: false, qualidade_material: null } as const
      : { disponibiliza_material: true, qualidade_material: material } as const),
  };
}

const rotulosCampos: Record<string, string> = {
  professor_id: "Professor",
  disciplina_id: "Disciplina",
  didatica: "Didática",
  dificuldade: "Dificuldade",
  chamada: "Chamada",
  disponibiliza_material: "Material",
  qualidade_material: "Material",
  recomenda: "Recomenda a matéria",
};

export function mensagemErroAvaliacao(erro: unknown): string {
  if (!(erro instanceof ApiError)) {
    return "Não foi possível confirmar o envio. Verifique sua conexão e tente novamente. Suas respostas foram mantidas.";
  }

  if (erro.status === 404 && erro.message === "Not Found") {
    return "O envio de avaliações ainda não está disponível. Tente novamente mais tarde. Resposta do serviço: Not Found.";
  }

  if (erro.status === 422 && Array.isArray(erro.detalhes)) {
    const campos = new Set<string>();
    const detalhes: string[] = [];
    for (const item of erro.detalhes) {
      if (item && typeof item === "object") {
        const campo = Array.isArray(item.loc) ? item.loc.at(-1) : undefined;
        if (typeof campo === "string" && rotulosCampos[campo]) campos.add(rotulosCampos[campo]);
        if (typeof item.msg === "string") detalhes.push(item.msg);
      }
    }
    return [
      campos.size ? `Revise os campos: ${[...campos].join(", ")}.` : "Revise as opções da avaliação.",
      ...detalhes,
    ].join(" ");
  }

  const orientacoes: Record<number, string> = {
    401: "Sua sessão está ausente ou inválida. Entre na sua conta e volte a este formulário para enviar.",
    403: "O envio não foi autorizado. Se seu e-mail ainda não foi confirmado, use o link recebido no cadastro antes de tentar novamente.",
    404: "Não foi possível localizar o destino da avaliação. Volte à consulta e tente novamente mais tarde.",
    405: "O envio de avaliações ainda não está disponível. Tente novamente mais tarde.",
    422: "Revise as opções da avaliação antes de enviar novamente.",
    429: "Há muitas tentativas de envio. Aguarde um pouco antes de tentar novamente.",
  };
  const orientacao = orientacoes[erro.status] ?? (erro.status >= 500
    ? "O serviço não conseguiu confirmar o envio. Tente novamente mais tarde."
    : "A avaliação foi rejeitada.");
  return `${orientacao} ${erro.message}`;
}
