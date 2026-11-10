import Link from "next/link";
import Caminho from "@/components/caminho";

export default function EstadosPage() {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <Caminho
        itens={[
          { nome: "Início", href: "/" },
          { nome: "Estados da exibição" },
        ]}
      />

      <div className="panel p-6">
        <h1 className="text-2xl font-bold">Estados da exibição</h1>
        <p className="mt-1 text-sm text-foreground/70">
          Exemplos ilustrativos das regras de privacidade e agregação. Não são resultados de professores reais.
        </p>
      </div>

      <div className="states-grid">
        <section className="panel state-card">
          <span className="badge blue">2 avaliações</span>
          <h2>Dados insuficientes</h2>
          <p>
            Nenhum critério é exibido abaixo de 3 avaliações, para proteger a identidade e o anonimato de quem avaliou.
          </p>
          <dl className="placeholder-list">
            {["Didática", "Dificuldade", "Chamada", "Material", "Recomenda"].map((c) => (
              <div key={c}>
                <dt>{c}</dt>
                <dd aria-label="Critério oculto por dados insuficientes">—</dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="panel state-card flex flex-col justify-between">
          <div>
            <span className="badge blue">0 avaliações</span>
            <h2>Sem avaliações</h2>
            <p>
              Falta de dados não significa avaliação negativa. A ausência de avaliações convida a comunidade a colaborar.
            </p>
          </div>
          <div className="mt-6">
            <Link className="button primary" href="/professores">
              Seja o primeiro a avaliar
            </Link>
          </div>
        </section>

        <section className="panel state-card">
          <span className="badge blue">Empate exato</span>
          <h2>Resposta conflitante</h2>
          <p>
            Em critérios factuais binários, um empate exato na agregação da API é apresentado como “Conflitante”.
          </p>
          <dl className="panel metric mt-4">
            <div className="metric-dash" aria-hidden="true" />
            <dt>Chamada</dt>
            <dd>Conflitante</dd>
            <p>4 avaliações · 2 sim, 2 não</p>
          </dl>
        </section>
      </div>
    </main>
  );
}
