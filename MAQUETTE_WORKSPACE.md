# Maquette Technique — Legacy Days Workspace

> Objectif : ajouter le concept workspace à côté du dashboard existant, sans le casser.
> Date : 10 juin 2026
> Statut : spécification avant code

---

## 1. Arborescence cible

```
dayslegacy-ai-os/
├── backend/
│   ├── main.py                    # + include_router workspaces, rooms, messages, documents, meetings
│   ├── models.py                  # + Workspace, WorkspaceMember, Room, Meeting, Document, Message
│   ├── database.py                # inchangé
│   ├── routers/
│   │   ├── auth.py                # minimal : ajout role dans JWT payload
│   │   ├── leads.py               # + filtre workspace_id (nullable)
│   │   ├── audits.py              # + filtre workspace_id (nullable)
│   │   ├── sophia.py              # + contexte workspace dans le prompt
│   │   ├── workspaces.py          # NOUVEAU
│   │   ├── rooms.py               # NOUVEAU
│   │   ├── messages.py            # NOUVEAU
│   │   ├── documents.py           # NOUVEAU
│   │   └── meetings.py            # NOUVEAU
│   └── static/
│       ├── dashboard.html         # INCHANGÉ (vue BD par défaut)
│       ├── workspace.html         # NOUVEAU (workspace complet)
│       └── assets/
│           ├── workspace.css      # NOUVEAU
│           └── workspace.js       # NOUVEAU
├── docker-compose.yml             # inchangé
├── Dockerfile                     # inchangé
└── INSTRUCTIONS_DEMO.md           # inchangé
```

---

## 2. Modèles SQLAlchemy

### 2.1 Workspace
```python
class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)           # ex: "Days Legacy Rhône-Alpes"
    slug = Column(String(50), unique=True, index=True)   # ex: "dl-rhone"
    owner_id = Column(Integer, ForeignKey("users.id"))   # référence future table users
    plan = Column(String(20), default="demo")            # demo / starter / pro
    branding_primary = Column(String(7), default="#CC9B12")
    branding_secondary = Column(String(7), default="#0b0b0c")
    logo_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    rooms = relationship("Room", back_populates="workspace", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
```

### 2.2 WorkspaceMember
```python
class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_email = Column(String(100), nullable=False)     # temporaire, pending vrai User model
    role = Column(String(20), default="bd")              # owner / admin / bd / expert / viewer
    display_name = Column(String(100))
    avatar_url = Column(String(255))
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    workspace = relationship("Workspace", back_populates="members")
```

### 2.3 Room
```python
class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(100), nullable=False)           # ex: "Réunion Marc D."
    type = Column(String(20), default="meeting")         # meeting / chat / document
    status = Column(String(20), default="active")        # active / archived
    created_by = Column(String(100))                     # email membre
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    workspace = relationship("Workspace", back_populates="rooms")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="room", cascade="all, delete-orphan")
```

### 2.4 Meeting
```python
class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    title = Column(String(200))
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    screen_share_url = Column(String(255))               # placeholder WebRTC
    recording_url = Column(String(255))
    status = Column(String(20), default="scheduled")     # scheduled / live / ended / cancelled
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    room = relationship("Room", back_populates="meetings")
```

### 2.5 Document
```python
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    name = Column(String(200), nullable=False)
    file_url = Column(String(255))
    mime_type = Column(String(100))
    size_bytes = Column(Integer)
    uploaded_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    workspace = relationship("Workspace", back_populates="documents")
```

### 2.6 Message
```python
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    sender_email = Column(String(100), nullable=False)
    sender_name = Column(String(100))
    content = Column(Text, nullable=False)
    type = Column(String(20), default="text")            # text / system / ai / file
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    room = relationship("Room", back_populates="messages")
```

### 2.7 Ajustements models existants
```python
# Lead — ajout optionnel
workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)

# AuditClient — ajout optionnel
workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
```

---

## 3. Routes API nécessaires

| Route | Méthode | Description |
|---|---|---|
| `/api/workspaces` | GET, POST | Liste / créer workspace |
| `/api/workspaces/{id}` | GET, PUT, DELETE | Détail / modifier / supprimer |
| `/api/workspaces/{id}/members` | GET, POST | Liste / inviter membre |
| `/api/workspaces/{id}/members/{mid}` | DELETE, PUT | Retirer / changer rôle |
| `/api/workspaces/{id}/rooms` | GET, POST | Liste / créer room |
| `/api/rooms/{id}` | GET, PUT, DELETE | Détail / modifier / supprimer room |
| `/api/rooms/{id}/messages` | GET, POST | Historique / envoyer message |
| `/api/workspaces/{id}/documents` | GET, POST | Liste / upload document |
| `/api/documents/{id}` | GET, DELETE | Télécharger / supprimer |
| `/api/workspaces/{id}/meetings` | GET, POST | Liste / planifier réunion |
| `/api/meetings/{id}` | GET, PUT, DELETE | Détail / modifier / annuler |
| `/api/meetings/{id}/start` | POST | Marquer comme live |
| `/api/meetings/{id}/end` | POST | Marquer comme terminée |
| `/workspace` | GET | Redirige vers le workspace par défaut de l'utilisateur |

---

## 4. Écran cible workspace.html

### Layout 3 colonnes

```
┌─────────────────┬──────────────────────────────┬─────────────────┐
│  SIDEBAR (250px)│  CENTRE (flex)               │  PANEL (300px)  │
├─────────────────┼──────────────────────────────┼─────────────────┤
│ Logo workspace  │  Topbar salle active         │  SOPHIA COPILOTE│
│                 │  - Nom room                  │                 │
│ WORKSPACES      │  - Onglets : Visio / Chat /  │  Avatar + statut│
│ - DL Rhône      │    Docs / Tableau            │  Zone chat      │
│ - DL Paris      │                              │  Suggestions    │
│                 │  CONTENU ACTIF               │  contextuelles  │
│ ROOMS ACTIVES   │                              │                 │
│ 📹 Réunion Marc │  [Visio placeholder]         │  ACTIONS RAPIDES│
│ 💬 Chat expert  │  ou                          │  - Créer tâche  │
│ 📁 Doc Pacte    │  [Chat historique]           │  - Voir prospect│
│                 │  ou                          │  - Générer doc  │
│ MEMBRES (en     │  [Documents grid]            │                 │
│ ligne)          │  ou                          │                 │
│ 🟢 Marc D.      │  [Tableau prospects filtré]  │                 │
│ 🟡 Sophie M.    │                              │                 │
│                 │                              │                 │
│ + Nouvelle room │  Zone saisie message/doc     │                 │
│                 │                              │                 │
└─────────────────┴──────────────────────────────┴─────────────────┘
```

### Comportements
- **Sidebar** : collapsible sur mobile
- **Centre** : adapte selon l'onglet actif (Visio = placeholder WebRTC, Chat = historique messages, Docs = grille fichiers, Tableau = leads du workspace)
- **Panel droit** : Sophia contextualisée à la room active (si room = "Réunion Marc D.", Sophia sait qu'on parle de Marc D.)
- **URL** : `/workspace?ws=dl-rhone&room=3` (paramètres pour deep-linking)

---

## 5. Démo vs Réel — matrice

| Élément | Statut aujourd'hui | Dans le workspace |
|---|---|---|
| Dashboard BD | ✅ Réel (fichier HTML) | **Inchangé** — reste la vue par défaut |
| Prospects démo | ❌ Mock / DEMO_DATA | ❌ Reste mock en mode démo |
| Prospects réels | ✅ API + base SQLite | ✅ Filtrés par workspace_id |
| Signaux marché | ❌ Statiques | ❌ Reste statiques en MVP |
| Audit YAWatch | ❌ Hardcodé | ❌ Reste hardcodé en mode démo |
| Workspace CRUD | ❌ N'existe pas | ✅ Réel (tables + API) |
| Rooms | ❌ N'existe pas | ✅ Réel |
| Chat messages | ❌ N'existe pas | ✅ Réel (pas temps réel WebSocket en MVP — polling 5s) |
| Documents | ❌ N'existe pas | ✅ Réel (upload stockage local Cloud Run / GCS plus tard) |
| Meetings | ❌ N'existe pas | ✅ Réel (planification, pas visio temps réel en MVP) |
| Visio / partage écran | ❌ N'existe pas | ❌ **Placeholder** (bouton "Démarrer visio" qui dit "Fonctionnalité à venir") |
| Sophia mock | ❌ Mock JS | ❌ Mock JS en mode démo, ✅ API réelle en mode prod |

---

## 6. Plan exact du premier commit (sans refonte massive)

### Commit 1 : « feat(models): ajoute Workspace, Member, Room, Meeting, Document, Message »
- Modifier `backend/models.py` — ajouter les 6 classes
- Modifier `backend/main.py` — ajouter `import models` suffit (Base.metadata.create_all gère le reste)
- **Aucun fichier existant supprimé**
- **Test** : backend démarre, nouvelles tables créées dans SQLite

### Commit 2 : « feat(api): CRUD workspaces + members »
- Créer `backend/routers/workspaces.py`
- Routes : POST/GET/PUT/DELETE `/workspaces`, GET/POST `/workspaces/{id}/members`
- Inclure dans `main.py`
- **Test** : créer un workspace via curl/API docs

### Commit 3 : « feat(api): CRUD rooms + messages (polling) »
- Créer `backend/routers/rooms.py` + `messages.py`
- Messages : GET historique + POST message (pas de WebSocket, polling côté frontend)
- **Test** : créer une room, envoyer un message, lire l'historique

### Commit 4 : « feat(api): CRUD documents + meetings (planification) »
- Créer `backend/routers/documents.py` + `meetings.py`
- Documents : upload local (pas GCS en MVP)
- Meetings : CRUD simple avec statut scheduled/live/ended
- **Test** : upload fichier, planifier réunion

### Commit 5 : « feat(ui): workspace.html minimal (layout 3 colonnes) »
- Créer `backend/static/workspace.html` (vide de data, juste le layout + fetch API)
- Créer `backend/static/assets/workspace.css` + `workspace.js`
- Route `GET /workspace` dans `main.py` pour servir le fichier
- **Le dashboard.html reste inchangé**
- **Test** : ouvrir `/workspace`, voir le layout, sidebar cliquable

### Commit 6 : « feat(integ): lien dashboard → workspace + workspace_id sur leads/audits »
- Ajouter `workspace_id` nullable sur `Lead` et `AuditClient`
- Modifier `leads.py` et `audits.py` pour filtrer par workspace
- Ajouter un bouton "Espace de travail" dans la topbar de `dashboard.html`
- **Test** : depuis le dashboard, cliquer sur "Espace de travail" → arrive sur `/workspace`

---

## 7. Risques et garde-fous

| Risque | Mitigation |
|---|---|
| Casser le dashboard existant | `dashboard.html` est **lecture seule** dans ce plan. On ne le touche qu'au commit 6 (ajout d'un lien). |
| Base SQLite trop légère pour workspace | Acceptable en MVP. Migration PostgreSQL quand le contrat est signé. |
| Upload documents sur Cloud Run (éphémère) | Stockage local temporaire en MVP. Passage à GCS dès le contrat signé. |
| Pas de WebSocket temps réel | Polling 5s en MVP. WebSocket ajouté en phase 2 si le client demande. |
| Visio / partage écran non fonctionnel | Bouton placeholder avec message "Fonctionnalité prochaine". Le client le sait dès le pitch. |

---

## 8. Validation utilisateur

Avant de coder, confirmes-tu :
- [ ] Ce plan couvre ta vision workspace ?
- [ ] Le dashboard reste la vue BD par défaut ?
- [ ] Les visio/partage écran sont en placeholder pour le MVP ?
- [ ] Tu veux que je commence par le Commit 1 (modèles) ?
