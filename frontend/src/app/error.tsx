"use client";

import Link from "next/link";

export default function ErroPagina({ retry }: { retry: () => void }) {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-4 px-4 py-10">
      <h1 className="text-2xl font-semibold">Não foi possível carregar esta página</h1>
      <p role="alert">O serviço pode estar temporariamente indisponível. Tente novamente em instantes.</p>
      <button onClick={retry} className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent hover:opacity-90">
        Tentar novamente
      </button>
      <Link href="/" className="text-accent underline">Voltar ao início</Link>
    </main>
  );
}
