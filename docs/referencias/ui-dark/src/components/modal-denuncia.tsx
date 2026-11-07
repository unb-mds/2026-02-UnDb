"use client";

import { useEffect, useState, useRef } from "react";
import {
  motivosDenuncia,
  ROTULOS_MOTIVOS_DENUNCIA,
  type MotivoDenuncia,
} from "@/lib/types/denuncia";
import { registrarDenuncia } from "@/lib/services/denuncias";
import { ApiError } from "@/lib/services/http-error";

type ModalDenunciaProps = {
  versaoId: string;
  aberto: boolean;
  aoFechar: () => void;
};

function ConteudoModalDenuncia({
  versaoId,
  aoFechar,
}: {
  versaoId: string;
  aoFechar: () => void;
}) {
  const [motivoSelecionado, setMotivoSelecionado] = useState<MotivoDenuncia | "">("");
  const [enviando, setEnviando] = useState(false);
  const [mensagemSucesso, setMensagemSucesso] = useState<string | null>(null);
  const [mensagemErro, setMensagemErro] = useState<string | null>(null);

  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
  }, []);

  const tratarCancel = (e: React.SyntheticEvent) => {
    e.preventDefault();
    if (!enviando) {
      aoFechar();
    }
  };

  const submeter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!motivoSelecionado || enviando) return;

    setEnviando(true);
    setMensagemErro(null);

    try {
      const resposta = await registrarDenuncia(versaoId, {
        motivo: motivoSelecionado,
      });
      setMensagemSucesso(resposta.mensagem || "Denúncia registrada. Obrigado por contribuir.");
    } catch (erro) {
      if (erro instanceof ApiError) {
        if (erro.status === 404) {
          setMensagemErro("Este comentário não está mais disponível para denúncia.");
        } else if (erro.status === 409) {
          setMensagemErro("Você já possui uma denúncia aberta para este comentário.");
        } else if (erro.status === 422) {
          setMensagemErro("Motivo inválido para a denúncia.");
        } else {
          setMensagemErro(erro.message || "Erro ao processar a denúncia.");
        }
      } else if (erro instanceof Error) {
        setMensagemErro(erro.message);
      } else {
        setMensagemErro("Não foi possível enviar a denúncia. Tente novamente.");
      }
    } finally {
      setEnviando(false);
    }
  };

  return (
    <dialog
      ref={dialogRef}
      onCancel={tratarCancel}
      className="fixed inset-0 z-50 m-auto w-full max-w-lg rounded-2xl border border-foreground/15 bg-background p-6 text-foreground shadow-2xl backdrop:bg-black/60 backdrop:backdrop-blur-xs"
      aria-labelledby="titulo-denuncia"
    >
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id="titulo-denuncia" className="text-xl font-semibold">
              Denunciar comentário
            </h2>
            <p className="mt-1 text-xs text-foreground/70">
              Versão do comentário: <span className="font-mono">{versaoId}</span>
            </p>
          </div>
          <button
            type="button"
            onClick={aoFechar}
            disabled={enviando}
            aria-label="Fechar diálogo de denúncia"
            className="rounded-lg p-1.5 text-foreground/60 transition hover:bg-foreground/10 hover:text-foreground disabled:opacity-50"
          >
            ✕
          </button>
        </div>

        {mensagemSucesso ? (
          <div className="flex flex-col gap-4 py-2" role="status">
            <div className="rounded-lg border border-green-500/30 bg-green-500/10 p-4 text-sm text-green-700 dark:text-green-300">
              <p className="font-medium">{mensagemSucesso}</p>
            </div>
            <button
              type="button"
              onClick={aoFechar}
              className="self-end rounded-lg bg-accent px-4 py-2 text-sm font-medium text-on-accent transition hover:opacity-90"
            >
              Fechar
            </button>
          </div>
        ) : (
          <form onSubmit={submeter} className="flex flex-col gap-4">
            <p className="text-sm text-foreground/80">
              Selecione o motivo que melhor descreve o problema com este comentário. Não é necessário fornecer justificativa livre.
            </p>

            {mensagemErro && (
              <div
                role="alert"
                className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-600 dark:text-red-400"
              >
                {mensagemErro}
              </div>
            )}

            <fieldset className="flex flex-col gap-2.5">
              <legend className="mb-1 text-sm font-medium">Motivo da denúncia:</legend>
              {motivosDenuncia.map((motivo) => {
                const id = `motivo-${motivo}`;
                return (
                  <label
                    key={motivo}
                    htmlFor={id}
                    className="flex cursor-pointer items-center gap-3 rounded-lg border border-foreground/10 p-3 text-sm transition hover:bg-foreground/5 has-checked:border-accent has-checked:bg-accent/5"
                  >
                    <input
                      type="radio"
                      id={id}
                      name="motivoDenuncia"
                      value={motivo}
                      checked={motivoSelecionado === motivo}
                      onChange={() => setMotivoSelecionado(motivo)}
                      disabled={enviando}
                      className="size-4 accent-accent"
                    />
                    <span>{ROTULOS_MOTIVOS_DENUNCIA[motivo]}</span>
                  </label>
                );
              })}
            </fieldset>

            <div className="mt-2 flex items-center justify-end gap-3 border-t border-foreground/10 pt-4">
              <button
                type="button"
                onClick={aoFechar}
                disabled={enviando}
                className="rounded-lg border border-foreground/20 px-4 py-2 text-sm font-medium text-foreground transition hover:bg-foreground/5 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={!motivoSelecionado || enviando}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {enviando ? "Enviando..." : "Confirmar denúncia"}
              </button>
            </div>
          </form>
        )}
      </div>
    </dialog>
  );
}

export default function ModalDenuncia({
  versaoId,
  aberto,
  aoFechar,
}: ModalDenunciaProps) {
  if (!aberto) return null;
  return <ConteudoModalDenuncia versaoId={versaoId} aoFechar={aoFechar} />;
}
