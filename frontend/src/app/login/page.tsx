"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { consultarSessao, entrar, sair } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";

export default function LoginPage() {
  const [carregando, setCarregando] = useState(false);
  const [sessaoCarregada, setSessaoCarregada] = useState(false);
  const [autenticado, setAutenticado] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let ativo = true;

    consultarSessao()
      .then((sessao) => {
        if (ativo) setAutenticado(sessao.autenticado);
      })
      .catch(() => {
        if (ativo) setErro("Não foi possível verificar a sessão agora.");
      })
      .finally(() => {
        if (ativo) setSessaoCarregada(true);
      });

    return () => {
      ativo = false;
    };
  }, []);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagem(null);
    setErro(null);
    const formulario = new FormData(evento.currentTarget);

    try {
      const resposta = await entrar({
        email: String(formulario.get("email") ?? ""),
        senha: String(formulario.get("senha") ?? ""),
      });
      setAutenticado(true);
      setMensagem(resposta.message);
    } catch (falha) {
      setAutenticado(false);
      setErro(
        falha instanceof ApiError && falha.status === 401
          ? "E-mail ou senha inválidos."
          : "Não foi possível entrar agora. Tente novamente em instantes.",
      );
    } finally {
      setCarregando(false);
    }
  }

  async function encerrarSessao() {
    setCarregando(true);
    setMensagem(null);
    setErro(null);

    try {
      const resposta = await sair();
      setAutenticado(false);
      setMensagem(resposta.message);
    } catch {
      setErro("Não foi possível encerrar a sessão agora.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold">Entrar</h1>
        <p className="mt-1 text-sm text-foreground/70">
          Use sua conta institucional para registrar avaliações. As consultas continuam públicas.
        </p>
      </div>

      {!sessaoCarregada ? (
        <p className="text-sm text-foreground/70">Verificando sessão…</p>
      ) : !autenticado ? (
        <form onSubmit={enviar} className="flex flex-col gap-4">
          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium">E-mail institucional</span>
            <input
              name="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              maxLength={150}
              placeholder="seu-email@aluno.unb.br"
              className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 outline-none focus:border-foreground/50"
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium">Senha</span>
            <input
              name="senha"
              type="password"
              autoComplete="current-password"
              required
              maxLength={128}
              className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 outline-none focus:border-foreground/50"
            />
          </label>

          <button
            type="submit"
            disabled={carregando}
            className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {carregando ? "Entrando…" : "Entrar"}
          </button>
        </form>
      ) : (
        <div className="flex flex-col gap-4 rounded-xl border border-foreground/10 p-5">
          <p className="text-sm text-foreground/70">
            Sua sessão está ativa neste navegador.
          </p>
          <button
            type="button"
            onClick={encerrarSessao}
            disabled={carregando}
            className="rounded-lg border border-foreground/20 px-4 py-2.5 font-medium transition hover:border-foreground/40 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {carregando ? "Saindo…" : "Sair"}
          </button>
        </div>
      )}

      <p className="text-sm text-foreground/70">
        Ainda não possui conta?{" "}
        <Link href="/cadastro" className="font-medium text-accent hover:underline underline-offset-4">
          Criar conta
        </Link>
      </p>

      <div aria-live="polite">
        {mensagem && (
          <p className="rounded-lg border border-green-600/30 bg-green-600/10 p-4 text-sm">{mensagem}</p>
        )}
        {erro && <p className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">{erro}</p>}
      </div>
    </main>
  );
}
