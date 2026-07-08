# JWT public key material (never commit private keys)

Place the Security Service **public** key here for RS256 verification:

```
public.pem
```

Copy from the team shared key:

```powershell
Copy-Item ..\jwt_public.pem .\certs\public.pem
```

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

All `*.pem` files in this directory are gitignored.
