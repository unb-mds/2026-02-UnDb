"use client";

import { useId, useState } from "react";

export default function CampoSenha({ cadastro = false }: { cadastro?: boolean }) {
  const [visivel, setVisivel] = useState(false);
  const id = useId();
  const ajudaId = `${id}-ajuda`;
  return (
    <div className="flex min-w-0 flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium">Senha</label>
      <input
        id={id}
        name="senha"
        type={visivel ? "text" : "password"}
        autoComplete={cadastro ? "new-password" : "current-password"}
        required
        minLength={cadastro ? 8 : undefined}
        maxLength={128}
        aria-describedby={cadastro ? ajudaId : undefined}
        className="min-w-0 rounded-lg border border-foreground/20 bg-background px-4 py-2.5 outline-none focus:border-foreground/50"
      />
      <button type="button" aria-controls={id} aria-pressed={visivel} onClick={() => setVisivel((valor) => !valor)} className="self-start rounded-lg px-2 py-2 text-sm font-medium text-accent underline underline-offset-4">
        {visivel ? "Ocultar senha" : "Mostrar senha"}
      </button>
      {cadastro && <span id={ajudaId} className="text-xs text-foreground/60">Use entre 8 e 128 caracteres.</span>}
    </div>
  );
}
