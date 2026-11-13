"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { apiClient } from "@/lib/services/api-client";

/** A sessão atual não expõe papéis: a rota protegida confirma a permissão no servidor. */
function VerificarModeracao() {
  const [permitido, setPermitido] = useState(false);
  useEffect(() => {
    let ativo = true;
    let atual: AbortController | undefined;
    let geracao = 0;
    async function verificar() {
      const versao = ++geracao;
      atual?.abort();
      const controller = new AbortController();
      atual = controller;
      try {
        const fila = await apiClient.request<unknown>("/api/moderacao/comentarios", { estado: "PENDENTE" }, { cache: "no-store", signal: controller.signal });
        if (ativo && versao === geracao) setPermitido(Array.isArray(fila));
      } catch { if (ativo && versao === geracao) setPermitido(false); }
    }
    function atualizar() { setPermitido(false); void verificar(); }
    function visibilidade() { if (!document.hidden) atualizar(); }
    void verificar();
    window.addEventListener(EVENTO_SESSAO_ALTERADA, atualizar);
    window.addEventListener("focus", atualizar);
    window.addEventListener("pageshow", atualizar);
    document.addEventListener("visibilitychange", visibilidade);
    return () => { ativo = false; ++geracao; atual?.abort(); window.removeEventListener(EVENTO_SESSAO_ALTERADA, atualizar); window.removeEventListener("focus", atualizar); window.removeEventListener("pageshow", atualizar); document.removeEventListener("visibilitychange", visibilidade); };
  }, []);
  return permitido ? <Link href="/moderacao">Moderação</Link> : null;
}

export default function LinkModeracao() {
  const caminho = usePathname();
  if (caminho === "/prototipo" || caminho.startsWith("/prototipo/")) return null;
  return <VerificarModeracao key={caminho} />;
}
