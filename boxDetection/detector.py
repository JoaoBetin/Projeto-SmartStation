"""
Smart Station - Módulo de Visão Computacional
=============================================
Responsável por detectar caixas de papelão via câmera,
calcular os tempos de entrada, saída e permanência,
e enviar os dados para a API Java.

Dependências:
    pip install opencv-python ultralytics requests
"""

import cv2
import time
import logging
import requests
import os
from datetime import date, datetime, time as dtime
from ultralytics import YOLO
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("smart_station.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------------------

CAMERA_SOURCE: int | str = 0

API_BASE_URL = "http://localhost:8080"

# ID do funcionário fixo para testes (Long no backend)
FUNCIONARIO_ID: int = 1

# ── Parâmetros de confirmação de ENTRADA ─────────────────────────────────

# Número mínimo de frames CONSECUTIVOS com detecção para confirmar entrada.
MIN_FRAMES_TO_CONFIRM = 10

# Confiança mínima do modelo YOLO para considerar uma detecção válida.
MIN_CONFIDENCE = 0.60

# Tempo mínimo (em segundos) de presença contínua para confirmar entrada.
MIN_SECONDS_TO_CONFIRM = 1.5

# Frames perdidos tolerados durante a janela de confirmação.
MAX_MISSED_FRAMES_DURING_CONFIRM = 2

# ── Parâmetros de confirmação de SAÍDA ───────────────────────────────────

# Tempo (em segundos) sem detecção para confirmar saída da caixa.
BOX_ABSENCE_TIMEOUT = 4.0

# Frames consecutivos sem detecção para iniciar contagem de saída.
MIN_ABSENT_FRAMES_TO_TIMEOUT = 5

# ── Parâmetros de ociosidade ──────────────────────────────────────────────

# Intervalo mínimo de ociosidade (segundos) para ser contabilizado.
IDLE_MIN_SECONDS = 5.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YOLO_MODEL = os.path.join(BASE_DIR, "best.pt")

# IDs de classe que representam caixas no modelo
CARDBOARD_CLASS_IDS = [0]

# Fuso horário local
TZ_LOCAL = datetime.now().astimezone().tzinfo


# ---------------------------------------------------------------------------
# Estrutura de dados — Caixa rastreada
# ---------------------------------------------------------------------------

@dataclass
class TrackedBox:
    """
    Representa uma caixa detectada sendo monitorada.

    Nota: o ID é gerado pelo backend (Long/auto-increment).
    O campo backend_id é preenchido após o envio bem-sucedido à API.
    """

    backend_id: Optional[int] = None           # ID retornado pelo backend (Long)
    entry_time: Optional[datetime] = None      # Momento confirmado de entrada
    exit_time: Optional[datetime] = None       # Momento confirmado de saída

    # Controle interno
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    frames_detected: int = 0
    frames_absent: int = 0
    missed_during_confirm: int = 0

    confirmed: bool = False
    sent_to_api: bool = False


# ---------------------------------------------------------------------------
# Cliente da API
# ---------------------------------------------------------------------------

class ApiClient:
    """Encapsula toda comunicação com a API Java."""

    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url
        self.timeout = timeout

    # ── Sessão ────────────────────────────────────────────────────────

    def criar_sessao(self, funcionario_id: int) -> Optional[int]:
        """
        Cria uma sessão no backend.
        Retorna o ID da sessão criada (Long) ou None em caso de falha.
        """
        agora = datetime.now(TZ_LOCAL)

        payload = {
            "funcionarioID": funcionario_id,          # CORRIGIDO: era "funcionarioModel": {"id": ...}
            "data": agora.date().isoformat(),
            "horaInicio": agora.strftime("%H:%M:%S"),  # CORRIGIDO: era "hora_inicio"
            "horaFim": None,                           # CORRIGIDO: era "hora_fim"
            "tempoOcioso": None,                       # CORRIGIDO: era "tempo_ocioso"
            "totalCaixas": 0,                          # CORRIGIDO: era "total_caixas"
            "ativa": True
        }

        try:
            response = requests.post(
                f"{self.base_url}/sessao/criar",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            sessao_id = response.json().get("id")
            logger.info("[API] Sessão criada | ID: %s", sessao_id)
            return sessao_id

        except requests.exceptions.ConnectionError:
            logger.error("[API] Falha de conexão ao criar sessão.")
        except requests.exceptions.Timeout:
            logger.error("[API] Timeout ao criar sessão.")
        except requests.exceptions.HTTPError as e:
            logger.error("[API] Erro HTTP %s ao criar sessão: %s", e.response.status_code, e.response.text)
        except Exception as e:
            logger.exception("[API] Erro inesperado ao criar sessão: %s", e)

        return None

    def encerrar_sessao(self, sessao_id: int, hora_fim: datetime, tempo_ocioso_segundos: float) -> bool:
        """
        Atualiza a sessão com hora_fim e tempo_ocioso.
        """
        # Converte segundos totais para HH:mm:ss
        horas = int(tempo_ocioso_segundos // 3600)
        minutos = int((tempo_ocioso_segundos % 3600) // 60)
        segundos = int(tempo_ocioso_segundos % 60)
        tempo_ocioso_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

        payload = {
            "horaFim": hora_fim.strftime("%H:%M:%S"),  # CORRIGIDO: era "hora_fim"
            "tempoOcioso": tempo_ocioso_str,            # CORRIGIDO: era "tempo_ocioso"
            "ativa": False
        }

        try:
            response = requests.patch(
                f"{self.base_url}/sessao/alterar/{sessao_id}",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.info(
                "[API] Sessão encerrada | ID: %s | hora_fim: %s | tempo_ocioso: %s",
                sessao_id,
                payload["hora_fim"],
                tempo_ocioso_str,
            )
            return True

        except requests.exceptions.ConnectionError:
            logger.error("[API] Falha de conexão ao encerrar sessão %s.", sessao_id)
        except requests.exceptions.Timeout:
            logger.error("[API] Timeout ao encerrar sessão %s.", sessao_id)
        except requests.exceptions.HTTPError as e:
            logger.error("[API] Erro HTTP %s ao encerrar sessão: %s", e.response.status_code, e.response.text)
        except Exception as e:
            logger.exception("[API] Erro inesperado ao encerrar sessão: %s", e)

        return False

    # ── Caixa ─────────────────────────────────────────────────────────

    def registrar_caixa(self, box: "TrackedBox", sessao_id: int) -> Optional[int]:
        """
        Registra uma caixa detectada no backend.

        O endpoint já:
            - Calcula tempo_detectado automaticamente (fim - início em segundos)
            - Incrementa total_caixas na sessão
        Retorna o ID da caixa criada (Long) ou None em caso de falha.

        Nota: o campo "id" NÃO é enviado — é gerado automaticamente
        pelo banco (GenerationType.IDENTITY no backend).
        """
        if not box.entry_time or not box.exit_time:
            logger.warning("[API] Tentativa de envio com dados incompletos. Ignorando.")
            return None

        payload = {
            "sessaoId": sessao_id,
            # LocalDateTime no backend espera "yyyy-MM-ddTHH:mm:ss" (sem timezone)
            "inicio_deteccao": box.entry_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "fim_deteccao": box.exit_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        try:
            response = requests.post(
                f"{self.base_url}/caixa/detectada",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            caixa_id = response.json().get("id")
            logger.info(
                "[API] Caixa registrada | ID backend: %s | Sessão: %s | "
                "Entrada: %s | Saída: %s",
                caixa_id,
                sessao_id,
                payload["inicio_deteccao"],
                payload["fim_deteccao"],
            )
            return caixa_id

        except requests.exceptions.ConnectionError:
            logger.error("[API] Falha de conexão ao registrar caixa.")
        except requests.exceptions.Timeout:
            logger.error("[API] Timeout ao registrar caixa.")
        except requests.exceptions.HTTPError as e:
            logger.error("[API] Erro HTTP %s ao registrar caixa: %s", e.response.status_code, e.response.text)
        except Exception as e:
            logger.exception("[API] Erro inesperado ao registrar caixa: %s", e)

        return None


# ---------------------------------------------------------------------------
# Detector principal
# ---------------------------------------------------------------------------

class BoxDetector:
    """
    Gerencia o loop de captura, detecção e rastreamento de caixas de papelão.

    Ciclo de vida:
        1. __init__: carrega YOLO, abre câmera, cria sessão no backend.
        2. run():    loop principal de captura e rastreamento.
        3. _finalize(): encerra sessão no backend com hora_fim e tempo_ocioso.
    """

    def __init__(self, camera_source=CAMERA_SOURCE):
        logger.info("Carregando modelo YOLO: %s", YOLO_MODEL)
        self.model = YOLO(YOLO_MODEL)

        logger.info("Abrindo fonte de vídeo: %s", camera_source)
        self.cap = cv2.VideoCapture(camera_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera/vídeo: {camera_source}")

        self.api_client = ApiClient(API_BASE_URL)

        # ── Sessão ────────────────────────────────────────────────────
        # A sessão é criada imediatamente ao iniciar o detector.
        # O ID retornado pelo backend é armazenado e usado em todas as
        # chamadas subsequentes de caixa.
        self.sessao_id: Optional[int] = self.api_client.criar_sessao(FUNCIONARIO_ID)

        if self.sessao_id is None:
            raise RuntimeError(
                "Não foi possível criar a sessão no backend. "
                "Verifique se a API está rodando em " + API_BASE_URL
            )

        self.sessao_inicio = datetime.now(TZ_LOCAL)
        self.total_caixas: int = 0  # contagem local (espelho do backend)

        # ── Rastreamento ──────────────────────────────────────────────
        self.current_box: Optional[TrackedBox] = None

        # ── Ociosidade ────────────────────────────────────────────────
        self.idle_start: Optional[float] = None
        self.total_idle_seconds: float = 0.0
        self._start_idle_timer()   # bancada começa ociosa

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def run(self):
        """Inicia o loop de captura e detecção. Pressione 'q' para encerrar."""
        logger.info(
            "Smart Station iniciado | Sessão: %s | Funcionário: %s | Pressione 'q' para encerrar.",
            self.sessao_id,
            FUNCIONARIO_ID,
        )

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Frame não capturado. Encerrando.")
                    break

                detections = self._detect_boxes(frame)
                self._update_tracking(detections)

                annotated = self._annotate_frame(frame, detections)
                cv2.imshow("Smart Station", annotated)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Encerrando por comando do usuário.")
                    break

        finally:
            self._finalize()

    # ------------------------------------------------------------------
    # Detecção via YOLO
    # ------------------------------------------------------------------

    def _detect_boxes(self, frame) -> list[dict]:
        """Executa inferência YOLO e filtra por classe e confiança mínima."""
        results = self.model(frame, verbose=False)
        boxes = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id not in CARDBOARD_CLASS_IDS:
                    continue

                confidence = float(box.conf[0])
                if confidence < MIN_CONFIDENCE:
                    logger.debug(
                        "[YOLO] Detecção descartada: confiança %.2f < %.2f",
                        confidence, MIN_CONFIDENCE,
                    )
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": confidence,
                    "class_id": class_id,
                })

        return boxes

    # ------------------------------------------------------------------
    # Rastreamento e lógica de tempo
    # ------------------------------------------------------------------

    def _update_tracking(self, detections: list[dict]):
        """Atualiza o estado de rastreamento para o frame atual."""
        box_detected_now = len(detections) > 0
        now = time.time()

        # Nenhuma caixa rastreada, nova detecção aparece
        if self.current_box is None:
            if box_detected_now:
                self.current_box = TrackedBox()
                self.current_box.frames_detected = 1
                self.current_box.first_seen = now
                self.current_box.last_seen = now
                logger.debug("[TRACKER] Candidata iniciada — aguardando confirmação...")
                self._stop_idle_timer()
            return

        # Caixa rastreada E detecção presente
        if box_detected_now:
            self.current_box.last_seen = now
            self.current_box.frames_absent = 0

            if not self.current_box.confirmed:
                self.current_box.frames_detected += 1
                self._try_confirm_entry(now)
            return

        # Caixa rastreada MAS sem detecção neste frame
        self.current_box.frames_absent += 1

        if not self.current_box.confirmed:
            self.current_box.missed_during_confirm += 1

            if self.current_box.missed_during_confirm > MAX_MISSED_FRAMES_DURING_CONFIRM:
                logger.debug(
                    "[TRACKER] Candidata descartada: %d frames perdidos durante confirmação.",
                    self.current_box.missed_during_confirm,
                )
                self.current_box = None
                self._start_idle_timer()
            return

        # Caixa confirmada: verifica limiar de saída
        elapsed_without_detection = now - self.current_box.last_seen

        if (self.current_box.frames_absent >= MIN_ABSENT_FRAMES_TO_TIMEOUT
                and elapsed_without_detection >= BOX_ABSENCE_TIMEOUT):
            self._register_box_exit()

    def _try_confirm_entry(self, now: float):
        """Verifica se a caixa candidata atende todos os critérios de entrada."""
        box = self.current_box

        frames_ok = box.frames_detected >= MIN_FRAMES_TO_CONFIRM
        time_ok = (now - box.first_seen) >= MIN_SECONDS_TO_CONFIRM

        if frames_ok and time_ok:
            box.confirmed = True
            box.entry_time = datetime.now(TZ_LOCAL)
            logger.info(
                "[ENTRADA] CAIXA CONFIRMADA | Sessão: %s | Horário: %s | "
                "Frames: %d | Tempo de confirmação: %.2fs",
                self.sessao_id,
                box.entry_time.isoformat(),
                box.frames_detected,
                now - box.first_seen,
            )
        else:
            logger.debug(
                "[TRACKER] Confirmação pendente | Frames: %d/%d | Tempo: %.2fs/%.2fs",
                box.frames_detected, MIN_FRAMES_TO_CONFIRM,
                now - box.first_seen, MIN_SECONDS_TO_CONFIRM,
            )

    def _register_box_exit(self):
        """
        Registra a saída da caixa, calcula permanência e envia à API.

        Após o envio bem-sucedido, armazena o ID retornado pelo backend
        em box.backend_id para rastreabilidade.
        """
        box = self.current_box
        if box is None:
            return

        if not box.confirmed:
            logger.debug("[TRACKER] Candidata descartada na saída (não confirmada).")
            self.current_box = None
            self._start_idle_timer()
            return

        box.exit_time = datetime.now(TZ_LOCAL)
        permanencia = (box.exit_time - box.entry_time).total_seconds()

        logger.info(
            "[SAÍDA] CAIXA SAIU | Sessão: %s | Entrada: %s | Saída: %s | Permanência: %.2fs",
            self.sessao_id,
            box.entry_time.isoformat(),
            box.exit_time.isoformat(),
            permanencia,
        )

        # Envia à API — o backend incrementa total_caixas na sessão automaticamente
        caixa_id = self.api_client.registrar_caixa(box, self.sessao_id)

        if caixa_id is not None:
            box.backend_id = caixa_id          
            box.sent_to_api = True
            self.total_caixas += 1            
            logger.info("[TRACKER] Caixa registrada no backend | ID: %d", caixa_id)
        else:
            logger.warning(
                "[TRACKER] Falha no envio à API. Dados perdidos para a sessão %s.",
                self.sessao_id,
            )

        self.current_box = None
        self._start_idle_timer()

    # ------------------------------------------------------------------
    # Gerenciamento de ociosidade
    # ------------------------------------------------------------------

    def _start_idle_timer(self):
        if self.idle_start is None:
            self.idle_start = time.time()
            logger.debug("[OCIOSIDADE] Bancada ociosa.")

    def _stop_idle_timer(self):
        if self.idle_start is not None:
            idle_duration = time.time() - self.idle_start
            self.total_idle_seconds += idle_duration

            if idle_duration >= IDLE_MIN_SECONDS:
                logger.info(
                    "[OCIOSIDADE] Período registrado: %.2fs | Total na sessão: %.2fs",
                    idle_duration,
                    self.total_idle_seconds,
                )

            self.idle_start = None

    # ------------------------------------------------------------------
    # Anotação visual
    # ------------------------------------------------------------------

    def _annotate_frame(self, frame, detections: list[dict]):
        """Desenha bounding boxes e painel de status no frame."""
        annotated = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                f"Caixa {conf:.0%}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2,
            )

        status_lines = [f"Sessao: #{self.sessao_id} | Funcionario: #{FUNCIONARIO_ID}"]

        if self.current_box and self.current_box.confirmed:
            status_lines.append("STATUS: CAIXA NA BANCADA")
            entry_str = self.current_box.entry_time.strftime("%H:%M:%S")
            status_lines.append(f"Entrada: {entry_str}")
            permanencia = time.time() - self.current_box.first_seen
            status_lines.append(f"Permanencia: {permanencia:.1f}s")

        elif self.current_box and not self.current_box.confirmed:
            progress_time = time.time() - self.current_box.first_seen
            status_lines.append("STATUS: CONFIRMANDO...")
            status_lines.append(f"Tempo: {progress_time:.1f}s/{MIN_SECONDS_TO_CONFIRM:.1f}s")

        else:
            status_lines.append("STATUS: OCIOSO")
            if self.idle_start:
                idle_elapsed = time.time() - self.idle_start
                status_lines.append(f"Ocioso ha: {idle_elapsed:.1f}s")

        status_lines.append(f"Ociosidade total: {self.total_idle_seconds:.1f}s")
        status_lines.append(f"Caixas na sessao: {self.total_caixas}")

        overlay = annotated.copy()
        panel_h = 20 + len(status_lines) * 22
        cv2.rectangle(overlay, (0, 0), (360, panel_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, annotated, 0.5, 0, annotated)

        for i, line in enumerate(status_lines):
            color = (0, 255, 100) if "CAIXA" in line else (200, 200, 200)
            if "CONFIRMANDO" in line:
                color = (0, 200, 255)
            if "Sessao" in line:
                color = (255, 200, 0)
            cv2.putText(
                annotated, line,
                (8, 22 + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1,
            )

        return annotated

    # ------------------------------------------------------------------
    # Finalização
    # ------------------------------------------------------------------

    def _finalize(self):
        """
        Encerra a sessão:
            1. Registra saída de caixa em aberto (se houver).
            2. Para o timer de ociosidade.
            3. Atualiza a sessão no backend com hora_fim e tempo_ocioso.
        """
        # Registra eventual caixa que ainda estava sendo rastreada
        if self.current_box and self.current_box.confirmed:
            logger.info("[FINALIZANDO] Registrando saída de caixa em aberto.")
            self._register_box_exit()

        self._stop_idle_timer()
        self.cap.release()
        cv2.destroyAllWindows()

        # Atualiza sessão no backend
        hora_fim = datetime.now(TZ_LOCAL)
        self.api_client.encerrar_sessao(
            sessao_id=self.sessao_id,
            hora_fim=hora_fim,
            tempo_ocioso_segundos=self.total_idle_seconds,
        )

        duracao_total = (hora_fim - self.sessao_inicio).total_seconds()

        logger.info(
            "Sessão encerrada | ID: %s | Duração: %.0fs | "
            "Caixas processadas: %d | Tempo ocioso: %.2fs",
            self.sessao_id,
            duracao_total,
            self.total_caixas,
            self.total_idle_seconds,
        )


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    detector = BoxDetector(camera_source=CAMERA_SOURCE)
    detector.run()