import CadastroForm from "./cadastro-form";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";

export default async function CadastroPage({
  searchParams,
}: PageProps<"/cadastro">) {
  const parametros = await searchParams;
  const valor = typeof parametros.returnTo === "string" ? parametros.returnTo : null;
  return <CadastroForm retorno={retornoAvaliacaoSeguro(valor)} />;
}
