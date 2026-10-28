import Form from "next/form";

export default function BuscaEntrada() {
  return (
    <Form action="/busca" className="flex flex-col gap-4 rounded-xl border border-foreground/10 bg-foreground/[0.02] p-5">
      <fieldset className="flex flex-wrap gap-4">
        <legend className="mb-2 text-sm font-medium">Buscar por</legend>
        <label className="flex items-center gap-2"><input type="radio" name="busca" value="professores" />Professor</label>
        <label className="flex items-center gap-2"><input type="radio" name="busca" value="disciplinas" defaultChecked />Disciplina</label>
      </fieldset>
      <label className="flex flex-col gap-2">
        <span className="text-sm font-medium">Nome do professor, nome ou código da disciplina</span>
        <input type="search" name="q" required minLength={2} aria-describedby="busca-entrada-ajuda"
          placeholder="Nome completo ou parcial, ou código institucional"
          className="min-w-0 w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base" />
      </label>
      <input type="hidden" name="ordem" value="nome" />
      <p id="busca-entrada-ajuda" className="text-sm text-foreground/70">Informe ao menos 2 caracteres. Você pode buscar em qualquer unidade acadêmica.</p>
      <button type="submit" className="self-start rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-on-accent hover:opacity-90">Buscar</button>
    </Form>
  );
}
