import Link from "next/link";
import { listarDisciplinas } from "@/lib/services/disciplinas";
export const dynamic = "force-dynamic";

export default async function Departamentos({ searchParams }: { searchParams: Promise<{ unidade?: string }> }) {
  const { unidade } = await searchParams;
  const disciplinas = await listarDisciplinas().catch(() => null);
  if (!disciplinas) return <main className="container page-content"><h1>Unidades acadêmicas</h1><p>Não foi possível carregar o catálogo agora.</p><Link href="/disciplinas" className="text-link">Tentar pela busca →</Link></main>;
  const unidades = [...new Set(disciplinas.map(d => d.departamento))].sort((a,b) => a.localeCompare(b,"pt-BR"));
  const itens = unidade ? disciplinas.filter(d => d.departamento === unidade) : disciplinas;
  return <main className="container page-content"><Link href="/" className="text-link">← Voltar ao início</Link><h1>Explore qualquer unidade acadêmica</h1><p>Departamento, instituto ou faculdade, conforme o cadastro institucional. A consulta é pública.</p>
    <nav className="department-chips" aria-label="Unidades acadêmicas"><Link href="/departamentos" className={`chip ${!unidade ? "active" : ""}`}>Todas</Link>{unidades.map(u => <Link className={`chip ${unidade === u ? "active" : ""}`} href={`/departamentos?unidade=${encodeURIComponent(u)}`} key={u}>{u}</Link>)}</nav>
    <div className="subject-grid">{itens.map(d => <Link className="panel subject-card" href={`/disciplinas/${d.id}`} key={d.id}><span className="code">{d.codigo}</span><h2>{d.nome}</h2><p>Unidade acadêmica: {d.departamento}</p><span className="text-link">Comparar professores →</span></Link>)}</div>{!itens.length && <p>Nenhuma disciplina encontrada nesta unidade.</p>}
  </main>;
}
