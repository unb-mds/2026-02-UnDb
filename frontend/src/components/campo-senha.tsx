"use client";

import { useId, useState } from "react";

export default function CampoSenha({ cadastro = false }: { cadastro?: boolean }) {
  const [visivel, setVisivel] = useState(false);
  const id = useId();
  const ajudaId = `${id}-ajuda`;
  return (
    <div className="underline-field">
      <label htmlFor={id} className="label-mono">Senha</label>
      <input
        id={id}
        name="senha"
        type={visivel ? "text" : "password"}
        autoComplete={cadastro ? "new-password" : "current-password"}
        required
        minLength={cadastro ? 8 : undefined}
        maxLength={128}
        aria-describedby={cadastro ? ajudaId : undefined}
      />
      <button type="button" aria-controls={id} aria-pressed={visivel} onClick={() => setVisivel((valor) => !valor)} className="link mt-1 inline-flex min-h-11 items-center self-end text-sm">
        {visivel ? "Ocultar senha" : "Mostrar senha"}
      </button>
      {cadastro && <span id={ajudaId} className="text-xs text-(--muted)">Use entre 8 e 128 caracteres.</span>}
    </div>
  );
}
