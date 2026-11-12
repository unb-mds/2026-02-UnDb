"use client";

import CampoSenha from "@/components/campo-senha";
import MolduraConta from "@/components/moldura-conta";
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
    <MolduraConta titulo="Criar conta" descricao="Use seu e-mail institucional de estudante. Você precisará confirmá-lo antes de registrar avaliações." retorno={retorno} contexto={contexto} rotulo="Cadastro de conta">
        <OpcoesAcesso atual="cadastro" retorno={retorno} />
        <form onSubmit={enviar} className="flex min-w-0 flex-col gap-5">
          <label className="underline-field">
            <span className="label-mono">Nome</span>
            <input
              name="nome"
              type="text"
              autoComplete="name"
              required
              maxLength={100}
              aria-invalid={erroNome}
              aria-describedby={erroNome ? "nome-erro" : undefined}
              onChange={() => setErroNome(false)}
              className="aria-invalid:border-(--danger)!"
            />
            {erroNome && <span id="nome-erro" role="alert" className="mt-2 text-sm">Informe seu nome; ele não pode conter apenas espaços.</span>}
          </label>

          <label className="underline-field">
            <span className="label-mono">E-mail institucional</span>
            <input
              name="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              maxLength={150}
              pattern="[^@]+@[aA][lL][uU][nN][oO][.][uU][nN][bB][.][bB][rR]"
              placeholder="seu-email@aluno.unb.br"
            />
          </label>

          <CampoSenha cadastro />

          <button
            type="submit"
            disabled={carregando}
            className="button primary mt-2"
          >
            {carregando ? "Enviando…" : "Criar conta"}
          </button>
        </form>

        <p className="text-center text-sm leading-relaxed text-(--ink-soft)">
          Já possui uma conta?{" "}
          <Link
            href={retorno ? `/login?returnTo=${encodeURIComponent(retorno)}` : "/login"}
            className="link font-medium"
          >
            Entrar
          </Link>
        </p>

        <div aria-live="polite" className="min-w-0 break-words">
          {mensagem && <p className="status-box success">{mensagem} {retorno ? "O link de confirmação permitirá retomar esta avaliação." : "Depois de confirmar o e-mail, entre na conta para avaliar."}</p>}
          {erro && <p className="status-box error">{erro}</p>}
        </div>
    </MolduraConta>
  );
}
