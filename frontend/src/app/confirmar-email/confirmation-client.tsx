"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { confirmarEmail } from "@/lib/services/auth";
import { ApiError, mensagemErroTemporario } from "@/lib/services/http-error";
import Icone from "@/components/icone";
import IconeResultado from "@/components/icone-resultado";

export function ConfirmationClient({ token, retorno }: { token?: string; retorno: string | null }) {
  const [tentativa, setTentativa] = useState(0);
  const [podeTentar, setPodeTentar] = useState(false);
  const [estado, setEstado] = useState<"carregando" | "sucesso" | "erro">(
    token ? "carregando" : "erro",
  );
  const [mensagem, setMensagem] = useState(
    token ? "Confirmando seu e-mail…" : "O link de confirmação está incompleto.",
  );

  useEffect(() => {
    if (!token) return;
    let cancelado = false;

    // Cancela a montagem descartada pelo StrictMode antes de consumir um token de uso único.
    const inicio = window.setTimeout(() => void confirmarEmail(token)
      .then((resposta) => {
        if (!cancelado) {
          setEstado("sucesso");
          setMensagem(resposta.message);
        }
      })
      .catch((falha: unknown) => {
        if (!cancelado) {
          const linkInvalido = falha instanceof ApiError && [400, 422].includes(falha.status);
          setEstado("erro");
          setPodeTentar(!linkInvalido);
          setMensagem(mensagemErroTemporario(falha) ?? (linkInvalido
            ? "Este link é inválido ou expirou."
            : "Não foi possível confirmar seu e-mail agora. Verifique sua conexão e tente novamente."));
        }
      }), 0);

    return () => {
      cancelado = true;
      window.clearTimeout(inicio);
    };
  }, [token, tentativa]);

  return (
    <main className="flex flex-1 items-center justify-center px-4 py-12 sm:py-20">
      <section className="flex w-full max-w-lg min-w-0 flex-col gap-5 rounded-3xl border border-(--border) bg-(--panel) p-5 text-center break-words sm:p-10" aria-label="Resultado da confirmação" aria-busy={estado === "carregando"}>
      <IconeResultado estado={estado} />
      <h1 className="kicker">Confirmação de e-mail</h1>
      <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">{estado === "sucesso" ? "E-mail confirmado." : estado === "carregando" ? "Confirmando seu e-mail…" : "Não foi possível confirmar."}</h2>
      <p
        aria-live="polite"
        role={estado === "erro" ? "alert" : "status"}
        className={estado === "sucesso" ? "sr-only" : "text-sm leading-relaxed text-(--ink-soft)"}
      >
        {mensagem}
      </p>
      {estado === "sucesso" && <p className="text-sm leading-relaxed text-(--ink-soft)">Seu endereço institucional foi confirmado. Entre na sua conta para registrar avaliações.</p>}
      {estado === "erro" && podeTentar && (
        <button className="button primary" onClick={() => {
          setEstado("carregando");
          setMensagem("Confirmando seu e-mail…");
          setPodeTentar(false);
          setTentativa((valor) => valor + 1);
        }}>Tentar novamente</button>
      )}
      {estado !== "carregando" && (
        <div className="flex flex-col gap-3">
          {estado === "sucesso" && (
            <Link
              href={retorno ? `/login?returnTo=${encodeURIComponent(retorno)}` : "/login"}
              className="button primary"
            >
              {retorno ? "Continuar para a avaliação" : "Entrar na conta"}<Icone nome="arrow-right" pequeno />
            </Link>
          )}
          <Link href="/" className="link inline-flex min-h-11 items-center justify-center text-sm font-medium">
            Voltar ao início
          </Link>
        </div>
      )}
      </section>
    </main>
  );
}
