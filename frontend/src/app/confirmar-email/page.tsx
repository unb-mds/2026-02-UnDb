import { ConfirmationClient } from "./confirmation-client";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";

export default async function ConfirmarEmailPage({
  searchParams,
}: PageProps<"/confirmar-email">) {
  const parametros = await searchParams;
  const token = typeof parametros.token === "string" ? parametros.token : undefined;
  const retorno = typeof parametros.returnTo === "string" ? parametros.returnTo : null;
  return <ConfirmationClient token={token} retorno={retornoAvaliacaoSeguro(retorno)} />;
}
