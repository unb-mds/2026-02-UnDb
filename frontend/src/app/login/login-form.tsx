"use client";

import CampoSenha from "@/components/campo-senha";
import OpcoesAcesso from "@/components/opcoes-acesso";

import Link from "next/link";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { consultarSessao, entrar, sair } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";

export default function LoginForm({ retorno, contexto }: { retorno: string | null; contexto?: ReactNode }) {
  const router = useRouter();
  const [carregando, setCarregando] = useState(false);
  const [sessaoCarregada, setSessaoCarregada] = useState(false);
  const [autenticado, setAutenticado] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let ativo = true;
    consultarSessao()
      .then((sessao) => {
        if (!ativo) return;
        setAutenticado(sessao.autenticado);
        if (sessao.autenticado && retorno) router.replace(retorno);
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
  }, [retorno, router]);

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
      if (retorno) {
        router.replace(retorno);
        return;
      }
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
    <main className="container flex max-w-xl min-w-0 flex-1 flex-col gap-6 py-10 sm:py-14">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Entrar</h1>
        <p className="mt-2 text-sm leading-relaxed text-(--muted)">
          Use sua conta institucional para registrar avaliações. As consultas continuam públicas.
        </p>
      </div>

      {contexto}
      <section className="panel flex min-w-0 flex-col gap-6 p-4 sm:p-6" aria-label="Acesso à conta">
        <OpcoesAcesso atual="login" retorno={retorno} />
        {!sessaoCarregada ? (
          <p className="text-sm text-(--muted)" role="status">Verificando sessão…</p>
        ) : !autenticado ? (
          <form onSubmit={enviar} className="flex min-w-0 flex-col gap-5">
            <label className="flex min-w-0 flex-col gap-2">
              <span className="text-sm font-medium">E-mail institucional</span>
              <input
                name="email"
                type="email"
                inputMode="email"
                autoComplete="email"
                required
                maxLength={150}
                placeholder="seu-email@aluno.unb.br"
                className="min-h-11 w-full min-w-0 rounded-lg border border-(--control-border) bg-(--raised) px-4 py-3 text-base text-foreground placeholder:text-(--muted) focus:border-accent"
              />
            </label>

            <CampoSenha />

            <button
              type="submit"
              disabled={carregando}
              className="button primary"
            >
              {carregando ? "Entrando…" : "Entrar"}
            </button>
          </form>
        ) : (
          <div className="flex min-w-0 flex-col gap-4 rounded-xl border border-(--border) bg-(--raised) p-4">
            <p className="text-sm text-(--muted)">
              Sua sessão está ativa neste navegador.
            </p>
            <button
              type="button"
              onClick={encerrarSessao}
              disabled={carregando}
              className="button"
            >
              {carregando ? "Saindo…" : "Sair"}
            </button>
          </div>
        )}

        <p className="text-sm leading-relaxed text-(--muted)">
          Ainda não possui conta?{" "}
          <Link href={retorno ? `/cadastro?returnTo=${encodeURIComponent(retorno)}` : "/cadastro"} className="font-medium text-accent hover:underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
            Criar conta
          </Link>
        </p>

        <div aria-live="polite" className="min-w-0 break-words">
          {mensagem && (
            <p className="rounded-lg border border-green-600/30 bg-green-600/10 p-4 text-sm">{mensagem}</p>
          )}
          {erro && <p className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">{erro}</p>}
        </div>
      </section>
    </main>
  );
}
