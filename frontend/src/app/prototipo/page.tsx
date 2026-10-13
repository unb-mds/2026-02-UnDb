import Link from "next/link";
import { apresentacoesDemo, comparacoesDemo, correspondeBusca, disciplinasDemo, professoresDemo } from "./dados";
import FormularioDemo from "./formulario-demo";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import type { DisciplinaInstitucional, ProfessorInstitucional } from "@/lib/types/institucional";

const etapas = ["entrada", "busca", "resultados", "comparacao", "avaliacao"] as const;
type Etapa = typeof etapas[number];
const titulos: Record<Etapa, string> = {
  entrada: "Escolha sua próxima disciplina",
  busca: "O que você quer encontrar?",
  resultados: "Resultados da busca",
  comparacao: "Comparação de professores",
  avaliacao: "Avaliar professor na disciplina",
};
const nomes: Record<Etapa, string> = {
  entrada: "Entrada", busca: "Busca", resultados: "Resultados", comparacao: "Comparação", avaliacao: "Avaliação",
};
const acao = "inline-block rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-on-accent hover:opacity-90";
const cartao = "rounded-xl border border-foreground/10 p-5";

function href(etapa: Etapa, valores: Record<string, string> = {}) {
  return `/prototipo?${new URLSearchParams({ ...valores, etapa })}`;
}

function CriteriosDemo({ avaliacao }: { avaliacao: AvaliacaoAgregada }) {
  if (!avaliacao.dadosSuficientes) return (
    <p className="mt-4 rounded-lg bg-foreground/[0.03] p-3 text-sm text-foreground/70">
      {avaliacao.totalAvaliacoes === 0 ? "Ainda não há avaliações. Isso não representa uma avaliação negativa." : "Dados insuficientes para exibir os critérios."}
      {" "}Os critérios só aparecem a partir de 3 avaliações por professor e disciplina.
    </p>
  );
  const rotulos = { FACIL: "Fácil", MEDIO: "Médio", DIFICIL: "Difícil", BOM: "Bom", RUIM: "Ruim" } as const;
  const binario = (valor: boolean | "CONFLITANTE") => valor === "CONFLITANTE" ? "Conflitante" : valor ? "Sim" : "Não";
  const criterios = [
    ["Didática", `${avaliacao.didatica.toFixed(1)} / 5`],
    ["Dificuldade", rotulos[avaliacao.dificuldade]],
    ["Chamada", binario(avaliacao.chamada)],
    ["Material", avaliacao.disponibilizaMaterial === "CONFLITANTE" ? "Conflitante" : !avaliacao.disponibilizaMaterial ? "Não disponibiliza" : avaliacao.qualidadeMaterial ? rotulos[avaliacao.qualidadeMaterial] : "Disponibiliza"],
    ["Recomenda a matéria", `${avaliacao.recomenda}%`],
  ];
  return <dl className="mt-4 flex flex-col divide-y divide-foreground/10">{criterios.map(([rotulo, valor]) => (
    <div key={rotulo} className="flex flex-wrap justify-between gap-x-4 gap-y-1 py-2 text-sm">
      <dt className="text-foreground/70">{rotulo}</dt><dd className="font-medium">{valor}</dd>
    </div>
  ))}</dl>;
}

export default async function PrototipoPage({ searchParams }: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const consulta = await searchParams;
  const texto = (nome: string) => typeof consulta[nome] === "string" ? consulta[nome] : "";
  const etapa: Etapa = etapas.find((item) => item === texto("etapa")) ?? "entrada";
  const tipo = texto("tipo") === "professor" ? "professor" : "disciplina";
  const termo = texto("q").trim();
  const contexto = { tipo, q: termo };
  const professor = professoresDemo.find((item) => item.id === texto("professor"));
  const disciplina = disciplinasDemo.find((item) => item.id === texto("disciplina"));
  const comparacao = disciplina ? comparacoesDemo[disciplina.id] : [];
  const avaliacao = comparacao.find((item) => item.professorId === professor?.id);
  const resultados: (DisciplinaInstitucional | ProfessorInstitucional)[] = termo.length < 2 ? [] : tipo === "professor"
    ? professoresDemo.filter((item) => correspondeBusca(item.nome, termo))
    : disciplinasDemo.filter((item) => correspondeBusca(item.nome, termo) || correspondeBusca(item.codigo, termo));
  const selecionandoDisciplina = etapa === "resultados" && tipo === "professor" && professor;
  const disciplinasProfessor = professor ? disciplinasDemo.filter((item) => comparacoesDemo[item.id].some((registro) => registro.professorId === professor.id)) : [];
  const ordenada = texto("ordem") === "recomendacao";
  // As duas apresentações são fixtures: a ordenada já vem preparada, sem recalcular negócio.
  const apresentacao = ordenada ? comparacao : disciplina ? apresentacoesDemo[disciplina.id] : [];

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <aside className="rounded-lg border border-accent/30 bg-accent/5 p-4 text-sm">
        <p className="font-semibold text-accent">Protótipo navegável · Issue #152</p>
        <p className="mt-1 text-foreground/70">Dados demonstrativos fictícios. Nenhuma consulta à API ou avaliação real é realizada aqui.</p>
        <Link href="/" className="mt-2 inline-block underline underline-offset-4">Voltar ao sistema</Link>
      </aside>
      <nav aria-label="Etapas da jornada">
        <ol className="flex flex-wrap gap-2 text-sm">
          {etapas.map((item, indice) => <li key={item} aria-current={etapa === item ? "step" : undefined}
            className={etapa === item ? "rounded-lg bg-accent px-3 py-2 font-medium text-on-accent" : "rounded-lg bg-foreground/[0.03] px-3 py-2 text-foreground/70"}>
            {indice + 1}. {nomes[item]}
          </li>)}
        </ol>
      </nav>
      <div><h1 className="text-2xl font-semibold">{titulos[etapa]}</h1>
        <p className="mt-2 text-sm text-foreground/70">Consulta pública, sem cadastro. Para registrar uma avaliação no sistema, é preciso ter conta com e-mail confirmado.</p>
      </div>

      {etapa === "entrada" && <>
        <p className="max-w-2xl text-foreground/70">Encontre uma disciplina, compare as experiências compartilhadas e contribua com uma avaliação estruturada.</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href={href("busca", { tipo: "disciplina" })} className={`${cartao} transition hover:border-foreground/30 hover:bg-foreground/[0.03]`}>
            <h2 className="text-lg font-medium">Buscar disciplina</h2><p className="mt-2 text-sm text-foreground/70">Por nome ou código, em qualquer departamento.</p>
          </Link>
          <Link href={href("busca", { tipo: "professor" })} className={`${cartao} transition hover:border-foreground/30 hover:bg-foreground/[0.03]`}>
            <h2 className="text-lg font-medium">Buscar professor</h2><p className="mt-2 text-sm text-foreground/70">Por nome completo ou parcial; depois, escolha a disciplina.</p>
          </Link>
        </div>
      </>}

      {etapa === "busca" && <div className="flex max-w-2xl flex-col gap-6">
        <Link href={href("entrada")} className="text-sm text-accent underline underline-offset-4">← Voltar à entrada</Link>
        <form action="/prototipo" className="flex flex-col gap-4">
          <input type="hidden" name="etapa" value="resultados" />
          <fieldset className="flex flex-wrap gap-4"><legend className="mb-2 text-sm font-medium">Buscar por</legend>
            <label className="flex items-center gap-2"><input type="radio" name="tipo" value="disciplina" defaultChecked={tipo === "disciplina"} />Disciplina</label>
            <label className="flex items-center gap-2"><input type="radio" name="tipo" value="professor" defaultChecked={tipo === "professor"} />Professor</label>
          </fieldset>
          <label className="flex flex-col gap-2"><span className="text-sm font-medium">Nome do professor, nome ou código da disciplina</span>
            <input type="search" name="q" defaultValue={termo} placeholder="Ex.: Algoritmos, MAT-DEMO ou Ana" aria-describedby="ajuda-busca"
              className="w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5" />
          </label>
          <p id="ajuda-busca" className="text-sm text-foreground/70">Informe ao menos 2 caracteres. A busca não restringe seu curso ou departamento.</p>
          <button type="submit" className={`${acao} self-start`}>Buscar</button>
        </form>
        <div className={`${cartao} text-sm text-foreground/70`}><h2 className="font-medium text-foreground">Experimente a jornada</h2>
          <p className="mt-2">Use “Algoritmos” para comparar dados suficientes, conflitantes e insuficientes, ou “Cálculo” para ver ausência de avaliações em outro departamento.</p>
        </div>
      </div>}

      {etapa === "resultados" && <section className="flex max-w-2xl flex-col gap-4" aria-label="Resultados">
        <Link href={href("busca", contexto)} className="text-sm text-accent underline underline-offset-4">← Alterar busca</Link>
        {selecionandoDisciplina ? <>
          <h2 className="text-lg font-medium">Disciplinas de {professor.nome}</h2>
          <p className="text-sm text-foreground/70">Escolha a disciplina para comparar os professores que a oferecem.</p>
          <ul className="flex flex-col gap-3">{disciplinasProfessor.map((item) => <li key={item.id}>
            <Link href={href("comparacao", { ...contexto, disciplina: item.id })} className={`${cartao} block hover:border-foreground/30`}>
              <span className="font-mono text-sm">{item.codigo}</span><span className="block font-medium">{item.nome}</span>
            </Link>
          </li>)}</ul>
        </> : texto("estado") === "carregando" ? <p role="status">Buscando… Exemplo visual de carregamento.</p>
          : texto("estado") === "erro" ? <div role="alert" className={cartao}>
            <p>Não foi possível buscar agora. Exemplo visual de erro; seus critérios foram mantidos.</p>
            <Link href={href("resultados", contexto)} className={`${acao} mt-3`}>Tentar novamente</Link>
          </div> : termo.length < 2 ? <div className={cartao}><h2 className="font-medium">Informe sua busca</h2>
            <p className="mt-2 text-sm text-foreground/70">Digite ao menos 2 caracteres para encontrar professores ou disciplinas.</p>
          </div> : resultados.length === 0 ? <div className={cartao}><h2 className="font-medium">Nenhum resultado encontrado</h2>
            <p className="mt-2 text-sm text-foreground/70">Nenhum resultado para “{termo}” nos dados demonstrativos. Confira a grafia ou tente outro nome ou código.</p>
          </div> : <>
            <p role="status" className="text-sm text-foreground/70">{resultados.length} resultado(s) para “{termo}”. {tipo === "professor" ? "Escolha um professor." : "Escolha uma disciplina para comparar professores."}</p>
            <ul className="flex flex-col gap-3">{resultados.map((item) => <li key={item.id}>
              <Link href={tipo === "professor" ? href("resultados", { ...contexto, professor: item.id }) : href("comparacao", { ...contexto, disciplina: item.id })}
                className={`${cartao} block hover:border-foreground/30 hover:bg-foreground/[0.03]`}>
                {"codigo" in item && typeof item.codigo === "string" && <span className="font-mono text-sm text-foreground/70">{item.codigo}</span>}
                <span className="block font-medium">{item.nome}</span><span className="text-sm text-foreground/70">{item.departamento}</span>
              </Link>
            </li>)}</ul>
          </>}
        <nav aria-label="Estados demonstrativos" className="flex flex-wrap gap-4 text-sm text-accent underline underline-offset-4">
          <Link href={href("resultados", { tipo, q: "" })}>Busca vazia</Link>
          <Link href={href("resultados", { tipo, q: "inexistente" })}>Sem resultados</Link>
          <Link href={href("resultados", { ...contexto, estado: "carregando" })}>Ver carregamento</Link>
          <Link href={href("resultados", { ...contexto, estado: "erro" })}>Ver erro</Link>
        </nav>
      </section>}

      {etapa === "comparacao" && <>
        <Link href={href("resultados", contexto)} className="text-sm text-accent underline underline-offset-4">← Voltar aos resultados</Link>
        {disciplina ? <>
          <h2 className="text-lg font-medium">{disciplina.codigo} · {disciplina.nome}</h2>
          <p className="text-sm text-foreground/70">Compare apenas professores da mesma disciplina. Dificuldade e Chamada são informações neutras.</p>
          <Link href={href("comparacao", { ...contexto, disciplina: disciplina.id, ordem: "recomendacao" })} className={`${acao} self-start`}>Ordenar por recomendação</Link>
          <p role="status" className="text-sm text-foreground/70">{ordenada ? "Recomendação decrescente; desempate por quantidade e nome. Resultados insuficientes ao final, sem percentual artificial." : "Ordem de apresentação demonstrativa. Use a ordenação por recomendação para comparar."}</p>
          {comparacao.every((item) => !item.dadosSuficientes) && <p className={`${cartao} text-sm text-foreground/70`}>Não há dados suficientes para comparar os critérios. A ausência de avaliações não permite uma conclusão sobre o professor.</p>}
          <ul className="grid gap-4 sm:grid-cols-2">{apresentacao.map((item) => <li key={item.professorId} className={`${cartao} flex flex-col`}>
            <h3 className="text-lg font-medium">{item.professor.nome}</h3>
            <p className="mt-1 text-sm text-foreground/70">{item.totalAvaliacoes} {item.totalAvaliacoes === 1 ? "avaliação" : "avaliações"} nesta disciplina</p>
            <CriteriosDemo avaliacao={item} />
            <Link href={href("avaliacao", { ...contexto, disciplina: disciplina.id, professor: item.professorId })} className="mt-4 inline-block text-sm font-medium text-accent underline underline-offset-4">Avaliar {item.professor.nome} nesta disciplina →</Link>
          </li>)}</ul>
        </> : <p className={cartao}>Escolha uma disciplina nos resultados para iniciar a comparação.</p>}
      </>}

      {etapa === "avaliacao" && <div className="flex max-w-2xl flex-col gap-6">
        <Link href={href("comparacao", { ...contexto, disciplina: disciplina?.id ?? "", ordem: "recomendacao" })} className="text-sm text-accent underline underline-offset-4">← Voltar à comparação</Link>
        {avaliacao ? <>
          <dl className={cartao}><div><dt className="text-sm text-foreground/70">Professor</dt><dd className="font-medium">{avaliacao.professor.nome}</dd></div>
            <div className="mt-3"><dt className="text-sm text-foreground/70">Disciplina</dt><dd>{avaliacao.disciplina.codigo} · {avaliacao.disciplina.nome}</dd></div></dl>
          <FormularioDemo key={`${avaliacao.professorId}/${avaliacao.disciplinaId}`} professorId={avaliacao.professorId} disciplinaId={avaliacao.disciplinaId} />
          <p className="text-sm text-foreground/70">No sistema, um novo envio válido substitui sua avaliação anterior para este professor nesta disciplina. Não há campo de texto livre.</p>
        </> : <p className={cartao}>Escolha um professor na comparação para abrir o formulário da disciplina.</p>}
      </div>}
    </main>
  );
}
