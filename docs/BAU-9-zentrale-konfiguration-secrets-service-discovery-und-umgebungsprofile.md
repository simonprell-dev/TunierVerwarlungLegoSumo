# BAU-9 · Zentrale Konfiguration, Secrets, Service Discovery und Umgebungsprofile

## 1) Ziel
Dieses Dokument definiert ein konsistentes, testbares Konfigurationsmodell für alle Plattform-Services. Es trennt strikt zwischen Default-Konfiguration, umgebungsspezifischen Werten und Secrets, bereitet Service Discovery für Docker Compose und spätere Multi-Node-Umgebungen vor und beschreibt valide Startfehler bei Fehlkonfiguration.

---

## 2) Leitprinzipien

1. **Konfiguration gehört an Infrastrukturgrenzen** (Bootstrapping, Adapter, DI-Container) und nicht in Business-Logik.
2. **Keine ungeprüften String-Zugriffe auf Environment-Variablen** im Fachcode.
3. **Typed Configuration Objects pro Service** mit klaren, sprechenden Namen.
4. **Fail fast beim Start**: Fehlende Pflichtwerte oder ungültige Formate führen zu eindeutigen Startfehlern.
5. **Secrets strikt getrennt von normaler Konfiguration**.
6. **Profile-basiertes Verhalten** (`local`, `dev`, `staging`, `prod`) ohne Codeänderungen.

---

## 3) Konfigurationsschichten (precedence)

Reihenfolge von niedrig nach hoch (spätere Schicht überschreibt frühere):

1. `defaults` (im Repo, nicht sensibel)
2. `environment profile` (z. B. `local`, `dev`, `staging`, `prod`)
3. `runtime environment variables`
4. `secrets provider` (Datei-Mount, Docker/K8s Secret, Vault)

Regel: **Secrets dürfen nur aus Schicht 4 kommen**.

---

## 4) Namenskonventionen

### 4.1 Environment-Variablen

Format:

`BAUDOC_<SERVICE>_<SECTION>_<KEY>`

Beispiele:

- `BAUDOC_DOC_API_SERVER_PORT`
- `BAUDOC_DOC_API_DB_HOST`
- `BAUDOC_SEARCH_API_VECTORSTORE_URL`
- `BAUDOC_LLM_ORCHESTRATOR_PROVIDER`

### 4.2 Globale Runtime-Variablen

- `BAUDOC_ENV` = `local | dev | staging | prod`
- `BAUDOC_LOG_LEVEL` = `trace | debug | info | warn | error`
- `BAUDOC_CONFIG_STRICT` = `true | false`

### 4.3 Secret-Variablen

Format:

`BAUDOC_SECRET_<SERVICE>_<KEY>`

Beispiele:

- `BAUDOC_SECRET_DOC_API_DB_PASSWORD`
- `BAUDOC_SECRET_AUTH_JWT_SIGNING_KEY`
- `BAUDOC_SECRET_OBJECT_STORAGE_SECRET_KEY`

Regeln:

- Keine Secret-Beispielwerte in `README`, `.env.example` oder Sourcecode.
- Secret-Werte nur über Secret-Provider oder leere Platzhalter (`""`) in lokalen Overrides.

---

## 5) Profile-Modell

## 5.1 Profile

- **local**: Docker Compose, lokale Hostnamen, kurze Timeouts, Debug-Logging erlaubt.
- **dev**: Integrationsumgebung, realistischere Timeouts, Testdaten möglich.
- **staging**: produktionsnah, restriktiver, Monitoring aktiv.
- **prod**: minimale Angriffsfläche, strikte Defaults, keine unsicheren Features.

## 5.2 Profile-Ordnerstruktur (Soll)

```text
config/
  defaults/
    global.yaml
    doc-api.yaml
    search-api.yaml
    llm-orchestrator.yaml
  profiles/
    local/
      global.yaml
      services/*.yaml
    dev/
      global.yaml
      services/*.yaml
    staging/
      global.yaml
      services/*.yaml
    prod/
      global.yaml
      services/*.yaml
  secrets/
    # NICHT im Git, nur Laufzeit-Mount
```

---

## 6) Service-Konfigurationsschema (dokumentiert)

Im Folgenden sind die minimalen, verpflichtenden Konfigurationsobjekte je Service beschrieben.

## 6.1 Document API (`DocApiConfig`)

| Feld | Typ | Pflicht | Quelle | Beispiel (nicht sensibel) |
|---|---|---:|---|---|
| `server.port` | int | ja | env/default | `8080` |
| `db.host` | string | ja | env/profile | `postgres` |
| `db.port` | int | ja | env/default | `5432` |
| `db.name` | string | ja | env/profile | `baudoc` |
| `db.user` | string | ja | env/profile | `doc_api` |
| `db.password` | secret string | ja | secret | _nur Secret Provider_ |
| `objectStorage.endpoint` | url | ja | env/profile | `http://minio:9000` |
| `objectStorage.bucket` | string | ja | env/profile | `documents` |
| `objectStorage.accessKey` | string | ja | env/profile | `doc_api_client` |
| `objectStorage.secretKey` | secret string | ja | secret | _nur Secret Provider_ |
| `queue.url` | url | ja | env/profile | `redis://redis:6379` |

## 6.2 Search API (`SearchApiConfig`)

| Feld | Typ | Pflicht | Quelle | Beispiel (nicht sensibel) |
|---|---|---:|---|---|
| `server.port` | int | ja | env/default | `8081` |
| `db.url` | url | ja | env/profile | `postgresql://postgres:5432/baudoc` |
| `vectorStore.url` | url | ja | env/profile | `http://qdrant:6333` |
| `vectorStore.collection` | string | ja | env/profile | `documents_chunks` |
| `auth.jwksUrl` | url | ja | env/profile | `http://auth-service:8080/.well-known/jwks.json` |

## 6.3 LLM Orchestrator (`LlmOrchestratorConfig`)

| Feld | Typ | Pflicht | Quelle | Beispiel (nicht sensibel) |
|---|---|---:|---|---|
| `server.port` | int | ja | env/default | `8082` |
| `provider.name` | enum | ja | env/profile | `local | openai | azure-openai` |
| `provider.baseUrl` | url | nein* | env/profile | `http://llm-runtime:11434` |
| `provider.apiKey` | secret string | ja** | secret | _nur Secret Provider_ |
| `retrieval.searchApiUrl` | url | ja | env/profile | `http://search-api:8081` |
| `limits.maxTokens` | int | ja | env/default | `4096` |

\* Bei lokalem Provider kann `baseUrl` verpflichtend sein und `apiKey` entfallen.

\** Hängt vom Provider-Typ ab (conditional validation).

## 6.4 Ingestion Worker (`IngestionWorkerConfig`)

| Feld | Typ | Pflicht | Quelle | Beispiel (nicht sensibel) |
|---|---|---:|---|---|
| `queue.url` | url | ja | env/profile | `redis://redis:6379` |
| `queue.topic` | string | ja | env/default | `doc.ingest` |
| `storage.endpoint` | url | ja | env/profile | `http://minio:9000` |
| `ocr.enabled` | bool | ja | env/default | `true` |
| `ocr.language` | string | nein | env/profile | `deu+eng` |

## 6.5 Auth Service (`AuthServiceConfig`)

| Feld | Typ | Pflicht | Quelle | Beispiel (nicht sensibel) |
|---|---|---:|---|---|
| `server.port` | int | ja | env/default | `8083` |
| `issuer` | url | ja | env/profile | `https://auth.example.internal` |
| `jwt.signingKey` | secret string | ja | secret | _nur Secret Provider_ |
| `token.accessTtlSeconds` | int | ja | env/default | `900` |

---

## 7) Service Discovery

## 7.1 Local Compose

- Discovery über Docker-Netzwerk-DNS (Service-Name = Hostname), z. B. `postgres`, `redis`, `search-api`.
- Jede Service-URL als vollqualifizierbare Konfiguration halten, z. B. `http://search-api:8081`.
- Keine hartkodierten `localhost`-Abhängigkeiten zwischen Containern.

## 7.2 Vorbereitung Multi-Node

Discovery-Abstraktion als `ServiceEndpointsConfig`:

- `documentApiBaseUrl`
- `searchApiBaseUrl`
- `authIssuerUrl`
- `queueBrokerUrl`
- `objectStorageInternalUrl`

Empfehlung:

- Heute: Values aus Profile/Env.
- Später: Kubernetes Service DNS (`*.svc.cluster.local`) oder Service Mesh/Consul.

---

## 8) Validierung beim Start (Fail Fast)

## 8.1 Technische Anforderungen

- Validierung erfolgt **vor** Start des HTTP-Servers/Workers.
- Validierungsfehler enthalten:
  - betroffenes Feld,
  - erwartetes Format/Regel,
  - gefundenen Wert (für Secrets maskiert),
  - klare Abbruchmeldung mit Exit-Code `1`.

## 8.2 Validierungsregeln (Mindestmenge)

1. Pflichtfelder dürfen nicht fehlen.
2. URLs müssen parsebar und schema-konform sein (`http/https`, bei DB ggf. `postgresql`).
3. Ports in Range `1..65535`.
4. Numerische Limits (`maxTokens > 0`, Timeouts > 0).
5. Conditional Rules (z. B. `provider.name=openai` => `provider.apiKey` erforderlich).
6. Secrets dürfen nicht aus unsicheren Defaults gelesen werden.

## 8.3 Fehlerbeispiel

```text
CONFIG_VALIDATION_ERROR
service=llm-orchestrator
field=provider.apiKey
rule=required_when(provider.name in [openai, azure-openai])
message=Missing required secret 'BAUDOC_SECRET_LLM_ORCHESTRATOR_PROVIDER_API_KEY'
```

---

## 9) Referenz-Mapping Environment -> Config Objects

Beispiel `DocApiConfig`:

- `BAUDOC_DOC_API_SERVER_PORT` -> `server.port`
- `BAUDOC_DOC_API_DB_HOST` -> `db.host`
- `BAUDOC_DOC_API_DB_PORT` -> `db.port`
- `BAUDOC_DOC_API_DB_NAME` -> `db.name`
- `BAUDOC_DOC_API_DB_USER` -> `db.user`
- `BAUDOC_SECRET_DOC_API_DB_PASSWORD` -> `db.password`
- `BAUDOC_DOC_API_OBJECT_STORAGE_ENDPOINT` -> `objectStorage.endpoint`
- `BAUDOC_DOC_API_OBJECT_STORAGE_BUCKET` -> `objectStorage.bucket`
- `BAUDOC_DOC_API_OBJECT_STORAGE_ACCESS_KEY` -> `objectStorage.accessKey`
- `BAUDOC_SECRET_DOC_API_OBJECT_STORAGE_SECRET_KEY` -> `objectStorage.secretKey`
- `BAUDOC_DOC_API_QUEUE_URL` -> `queue.url`

---

## 10) Umsetzungscheckliste für BAU-9

- [x] Konfigurationsmodell pro Service definiert.
- [x] Default/Environment/Secret-Trennung festgelegt.
- [x] Namenskonventionen dokumentiert.
- [x] Service Discovery lokal und multi-node-vorbereitet beschrieben.
- [x] Startvalidierung mit klaren Fehlern spezifiziert.

## 11) Definition of Done (technisch überprüfbar)

1. Jeder Service besitzt genau ein typed Config-Objekt und einen Loader/Validator.
2. Business-Code erhält nur bereits validierte Config-Objekte (kein `process.env` / `System.getenv` / `os.Getenv` im Fachcode).
3. CI kann Profile laden und Validierungstests ausführen (`local`, `dev`, `staging`, `prod`).
4. Secrets sind nicht im Repository eingecheckt.

Damit ist die Lösung für lokale Compose-Setups und spätere Multi-Node-Runtimes konsistent vorbereitet.
