"use client";

import CampoSenha from "@/components/campo-senha";
import MolduraConta from "@/components/moldura-conta";
import OpcoesAcesso from "@/components/opcoes-acesso";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { consultarSessao, entrar, sair, EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";

export default function LoginForm({ retorno, contexto }: { retorno: string | null; contexto?: ReactNode }) {
  const router = useRouter();
  const [carregando, setCarregando] = useState(false);
  const [sessao, setSessao] = useState<"carregando" | "erro" | "visitante" | "autenticado">("carregando");
  const geracaoVerificacao = useRef(0);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const verificarSessao = useCallback(async () => {
    const geracao = ++geracaoVerificacao.current;
    setSessao("carregando");
    try {
      const resposta = await consultarSessao();
      if (geracao !== geracaoVerificacao.current) return;
      setSessao(resposta.autenticado ? "autenticado" : "visitante");
      if (resposta.autenticado && retorno) router.replace(retorno);
    } catch {
      if (geracao === geracaoVerificacao.current) setSessao("erro");
    }
  }, [retorno, router]);

  useEffect(() => {
    const inicio = window.setTimeout(() => void verificarSessao(), 0);
    const invalidar = () => { ++geracaoVerificacao.current; };
    const visibilidade = () => {
      if (document.visibilityState === "visible") void verificarSessao();
      else invalidar();
    };
    window.addEventListener(EVENTO_SESSAO_ALTERADA, verificarSessao);
    window.addEventListener("focus", verificarSessao);
    window.addEventListener("pageshow", verificarSessao);
    document.addEventListener("visibilitychange", visibilidade);
    return () => {
      invalidar();
      window.clearTimeout(inicio);
      window.removeEventListener(EVENTO_SESSAO_ALTERADA, verificarSessao);
      window.removeEventListener("focus", verificarSessao);
      window.removeEventListener("pageshow", verificarSessao);
      document.removeEventListener("visibilitychange", visibilidade);
    };
  }, [verificarSessao]);

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
      ++geracaoVerificacao.current;
      setSessao("autenticado");
      if (retorno) {
        router.replace(retorno);
        return;
      }
      setMensagem(resposta.message);
    } catch (falha) {
      setSessao("visitante");
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
      ++geracaoVerificacao.current;
      setSessao("visitante");
      setMensagem(resposta.message);
    } catch {
      setErro("Não foi possível encerrar a sessão agora.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <MolduraConta titulo={sessao === "visitante" ? "Entrar" : "Minha conta"} descricao={sessao === "autenticado" ? "Você já está conectado ao UnDb." : sessao === "visitante" ? "Use sua conta institucional para registrar avaliações. As consultas continuam públicas." : "Aguarde a verificação da sessão antes de continuar."} retorno={retorno} contexto={contexto} rotulo="Acesso à conta">
        {sessao === "visitante" && <OpcoesAcesso atual="login" retorno={retorno} />}
        {sessao === "carregando" ? (
          <p className="text-sm text-(--muted)" role="status">Verificando sessão…</p>
        ) : sessao === "erro" ? (
          <div className="flex flex-col gap-4">
            <p className="status-box error" role="alert">Não foi possível verificar a sessão agora. Isso não significa que você saiu da conta.</p>
            <button type="button" className="button" onClick={() => void verificarSessao()}>Verificar sessão novamente</button>
          </div>
        ) : sessao === "visitante" ? (
          <form onSubmit={enviar} className="flex min-w-0 flex-col gap-5">
            <label className="underline-field">
              <span className="label-mono">E-mail institucional</span>
              <input
                name="email"
                type="email"
                inputMode="email"
                autoComplete="email"
                required
                maxLength={150}
                placeholder="seu-email@aluno.unb.br"
              />
            </label>

            <CampoSenha />

            <button
              type="submit"
              disabled={carregando}
              className="button primary mt-2"
            >
              {carregando ? "Entrando…" : "Entrar"}
            </button>
          </form>
        ) : (
          <div className="flex min-w-0 flex-col gap-4 rounded-xl border border-(--border) bg-(--panel) p-4">
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

        {sessao === "visitante" && <p className="text-center text-sm leading-relaxed text-(--ink-soft)">
          Ainda não possui conta?{" "}
          <Link href={retorno ? `/cadastro?returnTo=${encodeURIComponent(retorno)}` : "/cadastro"} className="link font-medium">
            Criar conta
          </Link>
        </p>}

        <div aria-live="polite" className="min-w-0 break-words">
          {mensagem && (
            <p className="status-box success">{mensagem}</p>
          )}
          {erro && <p className="status-box error">{erro}</p>}
        </div>
    </MolduraConta>
  );
}
