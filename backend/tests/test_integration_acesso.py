import os
import socket
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from tests.integration_acesso import verificar_porta_api


class PortaIntegracaoAcessoTest(unittest.TestCase):
    def test_recusa_servico_ativo(self):
        with socket.socket() as servidor:
            servidor.bind(("127.0.0.1", 0))
            servidor.listen()
            with self.assertRaisesRegex(RuntimeError, "serviço em execução"):
                verificar_porta_api(servidor.getsockname()[1])

    def test_permite_porta_de_servidor_recem_encerrado(self):
        # Exercita conexão real e fechamento ativo do servidor: no Linux isso
        # pode manter a conexão em TIME_WAIT, mas não há mais listener na porta.
        with socket.socket() as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind(("127.0.0.1", 0))
            porta = servidor.getsockname()[1]
            servidor.listen()
            with socket.create_connection(("127.0.0.1", porta), timeout=1) as cliente:
                aceita, _ = servidor.accept()
                with aceita:
                    aceita.shutdown(socket.SHUT_RDWR)
                self.assertEqual(cliente.recv(1), b"")
        verificar_porta_api(porta)
