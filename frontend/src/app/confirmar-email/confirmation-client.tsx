"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { confirmarEmail } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";
import { lerRetornoAvaliacaoSalvo } from "@/lib/retorno-avaliacao";

export function ConfirmationClient({ token }: { token?: string }) {
  const [tentativa, setTentativa] = useState(0);
  const [podeTentar, setPodeTentar] = useState(false);
  const [retorno, setRetorno] = useState<string | null>(null);
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
          setRetorno(lerRetornoAvaliacaoSalvo());
        }
      })
      .catch((falha: unknown) => {
        if (!cancelado) {
          const linkInvalido = falha instanceof ApiError && [400, 422].includes(falha.status);
          setEstado("erro");
          setPodeTentar(!linkInvalido);
          setMensagem(linkInvalido
            ? "Este link é inválido ou expirou."
            : "Não foi possível confirmar seu e-mail agora. Verifique sua conexão e tente novamente.");
        }
      });

    return () => {
      cancelado = true;
    };
  }, [token, tentativa]);

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-10 text-center">
      <h1 className="text-2xl font-semibold">Confirmação de e-mail</h1>
      <p
        aria-live="polite"
        className={estado === "erro" ? "text-red-600 dark:text-red-400" : "text-foreground/70"}
      >
        {mensagem}
      </p>
      {estado === "erro" && podeTentar && (
        <button className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent hover:opacity-90" onClick={() => {
          setEstado("carregando");
          setMensagem("Confirmando seu e-mail…");
          setPodeTentar(false);
          setTentativa((valor) => valor + 1);
        }}>Tentar novamente</button>
      )}
      {estado !== "carregando" && (
        <div className="flex flex-col items-center gap-3">
          {estado === "sucesso" && retorno && (
            <Link
              href={`/login?returnTo=${encodeURIComponent(retorno)}`}
              className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent transition hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Continuar para a avaliação
            </Link>
          )}
          <Link href="/" className="font-medium text-accent hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
            Voltar ao início
          </Link>
        </div>
      )}
    </main>
  );
}
