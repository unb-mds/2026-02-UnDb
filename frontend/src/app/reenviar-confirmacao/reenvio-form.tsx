"use client";

import Link from "next/link";
import { useRef, useState, type FormEvent } from "react";
import MolduraConta from "@/components/moldura-conta";
import { reenviarConfirmacao } from "@/lib/services/auth";
import { mensagemErroTemporario } from "@/lib/services/http-error";

export default function ReenvioForm({ retorno }: { retorno: string | null }) {
  const trava = useRef(false);
  const [enviando, setEnviando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (trava.current) return;
    const email = String(new FormData(evento.currentTarget).get("email") ?? "");
    trava.current = true;
    setEnviando(true);
    setErro(null);
    setMensagem(null);
    try {
      const resposta = await reenviarConfirmacao(email, retorno);
      setMensagem(resposta.message);
    } catch (falha) {
      setErro(mensagemErroTemporario(falha) ?? "Não foi possível solicitar o link agora. Confira seu e-mail institucional e tente novamente.");
    } finally {
      trava.current = false;
      setEnviando(false);
    }
  }

  return <MolduraConta titulo="Confirme seu e-mail" descricao="Não recebeu o link ou ele expirou? Solicite uma nova confirmação para sua conta institucional." retorno={retorno} rotulo="Reenvio de confirmação">
    <form onSubmit={enviar} aria-busy={enviando} className="flex min-w-0 flex-col gap-5">
      <label className="underline-field"><span className="text-sm font-medium text-(--ink-soft)">E-mail institucional</span><input name="email" type="email" autoComplete="email" required maxLength={150} placeholder="seu-email@aluno.unb.br" /></label>
      <button type="submit" disabled={enviando} className="button primary">{enviando ? "Solicitando…" : "Reenviar link de confirmação"}</button>
    </form>
    <div role="status">{mensagem && <div className="status-box success"><p>{mensagem}</p><p className="mt-2">Confira também a pasta de spam. O link vale por 24 horas.</p></div>}</div>
    {erro && <p role="alert" className="status-box error">{erro}</p>}
    <Link href={retorno ? `/login?returnTo=${encodeURIComponent(retorno)}` : "/login"} className="link self-center text-sm">Voltar para minha conta</Link>
  </MolduraConta>;
}
