"""
Çok Şeritli Turing Makinesi (Multi-Tape TM) testleri.
3-şeritli ikili toplama makinesi ve motor temel işlevleri test edilir.
"""
import pytest
import yaml
import os
import io
from contextlib import redirect_stdout
from turinglab.multi_tape import MultiTapeTM, MultiTapeConfiguration
from turinglab.tm_engine import RunResult


# ────────────────────────────────────────────────────────
# Yardımcı fonksiyonlar
# ────────────────────────────────────────────────────────

def create_temp_config(tmp_path, config, filename="test_multi_config.yaml"):
    """Geçici YAML konfigürasyon dosyası oluşturur."""
    config_file = tmp_path / filename
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)
    return str(config_file)


def get_binary_addition_path():
    """binary_addition_3tape.yaml dosyasının yolunu döndürür."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "machines", "binary_addition_3tape.yaml")


def extract_tape3_result(result: RunResult) -> str:
    """RunResult'tan Şerit 3'ün sonucunu çıkarır ve baştaki/sondaki B'leri temizler."""
    # final_tape formatı: "tape1 | tape2 | tape3"
    parts = result.final_tape.split(" | ")
    tape3 = parts[2] if len(parts) >= 3 else ""
    return tape3.strip("B")


# ────────────────────────────────────────────────────────
# Basit 2-şeritli kopyalama makinesi fixture
# ────────────────────────────────────────────────────────

@pytest.fixture
def simple_copy_config():
    """2-şeritli basit kopyalama makinesi: Şerit 1'den Şerit 2'ye kopyalar."""
    return {
        "name": "simple_copy",
        "num_tapes": 2,
        "states": ["q_copy", "q_rewind", "q_accept"],
        "start_state": "q_copy",
        "accept_states": ["q_accept"],
        "transitions": [
            # Kopyalama: Şerit 1'den oku, Şerit 2'ye yaz
            {"state": "q_copy", "read": ["0", "B"], "next": "q_copy",
             "write": ["0", "0"], "move": ["R", "R"]},
            {"state": "q_copy", "read": ["1", "B"], "next": "q_copy",
             "write": ["1", "1"], "move": ["R", "R"]},
            # Girdi bitti → kabul et
            {"state": "q_copy", "read": ["B", "B"], "next": "q_accept",
             "write": ["B", "B"], "move": ["S", "S"]},
        ]
    }


# ────────────────────────────────────────────────────────
# 3-Şeritli İkili Toplama Testleri
# ────────────────────────────────────────────────────────

class TestBinaryAddition3Tape:
    """3-şeritli ikili toplama makinesi testleri."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Her test için TM'yi yükle."""
        self.tm = MultiTapeTM.from_yaml(get_binary_addition_path())

    def test_simple_addition_1_plus_1(self):
        """1 + 1 = 10 (ikili)"""
        result = self.tm.run("1#1")
        assert result.accepted is True
        assert result.reason == "accept"
        tape3 = extract_tape3_result(result)
        assert tape3 == "10", f"Beklenen: 10, Alınan: {tape3}"

    def test_addition_10_plus_1(self):
        """10 + 1 = 11 (ikili: 2 + 1 = 3)"""
        result = self.tm.run("10#1")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "11", f"Beklenen: 11, Alınan: {tape3}"

    def test_addition_11_plus_1(self):
        """11 + 1 = 100 (ikili: 3 + 1 = 4)"""
        result = self.tm.run("11#1")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "100", f"Beklenen: 100, Alınan: {tape3}"

    def test_addition_101_plus_11(self):
        """101 + 11 = 1000 (ikili: 5 + 3 = 8)"""
        result = self.tm.run("101#11")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "1000", f"Beklenen: 1000, Alınan: {tape3}"

    def test_addition_110_plus_101(self):
        """110 + 101 = 1011 (ikili: 6 + 5 = 11)"""
        result = self.tm.run("110#101")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "1011", f"Beklenen: 1011, Alınan: {tape3}"

    def test_addition_0_plus_0(self):
        """0 + 0 = 0 (sıfır toplama)"""
        result = self.tm.run("0#0")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "0", f"Beklenen: 0, Alınan: {tape3}"

    def test_addition_0_plus_1(self):
        """0 + 1 = 1"""
        result = self.tm.run("0#1")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "1", f"Beklenen: 1, Alınan: {tape3}"

    def test_carry_propagation_111_plus_1(self):
        """111 + 1 = 1000 (ikili: 7 + 1 = 8, çoklu taşma)"""
        result = self.tm.run("111#1")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "1000", f"Beklenen: 1000, Alınan: {tape3}"

    def test_equal_length_addition(self):
        """1010 + 0101 = 1111 (ikili: 10 + 5 = 15)"""
        result = self.tm.run("1010#0101")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "1111", f"Beklenen: 1111, Alınan: {tape3}"

    def test_large_carry_propagation(self):
        """1111 + 1 = 10000 (ikili: 15 + 1 = 16)"""
        result = self.tm.run("1111#1")
        assert result.accepted is True
        tape3 = extract_tape3_result(result)
        assert tape3 == "10000", f"Beklenen: 10000, Alınan: {tape3}"


# ────────────────────────────────────────────────────────
# Motor Temel İşlev Testleri
# ────────────────────────────────────────────────────────

class TestMultiTapeEngineBasics:
    """Çok şeritli TM motorunun temel işlevlerini test eder."""

    def test_from_yaml_loading(self):
        """YAML dosyasından başarılı yükleme."""
        tm = MultiTapeTM.from_yaml(get_binary_addition_path())
        assert tm.name == "binary_addition_3tape"
        assert tm.num_tapes == 3
        assert "q_accept" in tm.accept_states

    def test_simple_copy(self, tmp_path, simple_copy_config):
        """2-şeritli basit kopyalama testi."""
        config_path = create_temp_config(tmp_path, simple_copy_config)
        tm = MultiTapeTM.from_yaml(config_path)
        result = tm.run("1010")
        assert result.accepted is True
        # Şerit 2'de aynı girdi olmalı
        parts = result.final_tape.split(" | ")
        tape2 = parts[1].strip("B")
        assert tape2 == "1010"

    def test_timeout(self, tmp_path):
        """Zaman aşımı testi: sonsuz döngü durumunda timeout döner."""
        config = {
            "name": "infinite_loop",
            "num_tapes": 2,
            "states": ["q0"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "transitions": [
                {"state": "q0", "read": ["B", "B"], "next": "q0",
                 "write": ["B", "B"], "move": ["R", "R"]}
            ]
        }
        config_path = create_temp_config(tmp_path, config)
        tm = MultiTapeTM.from_yaml(config_path)
        result = tm.run("", max_steps=10)
        assert result.accepted is False
        assert result.reason == "timeout"
        assert result.steps == 10

    def test_no_transition(self, tmp_path):
        """Geçiş bulunamadığında no_transition döner."""
        config = {
            "name": "no_trans",
            "num_tapes": 2,
            "states": ["q0"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "transitions": []
        }
        config_path = create_temp_config(tmp_path, config)
        tm = MultiTapeTM.from_yaml(config_path)
        result = tm.run("1")
        assert result.accepted is False
        assert result.reason == "no_transition"

    def test_reject_state(self, tmp_path):
        """Ret durumuna geçildiğinde reject döner."""
        config = {
            "name": "rejector",
            "num_tapes": 2,
            "states": ["q0", "q_rej"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "reject_states": ["q_rej"],
            "transitions": [
                {"state": "q0", "read": ["1", "B"], "next": "q_rej",
                 "write": ["1", "B"], "move": ["S", "S"]}
            ]
        }
        config_path = create_temp_config(tmp_path, config)
        tm = MultiTapeTM.from_yaml(config_path)
        result = tm.run("1")
        assert result.accepted is False
        assert result.reason == "reject"

    def test_invalid_yaml(self, tmp_path):
        """Geçersiz YAML dosyası ValueError fırlatır."""
        config_path = tmp_path / "invalid.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: yaml: :")
        with pytest.raises(ValueError):
            MultiTapeTM.from_yaml(str(config_path))

    def test_missing_fields(self, tmp_path):
        """Eksik zorunlu alan ValueError fırlatır."""
        config = {"states": ["q0"]}
        config_path = create_temp_config(tmp_path, config)
        with pytest.raises(ValueError):
            MultiTapeTM.from_yaml(config_path)

    def test_missing_num_tapes(self, tmp_path):
        """num_tapes eksik olduğunda ValueError fırlatır."""
        config = {
            "states": ["q0"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "transitions": []
        }
        config_path = create_temp_config(tmp_path, config)
        with pytest.raises(ValueError):
            MultiTapeTM.from_yaml(config_path)

    def test_mismatched_tape_count(self, tmp_path):
        """Geçişte yanlış uzunlukta read/write/move listesi ValueError fırlatır."""
        config = {
            "name": "mismatch",
            "num_tapes": 3,
            "states": ["q0"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "transitions": [
                # 3 şerit ama sadece 2 elemanlı read listesi
                {"state": "q0", "read": ["B", "B"], "next": "q0",
                 "write": ["B", "B", "B"], "move": ["S", "S", "S"]}
            ]
        }
        config_path = create_temp_config(tmp_path, config)
        with pytest.raises(ValueError):
            MultiTapeTM.from_yaml(config_path)

    def test_verbose_output(self, tmp_path, simple_copy_config):
        """Verbose çıktı doğru formatlanır."""
        config_path = create_temp_config(tmp_path, simple_copy_config)
        tm = MultiTapeTM.from_yaml(config_path)

        f = io.StringIO()
        with redirect_stdout(f):
            tm.run("10", verbose=True)
        output = f.getvalue()

        # Verbose çıktıda "Adım", "Durum", "Şerit1", "Şerit2" kelimeleri olmalı
        assert "Adım 0" in output
        assert "Durum: q_copy" in output
        assert "Şerit1:" in output
        assert "Şerit2:" in output

    def test_history_tracking(self, tmp_path, simple_copy_config):
        """Tarihçe doğru kaydedilir (MultiTapeConfiguration)."""
        config_path = create_temp_config(tmp_path, simple_copy_config)
        tm = MultiTapeTM.from_yaml(config_path)
        result = tm.run("1")

        assert len(result.history) >= 2
        first = result.history[0]
        assert isinstance(first, MultiTapeConfiguration)
        assert first.state == "q_copy"
        assert len(first.tapes) == 2
        assert len(first.head_positions) == 2
        assert first.head_positions == [0, 0]

    def test_empty_input_on_copy(self, tmp_path, simple_copy_config):
        """Boş girdi ile kopyalama makinesi çalışır."""
        config_path = create_temp_config(tmp_path, simple_copy_config)
        tm = MultiTapeTM.from_yaml(config_path)
        result = tm.run("")
        assert result.accepted is True
        assert result.steps == 1  # Blank okur, q_accept'e geçer (1 adım)
