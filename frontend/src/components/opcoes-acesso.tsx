import Link from "next/link";

export default function OpcoesAcesso({ atual, retorno }: { atual: "login" | "cadastro"; retorno: string | null }) {
  const query = retorno ? `?returnTo=${encodeURIComponent(retorno)}` : "";
  return <nav aria-label="Opções de acesso" className="flex flex-wrap gap-2">
    {(["login", "cadastro"] as const).map((rota) => <Link key={rota} href={`/${rota}${query}`} aria-current={atual === rota ? "page" : undefined}
      className={atual === rota ? "button primary" : "button"}>
      {rota === "login" ? "Entrar" : "Criar conta"}
    </Link>)}
  </nav>;
}
