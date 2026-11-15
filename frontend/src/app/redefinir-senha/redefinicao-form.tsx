"use client";

import Link from "next/link";
import MolduraConta from "@/components/moldura-conta";
import { useRef, useState, type FormEvent } from "react";
import CampoSenha from "@/components/campo-senha";
import { redefinirSenha } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";

export default function RedefinicaoForm({ token }: { token: string | null }) {
  const enviandoRef = useRef(false);
  const [enviando, setEnviando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [invalido, setInvalido] = useState(!token);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!token || enviandoRef.current) return;
    const dados = new FormData(evento.currentTarget);
    const senha = String(dados.get("senha") ?? "");
    setErro(null);
    if (senha !== dados.get("confirmacao")) {
      setErro("As senhas não coincidem. Confira os dois campos.");
      return;
    }
    enviandoRef.current = true;
    setEnviando(true);
    try {
      const resposta = await redefinirSenha(token, senha);
      setMensagem(resposta.message);
      window.history.replaceState(null, "", "/redefinir-senha");
    } catch (falha) {
      if (falha instanceof ApiError && falha.status === 400) {
        setInvalido(true);
      } else {
        setErro("Não foi possível redefinir a senha agora. Tente novamente.");
      }
    } finally {
      enviandoRef.current = false;
      setEnviando(false);
    }
  }

  return <MolduraConta titulo="Redefinir senha" descricao="Escolha uma nova senha para sua conta." retorno={null} rotulo="Redefinir senha">
    {invalido ? <div role="alert" className="status-box error flex flex-col gap-3">
      <p>Link de recuperação inválido ou expirado. Solicite um novo link.</p>
      <Link href="/esqueci-senha" className="link">Solicitar novo link</Link>
    </div> : mensagem ? <p role="status" className="status-box success">{mensagem}</p> : <form onSubmit={enviar} aria-busy={enviando} className="flex min-w-0 flex-col gap-5">
      <CampoSenha cadastro />
      <label className="underline-field">
        <span className="text-sm font-medium text-(--ink-soft)">Confirmar nova senha</span>
        <input name="confirmacao" type="password" autoComplete="new-password" required minLength={8} maxLength={128} />
      </label>
      <button type="submit" disabled={enviando} className="button primary mt-2">{enviando ? "Salvando…" : "Salvar nova senha"}</button>
    </form>}
    {erro && <p role="alert" className="status-box error">{erro}</p>}
    <Link href="/login" className="link self-center text-sm">Voltar para entrar</Link>
  </MolduraConta>;
}
