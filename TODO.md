# Vos TODO:

1. Handler le leaderboard
2. Avoir un gabarit de JSON sur le site Web pour faciliter la soumission
```json
    submission_json = {
        "model_name": "a_model_name",
        "model_url": "a_model_url",
        "tasks": [
            {
                "qfrcola": {
                    "predictions": [1, 1, 1, 1, 1]
                }
            },
            {
                "allocine": {
                    "predictions": [1, 1, 1, 1, 1]
                }
            }
        ]
    }
```
2. Expliquer pour chaque tâche le format des prédictions attendus. P. ex. pour FQuaD:
   ```{"predictions": ["text1", "text 2", ...```
3. Le leaderboard ça ne fonctionne pas, ce ne sont pas toujours les mêmes métriques. Il faut trouver un moyen de faire ca adéquatement.
4. Finir le README.md du repor COLLE, inclure notamment:
   5. détail de chaque corpus et provenance du dataset


# TODO David:
1. Il y une erreur dans le corpus QFrCoLA. Le 2e tests de la task va break quand tu va faire le changement.