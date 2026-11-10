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
        className="min-h-11 w-full min-w-0 rounded-lg border border-(--control-border) bg-(--raised) px-4 py-3 text-base text-foreground focus:border-accent"
      />
      <button type="button" aria-controls={id} aria-pressed={visivel} onClick={() => setVisivel((valor) => !valor)} className="button self-start underline underline-offset-4">
        {visivel ? "Ocultar senha" : "Mostrar senha"}
      </button>
      {cadastro && <span id={ajudaId} className="text-xs text-(--muted)">Use entre 8 e 128 caracteres.</span>}
    </div>
  );
}
