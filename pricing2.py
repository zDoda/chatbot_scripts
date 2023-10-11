

pricing_dir = {
    "fixe" : {
        'TP' : [1.30, 2.36],
        'P' : [3.12, 5.67],
        'M' : [4.59, 8.35],
        'G' : [6.21, 11.29],
        'TG' : [7.68, 13.97]
    },
    "manivelle" : {
        'P' : [4.59, 8.35],
        'M' : [6.21, 11.29],
        'G' : [7.68, 13.97],
        'TG' : [8.66, 15.75]
    },
    "guillotine_simple" : {
        'P' : [6.21, 11.29],
        'M' : [7.68, 13.97],
        'G' : [9.04, 16.43],
    },
    "guillotine_double" : {
        'P' : [6.21, 19.58],
        'M' : [7.68, 22.19],
        'G' : [9.04, 24.80]
    },
    "couissante_simple" : {
        'TP' : [3.95, 7.17],
        'P' : [6.21, 9.40],
        'M' : [7.69, 12.86],
        'G' : [9.04, 14.33],
        'SS' : [9.82, 17.85]
    },
    "couissante_double" : {
        'TP' : [3.95, 8.93],
        'P' : [6.21, 11.55],
        'M' : [7.69, 14.70],
        'G' : [9.04, 17.85],
        'SS' : [9.82, 23.10]
    },
    "francaise" : [.58, 1.05],
    "puit_de_lumiere" : {
        'P' : [5.25, 9.45],
        'M' : [6.30, 15.75],
        'G' : [7.35, 18.90]
    },
    "porte_coulissante" : {
        'S' : [9.82, 17.85],
        'D' : [9.82, 28.66]
    }
}

estimate_prompt = """
[no prose]

[Output only in JSON]

[Include all of the JSON fields]

Vous essayez de convertir une chaîne en un objet JSON pour trouver le nombre de chaque type de fenêtre pour une entreprise de nettoyage de vitres. Vous recevrez une chaîne d'un utilisateur avec la catégorie de fenêtre/service, extérieur/intérieur et extérieur, et le nombre de fenêtres pour chaque catégorie. Si la catégorie JSON a un tableau, le 0e élément concerne uniquement les fenêtres extérieures et le 1er élément concerne à la fois les fenêtres intérieures et extérieures. Si la chaîne de l'utilisateur ne contient pas de fenêtre, mettez 0 pour cette catégorie. Veuillez uniquement imprimer l'objet JSON et aucune autre réponse.

TP - Très Petit, P - Petit, M - Moyen, G - Grand, TG or SS - Très Grand.

Chaque Catégorie:
Fixe (par vitre) TP,P,M,G,TG

Manivelle (par vitre)
P,M,G,TG

Guillotine simple ( fixe et amovible)
P,M,G

Guillotine double ( fixe et amovible)
P,M,G

Coulissante simple
TP,P,M,G,SS
Coulissante double
TP,P,M,G,SS

Française(carreaux)

Puit de lumière
P,M,G

Porte coulissante paire de vitres
S,D

Chaque Catégorie JSON:
{
    "fixe" : {
        "TP" : 0,
        "P" : 0,
        "M" : 0,
        "G" : 0,
        "TG" : 0
    },
    "manivelle" : {
        "P" : 0,
        "M" : 0,
        "G" : 0,
        "TG" : 0
    },
    "guillotine_simple" : {
        "P" : 0,
        "M" : 0,
        "G" : 0
    },
    "guillotine_double" : {
        "P" : 0,
        "M" : 0,
        "G" : 0
    },
    "couissante_simple" : {
        "TP" : 0,
        "P" : 0,
        "M" : 0,
        "G" : 0,
        "SS" : 0
    },
    "couissante_double" : {
        "TP" : 0,
        "P" : 0,
        "M" : 0,
        "G" : 0,
        "SS" : 0
    },
    "francaise" : 0,
    "puit_de_lumiere" : {
        "P" : 0,
        "M" : 0,
        "G" : 0
    },
    "porte_coulissante" : {
        "S" : 0,
        "D" : 0
    }}"""
