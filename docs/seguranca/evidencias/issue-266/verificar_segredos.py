"""Inspeção limitada de blobs alcançáveis. Nunca imprime o valor de uma correspondência."""

import json
import argparse
import re
import subprocess
from pathlib import Path

raiz = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=Path(__file__).with_name("segredos-resultado.json"))
saida = parser.parse_args().output
padroes = {
    "chave_provedor": re.compile(rb"(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}|re_[A-Za-z0-9]{30,})"),
    "token_github": re.compile(rb"(?:github_pat_[A-Za-z0-9_]{40,}|gh[pousr]_[A-Za-z0-9]{30,})"),
    "chave_privada": re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
}
objetos = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=raiz).splitlines()
blobs = []
for linha in objetos:
    partes = linha.split(b" ", 1)
    if len(partes) == 2:
        blobs.append((partes[0], partes[1].decode("utf-8", errors="replace")))
processo = subprocess.Popen(["git", "cat-file", "--batch"], cwd=raiz, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
achados = []
examinados = 0
grandes = 0
for oid, caminho in blobs:
    processo.stdin.write(oid + b"\n")
    processo.stdin.flush()
    cabecalho = processo.stdout.readline().split()
    tamanho = int(cabecalho[2])
    conteudo = processo.stdout.read(tamanho)
    processo.stdout.read(1)
    if cabecalho[1] != b"blob":
        continue
    if tamanho > 2_000_000:
        grandes += 1
        continue
    examinados += 1
    tipos = [nome for nome, padrao in padroes.items() if padrao.search(conteudo)]
    if tipos:
        achados.append({"blob": oid.decode(), "arquivo": caminho, "tipos": tipos})
processo.stdin.close()
processo.wait()
relatorio = {"escopo": "refs locais alcançáveis por --all; padrões limitados; não é certificação", "blobs_examinados": examinados, "blobs_grandes_nao_analisados": grandes, "ocorrencias_para_revisao": achados}
saida.parent.mkdir(parents=True, exist_ok=True)
saida.write_text(json.dumps(relatorio,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"blobs_examinados": examinados, "grandes_nao_analisados": grandes, "ocorrencias_para_revisao": len(achados)}))
