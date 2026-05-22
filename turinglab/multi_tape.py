"""
Çok Şeritli Turing Makinesi (Multi-Tape Turing Machine) motoru.
Bonus A ödevi kapsamında SingleTapeTM ile aynı kalıpları kullanır.
"""
import yaml
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from turinglab.tm_engine import RunResult


@dataclass
class MultiTapeConfiguration:
    """Çok şeritli TM için anlık konfigürasyon."""
    state: str
    tapes: List[str]
    head_positions: List[int]


class MultiTapeTM:
    """k-şeritli Turing Makinesi."""

    def __init__(self, config_dict: Dict[str, Any]):
        self.config = config_dict
        self.name = config_dict.get('name', 'Multi-Tape Turing Machine')
        self.num_tapes = config_dict.get('num_tapes', 1)
        self.states = config_dict['states']
        self.start_state = config_dict.get('start_state') or config_dict.get('initial_state')
        self.accept_states = config_dict['accept_states']
        self.reject_states = config_dict.get('reject_states', [])
        self.blank = config_dict.get('blank', 'B')

        # Geçiş fonksiyonunu standartlaştır
        # Anahtar: (durum, (okunan_1, okunan_2, ..., okunan_k))
        # Değer: (sonraki_durum, (yazılan_1, ..., yazılan_k), (hareket_1, ..., hareket_k))
        self.transitions: Dict[str, Dict[tuple, tuple]] = {}
        raw_transitions = config_dict['transitions']

        if isinstance(raw_transitions, list):
            for t in raw_transitions:
                state = t['state']
                # read, write, move alanları k uzunluklu listeler
                read_syms = tuple(str(s) for s in t['read'])
                write_syms = tuple(str(s) for s in t['write'])
                move_dirs = tuple(t['move'])

                if len(read_syms) != self.num_tapes:
                    raise ValueError(
                        f"Geçiş hatası: 'read' listesi {self.num_tapes} uzunlukta olmalı, "
                        f"ancak {len(read_syms)} verildi. Durum: {state}"
                    )
                if len(write_syms) != self.num_tapes:
                    raise ValueError(
                        f"Geçiş hatası: 'write' listesi {self.num_tapes} uzunlukta olmalı, "
                        f"ancak {len(write_syms)} verildi. Durum: {state}"
                    )
                if len(move_dirs) != self.num_tapes:
                    raise ValueError(
                        f"Geçiş hatası: 'move' listesi {self.num_tapes} uzunlukta olmalı, "
                        f"ancak {len(move_dirs)} verildi. Durum: {state}"
                    )

                if state not in self.transitions:
                    self.transitions[state] = {}
                self.transitions[state][read_syms] = (
                    t['next'],
                    write_syms,
                    move_dirs,
                )
        else:
            raise ValueError("Geçişler liste formatında olmalıdır.")

    @classmethod
    def from_yaml(cls, path: str):
        """YAML dosyasından çok şeritli Turing Makinesi yükler."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"YAML yüklenemedi: {e}")

        required_fields = ['states', 'accept_states', 'transitions', 'num_tapes']
        for fld in required_fields:
            if fld not in config:
                raise ValueError(f"Eksik zorunlu alan: {fld}")

        if 'start_state' not in config and 'initial_state' not in config:
            raise ValueError("Eksik zorunlu alan: start_state")

        return cls(config)

    def run(self, input_string: str = "", max_steps: int = 1000,
            verbose: bool = False) -> RunResult:
        """Çok şeritli Turing Makinesi'ni verilen girdi üzerinde çalıştırır.

        Girdi yalnızca 1. şeride yazılır, diğer şeritler boş başlar.
        """
        k = self.num_tapes

        # Şeritleri oluştur – her biri bağımsız Dict[int, str]
        tapes: List[Dict[int, str]] = [{}  for _ in range(k)]

        # Girdiyi 1. şeride (indeks 0) yaz
        for i, ch in enumerate(input_string):
            tapes[0][i] = ch

        head_positions = [0] * k
        current_state = self.start_state
        steps = 0
        history: List[MultiTapeConfiguration] = []
        reason = ""
        accepted = False

        def get_tape_str(tape_dict: Dict[int, str], head_pos: int) -> str:
            """Şeridin string temsilini döndürür."""
            if not tape_dict:
                return self.blank
            min_idx = min(tape_dict.keys())
            max_idx = max(tape_dict.keys())
            start = min(min_idx, head_pos)
            end = max(max_idx, head_pos)
            res = ""
            for i in range(start, end + 1):
                res += tape_dict.get(i, self.blank)
            return res

        def get_verbose_tape(tape_dict: Dict[int, str], head_pos: int) -> str:
            """Verbose çıktı için şerit gösterimi (kafa pozisyonu köşeli parantez ile)."""
            if not tape_dict:
                ch = self.blank
                return f"[{ch}]"
            min_idx = min(tape_dict.keys())
            max_idx = max(tape_dict.keys())
            start = min(min_idx, head_pos)
            end = max(max_idx, head_pos)
            res = ""
            for i in range(start, end + 1):
                ch = tape_dict.get(i, self.blank)
                if i == head_pos:
                    res += f"[{ch}]"
                else:
                    res += ch
            return res

        while steps <= max_steps:
            # Adım öncesi tarihçeye kaydet
            tape_strs = [get_tape_str(tapes[t], head_positions[t]) for t in range(k)]
            history.append(MultiTapeConfiguration(
                state=current_state,
                tapes=list(tape_strs),
                head_positions=list(head_positions),
            ))

            # Kabul/ret durumu kontrolü
            if current_state in self.accept_states:
                accepted = True
                reason = "accept"
                break
            if current_state in self.reject_states:
                accepted = False
                reason = "reject"
                break

            # Zaman aşımı kontrolü
            if steps == max_steps:
                accepted = False
                reason = "timeout"
                break

            # Her şeritten okunan sembolleri al
            read_syms = tuple(
                tapes[t].get(head_positions[t], self.blank) for t in range(k)
            )

            # Geçiş bul
            state_trans = self.transitions.get(current_state, {})
            if read_syms not in state_trans:
                accepted = False
                reason = "no_transition"
                break

            next_state, write_syms, move_dirs = state_trans[read_syms]

            if verbose:
                tape_displays = " | ".join(
                    f"Şerit{t+1}: {get_verbose_tape(tapes[t], head_positions[t])}"
                    for t in range(k)
                )
                print(f"Adım {steps} | Durum: {current_state} | {tape_displays}")

            # Geçişi uygula
            for t in range(k):
                tapes[t][head_positions[t]] = write_syms[t]
                if move_dirs[t] == 'R':
                    head_positions[t] += 1
                elif move_dirs[t] == 'L':
                    head_positions[t] -= 1
                # 'S' → kafa yerinde kalır

            current_state = next_state
            steps += 1

        # Sonuç şerit stringlerini oluştur – tüm şeritleri birleştir
        final_tapes = [get_tape_str(tapes[t], head_positions[t]) for t in range(k)]
        # RunResult.final_tape: tüm şeritleri " | " ile ayırarak göster
        final_tape_combined = " | ".join(final_tapes)

        return RunResult(
            accepted=accepted,
            final_tape=final_tape_combined,
            steps=steps,
            history=history,  # MultiTapeConfiguration nesneleri
            reason=reason,
        )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python -m turinglab.multi_tape <config_yaml> <girdi_string>")
    else:
        tm = MultiTapeTM.from_yaml(sys.argv[1])
        result = tm.run(sys.argv[2], verbose=True)
        print(f"\nSonuç: {'KABUL' if result.accepted else 'RED'} ({result.reason})")
        print(f"Son Şerit: {result.final_tape}")
        print(f"Adım Sayısı: {result.steps}")
