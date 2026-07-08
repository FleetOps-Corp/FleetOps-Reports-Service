# JWT public key material (never commit private keys)

<<<<<<< HEAD
Place the Security Service **public** key here for RS256 verification:
=======
Place the Security Service **public** key here when using RS256 verification:
>>>>>>> develop

```
public.pem
```

<<<<<<< HEAD
Copy from the team shared key:
=======
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
>>>>>>> develop

```powershell
Copy-Item ..\jwt_public.pem .\certs\public.pem
```

<<<<<<< HEAD
## Deployed Security integration (RS256 — current production)

Security signs tokens with a **private key**. Reports verifies with the **public key only**:

```env
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=/app/certs/public.pem
OPERATIONAL_GATEWAY_BASE_URL=http://3.237.75.68:8000
OPERATIONAL_VEHICLES_PATH=/api/vehicles/
OPERATIONAL_ASSIGNMENTS_PATH=/api/assignments/
OPERATIONAL_INCIDENTS_PATH=/api/incidents/
OPERATIONAL_MAINTENANCE_PATH=/api/maintenance/
```

Docker Compose mounts `./certs` at `/app/certs:ro`.

## Local development (HS256 — legacy Security dev stack)

```env
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=change_me_jwt_secret_key_minimum_32_characters_long
```

=======
>>>>>>> develop
All `*.pem` files in this directory are gitignored.
