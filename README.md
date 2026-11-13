# TLSentinel

**Lightweight TLS Diagnostics & Secure Callback Listener**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library-success.svg)]()
[![Protocol](https://img.shields.io/badge/Protocol-TLS-blueviolet.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

TLSentinel is a lightweight command-line utility designed for TLS connection diagnostics, certificate validation, mutual TLS authentication, and secure callback monitoring.

Built entirely with Python's standard library, TLSentinel requires no third-party dependencies.

---

## Features

- TLS endpoint diagnostics
- SSL certificate verification
- Custom certificate authority support
- Mutual TLS authentication
- Certificate subject and issuer inspection
- TLS version and cipher suite detection
- Automatic certificate error classification
- Local TLS callback listener
- Multithreaded connection handling
- UTC timestamped logging
- No external dependencies

---

## Repository Structure

```text
TLSentinel/
├── tlsentinel.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## Requirements

- Python 3.8 or newer
- OpenSSL support
- Server certificate and private key for listener mode

No external packages are required.

---

## Installation

Clone the repository
```bash
git clone https://github.com/SleepTheGod/TLSentinel/
```

Navigate into the project directory

```bash
cd TLSentinel
```

Run TLSentinel

```bash
python3 tlsentinel.py
```

Running without arguments automatically checks localhost on port 8443.

---

## Usage

TLSentinel provides two operating modes.

| Mode | Description |
|---|---|
| `check` | Inspect a TLS endpoint |
| `listen` | Start a TLS callback listener |

### TLS Endpoint Diagnostics

```bash
python3 tlsentinel.py check --host example.com --port 443
```

### Custom Certificate Authority

```bash
python3 tlsentinel.py check \
    --host internal.example.com \
    --port 8443 \
    --ca ca.crt
```

### Mutual TLS Client Authentication

```bash
python3 tlsentinel.py check \
    --host internal.example.com \
    --port 8443 \
    --cert client.crt \
    --key client.key \
    --ca ca.crt
```

### Start a TLS Listener

```bash
python3 tlsentinel.py listen \
    --bind 127.0.0.1 \
    --port 8443 \
    --cert server.crt \
    --key server.key
```

### Enable Mutual TLS

```bash
python3 tlsentinel.py listen \
    --bind 127.0.0.1 \
    --port 8443 \
    --cert server.crt \
    --key server.key \
    --ca ca.crt
```

Press `CTRL+C` to stop the listener.

---

## Certificate Error Classification

TLSentinel identifies common certificate verification failures.

| Classification | Description |
|---|---|
| `EXPIRED CERTIFICATE` | Certificate has expired |
| `SELF-SIGNED OR UNTRUSTED CERTIFICATE` | Certificate cannot be validated against a trusted CA |
| `HOSTNAME MISMATCH` | Certificate hostname does not match the requested hostname |
| `TLS VERIFICATION FAILURE` | Another certificate verification error occurred |

---

## Example Output

```text
[2026-11-13T00:00:00+00:00] Checking example.com:443
[2026-11-13T00:00:01+00:00] TLS HANDSHAKE: SUCCESS
[2026-11-13T00:00:01+00:00] TLS version: TLSv1.3
[2026-11-13T00:00:01+00:00] Cipher: TLS_AES_256_GCM_SHA384
[2026-11-13T00:00:01+00:00] CERTIFICATE VERIFICATION: SUCCESS
```

---

## Command Reference

### Check Mode

| Argument | Description | Default |
|---|---|---|
| `--host` | Target hostname or IP address | `127.0.0.1` |
| `--port` | Target TCP port | `8443` |
| `--ca` | Custom CA certificate | None |
| `--cert` | Client certificate | None |
| `--key` | Client private key | None |

### Listen Mode

| Argument | Description | Default |
|---|---|---|
| `--bind` | Local interface | `127.0.0.1` |
| `--port` | Listening port | `8443` |
| `--cert` | Server certificate | Required |
| `--key` | Server private key | Required |
| `--ca` | CA certificate for client authentication | None |

---

## Dependencies

TLSentinel uses exclusively built-in Python modules.

```python
argparse
socket
ssl
threading
sys
datetime
```

No `requirements.txt` file is necessary.

---

## Security

- Only test systems you own or have authorization to assess.
- Keep private keys secure.
- Use trusted certificate authorities.
- Enable mutual TLS when client identity verification is required.
- Avoid exposing the listener to untrusted networks.
- Use appropriate firewall restrictions.

Without a configured CA, the listener encrypts connections but does not authenticate client identities.

---

## Limitations

- The listener is designed for diagnostics rather than general-purpose application hosting.
- Callback connections receive a fixed response.
- Certificate revocation checking is not explicitly implemented.
- The listener uses individual worker threads for incoming connections.

---

## License

Released under the MIT License.

See the LICENSE file for additional information.

---

## Author

**Made by Taylor Christian Newsome**

---

**TLSentinel**

*Inspect. Validate. Monitor.*
