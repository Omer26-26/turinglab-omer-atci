"""
NTM (Non-Deterministic Turing Machine) testleri.
contains_01 makinesi ve çeşitli kenar durumları test edilir.
"""

import pytest
import yaml
import os
from turinglab.ntm import NondeterministicTM, NTMRunResult

# ── Yardımcı fonksiyonlar ─────────────────────────────────────

def create_temp_config(tmp_path, config, filename="test_ntm_config.yaml"):
    """Geçici YAML dosyası oluşturur."""
    config_file = tmp_path / filename
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    return str(config_file)


def get_contains_01_path():
    """contains_01_ntm.yaml dosyasının yolunu döndürür."""
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "machines", "contains_01_ntm.yaml"
    )


@pytest.fixture
def ntm():
    """contains_01 NTM'sini yükler."""
    return NondeterministicTM.from_yaml(get_contains_01_path())


# ── Kabul Testleri ────────────────────────────────────────────

class TestAcceptCases:
    """'01' alt dizgisini içeren girdiler kabul edilmeli."""

    def test_accept_01(self, ntm):
        """'01' doğrudan girdi — kabul edilmeli."""
        result = ntm.run("01")
        assert result.accepted is True
        assert result.reason == "accept"

    def test_accept_001(self, ntm):
        """'001' — '01' alt dizgisi sonda."""
        result = ntm.run("001")
        assert result.accepted is True
        assert result.reason == "accept"

    def test_accept_010(self, ntm):
        """'010' — '01' alt dizgisi başta."""
        result = ntm.run("010")
        assert result.accepted is True
        assert result.reason == "accept"

    def test_accept_1101(self, ntm):
        """'1101' — '01' alt dizgisi sonda."""
        result = ntm.run("1101")
        assert result.accepted is True
        assert result.reason == "accept"

    def test_accept_0011(self, ntm):
        """'0011' — '01' ortada."""
        result = ntm.run("0011")
        assert result.accepted is True
        assert result.reason == "accept"


# ── Red Testleri ──────────────────────────────────────────────

class TestRejectCases:
    """'01' alt dizgisini içermeyen girdiler reddedilmeli."""

    def test_reject_1(self, ntm):
        """'1' — tek karakter, '01' yok."""
        result = ntm.run("1")
        assert result.accepted is False

    def test_reject_111(self, ntm):
        """'111' — sadece 1'ler."""
        result = ntm.run("111")
        assert result.accepted is False

    def test_reject_0(self, ntm):
        """'0' — tek karakter, '01' yok."""
        result = ntm.run("0")
        assert result.accepted is False

    def test_reject_10(self, ntm):
        """'10' — ters sıra, '01' değil."""
        result = ntm.run("10")
        assert result.accepted is False

    def test_reject_000(self, ntm):
        """'000' — sadece 0'lar."""
        result = ntm.run("000")
        assert result.accepted is False


# ── Kenar Durumları ───────────────────────────────────────────

class TestEdgeCases:
    """Boş girdi ve tek karakter gibi kenar durumları."""

    def test_empty_string(self, ntm):
        """Boş girdi — '01' yok, reddedilmeli."""
        result = ntm.run("")
        assert result.accepted is False

    def test_single_0(self, ntm):
        """Tek '0' — '01' tamamlanamaz."""
        result = ntm.run("0")
        assert result.accepted is False

    def test_single_1(self, ntm):
        """Tek '1' — '01' başlangıcı bile yok."""
        result = ntm.run("1")
        assert result.accepted is False


# ── accepting_paths Testi ─────────────────────────────────────

class TestAcceptingPaths:
    """Kabul eden yolların doğruluğunu test eder."""

    def test_accepting_paths_non_empty(self, ntm):
        """Kabul durumunda accepting_paths boş olmamalı."""
        result = ntm.run("01")
        assert result.accepted is True
        assert len(result.accepting_paths) > 0

    def test_accepting_paths_valid_sequence(self, ntm):
        """Her kabul yolu başlangıç durumundan kabul durumuna gitmeli."""
        result = ntm.run("01")
        for path in result.accepting_paths:
            # Yol ilk konfigürasyonda başlangıç durumunda olmalı
            assert path[0].state == "q0"
            # Yol son konfigürasyonda kabul durumunda olmalı
            assert path[-1].state == "q_acc"

    def test_multiple_paths_for_multiple_01(self, ntm):
        """'0101' gibi birden fazla '01' içeren girdide birden fazla yol olabilir."""
        result = ntm.run("0101")
        assert result.accepted is True
        # '01' iki kere geçiyor, en az 2 kabul yolu beklenir
        assert len(result.accepting_paths) >= 2


# ── Limit Testleri ────────────────────────────────────────────

class TestLimits:
    """max_depth ve max_branches limitlerinin çalışmasını test eder."""

    def test_depth_limit(self, tmp_path):
        """Sonsuz döngüye girebilecek makine derinlik limiti ile durmalı."""
        # Sonsuz döngü yapan NTM — q0'da sürekli sağa gider, asla kabul etmez
        config = {
            "name": "infinite_loop",
            "states": ["q0", "q_acc"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "blank": "B",
            "transitions": [
                {
                    "state": "q0",
                    "read": "B",
                    "choices": [
                        {"next": "q0", "write": "B", "move": "R"}
                    ]
                }
            ]
        }
        config_path = create_temp_config(tmp_path, config)
        ntm = NondeterministicTM.from_yaml(config_path)
        result = ntm.run("", max_depth=5)
        assert result.accepted is False
        assert result.reason == "depth_limit"

    def test_branch_limit(self, tmp_path):
        """Çok fazla dal oluşturan makine dal limiti ile durmalı."""
        # Her adımda 2 seçenek — dallanma çok hızlı büyür
        config = {
            "name": "branching",
            "states": ["q0", "q_acc"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "blank": "B",
            "transitions": [
                {
                    "state": "q0",
                    "read": "B",
                    "choices": [
                        {"next": "q0", "write": "B", "move": "R"},
                        {"next": "q0", "write": "X", "move": "R"}
                    ]
                }
            ]
        }
        config_path = create_temp_config(tmp_path, config)
        ntm = NondeterministicTM.from_yaml(config_path)
        result = ntm.run("", max_depth=100, max_branches=20)
        assert result.accepted is False
        assert result.reason == "branch_limit"
        assert result.total_nodes_explored <= 20


# ── total_nodes_explored Testi ────────────────────────────────

class TestNodesExplored:
    """Keşfedilen düğüm sayısının makul olduğunu test eder."""

    def test_nodes_explored_is_positive(self, ntm):
        """Herhangi bir çalıştırmada en az 1 düğüm keşfedilmeli."""
        result = ntm.run("01")
        assert result.total_nodes_explored >= 1

    def test_nodes_explored_bounded(self, ntm):
        """Kısa girdilerde keşfedilen düğüm sayısı makul olmalı."""
        result = ntm.run("01")
        # '01' gibi kısa bir girdi için çok fazla düğüm keşfedilmemeli
        assert result.total_nodes_explored < 100

    def test_nodes_explored_respects_branch_limit(self, ntm):
        """max_branches limiti aşılmamalı."""
        result = ntm.run("01", max_branches=5)
        assert result.total_nodes_explored <= 5


# ── YAML Yükleme Testleri ────────────────────────────────────

class TestYAMLLoading:
    """YAML dosya yükleme ve hata durumlarını test eder."""

    def test_from_yaml_file(self):
        """contains_01_ntm.yaml dosyası başarıyla yüklenmeli."""
        ntm = NondeterministicTM.from_yaml(get_contains_01_path())
        assert ntm.name == "contains_01"
        assert "q0" in ntm.states
        assert "q_acc" in ntm.accept_states

    def test_missing_field_raises(self, tmp_path):
        """Zorunlu alan eksikse ValueError fırlatılmalı."""
        config = {"states": ["q0"]}
        config_path = create_temp_config(tmp_path, config)
        with pytest.raises(ValueError):
            NondeterministicTM.from_yaml(config_path)

    def test_deterministic_format_fallback(self, tmp_path):
        """Deterministik formattaki geçişler de yüklenebilmeli (tek seçenek)."""
        config = {
            "states": ["q0", "q_acc"],
            "start_state": "q0",
            "accept_states": ["q_acc"],
            "transitions": [
                {"state": "q0", "read": "1", "next": "q_acc", "write": "1", "move": "R"}
            ]
        }
        config_path = create_temp_config(tmp_path, config)
        ntm = NondeterministicTM.from_yaml(config_path)
        result = ntm.run("1")
        assert result.accepted is True
