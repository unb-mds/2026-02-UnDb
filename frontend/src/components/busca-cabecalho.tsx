"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { ordemBusca } from "@/lib/contexto-busca";
import BuscaNavegacao from "./busca-navegacao";

export default function BuscaCabecalho() {
  const caminho = usePathname();
  const parametros = useSearchParams();
  const tipo = parametros.get("busca") === "professores"
    || (!parametros.has("busca") && caminho.startsWith("/professores")) ? "professores" : "disciplinas";
  const termo = parametros.get("q") ?? "";
  const ordem = ordemBusca(parametros.get("ordem"));
  return <BuscaNavegacao key={`${tipo}:${termo}:${ordem}`} id="cabecalho" tipo={tipo} termo={termo} ordem={ordem} compacta />;
}
