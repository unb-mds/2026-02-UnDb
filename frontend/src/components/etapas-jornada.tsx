export default function EtapasJornada({ atual }: { atual: 0 | 1 | 2 }) {
  return (
    <nav aria-label="Etapas da jornada">
      <ol className="flex flex-wrap gap-2 text-sm">
        {["Busque", "Escolha a disciplina", "Consulte ou avalie"].map((nome, indice) => (
          <li key={nome} aria-current={indice === atual ? "step" : undefined}
            className={indice === atual
              ? "rounded-lg bg-accent px-3 py-2 font-medium text-on-accent"
              : "rounded-lg bg-foreground/[0.03] px-3 py-2 text-foreground/70"}>
            {indice + 1}. {nome}
          </li>
        ))}
      </ol>
    </nav>
  );
}
