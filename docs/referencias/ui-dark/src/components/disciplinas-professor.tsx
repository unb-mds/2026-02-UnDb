import Link from "next/link";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";

export default function DisciplinasProfessor({ professorId, disciplinas, contexto = null }: {
  professorId: string; disciplinas: DisciplinaDetalhe[]; contexto?: ContextoBusca | null;
}) {
  if (!disciplinas.length) return <p className="muted">Nenhuma turma ativa registrada para este professor no momento.</p>;
  return <ul className="professor-subjects">{disciplinas.map(d => {
    const consulta = comContextoBusca(`/professores/${professorId}/disciplinas/${d.id}`, contexto);
    return <li key={d.id} className="professor-subject"><div><span className="code subject-code">{d.codigo}</span><Link className="subject-name" href={consulta}>{d.nome}</Link><p>{d.departamento}</p></div><div className="subject-actions"><Link href={consulta} className="button">Consultar</Link><Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${d.id}/avaliar`, contexto)} className="button primary">Avaliar</Link><Link className="text-link" href={comContextoBusca(`/disciplinas/${d.id}`, contexto)}>Comparar professores →</Link></div></li>;
  })}</ul>;
}
