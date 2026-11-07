import Form from "next/form";
import type { OrdemBusca, TipoBusca } from "@/lib/contexto-busca";

/** GET compartilhado: /busca mantém o contrato de redirecionamento existente. */
export default function BuscaNavegacao({ id, tipo = "disciplinas", termo = "", ordem = "nome", compacta = false }: {
  id: string;
  tipo?: TipoBusca;
  termo?: string;
  ordem?: OrdemBusca;
  compacta?: boolean;
}) {
  return <Form action="/busca" role="search" aria-label={compacta ? "Busca no cabeçalho" : "Busca de professores e disciplinas"}
    className={`search${compacta ? " search-header" : ""}`}>
    <label className="sr-only" htmlFor={`${id}-tipo`}>Buscar por</label>
    <select name="busca" id={`${id}-tipo`} defaultValue={tipo}>
      <option value="disciplinas">Disciplina</option><option value="professores">Professor</option>
    </select>
    <div className="search-field">
      <span className="search-icon" aria-hidden="true" />
      <label className="sr-only" htmlFor={`${id}-termo`}>Buscar professor, disciplina ou código</label>
      <input type="search" name="q" id={`${id}-termo`} required minLength={2} defaultValue={termo}
        placeholder="Buscar professor, disciplina ou código" />
    </div>
    <input type="hidden" name="ordem" value={ordem} />
    <button type="submit" className="button primary">Buscar</button>
  </Form>;
}
