import type { Metadata } from "next";
import FilaModeracao from "./fila-moderacao";

export const metadata: Metadata = {
  title: "Fila de moderação — UnDb",
  robots: { index: false, follow: false },
};

export default function ModeracaoPage() {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold">Fila de moderação</h1>
        <p className="mt-2 text-sm text-foreground/70">Analise comentários pendentes, denunciados e suspensos. As decisões sobre o texto preservam os critérios da avaliação.</p>
      </div>
      <FilaModeracao />
    </main>
  );
}
