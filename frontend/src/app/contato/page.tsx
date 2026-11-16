import CanalTitulares from "./canal";
export const metadata = { title: "Contato e solicitações — UnDb", robots: { index: false, follow: false }, referrer: "no-referrer" as const };
export default function Pagina() {
  return <main className="container flex flex-1 flex-col gap-6 py-12">
    <h1 className="page-title">Contato e solicitações</h1>
    <p className="lead">Informe erros, conteste conteúdo ou solicite atendimento sobre seus dados. Não é necessário ter conta estudantil.</p>
    <p>Uma única solicitação fundamentada é suficiente para análise. Discordância com uma avaliação não provoca remoção automática. Preserve a identidade dos estudantes e envie somente informações necessárias.</p>
    <CanalTitulares />
  </main>;
}
