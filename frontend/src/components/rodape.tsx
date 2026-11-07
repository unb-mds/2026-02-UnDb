import Link from "next/link";

export default function Rodape() {
  return <footer className="footer"><div className="container footer-inner">
    <span>UnDb · Grupo 7 · UnB 2026/2</span>
    <nav aria-label="Navegação do rodapé"><Link href="/professores">Professores</Link><Link href="/disciplinas">Disciplinas</Link><Link href="/moderacao">Moderação</Link></nav>
    <span>Dados institucionais públicos do SIGAA</span>
  </div></footer>;
}
