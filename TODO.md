# Vos TODO:

1. ~~Le leaderboard ça ne fonctionne pas, ce ne sont pas toujours les mêmes métriques. Il faut trouver un moyen de faire ca adéquatement.~~
2. ~~2. Avoir un gabarit de JSON sur le site Web pour faciliter la soumission~~
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
4. ~~Finir le README.md du repor COLLE, inclure notamment les détail de chaque corpus et provenance du dataset.~~
7. ~~Retirer les étiquettes des tests set des jeu de données dans [COLLE-public](https://huggingface.co/datasets/graalul/COLLE-public/).~~
6. ~~Vérifier les licences des datasets pour respecter l'acchiage de licence de [COLLE-public](https://huggingface.co/datasets/graalul/COLLE-public).~~ (Voir datasets_metadata)
~~3. Expliquer pour chaque tâche le format des prédictions attendus. P. ex. pour FQuaD:~~ (Voir datasets_metadata)
   ```{"predictions": ["text1", "text 2", ...```
4. ~~Étoffer le contenu du README.md de COLLE-public et copier-coller dans COLLE.~~

# TODO David:
1. ~~Il y une erreur dans le corpus QFrBLiMP sur COLLE et COLLE-public. Le 2e tests de la task va break quand tu va faire le changement.~~
2. La description de QFrBLiMP n'est pas bonne à finaliser.
3. Publication de QFrCoLA à corriger aussi.
