import { redirect } from "next/navigation";
import { ordemBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";

export default async function EncaminharBuscaPage({ searchParams }: {
  searchParams: Promise<ParametrosBusca>;
}) {
  const parametros = await searchParams;
  // O formulário HTML também envia a modalidade antes de carregar o JavaScript.
  redirect(urlBusca({
    tipo: parametros.busca === "professores" ? "professores" : "disciplinas",
    termo: typeof parametros.q === "string" ? parametros.q : "",
    ordem: ordemBusca(parametros.ordem),
  }));
}
