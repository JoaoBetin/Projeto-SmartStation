"""
Smart Station - Módulo de Visão Computacional
=============================================
Responsável por detectar caixas de papelão via câmera,
calcular os tempos de entrada, saída e permanência,
e enviar os dados para a API Java.

Dependências:
    pip install opencv-python ultralytics requests python-dotenv
"""

import cv2
import time
import uuid
import logging
import requests
import os
from datetime import datetime, timezone
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
# Configurações gerais – ajuste conforme o ambiente
# ---------------------------------------------------------------------------

# Índice da câmera (0 = câmera padrão, ou caminho para arquivo de vídeo)
CAMERA_SOURCE: int | str = 0

# URL base da API Java
API_BASE_URL = "http://localhost:8080"

# Endpoint para registrar eventos de caixa
API_ENDPOINT = f"{API_BASE_URL}/caixa/registrar"

# ID do funcionário responsável pela bancada (fixo por enquanto)
FUNCIONARIO_ID = 1

# ── Parâmetros de confirmação de ENTRADA ──────────────────────────────────

# Número mínimo de frames CONSECUTIVOS com detecção para confirmar entrada.
# Aumente este valor se ainda houver falsos positivos.
# Recomendado: 8–15 para câmeras a 30 fps (≈ 0,3–0,5 s de presença contínua).
MIN_FRAMES_TO_CONFIRM = 10

# Confiança mínima do modelo YOLO para considerar uma detecção válida.
# Detecções abaixo deste limiar são completamente ignoradas antes mesmo
# de entrar na contagem de frames.
# Recomendado: 0.55–0.70.
MIN_CONFIDENCE = 0.60

# Tempo mínimo (em segundos) que a caixa deve estar presente de forma
# contínua para que a entrada seja confirmada.
# Atua como segunda barreira além de MIN_FRAMES_TO_CONFIRM.
# Útil para câmeras com fps variável.
MIN_SECONDS_TO_CONFIRM = 1.5

# Número máximo de frames SEM detecção permitidos dentro da janela de
# confirmação antes de zerar o contador.
# Define tolerância a falhas esparsas do modelo durante a fase de confirmação.
# 0 = sem tolerância (qualquer frame sem detecção reinicia a contagem).
MAX_MISSED_FRAMES_DURING_CONFIRM = 2

# ── Parâmetros de confirmação de SAÍDA ───────────────────────────────────

# Tempo (em segundos) sem nenhuma detecção válida para confirmar que a
# caixa saiu da bancada. Aumente se a câmera perder a caixa momentaneamente.
BOX_ABSENCE_TIMEOUT = 4.0

# Número mínimo de frames consecutivos SEM detecção para iniciar a
# contagem do timeout de saída.
# Evita que um único frame "vazio" (oclusão momentânea) dispare o timeout.
MIN_ABSENT_FRAMES_TO_TIMEOUT = 5

# ── Parâmetros de ociosidade ──────────────────────────────────────────────

# Intervalo mínimo de ociosidade (segundos) para ser registrado no log.
IDLE_MIN_SECONDS = 5.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Modelo treinado com o dataset da Universidade de Heidelberg
YOLO_MODEL = os.path.join(BASE_DIR, "best.pt")

# IDs de classe que representam caixa de papelão no modelo
CARDBOARD_CLASS_IDS = [0]


# ---------------------------------------------------------------------------
# Estrutura de dados para uma caixa rastreada
# ---------------------------------------------------------------------------

@dataclass
class TrackedBox:
    """Representa uma caixa de papelão detectada e sendo monitorada."""

    box_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entry_time: Optional[datetime] = None        # Momento confirmado de entrada
    exit_time: Optional[datetime] = None         # Momento confirmado de saída

    # Timestamps internos de controle
    first_seen: float = field(default_factory=time.time)   # Primeiro frame com detecção
    last_seen: float = field(default_factory=time.time)    # Último frame com detecção válida

    # Contadores de frames
    frames_detected: int = 0       # Frames válidos CONSECUTIVOS desde first_seen
    frames_absent: int = 0         # Frames consecutivos SEM detecção (pós-confirmação)
    missed_during_confirm: int = 0 # Frames perdidos dentro da janela de confirmação

    # Flags de estado
    confirmed: bool = False        # Entrada confirmada (passou todos os critérios)
    sent_to_api: bool = False      # Dados já enviados à API


# ---------------------------------------------------------------------------
# Cliente da API
# ---------------------------------------------------------------------------

class ApiClient:
    """Encapsula o envio de dados para a API Java."""

    def __init__(self, endpoint: str, timeout: int = 5):
        self.endpoint = endpoint
        self.timeout = timeout

    def enviar_evento(self, box: TrackedBox) -> bool:
        """
        Serializa e envia os dados da caixa para a API.

        Payload:
            {
                "idCaixa": "<uuid>",
                "horarioEntrada": "2025-01-01T10:00:00Z",
                "horarioSaida":   "2025-01-01T10:05:00Z",
                "funcionarioId":  1
            }
        """
        if not box.entry_time or not box.exit_time:
            logger.warning("[API] Tentativa de envio com dados incompletos. Ignorando.")
            return False

        payload = {
            "idCaixa": box.box_id,
            "horarioEntrada": box.entry_time.isoformat(),
            "horarioSaida": box.exit_time.isoformat(),
            "funcionarioId": FUNCIONARIO_ID,
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.info(
                "[API] Evento enviado | ID: %s | Status: %d",
                box.box_id,
                response.status_code,
            )
            return True

        except requests.exceptions.ConnectionError:
            logger.error("[API] Falha de conexão com %s.", self.endpoint)
        except requests.exceptions.Timeout:
            logger.error("[API] Timeout ao alcançar %s.", self.endpoint)
        except requests.exceptions.HTTPError as e:
            logger.error("[API] Erro HTTP %s: %s", e.response.status_code, e.response.text)
        except Exception as e:
            logger.exception("[API] Erro inesperado: %s", e)

        return False


# ---------------------------------------------------------------------------
# Detector principal
# ---------------------------------------------------------------------------

class BoxDetector:
    """
    Gerencia o loop de captura, detecção e rastreamento de caixas de papelão.

    Fluxo de confirmação de ENTRADA (todas as condições devem ser satisfeitas):
        1. Confiança da detecção >= MIN_CONFIDENCE.
        2. Frames consecutivos válidos >= MIN_FRAMES_TO_CONFIRM.
        3. Tempo contínuo de presença >= MIN_SECONDS_TO_CONFIRM.
        4. Frames perdidos durante a janela <= MAX_MISSED_FRAMES_DURING_CONFIRM.
           Se exceder, o contador é zerado e o processo reinicia.

    Fluxo de confirmação de SAÍDA:
        1. Frames consecutivos sem detecção válida >= MIN_ABSENT_FRAMES_TO_TIMEOUT.
        2. E tempo sem detecção >= BOX_ABSENCE_TIMEOUT.
           Ambas as condições devem ser satisfeitas simultaneamente.
    """

    def __init__(self, camera_source=CAMERA_SOURCE):
        logger.info("Carregando modelo YOLO: %s", YOLO_MODEL)
        self.model = YOLO(YOLO_MODEL)

        logger.info("Abrindo fonte de vídeo: %s", camera_source)
        self.cap = cv2.VideoCapture(camera_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera/vídeo: {camera_source}")

        self.api_client = ApiClient(API_ENDPOINT)

        # Caixa sendo rastreada no momento (apenas uma por vez neste protótipo)
        self.current_box: Optional[TrackedBox] = None

        # Controle de ociosidade
        self.idle_start: Optional[float] = None
        self.total_idle_seconds: float = 0.0

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def run(self):
        """Inicia o loop de captura e detecção. Pressione 'q' para encerrar."""
        logger.info("Smart Station iniciado. Pressione 'q' para encerrar.")

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Frame não capturado. Encerrando.")
                    break

                detections = self._detect_boxes(frame)
                self._update_tracking(detections)

                annotated = self._annotate_frame(frame, detections)
                cv2.imshow("Smart Station - Detecção de Caixas", annotated)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Encerrando por comando do usuário.")
                    break

        finally:
            self._finalize()

    # ------------------------------------------------------------------
    # Detecção via YOLO
    # ------------------------------------------------------------------

    def _detect_boxes(self, frame) -> list[dict]:
        """
        Executa inferência YOLO e filtra por classe e confiança mínima.

        A filtragem por MIN_CONFIDENCE aqui é a PRIMEIRA barreira contra
        falsos positivos — detecções fracas nunca chegam ao rastreador.
        """
        results = self.model(frame, verbose=False)
        boxes = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id not in CARDBOARD_CLASS_IDS:
                    continue

                confidence = float(box.conf[0])

                # ── Barreira 1: confiança mínima ──────────────────────
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
        """
        Atualiza o estado de rastreamento para o frame atual.

        Casos tratados:
            A) Sem caixa rastreada + nova detecção válida → inicia candidata.
            B) Candidata em confirmação + detecção → acumula frames.
               B1) Muitos frames perdidos → reinicia candidata (falso positivo).
               B2) Todos os critérios atingidos → confirma entrada.
            C) Caixa confirmada + detecção → atualiza last_seen, zera ausência.
            D) Caixa rastreada + sem detecção → acumula frames ausentes.
               D1) Limiar de saída atingido → registra saída.
        """
        box_detected_now = len(detections) > 0
        now = time.time()

        # ── Caso A: Nenhuma caixa rastreada, nova detecção aparece ────
        if self.current_box is None:
            if box_detected_now:
                self.current_box = TrackedBox()
                self.current_box.frames_detected = 1
                self.current_box.first_seen = now
                self.current_box.last_seen = now
                logger.debug("[TRACKER] Candidata iniciada — aguardando confirmação...")
                self._stop_idle_timer()
            return

        # A partir daqui, self.current_box existe.

        # ── Caso B / C: Caixa rastreada E detecção presente ──────────
        if box_detected_now:
            self.current_box.last_seen = now
            self.current_box.frames_absent = 0  # zera contador de ausência

            if not self.current_box.confirmed:
                # Fase de confirmação de entrada
                self.current_box.frames_detected += 1
                self._try_confirm_entry(now)
            # Se já confirmada, apenas atualiza last_seen (já feito acima)
            return

        # ── Caso D: Caixa rastreada MAS sem detecção neste frame ─────
        self.current_box.frames_absent += 1

        if not self.current_box.confirmed:
            # Durante a confirmação, frames perdidos consomem a tolerância
            self.current_box.missed_during_confirm += 1

            if self.current_box.missed_during_confirm > MAX_MISSED_FRAMES_DURING_CONFIRM:
                # ── B1: Tolerância esgotada → era falso positivo, reinicia ──
                logger.debug(
                    "[TRACKER] Candidata descartada: %d frames perdidos durante confirmação "
                    "(máx. %d). Reiniciando.",
                    self.current_box.missed_during_confirm,
                    MAX_MISSED_FRAMES_DURING_CONFIRM,
                )
                self.current_box = None
                self._start_idle_timer()
            return

        # Caixa já confirmada: verifica se atingiu o limiar de saída
        elapsed_without_detection = now - self.current_box.last_seen

        both_conditions_met = (
            self.current_box.frames_absent >= MIN_ABSENT_FRAMES_TO_TIMEOUT
            and elapsed_without_detection >= BOX_ABSENCE_TIMEOUT
        )

        if both_conditions_met:
            self._register_box_exit()

    def _try_confirm_entry(self, now: float):
        """
        Verifica se a caixa candidata atende TODOS os critérios de entrada.

        Critérios (todas devem ser verdadeiras):
            1. frames_detected >= MIN_FRAMES_TO_CONFIRM
            2. Tempo desde first_seen >= MIN_SECONDS_TO_CONFIRM
        """
        box = self.current_box

        frames_ok = box.frames_detected >= MIN_FRAMES_TO_CONFIRM
        time_ok = (now - box.first_seen) >= MIN_SECONDS_TO_CONFIRM

        if frames_ok and time_ok:
            box.confirmed = True
            box.entry_time = datetime.now(timezone.utc)
            logger.info(
                "[ENTRADA] ✔ Caixa confirmada | ID: %s | Horário: %s | "
                "Frames: %d | Tempo de confirmação: %.2fs",
                box.box_id,
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
        """Registra a saída da caixa, calcula permanência e envia à API."""
        box = self.current_box
        if box is None:
            return

        if not box.confirmed:
            logger.debug("[TRACKER] Candidata descartada na saída (não confirmada).")
            self.current_box = None
            self._start_idle_timer()
            return

        box.exit_time = datetime.now(timezone.utc)
        permanencia = (box.exit_time - box.entry_time).total_seconds()

        logger.info(
            "[SAÍDA] ✔ Caixa saiu | ID: %s | Entrada: %s | Saída: %s | Permanência: %.2fs",
            box.box_id,
            box.entry_time.isoformat(),
            box.exit_time.isoformat(),
            permanencia,
        )

        success = self.api_client.enviar_evento(box)
        if not success:
            logger.warning("[TRACKER] Falha no envio à API. Dados perdidos — ID: %s.", box.box_id)

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

        # ── Painel de status ──────────────────────────────────────────
        status_lines = []

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

        overlay = annotated.copy()
        panel_h = 20 + len(status_lines) * 22
        cv2.rectangle(overlay, (0, 0), (340, panel_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, annotated, 0.5, 0, annotated)

        for i, line in enumerate(status_lines):
            color = (0, 255, 100) if "CAIXA" in line else (200, 200, 200)
            if "CONFIRMANDO" in line:
                color = (0, 200, 255)
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
        if self.current_box and self.current_box.confirmed:
            logger.info("[FINALIZANDO] Registrando saída de caixa em aberto.")
            self._register_box_exit()

        self._stop_idle_timer()
        self.cap.release()
        cv2.destroyAllWindows()

        logger.info(
            "Sessão encerrada | Tempo total ocioso: %.2fs",
            self.total_idle_seconds,
        )


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    detector = BoxDetector(camera_source=CAMERA_SOURCE)
    detector.run()