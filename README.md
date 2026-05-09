# TuringLab Project - Ömer {Soyadı}

---
TEORİK BİLGİSAYAR BİLİMLERİ · HESAPLAMA KURAMI · FİNAL ÖDEVİ
TURINGLAB
Öğrenci El Kitabı
~3 Haftalık Final Ödevi (4–22 Mayıs)
Tasarım · İnşa · Analiz · Sentez

## Proje Tanıtımı
TuringLab, Turing makinelerini araştıran, tasarlayan ve çalıştırılabilir hale getiren kapsamlı bir Python projesidir.

## Kullanım
### Gereksinimler
```bash
pip install -r requirements.txt
```

### Motorun Çalıştırılması
```python
from turinglab import SingleTapeTM

tm = SingleTapeTM.from_yaml("machines/binary_increment.yaml")
result = tm.run(input_string="1011", max_steps=1000, verbose=True)

print(f"Accepted: {result.accepted}")
print(f"Final Tape: {result.final_tape}")
print(f"Reason: {result.reason}")
```

### Kafa Sola Taşma (Left Overflow) Politikası
Bu motor, şeridi temsil etmek için `dict[int, str]` (sparse tape) yapısını kullanır. Bu sayede kafa negatif indekslere (`head_position < 0`) geçtiğinde şerit sol tarafa doğru otomatik olarak genişler ve işlem kesintisiz devam eder.

---
*(Orijinal El Kitabı İçeriği Aşağıdadır)*

### TuringLab Nedir?
4–22 Mayıs 2026 arasında, Turing makinelerini araştıran, tasarlayan ve çalıştırılabilir hale getiren tek bir Python projesi geliştireceksiniz: TuringLab.

### Ödev Yapısı
| BÖLÜM | TARİH | KONU | PUAN |
| :--- | :--- | :--- | :--- |
| Bölüm 1 | 4–10 Mayıs | TM Motoru | 50 |
| Bölüm 2 | 11–17 Mayıs | 4 TM Tasarımı | 35 |
| Bölüm 3 | 18–22 Mayıs | Demo Video + Rapor | 15 |
| Bonus | Esnek | MTM, NTM, Görselleştirici | +20 |

### Teknik Standartlar
- Dil: Python 3.10+
- Kod stili: PEP 8
- Test: pytest
- Bağımlılıklar: PyYAML, pytest
