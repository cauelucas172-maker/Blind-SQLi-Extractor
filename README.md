# Blind SQLi Extractor

Automacao de Blind SQL injection (boolean-based) com busca binaria, auto-deteccao de cookie/sinal e single-session handling.

## Destaques

- **Auto-tracking cookie** — pega o TrackingId na propria sessao
- **Single-session architecture** — o sinal "Welcome back" e POR SESSAO; ferramenta usa uma Session unica pra tudo (bug real descoberto em debug)
- **Busca binaria** — ~6 requests por caractere em vez de ~26 (linear)
- **Progresso ao vivo** — barra + req/s em tempo real
- **Painel interativo + CLI**

## Uso

    blind_sqli
    [?] URL do lab: https://xxx.web-security-academy.net/

    → pega cookie, detecta sinal, extrai senha automaticamente

## A licao tecnica

O sinal condicional (Welcome back) e vinculado a SESSAO do cliente.
Pegar o cookie numa sessao e injetar noutra quebra o canal.
Tudo (registro + extracao) precisa da mesma Session.

## Uso etico

Labs autorizados (PortSwigger/HTB/THM) ou sistemas proprios apenas.

## Autor

shinei
