"""
Bonus C — Karşılaştırmalı Analiz
Aynı dil (L = {w | w'de '01' var}) tek-şeritli, çok-şeritli ve NTM ile çözülüp
adım sayıları karşılaştırılır. matplotlib ile grafik çizilir.
"""
import sys
import os
import random
import string

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalıştır
import matplotlib.pyplot as plt

from turinglab.tm_engine import SingleTapeTM
from turinglab.multi_tape import MultiTapeTM
from turinglab.ntm import NondeterministicTM


def generate_test_inputs(max_len=30):
    """Farklı uzunluklarda '01' içeren ve içermeyen test girdileri üretir."""
    inputs = {}
    for n in range(1, max_len + 1):
        # '01' içeren girdi üret: rastgele konuma '01' yerleştir
        if n >= 2:
            pos = random.randint(0, n - 2)
            chars = [random.choice('01') for _ in range(n)]
            chars[pos] = '0'
            chars[pos + 1] = '1'
            inputs[n] = ''.join(chars)
        else:
            # n=1 için '01' yerleştirilemez, yine de tek karakter
            inputs[n] = '0'
    return inputs


def measure_steps_single(tm, input_str):
    """Tek-şeritli TM adım sayısını ölçer."""
    result = tm.run(input_str, max_steps=5000)
    return result.steps


def measure_steps_multi(tm, input_str):
    """Çok-şeritli TM adım sayısını ölçer."""
    result = tm.run(input_str, max_steps=5000)
    return result.steps


def measure_steps_ntm(ntm, input_str):
    """NTM toplam keşfedilen düğüm sayısını ölçer."""
    result = ntm.run(input_str, max_depth=200, max_branches=50000)
    return result.total_nodes_explored


def main():
    print("Bonus C — Karşılaştırmalı Analiz")
    print("=" * 50)

    # Makineleri yükle
    base_dir = os.path.join(os.path.dirname(__file__), '..')

    single_tm = SingleTapeTM.from_yaml(os.path.join(base_dir, 'machines', 'contains_01_single.yaml'))
    multi_tm = MultiTapeTM.from_yaml(os.path.join(base_dir, 'machines', 'contains_01_multi.yaml'))
    ntm = NondeterministicTM.from_yaml(os.path.join(base_dir, 'machines', 'contains_01_ntm.yaml'))

    print("Makineler yüklendi ✓")

    # Test girdileri üret
    random.seed(42)  # Tekrarlanabilirlik için
    max_len = 40
    test_inputs = generate_test_inputs(max_len)

    # Adım sayılarını ölç
    lengths = sorted(test_inputs.keys())
    single_steps = []
    multi_steps = []
    ntm_steps = []

    for n in lengths:
        inp = test_inputs[n]

        s_steps = measure_steps_single(single_tm, inp)
        single_steps.append(s_steps)

        m_steps = measure_steps_multi(multi_tm, inp)
        multi_steps.append(m_steps)

        n_steps = measure_steps_ntm(ntm, inp)
        ntm_steps.append(n_steps)

        if n % 10 == 0 or n <= 5:
            print(f"  n={n:3d}: DTM={s_steps:4d}, Multi-Tape={m_steps:4d}, NTM={n_steps:4d}")

    # Grafik çiz
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(lengths, single_steps, 'o-', color='#E74C3C', linewidth=2,
            markersize=4, label='Tek-Şeritli DTM', alpha=0.9)
    ax.plot(lengths, multi_steps, 's-', color='#3498DB', linewidth=2,
            markersize=4, label='Çok-Şeritli TM (2 şerit)', alpha=0.9)
    ax.plot(lengths, ntm_steps, '^-', color='#2ECC71', linewidth=2,
            markersize=4, label='Non-Deterministik TM (BFS düğüm)', alpha=0.9)

    ax.set_xlabel('Girdi Uzunluğu (n)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Adım / Keşfedilen Düğüm Sayısı', fontsize=13, fontweight='bold')
    ax.set_title('TM Varyantları Performans Karşılaştırması\nL = {w | w\'de \'01\' alt-dizgisi var}',
                 fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=12, loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')

    # Y ekseni minimum 0
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    # Kaydet
    output_path = os.path.join(os.path.dirname(__file__), 'comparison.png')
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\nGrafik kaydedildi: {output_path}")
    print("Tamamlandı ✓")


if __name__ == '__main__':
    main()
