import Icone from "./icone";

/** Estado decorativo: o título e a região de status fornecem a mensagem acessível. */
export default function IconeResultado({ estado }: { estado: "sucesso" | "erro" | "carregando" }) {
  return <span aria-hidden="true" className={`mx-auto grid size-16 shrink-0 place-items-center rounded-full ${estado === "sucesso" ? "bg-(--success-soft) text-(--success)" : estado === "erro" ? "bg-(--danger-soft) text-(--danger)" : "bg-(--accent-soft) text-accent"}`}>
    {estado === "carregando" ? <span className="size-6 animate-spin rounded-full border-2 border-current border-t-transparent motion-reduce:animate-none" /> : <Icone nome={estado === "sucesso" ? "check" : "info"} />}
  </span>;
}
