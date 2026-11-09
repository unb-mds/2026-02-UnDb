import Link from "next/link";

export type ItemCaminho = { nome: string; href?: string; retornoBusca?: boolean };

export default function Caminho({ itens }: { itens: ItemCaminho[] }) {
  return <nav aria-label="Caminho da página" className="breadcrumb"><ol>
    {itens.map((item, index) => <li className="breadcrumb-item" key={`${item.nome}:${index}`}>
      {index > 0 && <span aria-hidden="true">›</span>}
      {item.href ? <Link href={item.href} data-search-return={item.retornoBusca || undefined}
        aria-label={item.retornoBusca ? "Voltar aos resultados da busca" : undefined}>{item.nome}</Link>
        : <span aria-current="page">{item.nome}</span>}
    </li>)}
  </ol></nav>;
}
