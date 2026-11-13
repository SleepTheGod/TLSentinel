import socket
import ssl
import threading
import sys
from datetime import datetime, timezone
printf("Made by Taylor Christian Newsome")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8443


def log(message):
    # Avoid print(..., flush=True): some sandboxes shadow builtins.print
    # with an object that doesn't accept the flush keyword.
    timestamp = datetime.now(timezone.utc).isoformat()
    sys.stdout.write(f"[{timestamp}] {message}\n")
    sys.stdout.flush()


def classify_error(error):
    message = str(error).lower()
    code = getattr(error, "verify_code", None)

    if code == 10 or "expired" in message:
        return "EXPIRED CERTIFICATE"

    if code in (18, 19, 20, 21) or "self-signed" in message:
        return "SELF-SIGNED OR UNTRUSTED CERTIFICATE"

    if code == 62 or "hostname mismatch" in message:
        return "HOSTNAME MISMATCH"

    return "TLS VERIFICATION FAILURE"


def client_check(args):
    context = ssl.create_default_context()

    if args.ca:
        context.load_verify_locations(cafile=args.ca)

    if args.cert and args.key:
        context.load_cert_chain(args.cert, args.key)

    log(f"Checking {args.host}:{args.port}")

    try:
        with socket.create_connection(
            (args.host, args.port),
            timeout=10
        ) as raw:

            with context.wrap_socket(
                raw,
                server_hostname=args.host
            ) as tls:

                log("TLS HANDSHAKE: SUCCESS")
                log(f"TLS version: {tls.version()}")
                log(f"Cipher: {tls.cipher()[0]}")

                certificate = tls.getpeercert()

                log(f"Certificate subject: {certificate.get('subject')}")
                log(f"Certificate issuer: {certificate.get('issuer')}")
                log("CERTIFICATE VERIFICATION: SUCCESS")

    except ssl.SSLCertVerificationError as error:
        log("TLS HANDSHAKE: FAILED")
        log(f"Classification: {classify_error(error)}")
        log(f"Details: {error}")

    except (ssl.SSLError, OSError) as error:
        log(f"CONNECTION FAILED: {error}")


def create_server_context(args):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(args.cert, args.key)

    if args.ca:
        context.load_verify_locations(cafile=args.ca)
        context.verify_mode = ssl.CERT_REQUIRED
        log("Mutual TLS enabled.")
    else:
        context.verify_mode = ssl.CERT_NONE
        log("Client certificate authentication disabled.")

    return context


def handle_callback(raw, address, context):
    log(f"Connection from {address[0]}:{address[1]}")

    try:
        with context.wrap_socket(raw, server_side=True) as tls:
            log("TLS HANDSHAKE: SUCCESS")
            log(f"TLS version: {tls.version()}")

            certificate = tls.getpeercert()

            if context.verify_mode == ssl.CERT_REQUIRED:
                if not certificate:
                    log("CLIENT AUTHENTICATION: FAILED")
                    return

                log("CLIENT AUTHENTICATION: SUCCESS")
                log(f"Client certificate: {certificate.get('subject')}")

            else:
                log("Client identity was not verified.")

            tls.sendall(b"Callback received.\n")
            log("Callback logged.")

    except ssl.SSLError as error:
        log(f"TLS ERROR: {error}")

    except OSError as error:
        log(f"CONNECTION ERROR: {error}")

    finally:
        raw.close()


def start_listener(args):
    context = create_server_context(args)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR is not guaranteed to exist on every Python build
    # (some sandboxes expose a stripped socket module).
    reuse = getattr(socket, "SO_REUSEADDR", None)
    if reuse is None:
        reuse = getattr(socket, "SO_REUSEPORT", None)
    if reuse is not None:
        server.setsockopt(socket.SOL_SOCKET, reuse, 1)
    else:
        log("SO_REUSEADDR unavailable; continuing without it")

    try:
        server.bind((args.bind, args.port))
        server.listen(10)

        log(f"TLS listener running on {args.bind}:{args.port}")

        while True:
            raw, address = server.accept()

            worker = threading.Thread(
                target=handle_callback,
                args=(raw, address, context),
                daemon=True
            )
            worker.start()

    except KeyboardInterrupt:
        log("Listener stopped.")

    except OSError as error:
        log(f"LISTENER ERROR: {error}")

    finally:
        server.close()


def build_parser():
    parser = argparse.ArgumentParser(
        description="Standard-library TLS diagnostics"
    )

    subparsers = parser.add_subparsers(
        dest="mode",
        required=False
    )

    check = subparsers.add_parser(
        "check",
        help="Check a TLS endpoint"
    )

    check.add_argument("--host", default=DEFAULT_HOST)
    check.add_argument("--port", type=int, default=DEFAULT_PORT)
    check.add_argument("--ca")
    check.add_argument("--cert")
    check.add_argument("--key")

    listen = subparsers.add_parser(
        "listen",
        help="Start a local TLS callback logger"
    )

    listen.add_argument("--bind", default="127.0.0.1")
    listen.add_argument("--port", type=int, default=DEFAULT_PORT)
    listen.add_argument("--cert", required=True)
    listen.add_argument("--key", required=True)
    listen.add_argument("--ca")

    return parser


def main():
    parser = build_parser()

    argv = sys.argv[1:]

    # No arguments means a localhost TLS check.
    if not argv:
        argv = [
            "check",
            "--host", DEFAULT_HOST,
            "--port", str(DEFAULT_PORT)
        ]

    args = parser.parse_args(argv)

    if args.mode == "check":
        if bool(args.cert) != bool(args.key):
            parser.error("--cert and --key must be supplied together")

        client_check(args)

    elif args.mode == "listen":
        start_listener(args)

    else:
        parser.error("Choose either check or listen")


if __name__ == "__main__":
    main()
