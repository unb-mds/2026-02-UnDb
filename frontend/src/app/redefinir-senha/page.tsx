import type { Metadata } from "next";
import RedefinicaoForm from "./redefinicao-form";

export const metadata: Metadata = { title: "Redefinir senha | UnDb", referrer: "no-referrer", robots: { index: false, follow: false } };

export default async function RedefinirSenhaPage({ searchParams }: PageProps<"/redefinir-senha">) {
  const parametros = await searchParams;
  const token = typeof parametros.token === "string" && parametros.token.length >= 32 && parametros.token.length <= 200 ? parametros.token : null;
  return <RedefinicaoForm token={token} />;
}
