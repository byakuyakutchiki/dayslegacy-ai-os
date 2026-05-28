# DAYS LEGACY AI OS — Document Maître

**Créateur & propriétaire IP :** Ludovic Saint-Louis  
**Protection :** Dépôt INPI (logiciel + marque)  
**Premier licencié :** Days Legacy  
**Statut :** En cours de conception — v0.1

---

## Section 1 — Vision

**Vision :**
> Créer le premier système d'intelligence commerciale IA dédié aux réseaux de gestion de patrimoine — permettant à chaque business developer, expert et prescripteur d'opérer comme une équipe entière, sans démarchage agressif, 24h/24.

**Problème résolu :**
Days Legacy fonctionne aujourd'hui manuellement. Aucun outil ne centralise la prospection, la qualification, l'assistance BD et la relation prospect. Des leads sont perdus chaque soir quand personne ne répond.

**Ce que le système apporte :**
- Zéro lead perdu (réponse automatique 24h/24)
- Prospects qualifiés avant le premier appel humain
- BDs plus productifs, moins de tâches répétitives
- Contenu généré et diffusé sans effort manuel
- Mémoire commerciale centralisée

---

## Section 2 — Utilisateurs et rôles

| Utilisateur | Rôle dans le système | Ce que l'IA fait pour lui |
|---|---|---|
| **Business Developer** | Reçoit les leads qualifiés, gère la relation | Prépare ses RDV, résume les échanges, relance automatiquement, filtre les appels |
| **Expert Patrimonial** | Valide les stratégies complexes | Reçoit les dossiers pré-analysés, n'intervient que sur les cas à valeur ajoutée |
| **Prescripteur** | Apporte des contacts (notaire, expert-comptable, avocat) | Reçoit des alertes sur les opportunités détectées dans sa clientèle |
| **Direction Days Legacy** | Pilote le réseau | Voit les stats, le ROI, les tendances, les performances par BD |
| **Prospect / Client** | Interagit avec le système sans le savoir | Obtient une réponse immédiate, se qualifie naturellement |
| **Ludovic (éditeur)** | Maintient et fait évoluer le système | Accès technique uniquement, jamais aux données clients |

---

## Section 3 — Cas d'usage prioritaires

**CU-01 — Réponse prospect 24h/24**
Un prospect appelle ou écrit en dehors des heures de bureau. L'IA répond en vocal ou en texte, pose 4-5 questions de qualification, rassure, fixe un rendez-vous. Le BD reçoit le résumé le lendemain matin.

**CU-02 — Préparation rendez-vous BD**
Avant un appel, le BD demande à l'IA : *"Rappelle-moi ce que je sais sur ce prospect."* L'IA sort : profil, historique des échanges, centres d'intérêt détectés, objections probables, angle recommandé.

**CU-03 — Génération de contenu validé**
L'IA détecte les sujets patrimoniaux montants (transmission PME, SCPI retraite, etc.) et propose un post LinkedIn ou un article. Un humain valide en 1 clic. Jamais de publication automatique.

**CU-04 — Qualification des leads entrants**
Quand un prospect interagit avec un contenu (simulateur, guide PDF, vidéo), l'IA note son niveau d'intérêt, crée une fiche, et alerte le bon BD selon le sujet et la région.

**CU-05 — Résumé CRM automatique**
Après chaque échange (appel, chat, email), l'IA génère un résumé structuré et le pousse dans la fiche prospect. Le BD ne saisit jamais rien manuellement.

---

## Section 4 — Architecture système

Six blocs. Chacun a une fonction précise, un stack technique, des entrées, des sorties et un coût.

---

### BLOC A — Moteur d'Intention
*Le cerveau qui écoute le marché*

**Ce qu'il fait :** Détecte les sujets patrimoniaux qui montent par région, avant que la concurrence les traite.

**Entrées :**
- Google Trends API (gratuit, tendances par région)
- Flux RSS presse économique et fiscale (Les Échos, Capital, BFM Business)
- Forums publics (Reddit, SeLoger, forums patrimoine)
- Actualités fiscales (legifrance.gouv.fr)

**Sorties :**
- Liste de sujets chauds par région et par semaine
- Score de priorité par sujet
- Suggestions de contenu pour Bloc B

**Stack :** Python + cron job hebdomadaire + GPT-4o-mini pour la classification

**Coût estimé :** ~10-20€/mois

---

### BLOC B — Moteur Contenu IA
*La machine à contenu validé*

**Ce qu'il fait :** Génère des contenus à partir des signaux du Bloc A. Jamais de publication automatique — toujours validation humaine.

**Entrées :** Sujets chauds du Bloc A + templates par format + identité de marque Days Legacy

**Sorties :**
- Post LinkedIn (300-500 mots)
- Script vidéo courte (60-90 secondes)
- Article SEO (800-1200 mots)
- Email newsletter
- Guide PDF thématique (lead magnet)

**Workflow :**
```
IA génère → Interface validation → Humain approuve/corrige → Publication
```

**Stack :** GPT-4o + interface web simple (approve/reject) + LinkedIn API pour publication

**Coût estimé :** ~20-50€/mois selon volume

---

### BLOC C — Moteur d'Engagement
*La présence permanente*

**Ce qu'il fait :** Répond aux prospects 24h/24, en vocal ou en texte, sur tous les canaux. Filtre les appels non-pertinents. Ne donne jamais de conseil financier direct.

**Canaux :**
- Téléphone (vocal)
- Chat web (widget sur site Days Legacy)
- WhatsApp Business

**Workflow vocal :**
```
Appel entrant → Twilio → OpenAI Realtime API → IA pose 4-5 questions
→ Détecte : prospect légitime ou non → Si légitime : collecte infos + fixe RDV
→ Résumé → Bloc E (CRM) → Alerte BD
```

**Filtrage intelligent :**
- Durée max si aucun intérêt détecté : 3 minutes
- Mots-clés concurrents → clôture polie
- Questions hors périmètre → redirection humaine

**Stack :** Twilio (téléphonie) + OpenAI Realtime API (voix) + WhatsApp Business API

**Coût estimé :** ~150-400€/mois selon volume d'appels

---

### BLOC D — Shadow BD
*L'assistant invisible du business developer*

**Ce qu'il fait :** Travaille en arrière-plan pour chaque BD. Prépare, résume, relance, anticipe. Le BD ne saisit rien manuellement.

**Fonctions :**
- Briefing pré-appel : *"Voici ce que vous savez sur ce prospect, l'angle recommandé, les objections probables"*
- Résumé post-échange automatique → poussé dans Bloc E
- Relance automatique des leads sans réponse (J+7, J+14, J+30)
- Alerte événement déclencheur : *"Ce prospect a lu 3 nouveaux articles depuis votre dernier échange"*

**Stack :** GPT-4o + RAG sur historique prospect (Bloc E) + notification SMS/email (Twilio)

**Coût estimé :** ~30-80€/mois

---

### BLOC E — Mémoire & CRM IA
*La colonne vertébrale du système*

**Ce qu'il fait :** Stocke tout, structure tout, relie tout. Source de vérité unique.

**Ce qu'il stocke :**
- Profil prospect (nom, situation, objectifs, historique)
- Score d'intérêt (Froid → Tiède → Chaud → Brûlant)
- Tous les échanges (vocal transcrit, chat, email)
- Actions BD effectuées
- Contenu consulté

**Stack technique :**
```
PostgreSQL (données persistantes)
    + Redis (sessions et cache temps réel)
    + Dashboard web simple (stats, fiches prospects, pipeline)
```

**Coût estimé :** ~50-80€/mois (hébergement Cloud Run + base de données)

---

### BLOC F — Conformité
*Le garde-fou légal permanent*

**Ce qu'il fait :** Enveloppe tous les autres blocs. Aucune donnée ne circule sans passer par ce bloc.

| Règle | Implémentation |
|---|---|
| Consentement RGPD | Opt-in explicite avant tout stockage |
| Identification IA obligatoire | L'IA se présente toujours comme assistant IA |
| Interdiction conseil financier | Filtrage prompt + liste de sujets bloqués |
| Droit à l'effacement | Route admin suppression complète |
| Conservation limitée | Suppression automatique après 3 ans d'inactivité |
| Audit trail | Log horodaté de chaque décision IA |
| Hébergement EU | Cloud Run région europe-west1 uniquement |

**Coût estimé :** inclus dans l'hébergement

---

### Vue d'ensemble — Flux de données

```
[Marché] → BLOC A → sujets chauds
                  ↓
              BLOC B → contenu → validation humaine → publication
                                                         ↓
[Prospect] ──────────────────────────────────────→ découvre et interagit
                  ↓
              BLOC C → qualification → BLOC E (stockage)
                                           ↓
                                       BLOC D → alerte BD → RDV

              BLOC F enveloppe tout — conformité permanente
```

---

### Récapitulatif des coûts infrastructure

| Bloc | Coût mensuel estimé |
|---|---|
| A — Intention | 10-20€ |
| B — Contenu | 20-50€ |
| C — Engagement vocal | 150-400€ |
| D — Shadow BD | 30-80€ |
| E — CRM / hébergement | 50-80€ |
| F — Conformité | inclus |
| **Total MVP** | **260-630€/mois** |

---

## Section 5 — Stack technique

### 5.1 Backend
| Décision | Choix retenu |
|---|---|
| Langage | Python 3.11+ |
| Framework | FastAPI |
| Architecture | Multi-tenant (tenant_id sur toutes les tables) |

### 5.2 IA & LLM
| Usage | Modèle |
|---|---|
| Génération contenu, analyse prospect, Shadow BD | GPT-4o |
| Filtrage, classification, scoring | GPT-4o-mini |
| Voix temps réel | OpenAI Realtime API |
| RAG (mémoire prospect) | pgvector + GPT-4o |

### 5.3 Voix & Téléphonie
```
Appel entrant → Twilio → OpenAI Realtime API → FastAPI backend → Twilio
```
- Numéro FR : Twilio (~1€/mois)
- Appels entrants : ~0,013€/min
- Voix IA : ~0,06€/min in + ~0,24€/min out
- SMS BD : ~0,07€/SMS

### 5.4 Base de données
| Besoin | Outil |
|---|---|
| Données persistantes | PostgreSQL + pgvector |
| Sessions / cache | Redis |
| Recherche sémantique | pgvector (embeddings OpenAI) |

### 5.5 Hébergement
| Composant | Service | Région |
|---|---|---|
| API backend | Google Cloud Run | europe-west1 |
| Base de données | Cloud SQL PostgreSQL | europe-west1 |
| Cache | Redis Cloud Memorystore | europe-west1 |
| Fichiers | Cloud Storage | europe-west1 |

### 5.6 Canaux & Intégrations
| Canal | Outil |
|---|---|
| Chat web | Widget JS custom |
| WhatsApp | Meta WhatsApp Business Cloud API |
| Email | Brevo (entreprise FR, RGPD natif) |
| LinkedIn | LinkedIn API |
| Blog/articles | WordPress REST API |

### 5.7 Authentification & Rôles
JWT avec 5 niveaux : superadmin (Ludo) / direction / bd / expert / prescripteur

### 5.8 Intelligence marché
- Google Trends : pytrends (hebdomadaire)
- RSS presse éco : feedparser (quotidien)
- Légifrance : RSS officiel (quotidien)

### Résumé stack
```
Backend         : Python 3.11 + FastAPI
LLM principal   : GPT-4o
LLM économique  : GPT-4o-mini
Voix            : OpenAI Realtime API + Twilio
Base données    : PostgreSQL + pgvector + Redis
Hébergement     : Google Cloud Run (europe-west1)
Email           : Brevo
WhatsApp        : Meta Cloud API
Auth            : JWT multi-rôles
Marché          : pytrends + feedparser RSS
Multi-tenant    : tenant_id natif sur toutes les tables
```

## Section 6 — Flux de données détaillé

### 6.1 Flux prospect entrant (voix)

```
1. Prospect appelle le numéro Days Legacy
2. Twilio reçoit l'appel → webhook FastAPI
3. FastAPI vérifie : heure, numéro blacklisté, tenant actif
4. OpenAI Realtime API prend la conversation
   → L'IA se présente : "Bonjour, je suis l'assistante Days Legacy..."
   → Pose 4-5 questions de qualification
   → Détecte : prospect légitime / spam / concurrent
5. Si légitime :
   → Collecte : prénom, sujet d'intérêt, disponibilité
   → Propose un créneau de rappel
   → Rassure et clôture chaleureusement
6. FastAPI stocke dans PostgreSQL (Bloc E)
   → Fiche prospect créée (ou mise à jour)
   → Score initial : TIÈDE
7. Twilio envoie SMS au BD concerné
   → "Nouveau prospect : [prénom], sujet : [transmission PME], rappeler [créneau]"
8. Tableau de bord mis à jour en temps réel
```

### 6.2 Flux contenu (Bloc A → B → publication)

```
1. Cron hebdomadaire → Bloc A interroge Google Trends + RSS
2. GPT-4o-mini classe et score les sujets par région
3. Top 3 sujets → Bloc B génère les contenus proposés
4. Notification à l'humain validateur (email + dashboard)
5. Humain approuve / corrige / refuse
6. Si approuvé → publication via LinkedIn API / WordPress API
7. Logs stockés : date, sujet, taux engagement (J+7)
```

### 6.3 Flux Shadow BD (préparation RDV)

```
1. BD consulte la fiche prospect sur le dashboard
2. Il clique "Préparer mon appel"
3. FastAPI interroge PostgreSQL : historique complet du prospect
4. pgvector cherche les échanges similaires passés
5. GPT-4o génère le briefing :
   → Résumé du profil
   → Points sensibles détectés
   → Objections probables + réponses suggérées
   → Angle recommandé selon le sujet
6. Briefing affiché sur le dashboard + envoyé par SMS si demandé
```

### 6.4 Flux relance automatique (Shadow BD)

```
1. Cron quotidien → vérifie les prospects sans activité
2. Si J+7 sans réponse → SMS de relance automatique au prospect
3. Si J+14 sans réponse → alerte BD : "Ce prospect est inactif"
4. Si J+30 → passage automatique en score FROID
5. Tout log horodaté dans PostgreSQL (audit trail)
```

---

## Section 7 — Conformité RGPD / AMF

### 7.1 RGPD — Règles non négociables

| Règle | Implémentation technique |
|---|---|
| Consentement avant tout stockage | Message d'accueil vocal : "Cet échange est traité par une IA. En continuant, vous acceptez notre politique de confidentialité." |
| Identification comme IA | L'IA se présente toujours explicitement comme assistante IA (EU AI Act, août 2025) |
| Droit à l'effacement | Route admin `DELETE /prospect/{id}` supprime toutes les données liées |
| Portabilité des données | Export JSON disponible sur demande |
| Conservation limitée | Suppression automatique après 3 ans d'inactivité (cron mensuel) |
| Hébergement EU | Cloud Run europe-west1 exclusivement |
| Audit trail | Chaque action IA loggée avec timestamp, tenant_id, type d'action |
| Chiffrement | HTTPS obligatoire, données sensibles chiffrées AES-256 en base |

### 7.2 AMF / MiFID II — Ce que l'IA ne fait JAMAIS

L'IA ne donne jamais de conseil en investissement personnalisé.
Ce périmètre est gravé dans le system prompt ET dans un filtre de détection.

**Phrases bloquées automatiquement :**
- "Vous devriez investir dans..."
- "Je vous recommande ce produit..."
- "Avec votre profil, le meilleur placement est..."

**Ce que l'IA dit à la place :**
- "C'est une question que notre expert patrimonial pourra traiter avec vous lors de votre rendez-vous."

### 7.3 Protection IP — Ludo Saint-Louis

| Élément | Protection |
|---|---|
| Code source | Droit d'auteur automatique (France) — prouvé par commits GitHub horodatés |
| Marque / nom produit | À déposer INPI quand les finances le permettent |
| Dépôt logiciel formel | APP (Agence pour la Protection des Programmes) — ~25€ — à faire avant la première signature |
| Contrat de licence | Obligatoire avant tout accès Days Legacy au système |

### 7.4 Clause clé du contrat de licence

> Le code source n'est jamais livré au licencié.
> Le licencié obtient un droit d'usage, pas un droit de propriété.
> En cas de rupture de contrat, l'accès au système est coupé sous 48h.
> Toutes les données du licencié restent sa propriété et lui sont restituées sur demande.

---

## Section 8 — Modèle économique

### 8.1 Ce que Days Legacy paie directement (infrastructure)

| Poste | Estimé/mois | Payeur |
|---|---|---|
| OpenAI API (LLM + voix) | 100-300€ | Days Legacy |
| Twilio (téléphone + SMS) | 50-100€ | Days Legacy |
| Google Cloud Run + BDD | 50-80€ | Days Legacy |
| Brevo, WhatsApp API | 20-50€ | Days Legacy |
| **Total infrastructure** | **220-530€** | **Days Legacy** |

### 8.2 Royalties Ludovic Saint-Louis

**Modèle recommandé : Hybride fixe + variable**

| Élément | Montant |
|---|---|
| Frais d'intégration (setup, unique) | **3 000€** |
| Licence de base mensuelle | **500€/mois** |
| Par business developer actif | **150€/BD/mois** |

**Exemples :**

| Nombre de BDs | Royalties mensuelles |
|---|---|
| 5 BDs | 500 + (5×150) = **1 250€/mois** |
| 10 BDs | 500 + (10×150) = **2 000€/mois** |
| 20 BDs | 500 + (20×150) = **3 500€/mois** |

### 8.3 Clauses contractuelles

- Durée minimale : 12 mois
- Renouvellement tacite par période de 12 mois
- Révision tarifaire : maximum +15% par an
- Paiement : mensuel, virement, sous 30 jours
- Résiliation : préavis 3 mois

### 8.4 Projection revenus Ludo (scénario conservateur)

| Mois | Événement | Revenu |
|---|---|---|
| M0 | Signature + setup | **3 000€** |
| M1-M6 | 5 BDs actifs | **1 250€/mois** |
| M7-M12 | 10 BDs actifs | **2 000€/mois** |
| M13+ | 2e licencié | **+1 250€/mois** |

---

## Section 9 — MVP — Premier palier livrable

### 9.1 Définition

Le MVP est la version minimale qui prouve que le système marche et justifie la signature du contrat de licence.

**Périmètre MVP :**
- Bloc C partiel : IA répond aux appels, pose 4 questions, prend les infos
- Bloc D partiel : BD reçoit un SMS résumé après chaque appel
- Bloc E minimal : base de données prospects simple
- Dashboard minimal : liste des prospects + statut

**Hors périmètre MVP :**
- Carte des tendances (Bloc A)
- Génération de contenu (Bloc B)
- Scoring dynamique avancé
- WhatsApp et chat web
- Relances automatiques

### 9.2 Délai estimé

| Phase | Durée | Contenu |
|---|---|---|
| Setup infrastructure | 3-4 jours | Cloud Run, PostgreSQL, Redis, Twilio |
| Bloc C — voix | 5-7 jours | Intégration OpenAI Realtime + Twilio + system prompt |
| Bloc D — SMS BD | 2-3 jours | Notification SMS + résumé GPT-4o |
| Bloc E — BDD | 3-4 jours | Schéma prospects + CRUD |
| Dashboard minimal | 4-5 jours | Liste prospects + statuts |
| Tests + ajustements | 3-5 jours | Tests réels, calibration voix |
| **Total** | **~4 semaines** | |

### 9.3 Critère de validation MVP

> Un prospect appelle un samedi soir.
> Aucun humain ne répond.
> L'IA engage la conversation, collecte les informations, fixe un créneau.
> Le BD reçoit un SMS résumé.
> Le lundi matin, le prospect est dans le dashboard avec son profil complet.

Si ça marche : le contrat est signé.

---

## Section 10 — Roadmap

```
PHASE 1 — MVP (mois 1)
├── Bloc C : voix IA 24h/24
├── Bloc D : SMS résumé BD
└── Bloc E : base prospects minimale

PHASE 2 — Consolidation (mois 2-3)
├── Bloc E complet : CRM + scoring + historique
├── Bloc D complet : briefing pré-appel + relances auto
├── Chat web (widget)
└── Dashboard complet

PHASE 3 — Attraction (mois 4-6)
├── Bloc A : moteur d'intention (tendances régionales)
├── Bloc B : génération contenu + interface validation
├── Simulateur patrimonial public (lead magnet)
└── WhatsApp Business

PHASE 4 — Intelligence (mois 7-12)
├── Scoring dynamique (Froid → Brûlant)
├── Patrimonial Twin (jumeau numérique client)
├── Carte de France des intentions
├── Analytics & reporting direction
└── Multi-licencié : 2e client

PHASE 5 — Expansion (an 2)
├── Onboarding nouveaux licenciés en autonomie
├── Marketplace de templates contenus
├── API publique pour intégrations tierces
└── Version mobile BD
```

---

## Section 11 — Contrat de licence (structure)

*À faire rédiger par un avocat spécialisé IP avant signature.*
*En attendant, voici les clauses essentielles à inclure.*

### Clauses obligatoires

1. **Identification des parties** : Ludovic Saint-Louis (éditeur) / Days Legacy (licencié)
2. **Objet** : droit d'usage non-exclusif du système Days Legacy AI OS
3. **Propriété** : le code source reste la propriété exclusive de Ludovic Saint-Louis
4. **Non-livraison du code** : le licencié n'a jamais accès au code source
5. **Non-cession** : le licencié ne peut pas sous-licencier ou revendre le système
6. **Rémunération** : setup 3 000€ + 500€/mois + 150€/BD actif/mois
7. **Durée** : 12 mois renouvelables
8. **Résiliation** : préavis 3 mois, accès coupé sous 48h après fin de contrat
9. **Données** : les données clients Days Legacy restent leur propriété
10. **Confidentialité** : les deux parties s'engagent à ne pas divulguer les termes
11. **Droit applicable** : droit français, tribunal compétent : [ville de Ludo]

### Protection immédiate avant avocat

Envoyer un email daté à Days Legacy avec :
> "Je vous confirme que le système Days Legacy AI OS est ma propriété intellectuelle exclusive. Tout accès ou utilisation est soumis à la signature d'un contrat de licence."

Cet email constitue une preuve de notification.

---

## Statut du document

| Section | Statut |
|---|---|
| 1 — Vision | ✅ Complète |
| 2 — Utilisateurs | ✅ Complète |
| 3 — Cas d'usage | ✅ Complète |
| 4 — Architecture | ✅ Complète |
| 5 — Stack technique | ✅ Complète |
| 6 — Flux de données | ✅ Complète |
| 7 — Conformité RGPD/AMF | ✅ Complète |
| 8 — Modèle économique | ✅ Complète |
| 9 — MVP | ✅ Complète |
| 10 — Roadmap | ✅ Complète |
| 11 — Contrat de licence | ✅ Structure complète |
