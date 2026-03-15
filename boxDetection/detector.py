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

# Número mínimo de frames consecutivos para confirmar entrada/saída
# (evita falsos positivos causados por ruído de detecção)
MIN_FRAMES_TO_CONFIRM = 3

# Tempo (segundos) sem detecção para considerar que a caixa saiu
BOX_ABSENCE_TIMEOUT = 3.0

# Intervalo mínimo de ociosidade (segundos) para ser registrado
IDLE_MIN_SECONDS = 5.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Inserindo o modelo treinado com o dataset da Universidade de Heidelberg
YOLO_MODEL = os.path.join(BASE_DIR, "best.pt")

CARDBOARD_CLASS_IDS = [0] 


# ---------------------------------------------------------------------------
# Estrutura de dados para uma caixa rastreada
# ---------------------------------------------------------------------------

@dataclass
class TrackedBox:
    """Representa uma caixa de papelão detectada e sendo monitorada."""

    box_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entry_time: Optional[datetime] = None       # Momento em que entrou na câmera
    exit_time: Optional[datetime] = None        # Momento em que saiu da câmera
    last_seen: float = field(default_factory=time.time)  # Timestamp do último frame com detecção
    frames_detected: int = 0                    # Frames consecutivos com detecção confirmada
    confirmed: bool = False                     # Se a entrada já foi confirmada (evita falso positivo)
    sent_to_api: bool = False                   # Se os dados já foram enviados à API


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

        Payload esperado pela API (conforme README):
            {
                "idCaixa": "<uuid>",
                "horarioEntrada": "2025-01-01T10:00:00Z",
                "horarioSaida": "2025-01-01T10:05:00Z"
            }

        Retorna True em caso de sucesso, False caso contrário.
        """
        if not box.entry_time or not box.exit_time:
            logger.warning("[API] Tentativa de envio com dados incompletos. Ignorando.")
            return False

        payload = {
            "idCaixa": box.box_id,
            "horarioEntrada": box.entry_time.isoformat(),
            "horarioSaida": box.exit_time.isoformat(),
            "funcionarioId": FUNCIONARIO_ID,  # ID fixo — substituir por lógica de login futuramente
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.info(
                "[API] Evento enviado com sucesso | ID: %s | Status: %d",
                box.box_id,
                response.status_code,
            )
            return True

        except requests.exceptions.ConnectionError:
            logger.error("[API] Falha de conexão com %s. Verifique se o backend está rodando.", self.endpoint)
        except requests.exceptions.Timeout:
            logger.error("[API] Timeout ao tentar alcançar %s.", self.endpoint)
        except requests.exceptions.HTTPError as e:
            logger.error("[API] Erro HTTP %s: %s", e.response.status_code, e.response.text)
        except Exception as e:
            logger.exception("[API] Erro inesperado ao enviar evento: %s", e)

        return False


# ---------------------------------------------------------------------------
# Detector principal
# ---------------------------------------------------------------------------

class BoxDetector:
    """
    Gerencia o loop de captura, detecção e rastreamento de caixas de papelão.

    Fluxo:
        1. Captura frame da câmera.
        2. Roda inferência YOLO para detectar caixas.
        3. Se uma caixa é vista pela 1ª vez → registra horário de entrada.
        4. Enquanto a caixa permanece → atualiza `last_seen`.
        5. Quando a caixa desaparece por > BOX_ABSENCE_TIMEOUT → registra
           horário de saída e envia os dados à API.
        6. Calcula e loga o tempo de ociosidade da bancada.
    """

    def __init__(self, camera_source=CAMERA_SOURCE):
        logger.info("Carregando modelo YOLO: %s", YOLO_MODEL)
        self.model = YOLO(YOLO_MODEL)

        logger.info("Abrindo fonte de vídeo: %s", camera_source)
        self.cap = cv2.VideoCapture(camera_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera/vídeo: {camera_source}")

        self.api_client = ApiClient(API_ENDPOINT)

        # Caixa atualmente na bancada (apenas uma por vez neste protótipo)
        self.current_box: Optional[TrackedBox] = None

        # Controle de ociosidade
        self.idle_start: Optional[float] = None   # Início do período ocioso (timestamp)
        self.total_idle_seconds: float = 0.0       # Acumulador de tempo ocioso na sessão

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def run(self):
        """Inicia o loop de captura e detecção. Pressione 'q' para encerrar."""
        logger.info("Smart Station iniciado. Pressione 'q' na janela de vídeo para encerrar.")

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Frame não capturado. Encerrando.")
                    break

                # Executa inferência no frame atual
                detections = self._detect_boxes(frame)

                # Atualiza estado da bancada com base nas detecções
                self._update_tracking(detections)

                # Desenha anotações visuais no frame para depuração
                annotated = self._annotate_frame(frame, detections)
                cv2.imshow("Smart Station - Detecção de Caixas", annotated)

                # Encerra com tecla 'q'
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
        Executa o modelo YOLO no frame e filtra apenas as classes de caixa.

        Retorna uma lista de dicionários com:
            - bbox: (x1, y1, x2, y2) em pixels
            - confidence: float entre 0 e 1
            - class_id: int
        """
        results = self.model(frame, verbose=False)
        boxes = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id not in CARDBOARD_CLASS_IDS:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])

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
        Atualiza o estado de rastreamento com base nas detecções do frame atual.

        Casos tratados:
            A) Nenhuma caixa presente + nova detecção → inicia rastreamento.
            B) Caixa rastreada + detecção confirmada → atualiza `last_seen`.
            C) Caixa rastreada + sem detecção por tempo > timeout → registra saída.
        """
        box_detected_now = len(detections) > 0
        now = time.time()

        # ── Caso A: Nenhuma caixa sendo rastreada e detectamos algo novo ──
        if self.current_box is None and box_detected_now:
            self.current_box = TrackedBox()
            self.current_box.frames_detected = 1
            logger.debug("[TRACKER] Possível caixa detectada — aguardando confirmação...")
            self._stop_idle_timer()
            return

        # ── Caso B: Caixa já rastreada e continua sendo detectada ──
        if self.current_box is not None and box_detected_now:
            self.current_box.last_seen = now
            self.current_box.frames_detected += 1

            # Confirma a entrada após MIN_FRAMES_TO_CONFIRM frames seguidos
            if not self.current_box.confirmed and \
               self.current_box.frames_detected >= MIN_FRAMES_TO_CONFIRM:
                self.current_box.confirmed = True
                self.current_box.entry_time = datetime.now(timezone.utc)
                logger.info(
                    "[ENTRADA] Caixa confirmada | ID: %s | Horário: %s",
                    self.current_box.box_id,
                    self.current_box.entry_time.isoformat(),
                )
            return

        # ── Caso C: Caixa rastreada mas sem detecção — verifica timeout ──
        if self.current_box is not None and not box_detected_now:
            elapsed_without_detection = now - self.current_box.last_seen

            if elapsed_without_detection >= BOX_ABSENCE_TIMEOUT:
                self._register_box_exit()

    def _register_box_exit(self):
        """Registra a saída da caixa, calcula permanência e envia à API."""
        box = self.current_box

        if box is None:
            return

        # Só processa caixas que tiveram a entrada confirmada
        if not box.confirmed:
            logger.debug("[TRACKER] Detecção descartada (não confirmada).")
            self.current_box = None
            self._start_idle_timer()
            return

        box.exit_time = datetime.now(timezone.utc)

        # Calcula o tempo de permanência na câmera
        permanencia = (box.exit_time - box.entry_time).total_seconds()

        logger.info(
            "[SAÍDA] Caixa saiu | ID: %s | Entrada: %s | Saída: %s | Permanência: %.2fs",
            box.box_id,
            box.entry_time.isoformat(),
            box.exit_time.isoformat(),
            permanencia,
        )

        # Envia para a API
        success = self.api_client.enviar_evento(box)
        if not success:
            logger.warning("[TRACKER] Falha no envio para API. Dados perdidos para ID %s.", box.box_id)

        # Libera o rastreador e inicia contagem de ociosidade
        self.current_box = None
        self._start_idle_timer()

    # ------------------------------------------------------------------
    # Gerenciamento de ociosidade
    # ------------------------------------------------------------------

    def _start_idle_timer(self):
        """Marca o início de um período ocioso da bancada."""
        if self.idle_start is None:
            self.idle_start = time.time()
            logger.debug("[OCIOSIDADE] Bancada ficou ociosa.")

    def _stop_idle_timer(self):
        """Encerra o período ocioso e acumula o tempo."""
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
    # Anotação visual (overlay no vídeo)
    # ------------------------------------------------------------------

    def _annotate_frame(self, frame, detections: list[dict]):
        """
        Desenha bounding boxes e informações de estado no frame.
        Retorna o frame anotado para exibição.
        """
        annotated = frame.copy()

        # Desenha bounding boxes das detecções
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                f"Caixa {conf:.0%}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
            )

        # Painel de status no canto superior esquerdo
        status_lines = []

        if self.current_box and self.current_box.confirmed:
            status_lines.append("STATUS: CAIXA NA BANCADA")
            entry_str = self.current_box.entry_time.strftime("%H:%M:%S") if self.current_box.entry_time else "---"
            status_lines.append(f"Entrada: {entry_str}")
            elapsed = time.time() - self.current_box.last_seen
            status_lines.append(f"Permanencia: {elapsed:.1f}s")
        elif self.current_box and not self.current_box.confirmed:
            status_lines.append("STATUS: DETECTANDO...")
        else:
            status_lines.append("STATUS: OCIOSO")
            if self.idle_start:
                idle_elapsed = time.time() - self.idle_start
                status_lines.append(f"Ocioso ha: {idle_elapsed:.1f}s")

        status_lines.append(f"Ociosidade total: {self.total_idle_seconds:.1f}s")

        # Fundo semi-transparente para o painel
        overlay = annotated.copy()
        panel_h = 20 + len(status_lines) * 22
        cv2.rectangle(overlay, (0, 0), (280, panel_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, annotated, 0.5, 0, annotated)

        for i, line in enumerate(status_lines):
            color = (0, 255, 100) if "CAIXA" in line else (200, 200, 200)
            cv2.putText(
                annotated, line,
                (8, 22 + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55, color, 1,
            )

        return annotated

    # ------------------------------------------------------------------
    # Finalização
    # ------------------------------------------------------------------

    def _finalize(self):
        """Libera recursos e exibe estatísticas da sessão."""
        # Se havia uma caixa em processo ao encerrar, registra saída
        if self.current_box and self.current_box.confirmed:
            logger.info("[FINALIZANDO] Registrando saída de caixa aberta.")
            self._register_box_exit()

        # Encerra timer de ociosidade
        self._stop_idle_timer()

        # Libera câmera e janelas OpenCV
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