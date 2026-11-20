"use client";

import CampoSenha from "@/components/campo-senha";
import MolduraConta from "@/components/moldura-conta";
import OpcoesAcesso from "@/components/opcoes-acesso";

import Link from "next/link";
import { useRef, useState, type FormEvent, type ReactNode } from "react";
import { cadastrarUsuario } from "@/lib/services/auth";
import { ApiError, mensagemErroTemporario } from "@/lib/services/http-error";
import { TERMOS_VERSAO } from "@/lib/termos";

export default function CadastroForm({ retorno, contexto }: { retorno: string | null; contexto?: ReactNode }) {
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [erroNome, setErroNome] = useState(false);
  const enviandoRef = useRef(false);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviandoRef.current) return;
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

    if (formulario.get("ciencia_termos") !== "on") {
      setErro("Confirme a ciência dos Termos de Uso para criar sua conta.");
      setCarregando(false);
      (elementoFormulario.elements.namedItem("ciencia_termos") as HTMLInputElement).focus();
      return;
    }

    enviandoRef.current = true;
    try {
      const resposta = await cadastrarUsuario({
        nome,
        ciencia_termos: true,
        termos_versao: TERMOS_VERSAO,
        email: String(formulario.get("email") ?? "").trim().toLowerCase(),
        senha: String(formulario.get("senha") ?? ""),
        ...(retorno ? { return_to: retorno } : {}),
      });
      setMensagem(resposta.message);
      elementoFormulario.reset();
    } catch (falha) {
      setErro(mensagemErroTemporario(falha) ?? (falha instanceof ApiError && falha.status === 422
        ? `Revise os dados do cadastro. ${falha.message}`
        : "Não foi possível realizar o cadastro agora. Tente novamente em instantes."));
    } finally {
      enviandoRef.current = false;
      setCarregando(false);
    }
  }

  return (
    <MolduraConta titulo="Criar conta" descricao="Use seu e-mail institucional da UnB. Você receberá um link para confirmar o endereço antes de avaliar." retorno={retorno} contexto={contexto} opcoes={<OpcoesAcesso atual="cadastro" retorno={retorno} />} rotulo="Cadastro de conta">
        <form onSubmit={enviar} aria-busy={carregando} className="flex min-w-0 flex-col gap-5">
          <label className="underline-field">
            <span className="text-sm font-medium text-(--ink-soft)">Nome</span>
            <input
              name="nome"
              type="text"
              autoComplete="name"
              required
              placeholder="Como você quer ser identificado"
              maxLength={100}
              aria-invalid={erroNome}
              aria-describedby={erroNome ? "nome-erro" : undefined}
              onChange={() => setErroNome(false)}
              className="aria-invalid:border-(--danger)!"
            />
            {erroNome && <span id="nome-erro" role="alert" className="mt-2 text-sm">Informe seu nome; ele não pode conter apenas espaços.</span>}
          </label>

          <label className="underline-field">
            <span className="text-sm font-medium text-(--ink-soft)">E-mail institucional</span>
            <input
              name="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              maxLength={150}
              pattern="[^@]+@[aA][lL][uU][nN][oO][.][uU][nN][bB][.][bB][rR]"
              title="Use seu e-mail institucional com domínio @aluno.unb.br."
              placeholder="seu-email@aluno.unb.br"
            />
          </label>

          <CampoSenha cadastro />

          <div className="space-y-3 text-sm leading-relaxed text-(--ink-soft)">
            <div className="flex items-start gap-3">
              <input id="ciencia-termos" name="ciencia_termos" type="checkbox" required
                aria-describedby="ciencia-termos-ajuda"
                className="mt-1 size-5 shrink-0 accent-accent focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent" />
              <label htmlFor="ciencia-termos">Li e estou ciente dos <Link href="/termos-de-uso" target="_blank" rel="noopener noreferrer" className="link">Termos de Uso (abre em outra aba)</Link>, versão {TERMOS_VERSAO}.</label>
            </div>
            <p id="ciencia-termos-ajuda">Veja como seus dados são usados na <Link href="/privacidade" target="_blank" rel="noopener noreferrer" className="link">Política de Privacidade (abre em outra aba)</Link>. Esta ciência não é consentimento genérico para tratamento de dados.</p>
          </div>

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
    <Link href={retorno ? `/reenviar-confirmacao?returnTo=${encodeURIComponent(retorno)}` : "/reenviar-confirmacao"} className="link self-center text-center text-sm">Não recebeu a confirmação de e-mail?</Link>
    </MolduraConta>
  );
}
