"""Avaliação exploratória com casos sintéticos; rótulos propostos, não homologados."""

import argparse
import json
from pathlib import Path

from app.domain.triagem_comentario import categorias_lexicais, contem_dados_sensiveis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--openai",
        action="store_true",
        help="consulta a Moderation API gratuita apenas com os casos sintéticos incluídos",
    )
    args = parser.parse_args()
    if args.openai:
        from app.services import openai_triagem
        from app.core import config
        from app.services.triagem_service import LimiteChamadas

        limite = LimiteChamadas()
    if args.openai and not (
        config.MODERACAO_IA_ATIVA and config.MODERACAO_IA_DADOS_APROVADOS and config.OPENAI_API_KEY
    ):
        parser.error("configure chave e flags no ambiente privado antes de usar --openai")
    casos = json.loads(
        (Path(__file__).resolve().parents[2] / "tests/fixtures/triagem_sintetica.json").read_text()
    )
    totais = {
        "analisados": 0,
        "falsos_positivos": 0,
        "falsos_negativos": 0,
        "sinalizados": 0,
        "nao_analisados": 0,
    }
    for caso in casos:
        if args.openai:
            if contem_dados_sensiveis(caso["texto"]) or not limite.reservar(
                config.MODERACAO_IA_POR_MINUTO, config.MODERACAO_IA_POR_DIA
            ):
                totais["nao_analisados"] += 1
                print(
                    json.dumps({"id": caso["id"], "status": "nao enviado: privacidade ou limite"})
                )
                continue
            try:
                resultado = openai_triagem.classificar(
                    caso["texto"],
                    chave=config.OPENAI_API_KEY,
                    modelo=config.OPENAI_MODERACAO_MODEL,
                    timeout=max(1, min(config.MODERACAO_IA_TIMEOUT, 30)),
                )
            except openai_triagem.TriagemIndisponivel:
                totais["nao_analisados"] += 1
                print(json.dumps({"id": caso["id"], "status": "indisponivel"}))
                continue
            categorias, sinalizado = [c.value for c in resultado.categorias], resultado.sinalizado
        else:
            categorias = categorias_lexicais(caso["texto"])
            sinalizado = bool(categorias)
        fp = sorted(
            set(categorias) - set(caso["categorias_openai"] if args.openai else caso["categorias"])
        )
        fn = sorted(
            set(caso["categorias_openai"] if args.openai else caso["categorias"]) - set(categorias)
        )
        totais["analisados"] += 1
        totais["falsos_positivos"] += len(fp)
        totais["falsos_negativos"] += len(fn)
        totais["sinalizados"] += int(sinalizado)
        print(
            json.dumps(
                {
                    "id": caso["id"],
                    "categorias": categorias,
                    "fp": fp,
                    "fn": fn,
                    "sinalizado": sinalizado,
                }
            )
        )
    print(
        json.dumps(
            {
                "modo": "openai" if args.openai else "lexical",
                "rotulos": "propostos; revisar com humanos",
                **totais,
            }
        )
    )


if __name__ == "__main__":
    main()
