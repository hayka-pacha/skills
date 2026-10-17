# Adaptation critique du registre GEO fourni par Estelle

Source consultée : `hayka-pacha/skills`, `seo/geo-audit-optimization/SKILL.md`, SHA de fichier GitHub `0dd7aaa3bf318025fb8b2ae1f4184fa754f16b88` (lecture du dépôt le 17 octobre 2026) : https://github.com/hayka-pacha/skills/tree/main/seo/geo-audit-optimization

## À réutiliser dans le workflow d'un éditeur affilié

- **État initial multi-moteur** : tester de vraies questions d'achat, consigner URL citées, mention, position, tonalité et exactitude de chaque réponse. La métrique décisive pour Estelle est la citation de *son comparatif*, suivie du trafic/clic/vente, pas la seule mention du marchand affilié.
- **Cartographie des sources visibles** : identifier les comparatifs, médias, forums, vidéos, annuaires et sites officiels récurrents ; lire les pages qui répondent déjà au besoin et chercher une information originale manquante. Catégoriser ne signifie pas attribuer un poids universel.
- **Hypothèse de requêtes secondaires** : tester des formulations proches (produit, public, alternative, année réellement actualisée, pays, budget) et ne noter comme « requête interne visible » que ce qu'un outil montre effectivement. Une URL citée ne révèle pas la liste de toutes les recherches internes.
- **Test bilingue conditionnel** : comparer requêtes et sources FR/EN si l'audience le justifie ; une page anglaise sur une offre française n'est utile que si elle sert un vrai public et apporte une valeur propre.
- **Tableau de bord léger** : tests hebdomadaires comparables + rapport mensuel (sources citées, erreurs, trafic référent mesuré, clics affiliés, conversions et incertitudes). Fixer un objectif à partir du point de départ réel, pas d'un score externe.
- **Contribution externe à valeur propre** : lorsque des sources pertinentes acceptent des contributions, offrir une étude ou un test sincère ; divulguer toute contrepartie et qualifier les liens rémunérés. Un placement acheté ne garantit pas une citation ni un retour sur investissement.

## À ne pas importer comme règles

- « 90 % réputation / 10 % technique », « 90 % du budget en placements », fourchette 50–300 €, poids fixes par type de source, objectifs de 30/80/95 % et score de maturité sur 12 cases : chiffres non sourcés et non transférables.
- « ChatGPT réécrit souvent en anglais » et « concurrence 100 fois moindre » : hypothèses à tester, non garanties. Ne pas publier de versions linguistiques artificielles pour manipuler une supposée requête cachée.
- `llms.txt` obligatoire, FAQ JSON-LD sur toutes les pages, et déblocage indistinct de `GPTBot` : pour ChatGPT Search vérifier spécifiquement `OAI-SearchBot`; distinguer ce robot du contrôle d'entraînement. Utiliser les données structurées seulement si elles sont éligibles et fidèles au contenu.
- « Parasite SEO » et domaines expirés comme accélérateurs automatiques : risque de contenu tiers sans valeur, abus de réputation, duplication ou spam ; préférer les contributions éditoriales légitimes.
- « Lancer un programme d'affiliation » : conseil destiné à une **marque marchande** qui recrute des affiliés, pas à Estelle qui publie déjà des contenus affiliés.
- « Si je change cette source, la réponse IA change » : causalité et délai non démontrés ; ne pas utiliser comme argument commercial certain.

## Notes de mise en œuvre

- OpenAI explique la distinction entre `OAI-SearchBot` et `GPTBot` : https://developers.openai.com/api/docs/bots
- Google, contenu utile et formats IA : https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?hl=fr
- Google, liens commerciaux et qualification : https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links?hl=fr
- Toujours vérifier à nouveau les interfaces, données disponibles et règles de chaque service avant de promettre une fonction ou un KPI.
