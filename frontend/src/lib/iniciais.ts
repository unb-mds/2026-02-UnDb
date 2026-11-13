/** Iniciais exibidas no avatar decorativo do professor; ignora o prefixo dos dados de demonstração. */
export function iniciaisProfessor(nome: string) {
  return nome.replace(/^DEMO - /, "").split(/\s+/).filter(Boolean).slice(0, 2).map((parte) => parte[0]).join("").toUpperCase() || "PR";
}
