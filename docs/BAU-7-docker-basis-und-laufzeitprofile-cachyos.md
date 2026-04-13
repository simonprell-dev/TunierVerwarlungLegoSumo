# BAU-7 · Docker-Basis, lokale Entwicklungsumgebung und Laufzeitprofile (CachyOS)

## Ziel

Reproduzierbare lokale Laufzeit mit klar getrennten Profilen für **Development**, **Test** und **Production**.

## Compose-Struktur

- `docker-compose.yml` → gemeinsame Basis (Netzwerk, Volumes, Kernservices, Healthchecks)
- `docker-compose.dev.yml` → Entwicklung (Bind-Mounts, Debug-Umgebung)
- `docker-compose.test.yml` → Tests (ephemere DB, reduzierte Persistenz)
- `docker-compose.prod.yml` → Produktion (restriktiver, Ressourcenlimits, AMD-Geräte-Mapping)

## Benannte Ressourcen

- Netzwerk: `baudoc_platform_net`
- Volumes:
  - `baudoc_postgres_data`
  - `baudoc_redis_data`
  - `baudoc_minio_data`
  - `baudoc_qdrant_data`
- Container:
  - `baudoc_gateway`
  - `baudoc_api`
  - `baudoc_worker`
  - `baudoc_postgres`
  - `baudoc_redis`
  - `baudoc_minio`
  - `baudoc_qdrant`

## Services und Build-Kontexte

Jeder eigenentwickelte Service besitzt einen separaten Build-Kontext:

- `./services/frontend`
- `./services/api`
- `./services/worker`

## Start/Stop lokal

### Development

```bash
./scripts/start-dev.sh
```

### Test

```bash
./scripts/start-test.sh
```

### Production

```bash
./scripts/start-prod.sh
```

### Stop

```bash
./scripts/stop.sh
```

## Healthchecks / Startbedingungen

Alle Container in der Basis erhalten Healthchecks.
Abhängigkeiten nutzen `depends_on.condition: service_healthy` für deterministische Startreihenfolge.

## AMD GPU-Zugriff (CachyOS)

### Voraussetzungen Host

- Docker Engine + Compose Plugin
- Benutzer in Gruppen `video` und `render`
- Vorhandene Device-Knoten:

```bash
ls -l /dev/dri
```

### Container-Zugriff (Production-Profil)

Im `docker-compose.prod.yml` ist für den Worker gesetzt:

- `devices: /dev/dri:/dev/dri`
- `group_add: render, video`

### Testbarkeit

1. Stack mit Production-Profil starten:

```bash
./scripts/start-prod.sh
```

2. Im Worker prüfen:

```bash
docker exec -it baudoc_worker ls -l /dev/dri
```

3. Optional (wenn ROCm am Host eingerichtet ist):

```bash
docker run --rm --device=/dev/dri --group-add=render --group-add=video rocm/rocm-terminal:latest rocminfo
```

> Hinweis: ROCm-Container sind optional und primär für Hardware-/Treiberdiagnose gedacht.

## Keine impliziten Host-Abhängigkeiten

- Alle relevanten Abhängigkeiten sind über Containerdienste modelliert.
- Kein Service erfordert lokale Host-Installationen von DB, Cache oder Objektspeicher.
- Konfigurationen erfolgen über Umgebungsvariablen und Compose-Dateien.

## Vorbereitung Multi-Host

Die Trennung in Basis + Profile, benannte Netz-/Volume-Ressourcen und eigene Build-Kontexte bildet eine direkte Grundlage für spätere Orchestrierung (z. B. k3s/Kubernetes, Swarm oder getrennte Compose-Deployments je Hostrolle).
