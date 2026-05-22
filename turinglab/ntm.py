"""
Belirsiz (Non-Deterministic) Turing Makinesi modülü.
BFS tabanlı hesaplama ağacı keşfi ile çalışır.
"""

import yaml
from collections import deque
from typing import Dict, List, Any
from dataclasses import dataclass, field
from .tm_engine import Configuration


@dataclass
class NTMRunResult:
    """NTM çalıştırma sonucunu temsil eden veri sınıfı."""
    accepted: bool
    accepting_paths: List[List[Configuration]] = field(default_factory=list)
    total_nodes_explored: int = 0
    reason: str = ""  # 'accept', 'reject', 'depth_limit', 'branch_limit'


class NondeterministicTM:
    """
    Belirsiz Turing Makinesi (NTM) implementasyonu.

    Aynı (durum, okunan) çifti için birden fazla geçiş seçeneği tanımlanabilir.
    BFS (Breadth-First Search) kullanılarak hesaplama ağacı keşfedilir.
    DFS yerine BFS tercih edilir çünkü DFS sonsuz döngülere takılabilir.
    """

    def __init__(self, config_dict: Dict[str, Any]):
        self.config = config_dict
        self.name = config_dict.get('name', 'NTM')
        self.states = config_dict['states']
        self.start_state = config_dict.get('start_state') or config_dict.get('initial_state')
        self.accept_states = config_dict['accept_states']
        self.reject_states = config_dict.get('reject_states', [])
        self.blank = config_dict.get('blank', 'B')

        # Geçişleri ayrıştır: {durum: {okunan_karakter: [(hedef, yaz, hareket), ...]}}
        self.transitions: Dict[str, Dict[str, List[tuple]]] = {}
        raw_transitions = config_dict['transitions']

        if isinstance(raw_transitions, list):
            for t in raw_transitions:
                state = t['state']
                read_char = t['read']
                if state not in self.transitions:
                    self.transitions[state] = {}
                if read_char not in self.transitions[state]:
                    self.transitions[state][read_char] = []

                # NTM formatı: 'choices' listesi ile birden fazla seçenek
                if 'choices' in t:
                    for choice in t['choices']:
                        self.transitions[state][read_char].append(
                            (choice['next'], choice['write'], choice['move'])
                        )
                else:
                    # Deterministik format desteği (tek seçenek)
                    self.transitions[state][read_char].append(
                        (t['next'], t['write'], t['move'])
                    )
        else:
            self.transitions = raw_transitions

    @classmethod
    def from_yaml(cls, path: str):
        """YAML dosyasından NTM yükler."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"YAML dosyası yüklenemedi: {e}")

        required_fields = ['states', 'accept_states', 'transitions']
        for field_name in required_fields:
            if field_name not in config:
                raise ValueError(f"Eksik zorunlu alan: {field_name}")

        if 'start_state' not in config and 'initial_state' not in config:
            raise ValueError("Eksik zorunlu alan: start_state")

        return cls(config)

    def _get_tape_str(self, tape: Dict[int, str], head_pos: int) -> str:
        """Şerit içeriğini string olarak döndürür."""
        if not tape:
            return self.blank
        min_idx = min(min(tape.keys()), head_pos)
        max_idx = max(max(tape.keys()), head_pos)
        return "".join(tape.get(i, self.blank) for i in range(min_idx, max_idx + 1))

    def _make_config(self, state: str, tape: Dict[int, str], head_pos: int) -> Configuration:
        """Mevcut durumdan Configuration nesnesi oluşturur."""
        return Configuration(
            state=state,
            tape=self._get_tape_str(tape, head_pos),
            head_position=head_pos
        )

    def run(self, input_string: str = "", max_depth: int = 100,
            max_branches: int = 10000) -> NTMRunResult:
        """
        NTM'yi verilen giriş üzerinde BFS ile çalıştırır.

        Args:
            input_string: Giriş dizgisi
            max_depth: BFS derinlik limiti
            max_branches: Toplam düğüm (node) limiti

        Returns:
            NTMRunResult: Çalıştırma sonucu
        """
        # Başlangıç şerit durumu
        initial_tape: Dict[int, str] = {i: char for i, char in enumerate(input_string)}
        head_pos = 0
        initial_config = self._make_config(self.start_state, initial_tape, head_pos)

        # BFS kuyruğu: (durum, şerit_dict, kafa_pozisyonu, derinlik, yol)
        queue = deque()
        queue.append((self.start_state, dict(initial_tape), head_pos, 0, [initial_config]))

        accepting_paths: List[List[Configuration]] = []
        total_explored = 0
        hit_depth_limit = False
        hit_branch_limit = False

        while queue:
            # Dal limiti kontrolü
            if total_explored >= max_branches:
                hit_branch_limit = True
                break

            current_state, tape, head_position, depth, path = queue.popleft()
            total_explored += 1

            # Kabul durumu kontrolü
            if current_state in self.accept_states:
                accepting_paths.append(path)
                continue  # Diğer yolları da aramaya devam et

            # Red durumu kontrolü — bu dalı kes
            if current_state in self.reject_states:
                continue

            # Derinlik limiti kontrolü
            if depth >= max_depth:
                hit_depth_limit = True
                continue

            # Mevcut karakteri oku
            current_char = tape.get(head_position, self.blank)

            # Geçiş var mı kontrol et
            state_trans = self.transitions.get(current_state, {})
            if current_char not in state_trans:
                # Geçiş yok — bu dal çıkmazda, devam et
                continue

            # Tüm seçenekleri kuyruğa ekle (belirsizlik burada!)
            choices = state_trans[current_char]
            for next_state, write_char, move in choices:
                # Şerit kopyasını oluştur (her dal kendi kopyasında çalışır)
                new_tape = dict(tape)
                new_tape[head_position] = write_char

                # Kafa hareketini uygula
                new_head = head_position
                if move == 'R':
                    new_head += 1
                elif move == 'L':
                    new_head -= 1
                # 'S' (Stay) durumunda kafa yerinde kalır

                new_config = self._make_config(next_state, new_tape, new_head)
                queue.append((next_state, new_tape, new_head, depth + 1, path + [new_config]))

        # Sonuç durumunu belirle
        if accepting_paths:
            reason = "accept"
            accepted = True
        elif hit_branch_limit:
            reason = "branch_limit"
            accepted = False
        elif hit_depth_limit:
            reason = "depth_limit"
            accepted = False
        else:
            reason = "reject"
            accepted = False

        return NTMRunResult(
            accepted=accepted,
            accepting_paths=accepting_paths,
            total_nodes_explored=total_explored,
            reason=reason
        )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Kullanım: python -m turinglab.ntm <config_yaml> <girdi_dizgisi>")
    else:
        ntm = NondeterministicTM.from_yaml(sys.argv[1])
        result = ntm.run(sys.argv[2])
        print(f"\nSonuç: {'KABUL' if result.accepted else 'RED'} ({result.reason})")
        print(f"Keşfedilen düğüm sayısı: {result.total_nodes_explored}")
        if result.accepting_paths:
            print(f"Kabul eden yol sayısı: {len(result.accepting_paths)}")
            for i, path in enumerate(result.accepting_paths):
                print(f"\n--- Yol {i+1} ---")
                for config in path:
                    print(f"  Durum: {config.state}, Şerit: {config.tape}, Kafa: {config.head_position}")
