"use client";

import CampoSenha from "@/components/campo-senha";
import OpcoesAcesso from "@/components/opcoes-acesso";

import Link from "next/link";
import { useState, type FormEvent, type ReactNode } from "react";
import { cadastrarUsuario } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";

export default function CadastroForm({ retorno, contexto }: { retorno: string | null; contexto?: ReactNode }) {
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [erroNome, setErroNome] = useState(false);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagem(null);
    setErro(null);
    const elementoFormulario = evento.currentTarget;
    const formulario = new FormData(elementoFormulario);
    const nome = String(formulario.get("nome") ?? "").trim();
    setErroNome(!nome);
    if (!nome) {
      setCarregando(false);
      (elementoFormulario.elements.namedItem("nome") as HTMLInputElement).focus();
      return;
    }

    try {
      const resposta = await cadastrarUsuario({
        nome,
        email: String(formulario.get("email") ?? "").trim().toLowerCase(),
        senha: String(formulario.get("senha") ?? ""),
        ...(retorno ? { return_to: retorno } : {}),
      });
      setMensagem(resposta.message);
      elementoFormulario.reset();
    } catch (falha) {
      setErro(falha instanceof ApiError && falha.status === 422
        ? `Revise os dados do cadastro. ${falha.message}`
        : "Não foi possível realizar o cadastro agora. Tente novamente em instantes.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="container flex max-w-xl min-w-0 flex-1 flex-col gap-6 py-10 sm:py-14">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Criar conta</h1>
        <p className="mt-2 text-sm leading-relaxed text-(--muted)">
          Use seu e-mail institucional de estudante. Você precisará confirmá-lo antes de registrar avaliações.
        </p>
      </div>

      {contexto}
      <section className="panel flex min-w-0 flex-col gap-6 p-4 sm:p-6" aria-label="Cadastro de conta">
        <OpcoesAcesso atual="cadastro" retorno={retorno} />
        <form onSubmit={enviar} className="flex min-w-0 flex-col gap-5">
          <label className="flex min-w-0 flex-col gap-2">
            <span className="text-sm font-medium">Nome</span>
            <input
              name="nome"
              type="text"
              autoComplete="name"
              required
              maxLength={100}
              aria-invalid={erroNome}
              aria-describedby={erroNome ? "nome-erro" : undefined}
              onChange={() => setErroNome(false)}
              className="min-h-11 w-full min-w-0 rounded-lg border border-(--control-border) bg-(--raised) px-4 py-3 text-base text-foreground focus:border-accent aria-invalid:border-(--danger)"
            />
            {erroNome && <span id="nome-erro" role="alert" className="text-sm text-red-600 dark:text-red-400">Informe seu nome; ele não pode conter apenas espaços.</span>}
          </label>

          <label className="flex min-w-0 flex-col gap-2">
            <span className="text-sm font-medium">E-mail institucional</span>
            <input
              name="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              maxLength={150}
              pattern="[^@]+@[aA][lL][uU][nN][oO][.][uU][nN][bB][.][bB][rR]"
              placeholder="seu-email@aluno.unb.br"
              className="min-h-11 w-full min-w-0 rounded-lg border border-(--control-border) bg-(--raised) px-4 py-3 text-base text-foreground placeholder:text-(--muted) focus:border-accent"
            />
          </label>

          <CampoSenha cadastro />

          <button
            type="submit"
            disabled={carregando}
            className="button primary"
          >
            {carregando ? "Enviando…" : "Criar conta"}
          </button>
        </form>

        <p className="text-sm leading-relaxed text-(--muted)">
          Já possui uma conta?{" "}
          <Link
            href={retorno ? `/login?returnTo=${encodeURIComponent(retorno)}` : "/login"}
            className="font-medium text-accent underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Entrar
          </Link>
        </p>

        <div aria-live="polite" className="min-w-0 break-words">
          {mensagem && <p className="rounded-lg border border-green-600/30 bg-green-600/10 p-4 text-sm">{mensagem} {retorno ? "O link de confirmação permitirá retomar esta avaliação." : "Depois de confirmar o e-mail, entre na conta para avaliar."}</p>}
          {erro && <p className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">{erro}</p>}
        </div>
      </section>
    </main>
  );
}
