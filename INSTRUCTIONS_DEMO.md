# Days Legacy AI OS — Instructions Démo Rendez-Vous

> **Version :** v0.1.1-qa  
> **Commit :** `42af86a`  
> **Date :** 10 juin 2026  
> **Statut :** Validé QA — 10/10 Playwright, 0 erreur console, 0 erreur réseau

---

## 🚀 Lancer la démo en 30 secondes

```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Puis ouvrir dans le navigateur :
```
http://localhost:8000/dashboard?demo=1
```

**Aucun mot de passe requis.** Le mode démo s'ouvre instantanément.

---

## 🎯 Scénario de démo recommandé (5 minutes)

### 1. Accueil — "Voici Days Legacy"
- Montrer la landing : **noir, or, premium**
- Souligner : *"Sophia est notre intelligence patrimoniale IA. Elle travaille 24h/24 pour les business developers."*

### 2. Mode démo — pipeline enrichi
- Montrer les **5 prospects qualifiés**
- Pointer le **score 9.4** de Marc D. — transmission PME
- Montrer le **script d'appel** généré par Sophia (clic "Voir le script")
- Mentionner : *"En vrai, Sophia a passé 18 minutes au téléphone avec lui samedi soir. Lundi matin, le BD reçoit ce briefing."*

### 3. Signaux marché
- Scroller vers **Signaux du marché**
- Dire : *"L'IA détecte les sujets qui montent par région. Cette semaine : +42% sur la transmission PME en Rhône-Alpes."*

### 4. Sophia en action
- Taper dans le chat : **"Bilan de la semaine"**
- Montrer la réponse instantanée avec **priorités + disclaimer**
- Dire : *"Sophia ne donne jamais de conseil financier. Elle prépare l'expert. C'est le garde-fou AMF."*

### 5. Audit YAWatch Industries
- Cliquer sur **"Audits Clients"**
- Présenter YAWatch comme **client audité** :
  - CA 28M€, 87 salariés
  - **Score audit 7.8/10**
  - 6 findings structurés (2 critiques, 2 élevés)
- Pointer le finding "Absence de holding familiale" — gain potentiel **800k€**
- Dire : *"C'est un exemple concret de ce que Days Legacy peut produire pour un client. YAWatch est un partenaire technologique et un client audité."*

### 6. Responsive / mobile
- Ouvrir l'URL sur votre téléphone
- Montrer que tout est fluide
- Dire : *"Le BD a ça dans sa poche entre deux rendez-vous."*

---

## 🛡️ Points de conformité à mentionner

| Règle | Ce que vous dites |
|---|---|
| Sophia = IA | *"Sophia est une assistante IA. Elle ne remplace pas l'expert patrimonial."* |
| Pas de conseil | *"Elle ne donne jamais de conseil financier personnalisé. C'est un garde-fou AMF."* |
| Disclaimer | *"Chaque réponse comportant des chiffres inclut un disclaimer juridique."* |
| RGPD | *"Tout est hébergé en Europe. Les données clients restent leur propriété."* |
| Mode démo | *"Ce que vous voyez ici sont des données de démonstration. En production, ce sont vos vrais prospects."* |

---

## 🔐 Accès production (si demandé)

```
URL : https://<votre-domaine>/dashboard
Login : mot de passe fort (fourni séparément)
```

**Ne jamais montrer le mot de passe à l'écran.**

---

## ⚠️ Ce qu'il ne faut PAS dire

❌ *"YAWatch est propriétaire de Days Legacy"* → C'est faux. YAWatch est **client/partenaire**.  
❌ *"Sophia conseille d'investir dans..."* → C'est faux. Sophia **prépare l'expert**, elle ne conseille pas.  
❌ *"C'est encore en développement, ça ne marche pas vraiment"* → C'est faux. Le MVP est **testé et fonctionnel**.  
❌ *"On peut tout automatiser"* → C'est faux. L'humain valide **chaque contenu** avant publication.

---

## 📁 Structure du repo (pour référence)

```
dayslegacy-ai-os/
├── backend/
│   ├── main.py              # FastAPI
│   ├── models.py            # Base de données (Lead, AuditClient, AuditFinding)
│   ├── routers/
│   │   ├── sophia.py        # Prompt compliance RGPD/AMF
│   │   ├── auth.py          # JWT sécurisé
│   │   ├── leads.py         # CRUD prospects
│   │   └── audits.py        # CRUD audits clients
│   └── static/
│       └── dashboard.html   # Frontend unique (démo + prod)
├── docs/                    # Documentation & captures d'audit
├── qa-tests/                # Tests Playwright complets
└── INSTRUCTIONS_DEMO.md     # Ce fichier
```

---

## 📞 Support technique

En cas de problème lors de la démo :
1. Vérifier que le backend tourne (`curl http://localhost:8000/health`)
2. Vérifier que le port 8000 est libre
3. Recharger la page avec `?demo=1`
4. Si Sophia ne répond pas en prod → vérifier `OPENAI_API_KEY` dans `.env`

---

**Bonne démo.** 🎯
