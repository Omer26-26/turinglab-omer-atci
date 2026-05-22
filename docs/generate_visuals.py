"""
Görsel Üretim Betiği (Visual Generation Script)
sample_incrementer.yaml makinesini '1011' girdisiyle çalıştırır ve
PNG kare dosyaları + animasyonlu GIF oluşturur.
"""

import os
import sys

# Proje kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from turinglab.tm_engine import SingleTapeTM
from turinglab.visualizer import TuringVisualizer


def main():
    # ── 1. Makineyi yükle ──
    yaml_path = os.path.join(project_root, "machines", "sample_incrementer.yaml")
    print(f"Makine yükleniyor: {yaml_path}")
    tm = SingleTapeTM.from_yaml(yaml_path)
    print(f"  Makine adı : {tm.name}")

    # ── 2. Makineyi '1011' girdisiyle çalıştır ──
    input_str = "1011"
    print(f"  Girdi       : {input_str}")
    result = tm.run(input_str, verbose=True)
    print(f"  Sonuç       : {'KABUL' if result.accepted else 'RED'} ({result.reason})")
    print(f"  Son şerit   : {result.final_tape}")
    print(f"  Adım sayısı : {result.steps}")
    print(f"  Geçmiş kayıt: {len(result.history)} konfigürasyon")

    # ── 3. Görselleştiriciyi oluştur ──
    viz = TuringVisualizer(
        history=result.history,
        machine_name=tm.name,
        accepted=result.accepted,
    )

    # ── 4. PNG karelerini oluştur ──
    images_dir = os.path.join(project_root, "docs", "images")
    print(f"\nPNG kareleri oluşturuluyor: {images_dir}")
    frame_paths = viz.generate_frames(images_dir, prefix="step")
    for p in frame_paths:
        print(f"  [OK] {os.path.basename(p)}")

    # ── 5. Animasyonlu GIF oluştur ──
    gif_path = os.path.join(images_dir, "animation.gif")
    print(f"\nGIF oluşturuluyor: {gif_path}")
    viz.generate_gif(gif_path, frame_duration=600)
    print(f"  [OK] {os.path.basename(gif_path)}")

    print(f"\nTamamlandı! Toplam {len(frame_paths)} kare + 1 GIF üretildi.")


if __name__ == "__main__":
    main()
