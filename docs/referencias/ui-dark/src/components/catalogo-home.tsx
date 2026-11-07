import Link from "next/link";
import { listarDisciplinas } from "@/lib/services/disciplinas";

export default async function CatalogoHome() {
  const disciplinas = await listarDisciplinas().catch(() => null);
  if (!disciplinas) return <section className="panel empty-state"><h2>Catálogo temporariamente indisponível</h2><p>Não foi possível consultar as disciplinas agora. Você pode tentar novamente pela busca.</p><Link href="/disciplinas" className="button">Abrir busca</Link></section>;
  const unidades = [...new Set(disciplinas.map(d => d.departamento))].sort((a,b) => a.localeCompare(b, "pt-BR"));
  const codigos = ["FGA0312", "FGA0313", "FGA0158", "FGA0173", "CIC0002"];
  const destaques = codigos.flatMap(codigo => disciplinas.filter(d => d.codigo === codigo));
  return <><section><div className="section-heading"><h2>Explore as disciplinas</h2><Link className="text-link" href="/disciplinas">Buscar disciplina →</Link></div>
    <div className="subject-grid">{(destaques.length ? destaques : disciplinas.slice(0,5)).map(d => <Link className="panel subject-card" href={`/disciplinas/${d.id}`} key={d.id}><span className="code">{d.codigo}</span><h3>{d.nome}</h3><p>Unidade acadêmica: {d.departamento}</p><span className="badge blue">Comparar professores →</span></Link>)}</div>
    {!disciplinas.length && <p>Nenhuma disciplina cadastrada neste ambiente.</p>}
  </section><section className="section"><div className="section-heading"><h2>Explore qualquer unidade acadêmica</h2><Link className="text-link" href="/departamentos">Ver unidades →</Link></div><div className="department-chips">{unidades.map(unidade => <Link className="chip" href={`/departamentos?unidade=${encodeURIComponent(unidade)}`} key={unidade}>{unidade}</Link>)}</div></section></>;
}
