# JWT public key material (never commit private keys)

Place the Security Service **public** key here when using RS256 verification:

```
public.pem
```

## Current FleetOps Security integration (HS256)

The Security cell currently signs tokens with **HS256** and `JWT_SECRET_KEY`.
Reports must use the **same secret** for inbound JWT validation:

```env
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<same value as FleetOps-Security-Service>
```

This matches the deployed Security Service (`.env.extern`) and local development stacks.

## Target RS256 verification (public key only)

When Security migrates to asymmetric signing, Reports verifies tokens with the
public key only — see `docs/token/Miniguia para verificar los tokens con llave publica.md`.

```env
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=/app/certs/public.pem
```

Docker Compose already mounts `./certs` at `/app/certs:ro`.

Copy the team public key:

```powershell
Copy-Item ..\jwt_public.pem .\certs\public.pem
```

All `*.pem` files in this directory are gitignored.
