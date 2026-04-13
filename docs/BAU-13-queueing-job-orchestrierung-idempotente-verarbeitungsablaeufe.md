# BAU-13 · Queueing, Job-Orchestrierung und idempotente Verarbeitungsabläufe

## 1) Zielbild
Dieses Dokument definiert ein robustes, fehlertolerantes und skalierbares Verarbeitungsmodell für die Dokumentpipeline von BauDoc Atlas.

Ziel ist eine Architektur, in der:
- Jobs als fachlich benannte Anwendungsfälle modelliert sind,
- Queue-Zugriffe vollständig hinter einer Infrastrukturgrenze liegen,
- Retry-/Timeout-/Dead-Letter-Regeln zentral und konsistent umgesetzt werden,
- doppelte Verarbeitung derselben Eingabe zuverlässig verhindert wird,
- Jobstatus persistiert und in API/UI abfragbar ist.

---

## 2) Architekturprinzipien für Orchestrierung

1. **Orchestrierung getrennt von Business-Logik**  
   Fachregeln liegen in Use Cases; Queueing, Retries und Scheduling liegen in einem separaten Orchestrierungs-/Infrastruktur-Layer.

2. **At-least-once + Idempotenz statt Exactly-once-Versprechen**  
   Broker/Worker dürfen Nachrichten erneut zustellen; fachliche Idempotenzregeln machen Wiederholungen sicher.

3. **Explizite Zustandsmaschine pro Job**  
   Jeder Job folgt demselben Lebenszyklusmodell und ist dadurch beobachtbar und steuerbar.

4. **Kein Copy-Paste zwischen Workern**  
   Gemeinsame Komponenten für Fehlerbehandlung, Retry-Berechnung, Statusupdates, Telemetrie und Idempotenzprüfung.

5. **Fehlerpfade sind First-Class**  
   Jeder Fehlerzustand führt zu einem definierten nächsten Schritt (Retry, Dead Letter, manuelle Aktion).

---

## 3) Queue-Technologie und Kapselung

## 3.1 Technologieentscheidung (MVP)

Für das MVP wird **Redis Streams** als Queue-Technologie gewählt.

Begründung:
- bereits im Zielbild als Infrastrukturkomponente vorgesehen,
- gute Integrationsfähigkeit für API- und Worker-Dienste,
- Consumer-Groups für parallele Worker,
- Pending/Claiming-Mechanismen für Recovery nach Worker-Ausfall,
- geringe operative Komplexität für Startphase.

Hinweis: Die fachliche Orchestrierung darf Redis-spezifische Details nicht nach außen leaken.

## 3.2 Infrastrukturgrenze (Ports & Adapter)

Queue-Zugriffe werden hinter einer klaren Schnittstelle gekapselt:

```text
/application
  /jobs
    enqueue_document_uploaded_use_case
    process_job_use_case

/domain
  job_types
  job_state_machine
  idempotency_rules

/infrastructure
  /queue
    queue_port (interface)
    redis_streams_queue_adapter
  /orchestration
    retry_policy
    timeout_policy
    dead_letter_policy
```

### 3.3 Port-Vertrag (beispielhaft)

`QueuePort` stellt mindestens bereit:
- `publish(jobEnvelope)`
- `consume(jobType, handler)`
- `ack(messageId)`
- `nack(messageId, reason)`
- `moveToDeadLetter(jobEnvelope, reason)`
- `scheduleRetry(jobEnvelope, retryAt)`

Damit bleibt die Fachlogik brokeragnostisch (späterer Wechsel zu RabbitMQ/NATS möglich).

---

## 4) Jobtypen als fachliche Anwendungsfälle

Jeder Job hat einen stabilen `job_type`, ein versionsfähiges Payload-Schema und eigene Idempotenzregeln.

1. **`document.upload.received`**
   - Zweck: Eingang dokumentieren und Pipeline starten
   - Input: `document_id`, `tenant_id`, `storage_key`, `content_hash`
   - Output: Folgeschritt `document.analysis.requested`

2. **`document.analysis.requested`**
   - Zweck: Parsing/OCR/Strukturierung auslösen
   - Input: Dokumentreferenzen + Analyseprofil
   - Output: strukturierte Inhalte, Artefaktverweise, `document.preparation.requested`

3. **`document.preparation.requested`**
   - Zweck: Chunking, Normalisierung, Metadatenanreicherung
   - Input: Analyseartefakte
   - Output: chunks + `document.embedding.requested`

4. **`document.embedding.requested`**
   - Zweck: Embeddings erzeugen/speichern
   - Input: Chunks + Modellversion
   - Output: Embedding-Referenzen + `document.artifact.build.requested`

5. **`document.artifact.build.requested`**
   - Zweck: finale Artefakte für Suche/UI erzeugen (z. B. Preview/Index-Payload)
   - Input: alle vorherigen Ergebnisse
   - Output: Dokumentstatus auf `ready`

---

## 5) Einheitliches Job-Lebenszyklusmodell

## 5.1 Persistierbarer Status

```text
queued -> running -> succeeded
              |         \
              |          -> compensating (optional)
              v
           failed_retryable -> queued (retry)
              |
              v
           failed_terminal -> dead_lettered
```

Empfohlene Statuswerte:
- `queued`
- `running`
- `succeeded`
- `failed_retryable`
- `failed_terminal`
- `dead_lettered`
- `cancelled` (optional für manuelle Eingriffe)

## 5.2 Minimale Persistenzfelder (`job_execution`)

- `job_id` (UUID)
- `job_type`
- `correlation_id` (für End-to-End-Trace)
- `idempotency_key`
- `dedupe_key`
- `status`
- `attempt`
- `max_attempts`
- `scheduled_at`, `started_at`, `finished_at`
- `timeout_at`
- `last_error_code`, `last_error_message`
- `payload_ref` (oder Payload-Hash)
- `created_at`, `updated_at`

## 5.3 UI/API-Abfragefähigkeit

Mindestens folgende Queries müssen unterstützt werden:
- Jobstatus nach `job_id`
- alle Jobs je `document_id`
- offene/festhängende Jobs (`queued/running` über Schwellwert)
- Dead-Letter-Queue inkl. Fehlergrund

---

## 6) Retry-, Timeout- und Dead-Letter-Strategie

## 6.1 Fehlerklassifikation

Fehler werden zentral in drei Klassen eingeteilt:

1. **Transient (retryable)**
   - z. B. Netzfehler, temporär nicht erreichbarer Storage/Vector Store
   - Aktion: Retry mit Backoff

2. **Rate-/Capacity-bedingt (retryable mit längerer Wartezeit)**
   - z. B. Modellprovider überlastet
   - Aktion: Retry mit erweitertem Backoff + Jitter

3. **Permanent (non-retryable/terminal)**
   - z. B. ungültiges Payload-Schema, irreparabel beschädigte Datei
   - Aktion: terminal fail -> Dead Letter

## 6.2 Retry-Policy (MVP)

- `max_attempts`: 5
- Backoff: exponentiell (z. B. 30s, 2m, 10m, 30m, 2h)
- + Jitter (10–20 %)
- Retry nur bei explizit retrybaren Fehlercodes

## 6.3 Timeout-Policy (MVP)

- Jobtyp-spezifische `timeout_seconds`
- Overshoot führt zu `failed_retryable` (wenn noch Attempts vorhanden), sonst `failed_terminal`
- Timeout-Überwachung über separaten Watchdog-Prozess, nicht in Business-Use-Cases verstreuen

## 6.4 Dead-Letter-Policy

Ein Job landet in Dead Letter, wenn:
- `attempt > max_attempts`, oder
- Fehler als `terminal` klassifiziert wurde.

Für Dead-Letter-Einträge werden zwingend gespeichert:
- Original-Envelope/Payload-Referenz
- Fehlerklasse + Fehlercode
- letzter Stack-/Diagnosehinweis (redacted)
- Zeitstempel und betroffener Worker-Typ

Manuelle Aktionen im Adminbereich:
- „Retry from DLQ“ (mit neuem `job_id`, gleicher `correlation_id`)
- „Mark as ignored“
- „Open diagnostics“

---

## 7) Idempotenzregeln je Jobtyp

## 7.1 Grundregel

Jeder Job führt vor fachlicher Verarbeitung einen Idempotenz-Check aus:
- Wenn ein semantisch gleicher Auftrag bereits `succeeded` ist, wird der Job als `succeeded` ohne Nebenwirkung beendet.
- Wenn ein gleicher Auftrag `running` ist, wird keine zweite Parallelverarbeitung gestartet.

## 7.2 Schlüsselkonzept

- **`idempotency_key`**: identifiziert denselben fachlichen Auftrag über Retries/Redeliveries hinweg.
- **`dedupe_key`**: verhindert konkurrierende Doppelstarts bei identischem Input.

## 7.3 Konkrete Regeln (MVP)

1. `document.upload.received`
   - `idempotency_key = tenant_id + document_id + content_hash`
   - Doppelte Upload-Events mit identischem Hash erzeugen keinen zweiten Pipeline-Start.

2. `document.analysis.requested`
   - `idempotency_key = document_id + analysis_profile_version + source_artifact_hash`
   - Bereits vorliegende Analyseartefakte gleicher Version werden wiederverwendet.

3. `document.preparation.requested`
   - `idempotency_key = document_id + preparation_profile_version + analysis_artifact_hash`
   - Chunking/Normalisierung nur neu bei geänderten Eingaben oder Profilversion.

4. `document.embedding.requested`
   - `idempotency_key = document_id + embedding_model_version + chunk_set_hash`
   - Embeddings gleicher Modellversion und Chunk-Menge werden nicht doppelt geschrieben.

5. `document.artifact.build.requested`
   - `idempotency_key = document_id + artifact_schema_version + upstream_bundle_hash`
   - Zielartefakt wird nur aktualisiert, wenn Input-Bundle neu ist.

## 7.4 Persistenzseitige Absicherung

- Unique Constraint auf (`job_type`, `idempotency_key`, `status in active_or_success_set`) über geeignete technische Umsetzung.
- State-Transitionen in einer Transaktion (oder atomaren Compare-and-Set-Logik).
- Outbox/Inbox-Muster für externe Nebenwirkungen, wenn notwendig.

---

## 8) Vollständiger Job-Lebenszyklus (Beispiel)

Beispiel: `document.embedding.requested`

1. Document API oder Orchestrator publisht Job mit `job_id`, `correlation_id`, `idempotency_key`.
2. Queue Adapter schreibt Event in Stream (`status=queued`, `attempt=0`).
3. Worker konsumiert, setzt atomar `running`, erhöht `attempt`.
4. Worker prüft Idempotenz:
   - Erfolg bereits vorhanden -> markiert `succeeded`, ack.
5. Falls nicht vorhanden: Embeddings berechnen, speichern, Status `succeeded`, ack.
6. Bei transientem Fehler: `failed_retryable`, Retry-Zeitpunkt berechnen, re-enqueue.
7. Nach Überschreiten von `max_attempts`: `failed_terminal` -> `dead_lettered`.
8. Admin/UI kann Verlauf, Fehlermeldung und nächste Aktion einsehen.

Damit ist ein kompletter Lifecycle inklusive Normal- und Fehlerpfad dokumentiert.

---

## 9) Worker-Design ohne Copy-Paste

Gemeinsame Basiskomponenten:
- `JobExecutionTemplate` (Template Method für Ablauf)
- `IdempotencyService`
- `RetryDecider`
- `TimeoutGuard`
- `JobStatusRepository`
- `JobTelemetry`

Ablauf pro Worker (vereinheitlicht):
1. Envelope validieren
2. Statuswechsel (`queued -> running`)
3. Idempotenz prüfen
4. Fach-Use-Case ausführen
5. Erfolg/Fail klassifizieren
6. Retry/DLQ entscheiden
7. Status persistieren + Telemetrie senden

Nur Schritt 4 ist jobtyp-spezifische Business-Logik.

---

## 10) Observability und Betriebsfähigkeit

Mindestanforderungen:
- strukturierte Logs mit `job_id`, `correlation_id`, `job_type`, `attempt`
- Metriken pro Jobtyp:
  - Durchsatz (`jobs_processed_total`)
  - Erfolgs-/Fehlerrate
  - Retry-Rate
  - DLQ-Rate
  - Laufzeit-P95/P99
- Tracing über API -> Queue -> Worker

Alarmierungsregeln (MVP):
- DLQ-Rate > Schwellwert
- Queue-Lag über Grenzwert
- Jobs in `running` länger als Timeout + Toleranz

---

## 11) Akzeptanzkriterien-Abdeckung BAU-13

1. **Mindestens ein vollständiger Job-Lebenszyklus dokumentiert**  
   Erfüllt über Abschnitt 8 (`document.embedding.requested`).

2. **Retry- und Fehlerstrategie definiert**  
   Erfüllt über Abschnitt 6 (Fehlerklassen, Retry, Timeout, Dead Letter).

3. **Doppelte Verarbeitung beherrscht**  
   Erfüllt über Abschnitt 7 (idempotency/dedupe keys + Persistenzregeln).

4. **Jobstatus persistierbar und abfragbar**  
   Erfüllt über Abschnitt 5 (`job_execution`-Felder + Query-Anforderungen).

---

## 12) Umsetzungsreihenfolge (empfohlen)

1. `job_execution`-Persistenzschema + Statusübergänge implementieren.
2. QueuePort + Redis-Adapter implementieren.
3. Gemeinsame Worker-Basis (Template + Retry/Idempotenz-Dienste) bereitstellen.
4. Einen End-to-End-Job (`document.embedding.requested`) produktiv durchstecken.
5. DLQ-Adminfunktionen und Monitoring ergänzen.
6. Weitere Jobtypen schrittweise auf dieselbe Basis migrieren.

Damit bleibt die Orchestrierung konsistent, testbar und wartbar.
