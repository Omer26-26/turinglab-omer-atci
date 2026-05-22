# TuringLab 🖥️

Hesaplama Kuramı dersi kapsamında geliştirilen Turing makinesi simülatörü.  
**Selçuk Üniversitesi — Bilgisayar Mühendisliği**

---

## 🚀 Özellikler

- **Tek-şeritli deterministik TM** — YAML tabanlı konfigürasyon, verbose mod, history kaydı
- **Çok-şeritli TM** — k adet şerit desteği, paralel kafa hareketi (Bonus A)
- **Non-deterministik TM** — BFS tabanlı hesaplama ağacı keşfi (Bonus B)
- **Karşılaştırmalı analiz** — DTM, Multi-tape ve NTM performans karşılaştırması (Bonus C)
- **Görselleştirici** — Adım adım PNG ve animasyonlu GIF üretimi (Bonus D)

---

## 📁 Proje Yapısı

```
turinglab/
├── __init__.py              # Public API
├── tm_engine.py             # Tek-şeritli TM motoru (SingleTapeTM)
├── multi_tape.py            # Çok-şeritli TM (MultiTapeTM)
├── ntm.py                   # Non-deterministik TM (NondeterministicTM)
└── visualizer.py            # Adım-adım görselleştirici (TuringVisualizer)

machines/
├── sample_incrementer.yaml  # Örnek: Binary increment
├── unary_to_binary.yaml     # TM-1: Unary → Binary çevirici
├── binary_compare.yaml      # TM-2: İkili karşılaştırıcı (N1 > N2?)
├── string_copy.yaml         # TM-3: Dizgi kopyalayıcı (w → w#w)
├── student_choice.yaml      # TM-4: Parantez denge kontrolü
├── binary_addition_3tape.yaml  # Bonus A: 3-şeritli ikili toplama
├── contains_01_ntm.yaml     # Bonus B: NTM — "01 var mı?"
├── contains_01_single.yaml  # Bonus C: DTM — "01 var mı?"
└── contains_01_multi.yaml   # Bonus C: Multi-tape — "01 var mı?"

tests/
├── test_tm_engine.py        # Motor birim testleri
├── test_machines.py         # 4 TM entegrasyon testleri
├── test_multi_tape.py       # Çok-şeritli TM testleri
└── test_ntm.py              # NTM testleri

docs/
├── design_notes.md          # TM tasarım kararları
├── comparison_analysis.py   # Karşılaştırmalı analiz scripti
├── comparison.png           # Performans karşılaştırma grafiği
└── images/                  # Görselleştirici çıktıları (PNG + GIF)
```

---

## ⚙️ Kurulum

```bash
# Python 3.10+ gereklidir
pip install -r requirements.txt

# Bonus D (görselleştirici) için ek bağımlılıklar
pip install Pillow imageio

# Bonus C (karşılaştırmalı analiz) için
pip install matplotlib
```

---

## 🎮 Kullanım

### Tek-Şeritli TM Çalıştırma

```bash
# Komut satırından
python -m turinglab.tm_engine machines/sample_incrementer.yaml 1011

# Python'dan
from turinglab import SingleTapeTM

tm = SingleTapeTM.from_yaml("machines/unary_to_binary.yaml")
result = tm.run("11111", verbose=True)
print(f"Sonuç: {'KABUL' if result.accepted else 'RED'}")
print(f"Şerit: {result.final_tape}")
print(f"Adım: {result.steps}")
```

### Çok-Şeritli TM (Bonus A)

```python
from turinglab.multi_tape import MultiTapeTM

tm = MultiTapeTM.from_yaml("machines/binary_addition_3tape.yaml")
result = tm.run("11#01")  # 3 + 1 = 4
```

### Non-Deterministik TM (Bonus B)

```python
from turinglab.ntm import NondeterministicTM

ntm = NondeterministicTM.from_yaml("machines/contains_01_ntm.yaml")
result = ntm.run("1101", max_depth=50, max_branches=1000)
print(f"Kabul yolları: {len(result.accepting_paths)}")
```

### Görselleştirici (Bonus D)

```python
from turinglab import SingleTapeTM
from turinglab.visualizer import TuringVisualizer

tm = SingleTapeTM.from_yaml("machines/sample_incrementer.yaml")
result = tm.run("1011")

vis = TuringVisualizer(result.history, machine_name="Binary Increment", accepted=result.accepted)
vis.generate_frames("docs/images/")
vis.generate_gif("docs/images/animation.gif")
```

---

## 🧪 Testler

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Belirli bir modülü test et
python -m pytest tests/test_tm_engine.py -v
python -m pytest tests/test_machines.py -v
python -m pytest tests/test_multi_tape.py -v
python -m pytest tests/test_ntm.py -v
```

---

## 📊 Karşılaştırmalı Analiz (Bonus C)

Aynı dil (`L = {w | w'de '01' var}`) üç farklı TM varyantı ile çözülmüş ve adım sayıları karşılaştırılmıştır:

```bash
python docs/comparison_analysis.py
# Çıktı: docs/comparison.png
```

Detaylar için: [REPORT.md](REPORT.md)

---

## 📝 Tasarım Kararları

Şerit `Dict[int, str]` ile temsil edilir — negatif indeks desteği ve sonsuz şerit illüzyonu sağlar.  
Detaylar: [docs/design_notes.md](docs/design_notes.md) · [REPORT.md](REPORT.md)

---

## 📄 Lisans

Bu proje Selçuk Üniversitesi Hesaplama Kuramı dersi final ödevi kapsamında hazırlanmıştır.
