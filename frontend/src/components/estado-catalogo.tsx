export default function EstadoCatalogo({ estado, tentarNovamente }: {
  estado: "carregando" | "erro" | "vazio";
  tentarNovamente: () => void;
}) {
  if (estado === "carregando") return <p role="status" className="py-6 text-sm text-(--muted)">Carregando catálogo…</p>;
  return (
    <div className="flex flex-col items-start gap-3 rounded-2xl border border-(--border) bg-(--panel) p-6">
      <h2 className="text-lg font-semibold">{estado === "erro" ? "Catálogo temporariamente indisponível" : "Catálogo vazio"}</h2>
      <p role={estado === "erro" ? "alert" : "status"} className="text-sm text-(--muted)">
        {estado === "erro" ? "Não foi possível carregar as disciplinas e unidades acadêmicas agora." : "Nenhuma disciplina cadastrada neste ambiente. As unidades aparecerão quando houver disciplinas no catálogo."}
      </p>
      <button type="button" onClick={tentarNovamente} className="button">Tentar novamente</button>
    </div>
  );
}
