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

## Section 5 — Stack technique *(à compléter)*

## Section 6 — Flux de données détaillé *(à compléter)*

## Section 7 — Conformité RGPD / AMF *(à compléter)*

## Section 8 — Modèle économique *(à compléter)*

## Section 9 — MVP — premier palier livrable *(à compléter)*

## Section 10 — Roadmap *(à compléter)*

## Section 11 — Modèle de licence INPI *(à compléter)*
