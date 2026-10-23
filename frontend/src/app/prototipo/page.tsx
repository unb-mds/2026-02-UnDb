import Link from "next/link";
import Form from "next/form";
import { apresentacoesDemo, comparacoesDemo, correspondeBusca, disciplinasDemo, professoresDemo } from "./dados";
import FormularioDemo from "./formulario-demo";
import AcessoDemo from "./acesso-demo";
import { AcessoParaAvaliar } from "./conta-demo";
import OrganizarResultadosDemo from "./organizar-resultados-demo";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import type { DisciplinaInstitucional, ProfessorInstitucional } from "@/lib/types/institucional";

const etapas = ["entrada", "busca", "resultados", "comparacao", "avaliacao", "acesso"] as const;
type Etapa = typeof etapas[number];
const titulos: Record<Etapa, string> = {
  entrada: "Encontre professores e disciplinas",
  busca: "O que você quer encontrar?",
  resultados: "Resultados da busca",
  comparacao: "Comparação de professores",
  avaliacao: "Avaliar professor na disciplina",
  acesso: "Minha conta",
};
const acao = "inline-block rounded-lg bg-accent px-4 py-2.5 text-center text-sm font-medium text-on-accent hover:opacity-90";
const secundaria = "inline-block rounded-lg border border-accent/30 px-4 py-2.5 text-center text-sm font-medium text-accent hover:bg-accent/5";
const voltar = "self-start text-sm text-accent underline underline-offset-4";
const cartao = "rounded-xl border border-foreground/10 p-5";
type Contexto = { tipo: string; q: string; ordemBusca: string };

function href(etapa: Etapa, valores: Record<string, string> = {}) {
  const parametros = new URLSearchParams(Object.entries(valores).filter(([, valor]) => valor !== ""));
  parametros.set("etapa", etapa);
  return `/prototipo?${parametros}`;
}

function BuscaDemo({ contexto }: { contexto: Contexto }) {
  return (
    <Form action="/prototipo" className={`${cartao} flex flex-col gap-4 bg-foreground/[0.02]`}>
      <input type="hidden" name="etapa" value="resultados" />
      <input type="hidden" name="ordemBusca" value={contexto.ordemBusca} />
      <fieldset className="flex flex-wrap gap-4"><legend className="mb-2 text-sm font-medium">Buscar por</legend>
        <label className="flex items-center gap-2"><input type="radio" name="tipo" value="professor" defaultChecked={contexto.tipo === "professor"} />Professor</label>
        <label className="flex items-center gap-2"><input type="radio" name="tipo" value="disciplina" defaultChecked={contexto.tipo === "disciplina"} />Disciplina</label>
      </fieldset>
      <label className="flex flex-col gap-2"><span className="text-sm font-medium">Nome do professor, nome ou código da disciplina</span>
        <input type="search" name="q" defaultValue={contexto.q} placeholder="Ex.: Ana, Algoritmos ou MAT-DEMO" aria-describedby="ajuda-busca"
          className="w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base" />
      </label>
      <p id="ajuda-busca" className="text-sm text-foreground/70">Informe ao menos 2 caracteres. Você pode buscar em qualquer departamento.</p>
      <button type="submit" className={`${acao} self-start`}>Buscar</button>
    </Form>
  );
}

function ContextoDisciplina({ disciplina }: { disciplina: DisciplinaInstitucional }) {
  return <div className="min-w-0">
    <p className="text-sm font-medium text-accent">Unidade acadêmica: {disciplina.departamento}</p>
    <p className="mt-1 text-lg font-semibold">{disciplina.nome}</p>
    <p className="mt-1 text-sm text-foreground/70">Código da disciplina: <span className="font-mono">{disciplina.codigo}</span></p>
  </div>;
}

function CriteriosDemo({ avaliacao }: { avaliacao: AvaliacaoAgregada }) {
  if (!avaliacao.dadosSuficientes) return (
    <p className="mt-4 rounded-lg bg-foreground/[0.03] p-3 text-sm text-foreground/70">
      {avaliacao.totalAvaliacoes === 0 ? "Ainda não há avaliações. Isso não representa uma avaliação negativa." : "Dados insuficientes para exibir os critérios."}
      {" "}Os critérios só aparecem a partir de 3 avaliações por professor e disciplina.
    </p>
  );
  const rotulos = { FACIL: "Fácil", MEDIO: "Médio", DIFICIL: "Difícil", BOM: "Bom", RUIM: "Ruim" } as const;
  const criterios = [
    ["Didática", `${avaliacao.didatica.toFixed(1)} / 5`],
    ["Dificuldade", rotulos[avaliacao.dificuldade]],
    ["Chamada", avaliacao.chamada === "CONFLITANTE" ? "Conflitante" : avaliacao.chamada ? "Faz chamada" : "Não faz chamada"],
    ["Material", avaliacao.disponibilizaMaterial === "CONFLITANTE" ? "Conflitante" : !avaliacao.disponibilizaMaterial ? "Não disponibiliza" : avaliacao.qualidadeMaterial ? rotulos[avaliacao.qualidadeMaterial] : "Disponibiliza"],
    ["Recomenda a matéria", `${avaliacao.recomenda}%`],
  ];
  return <dl className="mt-4 flex flex-col divide-y divide-foreground/10">{criterios.map(([rotulo, valor]) => (
    <div key={rotulo} className="flex flex-wrap justify-between gap-x-4 gap-y-1 py-2 text-sm">
      <dt className="text-foreground/70">{rotulo}</dt><dd className="font-medium">{valor}</dd>
    </div>
  ))}</dl>;
}

function disciplinasDoProfessor(professor: ProfessorInstitucional) {
  return disciplinasDemo.filter((disciplina) => comparacoesDemo[disciplina.id].some((item) => item.professorId === professor.id));
}

function DisciplinasProfessor({ professor, contexto }: { professor: ProfessorInstitucional; contexto: Contexto }) {
  return <ul className="mt-4 flex flex-col gap-3" aria-label={`Disciplinas de ${professor.nome} — ${professor.departamento}`}>
    {disciplinasDoProfessor(professor).map((disciplina) => <li key={disciplina.id} className="rounded-lg bg-foreground/[0.03] p-4">
      <ContextoDisciplina disciplina={disciplina} />
      <div className="mt-3 flex flex-wrap gap-3">
        <Link href={href("avaliacao", { ...contexto, professor: professor.id, disciplina: disciplina.id, origem: "professor" })} className={acao}
          aria-label={`Avaliar ${professor.nome} em ${disciplina.nome} — ${professor.departamento}`}>
          Avaliar nesta disciplina →
        </Link>
        <Link href={href("comparacao", { ...contexto, professor: professor.id, disciplina: disciplina.id })} className={secundaria}>
          Comparar professores
        </Link>
      </div>
    </li>)}
  </ul>;
}

export default async function PrototipoPage({ searchParams }: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const consulta = await searchParams;
  const texto = (nome: string) => typeof consulta[nome] === "string" ? consulta[nome] : "";
  const etapa: Etapa = etapas.find((item) => item === texto("etapa")) ?? "entrada";
  const tipo = texto("tipo") === "professor" ? "professor" : "disciplina";
  const termo = texto("q").trim();
  const contexto = { tipo, q: termo, ordemBusca: texto("ordemBusca") === "departamento" ? "departamento" : "nome" };
  const professor = professoresDemo.find((item) => item.id === texto("professor"));
  const disciplina = disciplinasDemo.find((item) => item.id === texto("disciplina"));
  const comparacao = disciplina ? comparacoesDemo[disciplina.id] : [];
  const avaliacao = comparacao.find((item) => item.professorId === professor?.id);
  const resultados: (DisciplinaInstitucional | ProfessorInstitucional)[] = termo.length < 2 ? [] : tipo === "professor"
    ? professoresDemo.filter((item) => correspondeBusca(item.nome, termo))
    : disciplinasDemo.filter((item) => correspondeBusca(item.nome, termo) || correspondeBusca(item.codigo, termo));
  resultados.sort((a, b) => (contexto.ordemBusca === "departamento" ? a.departamento.localeCompare(b.departamento, "pt-BR") : 0) || a.nome.localeCompare(b.nome, "pt-BR"));
  const selecionandoDisciplina = etapa === "resultados" && tipo === "professor" && professor;
  const ordenada = texto("ordem") === "recomendacao";
  // Retratos já preparados; ordenação de busca não altera a regra da comparação.
  const apresentacao = ordenada ? comparacao : disciplina ? apresentacoesDemo[disciplina.id] : [];
  const destino = { ...contexto, disciplina: disciplina?.id ?? "", professor: professor?.id ?? "", origem: texto("origem") === "professor" ? "professor" : "comparacao" };
  const retornoEtapa = etapas.find((item) => item !== "acesso" && item === texto("retornoEtapa")) ?? (avaliacao ? "avaliacao" : "entrada");
  const retornoConta = href(retornoEtapa, { ...destino, ordem: texto("ordem") === "recomendacao" ? "recomendacao" : "" });
  const retornoAvaliacao = destino.origem === "professor"
    ? href("resultados", { ...contexto, professor: professor?.id ?? "" })
    : href("comparacao", { ...contexto, disciplina: disciplina?.id ?? "", ordem: "recomendacao" });
  const passo = etapa === "entrada" || etapa === "busca" ? 0 : etapa === "resultados" ? 1 : 2;

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <aside className="rounded-lg border border-accent/30 bg-accent/5 p-4 text-sm">
        <p className="font-semibold text-accent">Protótipo navegável · proposta para teste com alunos</p>
        <p className="mt-1 text-foreground/70">Dados demonstrativos fictícios. Experimente a navegação; nenhuma avaliação é enviada ou salva.</p>
        <Link href="/" className="mt-2 inline-block underline underline-offset-4">Voltar ao sistema</Link>
      </aside>
      {etapa !== "acesso" && <nav aria-label="Etapas da jornada"><ol className="flex flex-wrap gap-2 text-sm">
        {["Busque", "Escolha a disciplina", "Consulte ou avalie"].map((nome, indice) => <li key={nome} aria-current={passo === indice ? "step" : undefined}
          className={passo === indice ? "rounded-lg bg-accent px-3 py-2 font-medium text-on-accent" : "rounded-lg bg-foreground/[0.03] px-3 py-2 text-foreground/70"}>
          {indice + 1}. {nome}
        </li>)}
      </ol></nav>}
      <div><h1 className="text-2xl font-semibold">{titulos[etapa]}</h1>
        <p className="mt-2 text-sm text-foreground/70">Consultar e comparar é público. Para enviar uma avaliação no sistema real, entre com sua conta de e-mail confirmado.</p>
      </div>

      {(etapa === "entrada" || etapa === "busca") && <div className="flex max-w-2xl flex-col gap-6">
        {etapa === "busca" && <Link href={href("entrada", contexto)} className={voltar}>← Voltar à entrada</Link>}
        <BuscaDemo key={`${tipo}/${termo}/${contexto.ordemBusca}`} contexto={contexto} />
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href={href("busca", { ...contexto, tipo: "professor" })} className={`${cartao} block hover:border-accent/40`}>
            <h2 className="text-lg font-medium">Buscar professor</h2><p className="mt-2 text-sm text-foreground/70">Veja as disciplinas agrupadas e escolha qual deseja consultar ou avaliar.</p>
          </Link>
          <Link href={href("busca", { ...contexto, tipo: "disciplina" })} className={`${cartao} block hover:border-accent/40`}>
            <h2 className="text-lg font-medium">Buscar disciplina</h2><p className="mt-2 text-sm text-foreground/70">Encontre a matéria pelo nome ou código e compare seus professores.</p>
          </Link>
        </div>
        <p className="text-sm text-foreground/70">Exemplos para experimentar: “Ana”, “Algoritmos”, “Estruturas” ou “MAT-DEMO”. Você pode ir direto à avaliação depois de escolher a matéria.</p>
      </div>}

      {etapa === "resultados" && <section className="flex flex-col gap-4" aria-label="Resultados">
        <Link href={href("busca", contexto)} className={voltar}>← Alterar busca</Link>
        {selecionandoDisciplina ? <>
          <Link href={href("resultados", contexto)} className={voltar}>← Voltar aos resultados da pesquisa “{termo}”</Link>
          <article className={`${cartao} max-w-2xl`}>
            <p className="text-sm font-medium text-accent">Unidade acadêmica: {professor.departamento}</p>
            <h2 className="mt-1 text-xl font-semibold">Disciplinas de {professor.nome}</h2>
            <p className="mt-2 text-sm text-foreground/70">Escolha a matéria abaixo. Você pode avaliar diretamente ou comparar os professores antes.</p>
            <DisciplinasProfessor professor={professor} contexto={contexto} />
          </article>
        </> : texto("estado") === "carregando" ? <p role="status">Buscando… Exemplo visual de carregamento.</p>
          : texto("estado") === "erro" ? <div role="alert" className={cartao}>
            <p>Não foi possível buscar agora. Exemplo visual de erro; seus critérios foram mantidos.</p>
            <Link href={href("resultados", contexto)} className={`${acao} mt-3`}>Tentar novamente</Link>
          </div> : termo.length < 2 ? <div className={cartao}><h2 className="font-medium">Informe sua busca</h2>
            <p className="mt-2 text-sm text-foreground/70">Digite ao menos 2 caracteres para encontrar professores ou disciplinas.</p>
          </div> : resultados.length === 0 ? <div className={cartao}><h2 className="font-medium">Nenhum resultado encontrado</h2>
            <p className="mt-2 text-sm text-foreground/70">Nenhum resultado para “{termo}” nos dados demonstrativos. Confira a grafia ou tente outro nome ou código.</p>
          </div> : <>
            <p role="status" className="text-sm text-foreground/70">{resultados.length} resultado(s) para “{termo}”. {tipo === "professor" ? "As disciplinas estão agrupadas por professor. Confira a unidade acadêmica antes de escolher." : "Escolha uma disciplina para comparar professores."}</p>
            <OrganizarResultadosDemo ordem={contexto.ordemBusca} tipo={tipo} />
            {tipo === "professor" && resultados.some((item, indice) => resultados.some((outro, outroIndice) => indice !== outroIndice && item.nome === outro.nome)) &&
              <p className="rounded-lg bg-accent/5 p-4 text-sm text-foreground/70">Há professores com o mesmo nome neste exemplo. São registros distintos: confira a unidade acadêmica e as disciplinas. Nomes iguais não identificam necessariamente a mesma pessoa.</p>}
            <ul className="grid gap-4 sm:grid-cols-2" aria-label="Lista de resultados">{resultados.map((item) => <li key={item.id}>
              <article className={`${cartao} h-full`}>
                {"codigo" in item ? <>
                  <ContextoDisciplina disciplina={item} />
                  <Link href={href("comparacao", { ...contexto, disciplina: item.id })} className={`${acao} mt-4`}>Ver professores de {item.nome} →</Link>
                </> : <>
                  <p className="text-sm font-medium text-accent">Unidade acadêmica: {item.departamento}</p>
                  <h2 className="mt-1 text-xl font-semibold">{item.nome}</h2>
                  <Link href={href("resultados", { ...contexto, professor: item.id })} className={`${voltar} mt-2 inline-block`}>Ver disciplinas de {item.nome}</Link>
                  <DisciplinasProfessor professor={item} contexto={contexto} />
                </>}
              </article>
            </li>)}</ul>
          </>}
        <details className="mt-2 text-sm text-foreground/70"><summary className="cursor-pointer py-2">Explorar estados de busca</summary>
          <nav aria-label="Estados demonstrativos" className="mt-3 flex flex-wrap gap-4 text-accent underline underline-offset-4">
            <Link href={href("resultados", { ...contexto, q: "" })}>Busca vazia</Link>
            <Link href={href("resultados", { ...contexto, q: "inexistente" })}>Sem resultados</Link>
            <Link href={href("resultados", { ...contexto, estado: "carregando" })}>Ver carregamento</Link>
            <Link href={href("resultados", { ...contexto, estado: "erro" })}>Ver erro</Link>
          </nav>
        </details>
      </section>}

      {etapa === "comparacao" && <>
        <Link href={href("resultados", contexto)} className={voltar}>← Voltar aos resultados</Link>
        {disciplina ? <>
          <div className={`${cartao} bg-accent/5`}><ContextoDisciplina disciplina={disciplina} />
            <p className="mt-3 text-sm text-foreground/70">Compare professores desta matéria ou escolha “Avaliar” no cartão. Dificuldade e Chamada são informações neutras.</p>
          </div>
          <Link href={href("comparacao", { ...contexto, disciplina: disciplina.id, ordem: "recomendacao" })} className={`${secundaria} self-start`}>Ordenar por recomendação</Link>
          <p role="status" className="text-sm text-foreground/70">{ordenada ? "Recomendação decrescente; desempate por quantidade e nome. Resultados insuficientes ao final, sem percentual artificial." : "Ordem de apresentação demonstrativa. Use a ordenação por recomendação para comparar."}</p>
          {comparacao.every((item) => !item.dadosSuficientes) && <p className={`${cartao} text-sm text-foreground/70`}>Não há dados suficientes para comparar os critérios. A ausência de avaliações não permite uma conclusão sobre o professor.</p>}
          <ul className="grid gap-4 sm:grid-cols-2" aria-label="Professores nesta disciplina">{apresentacao.map((item) => <li key={item.professorId} className={`${cartao} flex flex-col`}>
            <p className="text-sm font-medium text-accent">Unidade acadêmica: {item.professor.departamento}</p>
            <h3 className="mt-1 text-lg font-semibold">{item.professor.nome}</h3>
            <p className="mt-1 text-sm text-foreground/70">{item.totalAvaliacoes} {item.totalAvaliacoes === 1 ? "avaliação" : "avaliações"} nesta disciplina</p>
            <Link href={href("avaliacao", { ...contexto, disciplina: disciplina.id, professor: item.professorId, origem: "comparacao" })} className={`${acao} mt-4`}>Avaliar {item.professor.nome} nesta disciplina →</Link>
            <CriteriosDemo avaliacao={item} />
          </li>)}</ul>
        </> : <p className={cartao}>Escolha uma disciplina nos resultados para iniciar a comparação.</p>}
      </>}

      {etapa === "acesso" && <div className="flex flex-col gap-6">
        {avaliacao && <details className={`${cartao} max-w-2xl border-accent/30 bg-accent/5`}>
          <summary className="cursor-pointer text-sm font-medium">Avaliação selecionada: {avaliacao.disciplina.nome} · {avaliacao.professor.nome}</summary>
          <div className="mt-3" aria-label="Destino da avaliação">
          <ContextoDisciplina disciplina={avaliacao.disciplina} />
          <p className="mt-3 text-base">Professor: <strong>{avaliacao.professor.nome}</strong></p>
          </div>
        </details>}
        <AcessoDemo retorno={retornoConta} temAvaliacao={!!avaliacao && retornoEtapa === "avaliacao"} />
      </div>}

      {etapa === "avaliacao" && <div className="flex flex-col gap-6">
        <Link href={retornoAvaliacao} className={voltar}>{destino.origem === "professor" ? "← Voltar às disciplinas do professor" : "← Voltar à comparação"}</Link>
        {avaliacao ? <>
          <section className={`${cartao} border-accent/30 bg-accent/5`} aria-label="Destino da avaliação">
            <ContextoDisciplina disciplina={avaliacao.disciplina} />
            <p className="mt-3 text-base">Professor: <strong>{avaliacao.professor.nome}</strong></p>
          </section>
          <div className="flex max-w-2xl flex-col gap-6">
            <AcessoParaAvaliar href={href("acesso", { ...destino, retornoEtapa: "avaliacao" })} />
            <FormularioDemo key={`${avaliacao.professorId}/${avaliacao.disciplinaId}`} professorId={avaliacao.professorId} disciplinaId={avaliacao.disciplinaId} />
            <p className="text-sm text-foreground/70">No sistema, um novo envio válido substitui sua avaliação anterior para este professor nesta disciplina. Esta prévia contém apenas os cinco critérios estruturados.</p>
          </div>
        </> : <p className={cartao}>Escolha um professor na comparação para abrir o formulário da disciplina.</p>}
      </div>}
    </main>
  );
}
