"use client";

import Link from "next/link";
import MolduraConta from "@/components/moldura-conta";
import { useRef, useState, type FormEvent } from "react";
import { recuperarSenha } from "@/lib/services/auth";

export default function RecuperacaoForm() {
  const enviandoRef = useRef(false);
  const [enviando, setEnviando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviandoRef.current) return;
    const dados = new FormData(evento.currentTarget);
    enviandoRef.current = true;
    setEnviando(true);
    setErro(null);
    try {
      const resposta = await recuperarSenha(String(dados.get("email") ?? ""));
      setMensagem(resposta.message);
    } catch {
      setErro("Não foi possível solicitar a recuperação agora. Confira o e-mail institucional e tente novamente.");
    } finally {
      enviandoRef.current = false;
      setEnviando(false);
    }
  }

  return <MolduraConta titulo="Esqueci minha senha" descricao="Informe seu e-mail institucional para receber um link de recuperação." retorno={null} rotulo="Esqueci minha senha">
    {!mensagem && <form onSubmit={enviar} aria-busy={enviando} className="flex min-w-0 flex-col gap-5">
      <label className="underline-field">
        <span className="text-sm font-medium text-(--ink-soft)">E-mail institucional</span>
        <input name="email" type="email" autoComplete="email" required maxLength={150} placeholder="seu-email@aluno.unb.br" />
      </label>
      <button type="submit" disabled={enviando} className="button primary mt-2">{enviando ? "Solicitando…" : "Enviar link de recuperação"}</button>
    </form>}
    <div role="status" className="text-sm text-(--ink-soft)">
      {mensagem && <><p>{mensagem}</p><p className="mt-2">Confira também a pasta de spam. O link vale por uma hora.</p></>}
    </div>
    {erro && <p role="alert" className="status-box error">{erro}</p>}
    <Link href="/login" className="link self-center text-sm">Voltar para entrar</Link>
  </MolduraConta>;
}
