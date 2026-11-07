import Link from "next/link";

export default function Estados() {
  return <main className="container page-content"><h1>Estados da exibição</h1><p>Exemplos ilustrativos das regras de privacidade. Não são resultados de professores reais.</p><div className="states-grid">
    <section className="panel state-card"><span className="badge blue">2 avaliações</span><h2>Dados insuficientes</h2><p>Nenhum critério é exibido abaixo de 3 avaliações, para proteger quem avaliou.</p><dl className="placeholder-list">{["Didática","Dificuldade","Chamada","Material","Recomenda"].map(c => <div key={c}><dt>{c}</dt><dd>—</dd></div>)}</dl></section>
    <section className="panel state-card"><span className="badge blue">0 avaliações</span><h2>Sem avaliações</h2><p>Falta de dados não significa avaliação negativa.</p><Link className="button primary" href="/professores">Seja o primeiro a avaliar</Link></section>
    <section className="panel state-card"><span className="badge blue">Empate exato</span><h2>Resposta conflitante</h2><p>Em critérios factuais, um empate exato é apresentado como “Conflitante”.</p><dl className="panel metric"><dt>Chamada</dt><dd>Conflitante</dd><p>4 avaliações · 2 sim, 2 não</p></dl></section>
  </div></main>;
}
