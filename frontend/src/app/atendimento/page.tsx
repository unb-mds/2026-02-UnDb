import FilaAtendimento from "./fila";
export const metadata = { title: "Atendimento restrito — UnDb", robots: { index: false, follow: false }, referrer: "no-referrer" as const };
export default function Pagina() {
  return <main className="container flex flex-1 flex-col gap-6 py-12"><h1 className="page-title">Atendimento restrito</h1><p>Solicitações de titulares e contestações. Acesso exclusivo às contas autorizadas.</p><FilaAtendimento /></main>;
}
