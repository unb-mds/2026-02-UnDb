import Link from "next/link";

export default function OpcoesAcesso({ atual, retorno }: { atual: "login" | "cadastro"; retorno: string | null }) {
  const query = retorno ? `?returnTo=${encodeURIComponent(retorno)}` : "";
  return <nav aria-label="Opções de acesso" className="flex flex-wrap gap-2">
    {(["login", "cadastro"] as const).map((rota) => <Link key={rota} href={`/${rota}${query}`} aria-current={atual === rota ? "page" : undefined}
      className={atual === rota ? "rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-on-accent" : "rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium hover:bg-foreground/[0.03]"}>
      {rota === "login" ? "Entrar" : "Criar conta"}
    </Link>)}
  </nav>;
}
