import BotaoBuscar from "./botao-buscar";
import Form from "next/form";
import type { OrdemBusca, TipoBusca } from "@/lib/contexto-busca";
import Icone from "./icone";

const TIPOS = [["disciplinas", "Disciplina", "book"], ["professores", "Professor", "user"]] as const;

/**
 * GET compartilhado: /busca mantém o contrato de redirecionamento existente.
 * `segmentada` troca o select por botões de opção (mesmo campo `busca`), como no destaque da home.
 */
export default function BuscaNavegacao({ id, tipo = "disciplinas", termo = "", ordem = "nome", compacta = false, segmentada = false }: {
  id: string;
  tipo?: TipoBusca;
  termo?: string;
  ordem?: OrdemBusca;
  compacta?: boolean;
  segmentada?: boolean;
}) {
  return <Form action="/busca" role="search" aria-label={compacta ? "Busca no cabeçalho" : "Busca de professores e disciplinas"}
    className={`search${compacta ? " search-header" : ""}${segmentada ? " search-hero" : ""}`}>
    {segmentada ? <fieldset className="segmented">
      <legend className="sr-only">Buscar por</legend>
      {TIPOS.map(([valor, rotulo, icone]) => <label key={valor}>
        <input type="radio" name="busca" value={valor} defaultChecked={tipo === valor} />
        <span><Icone nome={icone} pequeno />{rotulo}</span>
      </label>)}
    </fieldset> : <>
      <label className="sr-only" htmlFor={`${id}-tipo`}>Buscar por</label>
      <select name="busca" id={`${id}-tipo`} defaultValue={tipo}>
        <option value="disciplinas">Disciplina</option><option value="professores">Professor</option>
      </select>
    </>}
    <div className="search-field">
      <Icone nome="search" pequeno={compacta} />
      <label className="sr-only" htmlFor={`${id}-termo`}>Buscar professor, disciplina ou código</label>
      <input type="search" name="q" id={`${id}-termo`} required minLength={2} defaultValue={termo}
        placeholder={compacta ? "Professor, disciplina ou código" : "Ex.: Cálculo 1, MAT0025 ou nome do professor"} />
    </div>
    <input type="hidden" name="ordem" value={ordem} />
    <BotaoBuscar compacto={compacta} />
  </Form>;
}
