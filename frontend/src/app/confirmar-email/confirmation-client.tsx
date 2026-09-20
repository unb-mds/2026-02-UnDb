"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { confirmarEmail } from "@/lib/services/auth";

export function ConfirmationClient({ token }: { token?: string }) {
  const [estado, setEstado] = useState<"carregando" | "sucesso" | "erro">(
    token ? "carregando" : "erro",
  );
  const [mensagem, setMensagem] = useState(
    token ? "Confirmando seu e-mail…" : "O link de confirmação está incompleto.",
  );

  useEffect(() => {
    if (!token) return;
    let cancelado = false;

    confirmarEmail(token)
      .then((resposta) => {
        if (!cancelado) {
          setEstado("sucesso");
          setMensagem(resposta.message);
        }
      })
      .catch(() => {
        if (!cancelado) {
          setEstado("erro");
          setMensagem("Este link é inválido ou expirou.");
        }
      });

    return () => {
      cancelado = true;
    };
  }, [token]);

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-10 text-center">
      <h1 className="text-2xl font-semibold">Confirmação de e-mail</h1>
      <p
        aria-live="polite"
        className={estado === "erro" ? "text-red-600 dark:text-red-400" : "text-foreground/70"}
      >
        {mensagem}
      </p>
      {estado !== "carregando" && (
        <Link href="/" className="font-medium text-accent hover:underline">
          Voltar ao início
        </Link>
      )}
    </main>
  );
}
