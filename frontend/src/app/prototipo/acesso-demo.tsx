"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useContaDemo } from "./conta-demo";

const acao = "rounded-lg bg-accent px-4 py-2.5 text-center text-sm font-medium text-on-accent hover:opacity-90";
const campo = "w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5";

export default function AcessoDemo({ retorno, temAvaliacao }: { retorno: string; temAvaliacao: boolean }) {
  const { estado, alterarEstado } = useContaDemo();
  const router = useRouter();
  const [modo, setModo] = useState<"entrar" | "cadastro">("entrar");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const nome = useRef<HTMLInputElement>(null);
  const email = useRef<HTMLInputElement>(null);
  const senha = useRef<HTMLInputElement>(null);

  function conferir() {
    if (modo === "cadastro" && !nome.current?.value.trim()) {
      setMensagem("Informe um nome fictício para experimentar o cadastro.");
      nome.current?.focus();
      return;
    }
    if (!email.current?.reportValidity() || !senha.current?.reportValidity()) return;
    setMostrarSenha(false);
    setMensagem("");
    if (modo === "cadastro") {
      alterarEstado("pendente");
    } else {
      alterarEstado("confirmada");
      router.push(retorno);
    }
  }

  function confirmar() {
    alterarEstado("confirmada");
    router.push(retorno);
  }

  function sair() {
    alterarEstado("visitante");
    setModo("entrar");
    setMostrarSenha(false);
    setMensagem("Você saiu da conta demonstrativa. Nenhuma sessão real foi alterada.");
  }

  return <div className="flex max-w-2xl flex-col gap-5">
    <p className="rounded-lg bg-accent/5 p-4 text-sm text-foreground/70">Área demonstrativa. Use dados fictícios: nenhuma conta ou sessão real é criada. O cenário reinicia ao recarregar a página.</p>
    {estado === "visitante" ? <section className="rounded-xl border border-foreground/10 p-5" aria-labelledby="acesso-demo-titulo">
      <div role="group" aria-label="Opções de acesso" className="mb-5 flex flex-wrap gap-2">
        {(["entrar", "cadastro"] as const).map((opcao) => <button key={opcao} type="button" aria-pressed={modo === opcao}
          onClick={() => { setModo(opcao); setMensagem(""); setMostrarSenha(false); }}
          className={modo === opcao ? acao : "rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium"}>
          {opcao === "entrar" ? "Entrar" : "Criar conta"}
        </button>)}
      </div>
      <h2 id="acesso-demo-titulo" className="text-lg font-semibold">{modo === "entrar" ? "Entre na sua conta" : "Crie sua conta"}</h2>
      <p id="acesso-demo-ajuda" className="mt-2 text-sm text-foreground/70">{modo === "entrar"
        ? "Este exemplo representa uma conta com e-mail já confirmado. Após simular a entrada, você retoma o que estava fazendo."
        : "No sistema real, o cadastro usa nome, e-mail institucional e senha. Depois, é preciso confirmar o e-mail antes de enviar avaliações."}</p>
      <div role="group" aria-label="Demonstração de acesso" aria-describedby="acesso-demo-ajuda" className="mt-5 flex flex-col gap-4">
        {modo === "cadastro" && <label className="flex flex-col gap-2"><span className="text-sm font-medium">Nome de exemplo</span>
          <input ref={nome} name="nome-demo" autoComplete="off" required maxLength={100} className={campo} />
        </label>}
        <label className="flex flex-col gap-2"><span className="text-sm font-medium">E-mail institucional de exemplo</span>
          <input ref={email} type="email" name="email-demo" autoComplete="off" required maxLength={150} pattern="[^@]+@[aA][lL][uU][nN][oO][.][uU][nN][bB][.][bB][rR]" placeholder="exemplo@aluno.unb.br" className={campo} />
        </label>
        <div className="flex flex-col gap-2"><label htmlFor="senha-demo" className="text-sm font-medium">Senha de exemplo</label>
          <input ref={senha} id="senha-demo" name="senha-demo" type={mostrarSenha ? "text" : "password"} autoComplete="off" required minLength={8} maxLength={128} className={campo} />
          <button type="button" onClick={() => setMostrarSenha(!mostrarSenha)} aria-controls="senha-demo" aria-pressed={mostrarSenha}
            className="self-start rounded-lg px-2 py-2 text-sm font-medium text-accent underline underline-offset-4">{mostrarSenha ? "Ocultar senha" : "Mostrar senha"}</button>
        </div>
        <button type="button" onClick={conferir} className={acao}>{modo === "entrar" ? "Simular entrada" : "Simular criação de conta"}</button>
      </div>
    </section> : <section className="rounded-xl border border-foreground/10 p-5" aria-labelledby="conta-demo-titulo">
      <h2 id="conta-demo-titulo" className="text-lg font-semibold">Seu acesso</h2>
      <dl className="mt-4 flex flex-col gap-3 text-sm">
        <div><dt className="text-foreground/70">Conta</dt><dd className="font-medium">Conta fictícia de estudante</dd></div>
        <div><dt className="text-foreground/70">Confirmação de e-mail</dt><dd className="font-medium">{estado === "pendente" ? "Ainda não confirmado" : "Confirmado"}</dd></div>
      </dl>
      {estado === "pendente" ? <>
        <p className="mt-4 text-sm text-foreground/70">Cadastro demonstrado. No sistema real, use o link de confirmação para liberar o envio de avaliações. Você continua podendo consultar e comparar sem confirmar o e-mail.</p>
        <button type="button" onClick={confirmar} className={`${acao} mt-5`}>Simular confirmação do e-mail e continuar →</button>
      </> : <>
        <p className="mt-4 text-sm text-foreground/70">Este cenário representa uma conta pronta para avaliar. A prévia continua sem envio ou gravação.</p>
        <Link href={retorno} className={`${acao} mt-5 inline-block`}>{temAvaliacao ? "Continuar avaliação escolhida →" : "Voltar à navegação →"}</Link>
      </>}
      <button type="button" onClick={sair} className="mt-5 block rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium">Sair da conta demonstrativa</button>
    </section>}
    <p role="status" className="text-sm text-foreground/70">{mensagem}</p>
    <Link href={retorno} className="self-start text-sm text-accent underline underline-offset-4">{temAvaliacao ? "Voltar à prévia da avaliação →" : "Voltar à navegação →"}</Link>
    <p className="text-sm text-foreground/70">Consultar e comparar é público. {temAvaliacao ? "Professor e disciplina continuam selecionados; nesta prévia você pode experimentar o formulário sem conta." : "Você pode continuar explorando sem criar uma conta."}</p>
  </div>;
}
