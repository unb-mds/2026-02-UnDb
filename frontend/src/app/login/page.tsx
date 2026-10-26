import LoginForm from "./login-form";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";

export default async function LoginPage({
  searchParams,
}: PageProps<"/login">) {
  const parametros = await searchParams;
  const valor = typeof parametros.returnTo === "string" ? parametros.returnTo : null;
  return <LoginForm retorno={retornoAvaliacaoSeguro(valor)} />;
}
