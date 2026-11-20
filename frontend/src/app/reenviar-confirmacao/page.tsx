import ReenvioForm from "./reenvio-form";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";

export const metadata = { title: "Reenviar confirmação | UnDb", robots: { index: false, follow: false } };

export default async function Page({ searchParams }: PageProps<"/reenviar-confirmacao">) {
  const parametros = await searchParams;
  const retorno = retornoAvaliacaoSeguro(typeof parametros.returnTo === "string" ? parametros.returnTo : null);
  return <ReenvioForm retorno={retorno} />;
}
