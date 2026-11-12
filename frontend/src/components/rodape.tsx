import Image from "next/image";
import Link from "next/link";

export default function Rodape() {
  return <footer className="footer"><div className="container footer-inner">
    <div className="footer-brand">
      <Image src="/brand/undb-logo.png" alt="UnDb" width={600} height={201} />
      <p>Um projeto acadêmico para decisões mais informadas na UnB.</p>
    </div>
    <nav aria-label="Navegação do rodapé"><Link href="/professores">Professores</Link><Link href="/disciplinas">Disciplinas</Link><Link href="/departamentos">Unidades acadêmicas</Link><Link href="/moderacao">Moderação</Link></nav>
    <p>UnDb · Grupo 7 · UnB 2026/2 · Dados institucionais públicos do SIGAA</p>
  </div></footer>;
}
