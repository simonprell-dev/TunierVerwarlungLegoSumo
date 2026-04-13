# BAU-10 · Identität, Authentifizierung, Autorisierung und Multiuser-Grundlagen

## 1) Zielbild
Dieses Dokument definiert ein belastbares Sicherheits- und Multiuser-Fundament für BauDoc Atlas:

- fachlich klar getrennte Identitäten (menschliche Benutzer vs. Service-Accounts),
- zentrale Authentifizierung,
- zentrale und testbare Autorisierung über Policies/Guards,
- vorbereitete Mandanten-/Projektgrenzen,
- auditierbare Sicherheits- und Fachaktionen.

Die Regeln sind so aufgebaut, dass keine Rechteprüfung verstreut in Endpunkten erfolgt.

---

## 2) Identitätsmodell

### 2.1 Entitäten

1. **Benutzer (`User`)**  
   Menschliche Identität mit Login, Profil und zugewiesenen Rollen.
2. **Service-Account (`ServiceAccount`)**  
   Nicht-menschliche technische Identität für Worker, Integrationen und interne Systemkommunikation.
3. **Rolle (`Role`)**  
   Bündelt Berechtigungen (RBAC) in fachlich verständliche Rechtepakete.
4. **Mitgliedschaft (`Membership`)**  
   Verknüpft Identität mit Projekt/Mandant und Rollen auf Scope-Ebene.
5. **Mandant (`Tenant`)** / **Projekt (`Project`)**  
   Sicherheits-Scope zur Trennung von Datenzugriff und Verantwortlichkeiten.

### 2.2 Trennung Mensch vs. Maschine

- `User` und `ServiceAccount` sind **separate Modelle** mit getrennten Lebenszyklen.
- `User` authentifiziert sich interaktiv (OIDC-Login + Session).
- `ServiceAccount` authentifiziert sich nicht-interaktiv (signierte Token, Key Rotation, kurze TTL).
- Aktionen werden im Audit-Log immer mit `actor_type` (`human`|`service`) und `actor_id` gespeichert.

### 2.3 Vorschlag für Kernattribute

#### User
- `id` (UUID)
- `email` (unique)
- `display_name`
- `is_active`
- `last_login_at`
- `created_at`, `updated_at`

#### ServiceAccount
- `id` (UUID)
- `name` (unique)
- `purpose` (z. B. `ingestion-worker`)
- `is_active`
- `key_id` / `credential_version`
- `created_at`, `rotated_at`

#### Role
- `id`
- `name` (`admin`, `editor`, `reader`, `service`)
- `description`

#### Membership
- `id`
- `subject_type` (`user`|`service_account`)
- `subject_id`
- `scope_type` (`tenant`|`project`)
- `scope_id`
- `role_id`

---

## 3) Rollenmodell (RBAC)

### 3.1 Standardrollen

1. **Admin**
   - Nutzer- und Rollenverwaltung
   - Tenant/Projektverwaltung
   - System- und Sicherheitskonfiguration
   - Audit- und Betriebszugriff

2. **Bearbeiter (Editor)**
   - Dokumente hochladen/ändern
   - Metadaten pflegen
   - Re-Indexing für eigene Sichten anstoßen (wenn fachlich erlaubt)

3. **Leser (Reader)**
   - Dokumente lesen/suchen
   - keine schreibenden Operationen

4. **Service**
   - rein technische Rechte nach Least-Privilege
   - z. B. nur Job-Status schreiben oder Embeddings aktualisieren

### 3.2 Rechtebeispiele pro Domäne

- **identity**: `users.read`, `users.write`, `roles.assign`
- **documents**: `documents.read`, `documents.write`, `documents.delete`
- **admin**: `admin.jobs.read`, `admin.jobs.retry`, `admin.settings.write`
- **audit**: `audit.read`, `audit.export`
- **system/service**: `pipeline.ingest`, `pipeline.embed`, `pipeline.reindex`

---

## 4) Authentifizierung & Session-/Token-Strategie

## 4.1 Für menschliche Benutzer

- **Protokoll**: OIDC Authorization Code Flow mit PKCE.
- **Session-Modell**: serverseitige Session (Redis) mit kurzlebigem Access-Kontext.
- **Cookie-Policy**: `HttpOnly`, `Secure`, `SameSite=Lax` (oder `Strict` bei rein internem UI).
- **Session-Lifetime**:
  - Idle Timeout: 30 Minuten
  - Absolute Timeout: 8 Stunden
- **Re-Authentifizierung** erforderlich für sensible Aktionen (z. B. Rollenänderung, Export personenbezogener Daten).

## 4.2 Für Service-Accounts

- **Token-Modell**: signierte JWTs oder mTLS-gebundene Tokens.
- **TTL**: kurz (z. B. 5–15 Minuten), automatische Erneuerung über sicheren Kanal.
- **Rotation**: regelmäßige Schlüsselrotation mit `kid`/Versionsführung.
- **Scope-Bindung**: Tokens enthalten minimal notwendige Rechte und Scope (`tenant_id`, optional `project_id`).

## 4.3 Minimalanforderungen an Claims/Kontext

- `sub`, `actor_type`, `role(s)`, `permissions`
- `tenant_id`, optional `project_id`
- `iat`, `exp`, `jti`

---

## 5) Autorisierung: zentrale Policies/Guards

Alle Endpunkte delegieren Rechteentscheidungen an zentrale Policy-/Guard-Komponenten.

### 5.1 Regel

- **Kein** Inline-`if role == ...` in Fachlogik.
- Endpunkte deklarieren benötigte Fähigkeit (`permission`) und Scope.
- Policy Engine entscheidet anhand von Identität, Rolle, Scope und Ressourcenkontext.

### 5.2 Referenzstruktur (beispielhaft)

```text
/security
  /auth
    authentication_guard
    session_resolver
  /authorization
    policy_registry
    document_policy
    admin_policy
    audit_policy
  /audit
    audit_logger
```

### 5.3 Pseudocode (nur zur Struktur)

```pseudo
guard authenticate(request):
  principal = auth.resolve_principal(request)
  if principal == null: deny(401)
  return principal

policy can(principal, action, resource, scope):
  if !principal.active: return false
  if !scope_matches(principal, scope): return false
  return permission_registry.has(principal.permissions, action)
```

---

## 6) Sichtbare RBAC-Beispiele (Akzeptanzkriterium)

## 6.1 Backend-Endpunkt (API)

- `POST /api/v1/documents`
  - Authentifizierung: erforderlich
  - Rollen/Permissions: `admin` oder `editor` mit `documents.write`
  - Scope: passender `tenant_id`, optional `project_id`

- `GET /api/v1/documents/:id`
  - Authentifizierung: erforderlich
  - Rollen/Permissions: `admin|editor|reader` mit `documents.read`
  - Scope: nur wenn Dokument im selben Tenant/Projekt liegt

## 6.2 Admin-Endpunkt

- `POST /admin/api/v1/users/:id/roles`
  - Authentifizierung: erforderlich
  - Rollen/Permissions: nur `admin` mit `roles.assign`
  - Zusätzliche Sicherheitsregel: Re-Auth + Audit-Pflicht

Damit ist rollenbasierter Zugriff sowohl im Backend als auch im Admin-Bereich explizit sichtbar.

---

## 7) Vorbereitung Mandanten-/Projektzugriff

- Jede geschützte Ressource trägt `tenant_id` und bei Bedarf `project_id`.
- Zugriff wird auf Scope-Ebene geprüft:
  - Tenant-Ebene (global innerhalb Mandant)
  - Projekt-Ebene (feingranular)
- Verhinderung von Cross-Tenant-Zugriff als harte Policy-Regel.

Empfohlenes Muster:
1. Scope aus Route/Token lesen,
2. Ressource laden,
3. Scope-Konsistenz prüfen,
4. Policy-Entscheidung ausführen.

---

## 8) Zugriffsregeln nach Kanal

### 8.1 API
- standardmäßig `authenticated`.
- Schreibzugriffe nur mit expliziter Permission.
- sensible Endpunkte zusätzlich mit Rate Limits und optional MFA/Re-Auth.

### 8.2 Adminoberfläche
- grundsätzlich nur `admin`.
- read-only Admin-Views optional für `editor` über eigene Permission (`admin.jobs.read`).

### 8.3 Dokumentbereiche
- `reader`: lesen/suchen
- `editor`: lesen + ändern
- `admin`: Vollzugriff inkl. Löschung/Restores (je nach Governance)

---

## 9) Auditierbare Benutzeraktionen

Folgende Aktionen sind audit-relevant und müssen eindeutig protokolliert werden:

1. Login-Erfolg / Login-Fehlschlag
2. Logout / Session-Invalidierung
3. Rollenänderungen
4. Benutzeraktivierung/-deaktivierung
5. Dokument-Upload, -Löschung, -Export
6. Admin-Änderungen an Sicherheits- oder Policy-Konfiguration
7. Service-Account-Key-Rotation

### 9.1 Audit-Log Minimalfelder

- `event_id`, `occurred_at`
- `actor_type`, `actor_id`
- `action` (z. B. `roles.assign`)
- `target_type`, `target_id`
- `scope` (`tenant_id`, `project_id`)
- `result` (`success`|`denied`|`error`)
- `trace_id` / `request_id`

---

## 10) Technische Leitplanken (Clean Code)

- Security-Entscheidungen zentralisieren (Policies/Guards).
- Fachlich benannte Modelle und Permissions verwenden.
- Security-Module isoliert testbar halten.
- Standardmäßig deny-by-default.
- Keine impliziten Rechteannahmen im Anwendungscode.

---

## 11) Abdeckung der Akzeptanzkriterien

1. **Benutzer- und Rollenmodell dokumentiert** -> Kapitel 2 und 3.
2. **Geschützte Endpunkte verlangen Authentifizierung** -> Kapitel 6, 8.
3. **RBAC sichtbar in Backend- und Admin-Endpunkt** -> Kapitel 6.1 und 6.2.
4. **Session-/Token-Strategie dokumentiert** -> Kapitel 4.
5. **Audit-relevante Aktionen identifizierbar** -> Kapitel 9.

