import Form from "next/form";

export default function BuscaHero() {
  return <Form action="/busca" className="search search-hero" role="search">
    <label className="sr-only" htmlFor="tipo-busca">Buscar por</label>
    <select id="tipo-busca" name="busca" defaultValue="disciplinas"><option value="disciplinas">Disciplina</option><option value="professores">Professor</option></select>
    <span className="search-icon" aria-hidden="true" />
    <label className="sr-only" htmlFor="termo-busca">Nome do professor, nome ou código da disciplina</label>
    <input id="termo-busca" name="q" type="search" minLength={2} required placeholder="Buscar professor, disciplina ou código" />
    <input type="hidden" name="ordem" value="nome" />
    <button type="submit" className="button primary">Buscar</button>
  </Form>;
}
