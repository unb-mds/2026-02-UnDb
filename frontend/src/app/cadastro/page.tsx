"use client";

import { FormEvent, useState } from "react";
import { cadastrarUsuario } from "@/lib/services/auth";

export default function CadastroPage() {
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagem(null);
    setErro(null);
    const elementoFormulario = evento.currentTarget;
    const formulario = new FormData(elementoFormulario);

    try {
      const resposta = await cadastrarUsuario({
        nome: String(formulario.get("nome") ?? ""),
        email: String(formulario.get("email") ?? ""),
        senha: String(formulario.get("senha") ?? ""),
      });
      setMensagem(resposta.message);
      elementoFormulario.reset();
    } catch {
      setErro("Não foi possível realizar o cadastro agora. Tente novamente em instantes.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold">Criar conta</h1>
        <p className="mt-1 text-sm text-foreground/70">
          Use seu e-mail institucional de estudante. Você precisará confirmá-lo antes de registrar avaliações.
        </p>
      </div>

      <form onSubmit={enviar} className="flex flex-col gap-4">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium">Nome</span>
          <input
            name="nome"
            type="text"
            autoComplete="name"
            required
            maxLength={100}
            className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 outline-none focus:border-foreground/50"
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium">E-mail institucional</span>
          <input
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            required
            maxLength={150}
            pattern="^[^@\\s]+@aluno\\.unb\\.br$"
            placeholder="seu-email@aluno.unb.br"
            className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 outline-none focus:border-foreground/50"
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium">Senha</span>
          <input
            name="senha"
            type="password"
            autoComplete="new-password"
            required
            minLength={15}
            maxLength={128}
            aria-describedby="senha-ajuda"
            className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 outline-none focus:border-foreground/50"
          />
          <span id="senha-ajuda" className="text-xs text-foreground/60">
            Use entre 15 e 128 caracteres. Frases longas são bem-vindas.
          </span>
        </label>

        <button
          type="submit"
          disabled={carregando}
          className="rounded-lg bg-accent px-4 py-2.5 font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {carregando ? "Enviando…" : "Criar conta"}
        </button>
      </form>

      <div aria-live="polite">
        {mensagem && <p className="rounded-lg border border-green-600/30 bg-green-600/10 p-4 text-sm">{mensagem}</p>}
        {erro && <p className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">{erro}</p>}
      </div>
    </main>
  );
}
