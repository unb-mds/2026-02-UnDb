import { identificadorValido } from "../identificador";
import { acoesModeracao, estadosComentario, motivosDenuncia, statusTriagem, categoriasOpenAI } from "../types/moderacao";
import type { AcaoModeracaoInput, ComentarioModeracao, DecisaoModeracao, DenunciaInterna, DenunciasDaVersao, EstadoFila, IdentidadeInterna, TriagemComentario } from "../types/moderacao";
import { apiClient } from "./api-client";

const base = "/api/moderacao/comentarios";
const registro = (valor: unknown): valor is Record<string, unknown> => typeof valor === "object" && valor !== null && !Array.isArray(valor);
const id = (valor: unknown): valor is string => typeof valor === "string" && identificadorValido(valor);
const data = (valor: unknown): valor is string => typeof valor === "string" && Number.isFinite(Date.parse(valor));
const identidade = (valor: unknown): valor is IdentidadeInterna => registro(valor) && id(valor.id) && typeof valor.nome === "string" && typeof valor.email === "string";
const estado = (valor: unknown) => estadosComentario.some((item) => item === valor);
const acao = (valor: unknown) => acoesModeracao.some((item) => item === valor);

function comentario(valor: unknown): valor is ComentarioModeracao {
  return registro(valor) && id(valor.id) && (valor.texto === null || typeof valor.texto === "string")
    && estado(valor.estado) && identidade(valor.autor) && (valor.substitui_id === null || id(valor.substitui_id)) && data(valor.created_at);
}
function decisao(valor: unknown): valor is DecisaoModeracao {
  return registro(valor) && id(valor.id) && id(valor.comentario_versao_id) && (valor.moderador_id === null || id(valor.moderador_id))
    && acao(valor.acao) && typeof valor.motivo === "string" && estado(valor.estado_anterior) && estado(valor.estado_posterior) && data(valor.created_at);
}
function denuncia(valor: unknown): valor is DenunciaInterna {
  return registro(valor) && id(valor.id) && id(valor.comentario_versao_id) && valor.estado === "EM_ABERTO"
    && motivosDenuncia.some((item) => item === valor.motivo) && data(valor.created_at)
    && (valor.denunciante === null || identidade(valor.denunciante));
}
function denuncias(valor: unknown): valor is DenunciasDaVersao {
  return registro(valor) && Array.isArray(valor.autenticadas) && valor.autenticadas.every(denuncia)
    && valor.autenticadas.every((item) => item.denunciante !== null)
    && Array.isArray(valor.visitantes) && valor.visitantes.every(denuncia) && valor.visitantes.every((item) => item.denunciante === null)
    && Number.isInteger(valor.contas_distintas) && Number(valor.contas_distintas) >= 0
    && Number.isInteger(valor.total_visitantes) && Number(valor.total_visitantes) >= 0;
}
function validar<T>(valor: unknown, guarda: (valor: unknown) => valor is T): T {
  if (!guarda(valor)) throw new Error("Resposta de moderação incompatível com o contrato.");
  return valor;
}
function caminho(versaoId: string): string {
  if (!identificadorValido(versaoId)) throw new Error("Identificador de versão inválido.");
  return `${base}/${versaoId}`;
}
const opcoes = (signal?: AbortSignal) => ({ cache: "no-store" as const, signal });

export async function listarFila(estado?: EstadoFila, signal?: AbortSignal): Promise<ComentarioModeracao[]> {
  const resposta = await apiClient.request<unknown>(base, { estado }, opcoes(signal));
  return validar(resposta, (valor): valor is ComentarioModeracao[] => Array.isArray(valor) && valor.every(comentario));
}
export async function consultarComentario(versaoId: string, signal?: AbortSignal): Promise<ComentarioModeracao> {
  const resposta = validar(await apiClient.request<unknown>(caminho(versaoId), {}, opcoes(signal)), comentario);
  if (resposta.id !== versaoId) throw new Error("A versão retornada não corresponde ao conteúdo solicitado.");
  return resposta;
}
export async function consultarDenuncias(versaoId: string, signal?: AbortSignal): Promise<DenunciasDaVersao> {
  const resposta = validar(await apiClient.request<unknown>(`${caminho(versaoId)}/denuncias`, {}, opcoes(signal)), denuncias);
  if ([...resposta.autenticadas, ...resposta.visitantes].some((item) => item.comentario_versao_id !== versaoId)) throw new Error("Denúncias de outra versão.");
  return resposta;
}
export async function consultarDecisoes(versaoId: string, signal?: AbortSignal): Promise<DecisaoModeracao[]> {
  const resposta = validar(await apiClient.request<unknown>(`${caminho(versaoId)}/decisoes`, {}, opcoes(signal)),
    (valor): valor is DecisaoModeracao[] => Array.isArray(valor) && valor.every(decisao));
  if (resposta.some((item) => item.comentario_versao_id !== versaoId)) throw new Error("Decisões de outra versão.");
  return resposta;
}
export async function executarAcao(versaoId: string, dados: AcaoModeracaoInput): Promise<DecisaoModeracao> {
  if (!acao(dados.acao) || !dados.motivo.trim()) throw new Error("Ação e motivo são obrigatórios.");
  const resposta = validar(await apiClient.post<unknown, AcaoModeracaoInput>(`${caminho(versaoId)}/acoes`,
    { acao: dados.acao, motivo: dados.motivo.trim() }, opcoes()), decisao);
  if (resposta.comentario_versao_id !== versaoId || resposta.acao !== dados.acao) throw new Error("Decisão de outra versão ou ação.");
  return resposta;
}

function triagem(valor: unknown): valor is TriagemComentario {
  const categorias = (itens: unknown) => Array.isArray(itens) && itens.length <= 7
    && itens.every((item) => motivosDenuncia.some((motivo) => motivo === item));
  return registro(valor) && id(valor.comentario_versao_id)
    && statusTriagem.some((item) => item === valor.status)
    && typeof valor.filtro_ativo === "boolean" && (valor.sinalizado === null || typeof valor.sinalizado === "boolean")
    && typeof valor.versao_lista === "string" && typeof valor.versao_integracao === "string"
    && (valor.modelo === null || typeof valor.modelo === "string")
    && categorias(valor.categorias_locais) && Array.isArray(valor.categorias_ia)
    && valor.categorias_ia.length <= 13 && valor.categorias_ia.every((c) => categoriasOpenAI.some((item) => item === c));
}

export async function analisarComentario(versaoId: string, signal?: AbortSignal): Promise<TriagemComentario> {
  const resposta = validar(await apiClient.post<unknown, Record<string, never>>(
    `${caminho(versaoId)}/triagem`, {}, opcoes(signal)), triagem);
  if (resposta.comentario_versao_id !== versaoId) throw new Error("Triagem de outra versão.");
  return resposta;
}
