import Link from "next/link";

export default function Caminho({ itens }: { itens: { nome: string; href?: string; retornoBusca?: boolean }[] }) {
  return <nav aria-label="Caminho da página" className="breadcrumb">{itens.map((item, index) => <span className="breadcrumb-item" key={`${item.nome}:${index}`}>
    {index > 0 && <span aria-hidden="true">›</span>}
    {item.href ? <Link href={item.href} data-search-return={item.retornoBusca || undefined} aria-label={item.retornoBusca ? "Voltar aos resultados da busca" : undefined}>{item.nome}</Link> : <span aria-current="page">{item.nome}</span>}
  </span>)}</nav>;
}
