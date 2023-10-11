from pricing import pricing_dir
import json

estimate_user_dir = {}
def window_sum(data,user_id):
    # Calculate the estimate for each category and update estimate_user_dir
    estimate_user_dir[str(user_id)]['ext'] += (
        (data['fixe']['TP'] * pricing_dir['fixe']['TP'][0]) +
        (data['fixe']['P'] * pricing_dir['fixe']['P'][0]) +
        (data['fixe']['M'] * pricing_dir['fixe']['M'][0]) +
        (data['fixe']['G'] * pricing_dir['fixe']['G'][0]) +
        (data['fixe']['TG'] * pricing_dir['fixe']['TG'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['fixe']['TP'] * pricing_dir['fixe']['TP'][1]) +
        (data['fixe']['P'] * pricing_dir['fixe']['P'][1]) +
        (data['fixe']['M'] * pricing_dir['fixe']['M'][1]) +
        (data['fixe']['G'] * pricing_dir['fixe']['G'][1]) +
        (data['fixe']['TG'] * pricing_dir['fixe']['TG'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['manivelle']['P'] * pricing_dir['manivelle']['P'][0]) +
        (data['manivelle']['M'] * pricing_dir['manivelle']['M'][0]) +
        (data['manivelle']['G'] * pricing_dir['manivelle']['G'][0]) +
        (data['manivelle']['TG'] * pricing_dir['manivelle']['TG'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['manivelle']['P'] * pricing_dir['manivelle']['P'][1]) +
        (data['manivelle']['M'] * pricing_dir['manivelle']['M'][1]) +
        (data['manivelle']['G'] * pricing_dir['manivelle']['G'][1]) +
        (data['manivelle']['TG'] * pricing_dir['manivelle']['TG'][1])
    )
    estimate_user_dir[str(user_id)]['ext'] += (
        (data['guillotine_simple']['P'] * pricing_dir['guillotine_simple']['P'][0]) +
        (data['guillotine_simple']['M'] * pricing_dir['guillotine_simple']['M'][0]) +
        (data['guillotine_simple']['G'] * pricing_dir['guillotine_simple']['G'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['guillotine_simple']['P'] * pricing_dir['guillotine_simple']['P'][1]) +
        (data['guillotine_simple']['M'] * pricing_dir['guillotine_simple']['M'][1]) +
        (data['guillotine_simple']['G'] * pricing_dir['guillotine_simple']['G'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['guillotine_double']['P'] * pricing_dir['guillotine_double']['P'][0]) +
        (data['guillotine_double']['M'] * pricing_dir['guillotine_double']['M'][0]) +
        (data['guillotine_double']['G'] * pricing_dir['guillotine_double']['G'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['guillotine_double']['P'] * pricing_dir['guillotine_double']['P'][1]) +
        (data['guillotine_double']['M'] * pricing_dir['guillotine_double']['M'][1]) +
        (data['guillotine_double']['G'] * pricing_dir['guillotine_double']['G'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['couissante_simple']['TP'] * pricing_dir['couissante_simple']['TP'][0]) +
        (data['couissante_simple']['P'] * pricing_dir['couissante_simple']['P'][0]) +
        (data['couissante_simple']['M'] * pricing_dir['couissante_simple']['M'][0]) +
        (data['couissante_simple']['G'] * pricing_dir['couissante_simple']['G'][0]) +
        (data['couissante_simple']['SS'] * pricing_dir['couissante_simple']['SS'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['couissante_simple']['TP'] * pricing_dir['couissante_simple']['TP'][1]) +
        (data['couissante_simple']['P'] * pricing_dir['couissante_simple']['P'][1]) +
        (data['couissante_simple']['M'] * pricing_dir['couissante_simple']['M'][1]) +
        (data['couissante_simple']['G'] * pricing_dir['couissante_simple']['G'][1]) +
        (data['couissante_simple']['SS'] * pricing_dir['couissante_simple']['SS'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['couissante_double']['TP'] * pricing_dir['couissante_double']['TP'][0]) +
        (data['couissante_double']['P'] * pricing_dir['couissante_double']['P'][0]) +
        (data['couissante_double']['M'] * pricing_dir['couissante_double']['M'][0]) +
        (data['couissante_double']['G'] * pricing_dir['couissante_double']['G'][0]) +
        (data['couissante_double']['SS'] * pricing_dir['couissante_double']['SS'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['couissante_double']['TP'] * pricing_dir['couissante_double']['TP'][1]) +
        (data['couissante_double']['P'] * pricing_dir['couissante_double']['P'][1]) +
        (data['couissante_double']['M'] * pricing_dir['couissante_double']['M'][1]) +
        (data['couissante_double']['G'] * pricing_dir['couissante_double']['G'][1]) +
        (data['couissante_double']['SS'] * pricing_dir['couissante_double']['SS'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (data['francaise'] * pricing_dir['francaise'][0])
    estimate_user_dir[str(user_id)]['both'] += (data['francaise'] * pricing_dir['francaise'][1])

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['puit_de_lumiere']['P'] * pricing_dir['puit_de_lumiere']['P'][0]) +
        (data['puit_de_lumiere']['M'] * pricing_dir['puit_de_lumiere']['M'][0]) +
        (data['puit_de_lumiere']['G'] * pricing_dir['puit_de_lumiere']['G'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['puit_de_lumiere']['P'] * pricing_dir['puit_de_lumiere']['P'][1]) +
        (data['puit_de_lumiere']['M'] * pricing_dir['puit_de_lumiere']['M'][1]) +
        (data['puit_de_lumiere']['G'] * pricing_dir['puit_de_lumiere']['G'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['porte_coulissante']['S'] * pricing_dir['porte_coulissante']['S'][0]) +
        (data['porte_coulissante']['D'] * pricing_dir['porte_coulissante']['D'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['porte_coulissante']['S'] * pricing_dir['porte_coulissante']['S'][1]) +
        (data['porte_coulissante']['D'] * pricing_dir['porte_coulissante']['D'][1])
    )
    _tmp = (
        (data['vider_les_gouttiere']['Facile'] * pricing_dir['vider_les_gouttiere']['Facile']) +
        (data['vider_les_gouttiere']['Moyen'] * pricing_dir['vider_les_gouttiere']['Moyen']) +
        (data['vider_les_gouttiere']['Difficile'] * pricing_dir['vider_les_gouttiere']['Difficile'])
    )

    _tmp += ( data['laver_soffites'] * pricing_dir['laver_soffites'] )

    _tmp += (data['installation_de_plaques'] * pricing_dir['installation_de_plaques'])

    _tmp += (
        (data['ampoules']['rdc'] * pricing_dir['ampoules']['rdc']) +
        (data['ampoules']['etage'] * pricing_dir['ampoules']['etage'])
    )

    _tmp += (data['nettoyage_de_lumiere'] * pricing_dir['nettoyage_de_lumiere'])

    _tmp += (
        (data['lavage_a_pression']['sols']['asphalte'] * pricing_dir['lavage_a_pression']['sols']['asphalte']) +
        (data['lavage_a_pression']['sols']['beton'] * pricing_dir['lavage_a_pression']['sols']['beton'])
    )

    _tmp += (data['lavage_a_pression']['murs'] * pricing_dir['lavage_a_pression']['murs'])

    _tmp += (
        (data['lavage_a_pression']['bois']['sols'] * pricing_dir['lavage_a_pression']['bois']['sols']) +
        (data['lavage_a_pression']['bois']['cloture'] * pricing_dir['lavage_a_pression']['bois']['cloture']) +
        (data['lavage_a_pression']['bois']['escalier'] * pricing_dir['lavage_a_pression']['bois']['escalier']) +
        (data['lavage_a_pression']['bois']['rampes'] * pricing_dir['lavage_a_pression']['bois']['rampes'])
    )

    _tmp += (
        (data['lavage_a_pression']['pave_seulment'] * pricing_dir['lavage_a_pression']['pave_seulment']) +
        (data['lavage_a_pression']['pave_sable_g'] * pricing_dir['lavage_a_pression']['pave_sable_g']) +
        (data['lavage_a_pression']['pave_sable_p'] * pricing_dir['lavage_a_pression']['pave_sable_p'])
    )

    _tmp += (
        (data['nettoyage_de_murs']['P'] * pricing_dir['nettoyage_de_murs']['P']) +
        (data['nettoyage_de_murs']['M'] * pricing_dir['nettoyage_de_murs']['M']) +
        (data['nettoyage_de_murs']['G'] * pricing_dir['nettoyage_de_murs']['G'])
    )

    _tmp += (
        (data['nettoyage_de_stores']['P'] * pricing_dir['nettoyage_de_stores']['P']) +
        (data['nettoyage_de_stores']['M'] * pricing_dir['nettoyage_de_stores']['M']) +
        (data['nettoyage_de_stores']['G'] * pricing_dir['nettoyage_de_stores']['G'])
    )

    _tmp += ( data['travaux_vip_heure'] * pricing_dir['travaux_vip_heure'] )
    estimate_user_dir[str(user_id)]['ext'] += _tmp
    estimate_user_dir[str(user_id)]['both'] += _tmp

def estimate_task(data_str):
    user_id = "123"
    if user_id not in estimate_user_dir:
        estimate_user_dir[str(user_id)] = {}
        estimate_user_dir[str(user_id)]['ext'] = 0
        estimate_user_dir[str(user_id)]['both'] = 0
    data = json.loads(data_str)
    window_sum(data,user_id)

    print(data)
    print(estimate_user_dir[str(user_id)]['ext'])
    print(estimate_user_dir[str(user_id)]['both'])
    #client.chat_postMessage(channel=channel_id, text=response.json()['output'])
tmp = """{\n    \"fixe\": {\n        \"TP\": 2,\n        \"P\": 0,\n        \"M\": 0,\n        \"G\": 0,\n        \"TG\": 0\n    },\n    \"manivelle\": {\n        \"P\": 5,\n        \"M\": 0,\n        \"G\": 0,\n        \"TG\": 0\n    },\n    \"guillotine_simple\": {\n        \"P\": 0,\n        \"M\": 0,\n        \"G\": 0\n    },\n    \"guillotine_double\": {\n        \"P\": 0,\n        \"M\": 0,\n        \"G\": 0\n    },\n    \"couissante_simple\": {\n        \"TP\": 0,\n        \"P\": 0,\n        \"M\": 0,\n        \"G\": 0,\n        \"SS\": 10\n    },\n    \"couissante_double\": {\n        \"TP\": 0,\n        \"P\": 0,\n        \"M\": 0,\n        \"G\": 0,\n        \"SS\": 0\n    },\n    \"francaise\": 0,\n    \"puit_de_lumiere\": {\n        \"P\": 0,\n        \"M\": 0,\n        \"G\": 0\n    },\n    \"porte_coulissante\": {\n        \"S\": 0,\n        \"D\": 0\n    },\n    \"vider_les_gouttiere\": {\n        \"Facile\": 0,\n        \"Moyen\": 0,\n        \"Difficile\": 1\n    },\n    \"laver_soffites\": 1,\n    \"installation_de_plaques\": 0,\n    \"ampoules\": {\n        \"rdc\": 3,\n        \"etage\": 2\n    },\n    \"nettoyage_de_lumiere\": 0,\n    \"lavage_a_pression\": {\n        \"sols\": {\n            \"asphalte\": 0,\n            \"beton\": 1\n        },\n        \"murs\": 0,\n        \"bois\": {\n            \"sols\": 1,\n            \"cloture\": 0,\n            \"escalier\": 0,\n            \"rampes\": 0\n        },\n        \"pave_seulment\": 0,\n        \"pave_sable_g\": 0,\n        \"pave_sable_p\": 0\n    },\n    \"nettoyage_de_murs\": {\n        \"P\": 0,\n        \"M\": 5,\n        \"G\": 0\n    },\n    \"nettoyage_de_stores\": {\n        \"P\": 2,\n        \"M\": 0,\n        \"G\": 0\n    },\n    \"travaux_vip_heure\": 0\n}"""
estimate_task(tmp)
