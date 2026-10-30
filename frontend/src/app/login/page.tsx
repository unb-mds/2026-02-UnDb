import LoginForm from "./login-form";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import DestinoAvaliacao from "@/components/destino-avaliacao";
import { Suspense } from "react";

export default async function LoginPage({
  searchParams,
}: PageProps<"/login">) {
  const parametros = await searchParams;
  const valor = typeof parametros.returnTo === "string" ? parametros.returnTo : null;
  const retorno = retornoAvaliacaoSeguro(valor);
  return <LoginForm retorno={retorno} contexto={<Suspense fallback={<p role="status">Carregando destino da avaliação…</p>}><DestinoAvaliacao retorno={retorno} /></Suspense>} />;
}
