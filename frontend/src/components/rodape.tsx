import Image from "next/image";
import LinkModeracao from "./link-moderacao";
import Link from "next/link";

export default function Rodape() {
  return <footer className="footer"><div className="container footer-inner">
    <div className="footer-brand">
      <Image src="/brand/undb-logo.png" alt="UnDb" width={600} height={201} />
      <p>Experiências compartilhadas. Escolhas mais informadas.</p>
    </div>
    <nav aria-label="Navegação do rodapé"><Link href="/professores">Professores</Link><Link href="/disciplinas">Disciplinas</Link><Link href="/departamentos">Unidades acadêmicas</Link><Link href="/sobre">Sobre o UnDb</Link><LinkModeracao /></nav>
    <p>UnDb · Feito por estudantes para estudantes · Dados institucionais públicos do SIGAA</p>
  </div></footer>;
}
