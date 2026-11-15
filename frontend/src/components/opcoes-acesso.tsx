import Link from "next/link";

export default function OpcoesAcesso({ atual, retorno }: { atual: "login" | "cadastro"; retorno: string | null }) {
  const query = retorno ? `?returnTo=${encodeURIComponent(retorno)}` : "";
  return <nav aria-label="Opções de acesso" className="grid min-w-0 grid-cols-2 gap-1 rounded-xl bg-(--panel) p-1">
    {(["login", "cadastro"] as const).map((rota) => <Link key={rota} href={`/${rota}${query}`} aria-current={atual === rota ? "page" : undefined}
      className={`inline-flex min-h-11 items-center justify-center rounded-lg border px-2 py-2 text-sm font-medium transition-colors ${atual === rota ? "border-(--border-strong) bg-(--surface-accent) text-foreground" : "border-transparent text-(--muted) hover:bg-(--raised) hover:text-foreground"}`}>
      {rota === "login" ? "Entrar" : "Criar conta"}
    </Link>)}
  </nav>;
}
