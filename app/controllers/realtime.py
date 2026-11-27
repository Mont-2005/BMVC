"""Servidor WebSocket (RFC 6455) feito só com a biblioteca padrão do Python.

Roda em uma thread própria, ao lado do Bottle, em outra porta (padrão 8765).
O navegador abre ws://localhost:8765/ws e recebe os eventos em tempo real:
  - filme_criado / filme_atualizado / filme_removido  -> para todos
  - atividade (quem fez o quê)                         -> só para quem está logado
  - presenca (quantas pessoas conectadas)              -> para todos
"""
import asyncio
import base64
import hashlib
import json
import threading
import time
from http.cookies import SimpleCookie
from urllib.parse import urlparse

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"   # constante do protocolo WebSocket
MAX_CLIENTES = 200
MAX_QUADRO = 65536
HISTORICO = 15


class ServidorTempoReal():

    def __init__(self, porta, resolver_usuario, nome_cookie, host="0.0.0.0"):
        self.porta = porta
        self.host = host
        self.resolver = resolver_usuario      # session_id -> Funcionario | None
        self.nome_cookie = nome_cookie
        self.clientes = {}                    # writer -> session_id (ou None)
        self.atividades = []                  # últimas ações (só para logados)
        self.trava = threading.Lock()
        self.loop = None
        self.pronto = threading.Event()
        self.erro = None


    # ------------------------------------------------------------------
    # Ciclo de vida

    def iniciar(self):
        """Sobe o servidor em segundo plano. Retorna True se deu certo."""
        threading.Thread(target=self._executar, daemon=True).start()
        self.pronto.wait(3)
        return self.erro is None and self.loop is not None


    def _executar(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                asyncio.start_server(self._atender, self.host, self.porta))
        except OSError as erro:               # ex.: porta já em uso
            self.erro = erro
            self.pronto.set()
            return
        self.loop = loop
        self.pronto.set()
        loop.run_forever()


    # ------------------------------------------------------------------
    # API chamada pelo Bottle (outra thread)

    def publicar(self, evento, so_logados=False):
        if self.loop is None:
            return
        asyncio.run_coroutine_threadsafe(
            self._difundir(evento, so_logados), self.loop)


    def registrar_atividade(self, texto):
        entrada = {"tipo": "atividade", "texto": texto,
                   "hora": time.strftime("%H:%M:%S")}
        with self.trava:
            self.atividades.append(entrada)
            del self.atividades[:-HISTORICO]
        self.publicar(entrada, so_logados=True)


    # ------------------------------------------------------------------
    # Conexões

    def _logado(self, session_id):
        return session_id is not None and self.resolver(session_id) is not None


    def _presenca(self):
        logados = sum(1 for sid in self.clientes.values() if self._logado(sid))
        return {"tipo": "presenca", "total": len(self.clientes),
                "funcionarios": logados}


    async def _difundir(self, evento, so_logados=False):
        for writer, sid in list(self.clientes.items()):
            if so_logados and not self._logado(sid):
                continue
            await self._enviar(writer, 0x1, json.dumps(evento).encode("utf-8"))


    async def _atender(self, reader, writer):
        sid = None
        registrado = False
        try:
            ok, sid = await self._handshake(reader, writer)
            if not ok:
                return
            if len(self.clientes) >= MAX_CLIENTES:
                await self._enviar(writer, 0x8, b"\x03\xf3")   # 1011: ocupado
                return
            self.clientes[writer] = sid
            registrado = True
            await self._difundir(self._presenca())
            if self._logado(sid):
                with self.trava:
                    historico = list(self.atividades)
                for item in historico:
                    await self._enviar(writer, 0x1, json.dumps(item).encode("utf-8"))

            while True:
                quadro = await self._ler_quadro(reader)
                if quadro is None:
                    break
                opcode, dados = quadro
                if opcode == 0x8:                               # close
                    await self._enviar(writer, 0x8, dados[:2])
                    break
                if opcode == 0x9:                               # ping -> pong
                    await self._enviar(writer, 0xA, dados)
                # texto/pong do cliente: ignorado (o cliente só escuta)
        except Exception:
            pass
        finally:
            if registrado:
                self.clientes.pop(writer, None)
                await self._difundir(self._presenca())
            try:
                writer.close()
            except Exception:
                pass


    # ------------------------------------------------------------------
    # Protocolo WebSocket

    async def _recusar(self, writer, status):
        resposta = f"HTTP/1.1 {status}\r\nConnection: close\r\nContent-Length: 0\r\n\r\n"
        writer.write(resposta.encode("latin-1"))
        try:
            await writer.drain()
        except Exception:
            pass


    @staticmethod
    def _origem_ok(origem, host):
        """Só aceita páginas servidas pelo mesmo host (evita uso por outros sites)."""
        host_sem_porta = host.rsplit(":", 1)[0] if host and not host.endswith("]") else host
        return urlparse(origem).hostname == host_sem_porta


    async def _handshake(self, reader, writer):
        try:
            bruto = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 5)
        except Exception:
            return False, None
        linhas = bruto.decode("latin-1").split("\r\n")
        partes = linhas[0].split(" ")
        if len(partes) < 3 or partes[0] != "GET" or partes[1].split("?")[0] != "/ws":
            await self._recusar(writer, "404 Not Found")
            return False, None
        cab = {}
        for linha in linhas[1:]:
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                cab[chave.strip().lower()] = valor.strip()
        if (cab.get("upgrade", "").lower() != "websocket"
                or "upgrade" not in cab.get("connection", "").lower()
                or cab.get("sec-websocket-version") != "13"
                or not cab.get("sec-websocket-key")):
            await self._recusar(writer, "400 Bad Request")
            return False, None
        origem = cab.get("origin")
        if origem and not self._origem_ok(origem, cab.get("host", "")):
            await self._recusar(writer, "403 Forbidden")
            return False, None

        cookies = SimpleCookie()
        try:
            cookies.load(cab.get("cookie", ""))
        except Exception:
            pass
        sid = cookies[self.nome_cookie].value if self.nome_cookie in cookies else None

        aceite = base64.b64encode(hashlib.sha1(
            (cab["sec-websocket-key"] + GUID).encode()).digest()).decode()
        writer.write(("HTTP/1.1 101 Switching Protocols\r\n"
                      "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                      f"Sec-WebSocket-Accept: {aceite}\r\n\r\n").encode("latin-1"))
        await writer.drain()
        return True, sid


    @staticmethod
    async def _ler_quadro(reader):
        try:
            cab = await reader.readexactly(2)
            fin, opcode = cab[0] & 0x80, cab[0] & 0x0F
            mascara, tam = cab[1] & 0x80, cab[1] & 0x7F
            if tam == 126:
                tam = int.from_bytes(await reader.readexactly(2), "big")
            elif tam == 127:
                tam = int.from_bytes(await reader.readexactly(8), "big")
            # Cliente precisa mascarar; não aceitamos fragmentos nem quadros grandes
            if not mascara or not fin or tam > MAX_QUADRO:
                return None
            chave = await reader.readexactly(4)
            dados = bytearray(await reader.readexactly(tam))
            for i in range(tam):
                dados[i] ^= chave[i % 4]
            return opcode, bytes(dados)
        except (asyncio.IncompleteReadError, ConnectionError):
            return None


    @staticmethod
    async def _enviar(writer, opcode, dados):
        tam = len(dados)
        cab = bytearray([0x80 | opcode])
        if tam < 126:
            cab.append(tam)
        elif tam < 65536:
            cab.append(126)
            cab += tam.to_bytes(2, "big")
        else:
            cab.append(127)
            cab += tam.to_bytes(8, "big")
        try:
            writer.write(bytes(cab) + dados)
            await writer.drain()
        except Exception:
            pass
