/** Erro tipado para respostas HTTP da API do G7, para telas distinguirem "não encontrado" de outra falha. */
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detalhes?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }

  get naoEncontrado(): boolean {
    return this.status === 404;
  }
}
