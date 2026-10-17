---
name: geo-affiliation
description: "Use when improving affiliate pages for AI citations (GEO)."
version: 0.2.0
author: Estelle, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GEO, SEO, affiliation, comparatifs, citations-IA]
    related_skills: [grounded-citations, seo-editorial-content]
---

# GEO — faire citer un site affilié par les moteurs de réponse

Transformer des contenus affiliés existants en sources fiables et comparables, puis mesurer leur présence dans les réponses IA. Inspiré des interventions de Lucio (01:09:34–02:10:36), puis de Léopold et Nicolas (06:07:30–06:45:30) dans la conférence Linkavista (https://www.youtube.com/watch?v=viwHB3lVLvg). Leurs chiffres et tactiques sont des études de cas présentées par des acteurs commercialisant aussi des placements, **pas** des garanties ni des recommandations officielles. Lire `references/conference-et-gardefous.md` et `references/audit-registre-geo.md` avant une campagne. La seconde référence adapte de façon critique le skill `geo-audit-optimization` du registre GitHub fourni par Estelle ; elle n'en reprend pas les ratios ni les promesses comme des faits.

## When to Use (Quand l'utiliser)

- L'utilisateur veut rendre ses articles, comparatifs ou offres affiliées plus susceptibles d'être cités dans ChatGPT Search ou Google AI.
- Il veut prioriser ses contenus existants, créer un comparatif, analyser des sources déjà citées ou mesurer ses progrès.
- Ne pas l'utiliser pour promettre une citation, fabriquer des avis, publier en masse des clones ou acheter des liens destinés à manipuler les classements.

## Prérequis

- URL du site, inventaire des pages / sitemap, produits promus et, si disponibles, données Search Console et clics affiliés. Ne jamais déduire les commissions ou programmes d'affiliation d'un simple lien.
- Pour les prix, caractéristiques, disponibilité et conditions du partenariat, vérifier les sources officielles au moment de rédiger.
- Accès aux réponses IA ciblées pour les tests ; documenter le moteur, le pays, la langue, la date, la requête et le type de compte si pertinent. Une requête isolée n'est pas une mesure de visibilité stable.
- Pour chaque offre, identifier le rôle : Estelle est **éditrice affiliée** qui cherche des citations vers sa page, pas automatiquement la marque marchande qui voudrait être recommandée. Les deux résultats se suivent séparément.

## Procédure

1. **Établir le point de départ.** Inventorier les pages publiées et leurs sujets ; choisir 2–3 familles cohérentes de produits parmi les contenus qui apportent déjà du trafic, des clics affiliés ou une expertise réelle. Noter pour chaque famille 5–10 questions d'achat précises et leurs variantes naturelles (« meilleur X pour débutant », « X ou Y », « alternative à X pour budget Z »). Privilégier les besoins de niche où l'expérience du site apporte une réponse supérieure aux classements généralistes ; si une source dominante est omniprésente, affiner l'usage ou le profil plutôt que copier son « top ». Livrable : liste priorisée de pages et requêtes, avec les données réelles ou la mention « données manquantes ».
2. **Vérifier l'accès et l'indexation.** Pour chaque URL prioritaire : statut HTTP 200, contenu principal visible dans le HTML, canonique correcte, absence de `noindex`, robots.txt et Search Console ; vérifier que Googlebot et, pour ChatGPT Search, `OAI-SearchBot` ne sont pas bloqués par robots/CDN. Ne pas confondre accessibilité et indexation, ni indexation et citation. Ne modifier robots.txt qu'après diagnostic.
3. **Observer les réponses réellement citées et leur écosystème.** Poser les mêmes questions d'achat séparément dans ChatGPT Search, Google AI Overviews et, si elles comptent pour le public, Perplexity/Copilot/Gemini avec recherche web. Pour chaque test : requête exacte, date, moteur, pays/langue, réponse, URL citées, mention de la page éditoriale, produit marchand recommandé, ton et erreurs factuelles. Classer les sources récurrentes (comparatif, média, vidéo, forum, fiche officielle, annuaire) et la pertinence de chacune ; ne pas attribuer de poids universel aux catégories. Une page peut être citée sans que ton site ou ta sélection soit recommandé. Les deux moteurs peuvent choisir des sources différentes. Comparer des formulations FR/EN **seulement si le public et les résultats observés le justifient** ; déduire des sources visibles des hypothèses de recherche, jamais des « fan-out » internes exacts non exposés.
4. **Améliorer d'abord les pages fortes.** Transformer les meilleures pages existantes en comparatifs à intention claire : réponse concise dès le début, tableau lisible (produit, profil, prix daté, avantages, limites, lien), critères de sélection et méthode, fiches structurées et comparables, cas d'usage, alternatives crédibles, FAQ répondant à de vraies objections. Le conférencier suggère souvent 5–10 options et 75–150 mots par option ; ce sont des repères éditoriaux, jamais des quotas SEO. Inclure des preuves originales (captures réellement faites, essais, calculs, critères documentés), vérifier les prix et conditions, dater les mises à jour effectives. Ne pas prétendre avoir testé un produit qui ne l'a pas été.
5. **Rendre l'intérêt commercial transparent et structurer sans magie.** Signaler clairement la présence de liens d'affiliation avant les recommandations ; marquer les liens rémunérés `rel="sponsored"` (éventuellement avec `nofollow`). Séparer classement éditorial et rémunération : ne pas placer un produit premier uniquement parce qu'il paie le plus. Préciser les limites et profils pour lesquels il ne convient pas. Titres H1/H2 clairs et informations factuelles accessibles en HTML ; données structurées uniquement quand elles correspondent au contenu visible et aux règles de l'outil concerné. Ne pas ajouter FAQ/Product/Review à toutes les pages ni créer `llms.txt` comme prérequis GEO.
6. **Développer une présence externe authentique et choisir le budget sur preuves.** Reprendre les observations originales sous un autre format (vidéo YouTube, présentation ou post pertinent) avec un lien vers le comparatif ; proposer à des éditeurs déjà présents dans les sources des données, tests ou contributions éditoriales qui apportent une valeur propre. Si un placement sponsorisé est envisagé, vérifier audience, pertinence, prix, transparence, qualification du lien et résultat mesurable avant un petit essai ; ne pas adopter d'allocation fixe de budget (comme « 90 % GEO »). Une source indépendante peut citer une étude utile sans vendre de placement. Ne pas poster de faux témoignages, de spam Reddit ou de listes dupliquées sur des domaines satellites.
7. **Mesurer puis itérer.** Enregistrer un état initial, puis tester hebdomadairement le même panel de requêtes pendant plusieurs semaines : URL de la page citée, mention de la marque du site, marchand recommandé, position, exactitude de la réponse, moteur/pays/langue/date ; rapprocher ces observations de Search Console, des références IA si accessibles dans l'analytics, des clics affiliés et conversions. Livrer un rapport mensuel compact avec `templates/rapport-geo.md` : tests comparables, sources gagnées/perdues, changements effectués, trafic et ventes attribuables ou attribution inconnue, trois prochaines actions. Lire une tendance sur plusieurs essais, pas un screenshot : réponses personnalisées, volatiles, et sondes de suivi géographiquement limitées. Ne pas inventer d'objectifs universels de 30 % ou 80 %. Modifier une page à la fois et consigner les changements. Si aucune citation ne suit, vérifier d'abord accès, pertinence et valeur originale ; ne pas annoncer une causalité sur un seul test.

## Priorité si l'utilisateur a beaucoup d'affiliation

P0 : audit des 2–3 pages affiliées les plus prometteuses et leurs questions commerciales ; corriger accès / `noindex` si nécessaire. P1 : améliorer ces pages avec des comparatifs réellement utiles et des preuves originales ; relier les articles connexes. P2 : publier une vidéo ou contribution éditoriale propre pour chaque comparatif réussi. Ne pas lancer simultanément des dizaines de « top 10 » non vérifiés.

## Garde-fous et vérification

- Le SEO de base demeure essentiel ; ni `llms.txt`, ni un format Markdown spécial, ni un schéma GEO magique ne remplace un contenu indexable et distinctif.
- Ne pas reprendre les affirmations des conférenciers selon lesquelles cinq domaines satellites, les liens achetés, les échanges systématiques ou un sous-domaine de « protection » seraient sans risque. Les règles Google peuvent les traiter comme spam ; un sous-domaine ne neutralise pas automatiquement une infraction.
- Le livrable doit identifier les URL auditées, les sources officielles des faits produits, les liens rémunérés, les requêtes de test, le point de départ et ce qui reste hypothétique. Succès vérifiable : page accessible et enrichie, puis URL effectivement citée dans des réponses documentées ; aucune garantie de classement ou commission.
