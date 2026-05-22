"""
Turing Machine Görselleştirici (Visualizer)
Pillow kütüphanesi kullanarak Turing Makinesi çalışma geçmişini
kare kare görselleştirir. PNG ve animasyonlu GIF çıktısı üretir.
"""

import os
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

from turinglab.tm_engine import Configuration


# ────────────────────────── Renk Paleti ──────────────────────────
_COLORS = {
    "bg":           "#F5F6FA",   # Açık gri arka plan
    "cell_fill":    "#FFFFFF",   # Normal hücre dolgusu
    "cell_border":  "#BDC3C7",   # Hücre kenarlık rengi
    "head_fill":    "#3498DB",   # Kafa pozisyonundaki hücre dolgusu (mavi)
    "head_text":    "#FFFFFF",   # Kafa hücresindeki yazı rengi
    "text":         "#2C3E50",   # Genel metin rengi
    "state_label":  "#2C3E50",   # Durum etiketi rengi
    "step_label":   "#7F8C8D",   # Adım sayacı rengi
    "accepted":     "#27AE60",   # Kabul rengi (yeşil)
    "rejected":     "#E74C3C",   # Ret rengi (kırmızı)
    "title":        "#2C3E50",   # Başlık rengi
    "arrow":        "#3498DB",   # Ok rengi
}

# ────────────────────────── Boyut Sabitleri ──────────────────────
_CELL_W       = 52        # Hücre genişliği (piksel)
_CELL_H       = 52        # Hücre yüksekliği
_CELL_GAP     = 6         # Hücreler arası boşluk
_CELL_RADIUS  = 8         # Yuvarlatılmış köşe yarıçapı
_TAPE_Y       = 140       # Şeridin üst kenarının Y konumu
_MARGIN_X     = 60        # Sol/sağ kenar boşluğu
_MIN_WIDTH    = 800       # Minimum görüntü genişliği
_IMG_HEIGHT   = 300       # Görüntü yüksekliği
_ARROW_SIZE   = 10        # Ok boyutu


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Windows'ta Consolas veya Courier New monospace fontunu yükler."""
    candidates = [
        "C:/Windows/Fonts/consola.ttf",   # Consolas
        "C:/Windows/Fonts/cour.ttf",      # Courier New
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    # Son çare: varsayılan bitmap font
    return ImageFont.load_default()


def _load_bold_font(size: int) -> ImageFont.FreeTypeFont:
    """Kalın font yükler (başlık ve durum için)."""
    candidates = [
        "C:/Windows/Fonts/consolab.ttf",  # Consolas Bold
        "C:/Windows/Fonts/courbd.ttf",    # Courier New Bold
        "C:/Windows/Fonts/consola.ttf",   # Consolas (fallback)
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    xy: tuple,
    radius: int,
    fill: str,
    outline: str,
    width: int = 2,
):
    """Yuvarlatılmış dikdörtgen çizer."""
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


class TuringVisualizer:
    """Turing Makinesi çalışma geçmişini görselleştirir."""

    def __init__(
        self,
        history: List[Configuration],
        machine_name: str = "Turing Machine",
        accepted: Optional[bool] = None,
    ):
        """
        Args:
            history:      Çalışma geçmişi (Configuration listesi)
            machine_name: Makine adı (başlıkta gösterilir)
            accepted:     Makinenin kabul/ret durumu (son karede gösterilir)
        """
        self.history = history
        self.machine_name = machine_name
        self.accepted = accepted

        # Fontları yükle
        self._font_symbol  = _load_font(22)       # Hücre sembolleri
        self._font_state   = _load_bold_font(20)   # Durum etiketi
        self._font_title   = _load_bold_font(18)    # Başlık
        self._font_step    = _load_font(15)         # Adım sayacı
        self._font_status  = _load_bold_font(22)    # Kabul/Ret durumu

    # ──────────────────────────────────────────────────────────────
    #  Tek bir adımı görüntüye dönüştürür
    # ──────────────────────────────────────────────────────────────
    def render_frame(self, step: int) -> Image.Image:
        """Belirtilen adımı PIL Image olarak oluşturur."""
        if step < 0 or step >= len(self.history):
            raise IndexError(f"Adım {step} geçersiz (toplam {len(self.history)} adım)")

        cfg = self.history[step]
        tape_str = cfg.tape if cfg.tape else "B"
        head_pos = cfg.head_position
        is_last = (step == len(self.history) - 1)

        # ── Görüntü boyutunu hesapla ──
        num_cells = len(tape_str)
        tape_width = num_cells * (_CELL_W + _CELL_GAP) - _CELL_GAP
        img_width = max(_MIN_WIDTH, tape_width + 2 * _MARGIN_X)

        img = Image.new("RGB", (img_width, _IMG_HEIGHT), _COLORS["bg"])
        draw = ImageDraw.Draw(img)

        # ── 1. Başlık ──
        title_text = self.machine_name
        title_bbox = draw.textbbox((0, 0), title_text, font=self._font_title)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(
            ((img_width - title_w) / 2, 18),
            title_text,
            fill=_COLORS["title"],
            font=self._font_title,
        )

        # ── 2. Adım sayacı (sağ üst) ──
        step_text = f"Adım: {step}/{len(self.history) - 1}"
        step_bbox = draw.textbbox((0, 0), step_text, font=self._font_step)
        step_w = step_bbox[2] - step_bbox[0]
        draw.text(
            (img_width - step_w - 20, 20),
            step_text,
            fill=_COLORS["step_label"],
            font=self._font_step,
        )

        # ── 3. Durum etiketi (şeridin üstünde, ortada) ──
        state_text = f"Durum: {cfg.state}"
        state_bbox = draw.textbbox((0, 0), state_text, font=self._font_state)
        state_w = state_bbox[2] - state_bbox[0]
        draw.text(
            ((img_width - state_w) / 2, 70),
            state_text,
            fill=_COLORS["state_label"],
            font=self._font_state,
        )

        # ── 4. Aşağı ok (kafa pozisyonunu gösterir) ──
        tape_start_x = (img_width - tape_width) / 2
        head_center_x = tape_start_x + head_pos * (_CELL_W + _CELL_GAP) + _CELL_W / 2
        arrow_top_y = 98
        arrow_bot_y = _TAPE_Y - 6

        # Ok gövdesi
        draw.line(
            [(head_center_x, arrow_top_y), (head_center_x, arrow_bot_y)],
            fill=_COLORS["arrow"],
            width=3,
        )
        # Ok ucu (üçgen)
        draw.polygon(
            [
                (head_center_x, arrow_bot_y),
                (head_center_x - _ARROW_SIZE, arrow_bot_y - _ARROW_SIZE),
                (head_center_x + _ARROW_SIZE, arrow_bot_y - _ARROW_SIZE),
            ],
            fill=_COLORS["arrow"],
        )

        # ── 5. Şerit hücreleri ──
        for i, symbol in enumerate(tape_str):
            x0 = tape_start_x + i * (_CELL_W + _CELL_GAP)
            y0 = _TAPE_Y
            x1 = x0 + _CELL_W
            y1 = y0 + _CELL_H

            is_head = (i == head_pos)

            # Hücre arka planı
            fill_color = _COLORS["head_fill"] if is_head else _COLORS["cell_fill"]
            border_color = _COLORS["head_fill"] if is_head else _COLORS["cell_border"]
            _rounded_rectangle(draw, (x0, y0, x1, y1), _CELL_RADIUS, fill_color, border_color, width=2)

            # Hücre gölge efekti (hafif)
            if not is_head:
                shadow_color = "#E8E8E8"
                draw.line([(x0 + _CELL_RADIUS, y1), (x1 - _CELL_RADIUS, y1)], fill=shadow_color, width=2)

            # Sembol metni
            text_color = _COLORS["head_text"] if is_head else _COLORS["text"]
            sym_bbox = draw.textbbox((0, 0), symbol, font=self._font_symbol)
            sym_w = sym_bbox[2] - sym_bbox[0]
            sym_h = sym_bbox[3] - sym_bbox[1]
            draw.text(
                (x0 + (_CELL_W - sym_w) / 2, y0 + (_CELL_H - sym_h) / 2 - 2),
                symbol,
                fill=text_color,
                font=self._font_symbol,
            )

        # ── 6. Hücre indeksleri (şeridin altında) ──
        for i in range(num_cells):
            idx_text = str(i)
            idx_bbox = draw.textbbox((0, 0), idx_text, font=self._font_step)
            idx_w = idx_bbox[2] - idx_bbox[0]
            cx = tape_start_x + i * (_CELL_W + _CELL_GAP) + _CELL_W / 2
            draw.text(
                (cx - idx_w / 2, _TAPE_Y + _CELL_H + 6),
                idx_text,
                fill=_COLORS["step_label"],
                font=self._font_step,
            )

        # ── 7. Son karede KABUL / RED durumu ──
        if is_last and self.accepted is not None:
            if self.accepted:
                status_text = "✔ KABUL EDİLDİ (ACCEPTED)"
                status_color = _COLORS["accepted"]
            else:
                status_text = "✘ REDDEDİLDİ (REJECTED)"
                status_color = _COLORS["rejected"]

            st_bbox = draw.textbbox((0, 0), status_text, font=self._font_status)
            st_w = st_bbox[2] - st_bbox[0]
            draw.text(
                ((img_width - st_w) / 2, _TAPE_Y + _CELL_H + 38),
                status_text,
                fill=status_color,
                font=self._font_status,
            )

        # Alt çizgi (dekoratif)
        draw.line(
            [(30, _IMG_HEIGHT - 15), (img_width - 30, _IMG_HEIGHT - 15)],
            fill="#E0E0E0",
            width=1,
        )

        return img

    # ──────────────────────────────────────────────────────────────
    #  Tüm adımları PNG dosyalarına yazar
    # ──────────────────────────────────────────────────────────────
    def generate_frames(self, output_dir: str, prefix: str = "step") -> List[str]:
        """Tüm adımları PNG dosyalarına kaydeder.

        Args:
            output_dir: Çıktı dizini
            prefix:     Dosya adı ön eki

        Returns:
            Oluşturulan dosya yollarının listesi
        """
        os.makedirs(output_dir, exist_ok=True)
        paths: List[str] = []

        for i in range(len(self.history)):
            frame = self.render_frame(i)
            filename = f"{prefix}_{i:03d}.png"
            filepath = os.path.join(output_dir, filename)
            frame.save(filepath)
            paths.append(filepath)

        return paths

    # ──────────────────────────────────────────────────────────────
    #  Animasyonlu GIF oluşturur
    # ──────────────────────────────────────────────────────────────
    def generate_gif(self, output_path: str, frame_duration: int = 500) -> str:
        """Tüm adımlardan animasyonlu GIF oluşturur.

        Args:
            output_path:    Çıktı GIF dosya yolu
            frame_duration: Her karenin gösterim süresi (milisaniye)

        Returns:
            Oluşturulan GIF dosya yolu
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        frames = [self.render_frame(i) for i in range(len(self.history))]

        # Son kareyi daha uzun göster (sonuç görünsün)
        durations = [frame_duration] * len(frames)
        if len(durations) > 0:
            durations[-1] = frame_duration * 3

        # Pillow'un GIF desteğini kullan
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,  # Sonsuz döngü
        )

        return output_path
