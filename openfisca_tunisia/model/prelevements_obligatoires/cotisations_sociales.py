# -*- coding: utf-8 -*-


from __future__ import division

from numpy import zeros

from openfisca_tunisia.model.base import *  # noqa analysis:ignore

CAT = Enum(['rsna', 'rsa', 'rsaa', 'rtns', 'rtte', 're', 'rtfr', 'raci', 'cnrps_sal', 'cnrps_pen'])


def compute_cotisation(individu, period, cotisation_type = None, bareme_name = None, legislation = None):
    assert cotisation_type in ['employeur', 'salarie']
    assiette_cotisations_sociales = individu('assiette_cotisations_sociales', period)
    categorie_salarie = individu('categorie_salarie', period)  # TODO change to regime_salarie
    baremes_by_regime = legislation(period.start).cotisations_sociales
    cotisation = zeros(len(assiette_cotisations_sociales))
    for regime_name, regime_index in CAT:
        bareme_by_name = baremes_by_regime[regime_name].get(
            'cotisations_{}'.format(cotisation_type))
        if bareme_by_name is not None:
            if bareme_name in ['maladie', 'maternite', 'deces']:
                baremes_assurances_sociales = bareme_by_name.get('assurances_sociales')
                if baremes_assurances_sociales is not None:
                    bareme = baremes_assurances_sociales.get(bareme_name)
                else:
                    bareme = bareme_by_name.get(bareme_name)
            else:
                bareme = bareme_by_name.get(bareme_name)

            if bareme is not None:
                cotisation += bareme.calc(
                    assiette_cotisations_sociales * (categorie_salarie == regime_index),
                    )
    return - cotisation


class assiette_cotisations_sociales(Variable):
    column = FloatCol
    entity = Individu
    label = u"Assiette des cotisations sociales"
    definition_period = MONTH

    def formula(individu, period):
        return (
            individu('salaire_de_base', period) +
            individu('primes', period)
            )


class categorie_salarie(Variable):
    column = EnumCol(CAT, default = 0)
    entity = Individu
    label = u"Catégorie de salarié"
    definition_period = ETERNITY


class cotisations_sociales(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisations sociales"
    definition_period = MONTH

    def formula(individu, period):
        return (
            individu('cotisations_employeur', period) +
            individu('cotisations_salarie', period)
            )


class cotisations_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation sociales employeur"
    definition_period = MONTH

    def formula(individu, period):
        return (
            individu('accident_du_travail_employeur', period) +
            individu('deces_employeur', period) +
            individu('fonds_special_etat', period) +
            individu('famille_employeur', period) +
            individu('maladie_employeur', period) +
            individu('maternite_employeur', period) +
            individu('protection_sociale_travailleurs_employeur', period) +
            individu('retraite_employeur', period)
            )


class cotisations_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation sociales salarié"
    definition_period = MONTH

    def formula(individu, period):
        return (
            individu('accident_du_travail_salarie', period) +
            individu('deces_salarie', period) +
            individu('famille_salarie', period) +
            individu('maladie_salarie', period) +
            individu('maternite_salarie', period) +
            individu('protection_sociale_travailleurs_salarie', period) +
            individu('retraite_salarie', period) +
            individu('ugtt', period, options = [ADD])
            )


class accident_du_travail_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation accidents du travail et maladies professionnelles (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'accident_du_travail',
            legislation = legislation
            )


class accident_du_travail_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation accidents du travail et maladies professionnelles (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'accident_du_travail',
            legislation = legislation
            )


class deces_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation assurances sociales: décès (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'deces',
            legislation = legislation
            )


class deces_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation assurances sociales: décès (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'deces',
            legislation = legislation
            )


class famille_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation sociale allocations familiales (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'famille',
            legislation = legislation
            )


class famille_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation sociale allocations familiales (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'famille',
            legislation = legislation
            )


class fonds_special_etat(Variable):
    column = FloatCol
    entity = Individu
    label = u"Fonds spécial de l'Etat"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'fonds_special_etat',
            legislation = legislation
            )


class maladie_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation assurances sociales: maladie (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'maladie',
            legislation = legislation
            )


class maladie_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation assurances sociales: maladie (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'maladie',
            legislation = legislation
            )


class maternite_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation assurances sociales : maternité (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'maternite',
            legislation = legislation
            )


class maternite_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation assurances sociales : maternité (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'maternite',
            legislation = legislation
            )


class protection_sociale_travailleurs_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation protection sociale des travailleurs (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'protection_sociale_travailleurs',
            legislation = legislation
            )


class protection_sociale_travailleurs_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation protection sociale des travailleurs (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'protection_sociale_travailleurs',
            legislation = legislation
            )


class retraite_employeur(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation pensions de retraite (employeur)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'employeur',
            bareme_name = 'retraite',
            legislation = legislation
            )


class retraite_salarie(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation pensions de retraite (salarié)"
    definition_period = MONTH

    def formula(individu, period, legislation):
        return compute_cotisation(
            individu,
            period,
            cotisation_type = 'salarie',
            bareme_name = 'retraite',
            legislation = legislation
            )


class salaire_imposable(Variable):
    column = FloatCol
    entity = Individu
    label = u"Salaire imposable"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period):
        return (
            individu('assiette_cotisations_sociales', period) +
            individu('cotisations_salarie', period)
            )


class salaire_net_a_payer(Variable):
    column = FloatCol
    entity = Individu
    label = u"Salaire net à payer (fiche de paie)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period):
        return (
            individu('salaire_imposable', period) +
            individu.foyer_fiscal('irpp', period.this_year) / 12
            )


# class salaire_brut(Variable):
#     column = FloatCol
#     entity = Individu
#     label = u"Salaires bruts"

#     def formula(individu, period, legislation):
#         '''
#         Calcule le salaire brut à partir du salaire net
#         '''

#         salaire_imposable = individu('salaire_imposable', period = period)
#         categorie_salarie = individu('categorie_salarie', period = period)
#         cotisations_sociales = legislation(period.start, reference = True).cotisations_sociales

#         smig = cotisations_sociales.gen.smig_40h_mensuel
#         cotisations_sociales = MarginalRateTaxScale('cotisations_sociales', cotisations_sociales)
#         plafond_securite_sociale = 12 * smig

#         n = len(salaire_imposable)
#         salaire_brut = zeros(n)
#         # TODO améliorer tout cela !!
#         for categ in CAT:
#             iscat = (categorie_salarie == categ[1])
#             if categ[0] == 're':
#                 return salaire_imposable  # on retourne le salaire_imposable pour les étudiants
#             else:
#                 continue

#             if 'sal' in cotisations_sociales[categ[0]]:
#                 sal = cotisations_sociales[categ[0]]['sal']
#                 baremes = sal.scale_tax_scales(plafond_securite_sociale)
#                 bar = combine_bracket(baremes)
#                 invbar = bar.inverse()
#                 temp = iscat * invbar.calc(salaire_imposable)
#                 salaire_brut += temp
#         return salaire_brut


class salaire_super_brut(Variable):
    column = FloatCol
    entity = Individu
    label = u"Salaires super bruts"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period):
        return (
            individu('salaire_de_base', period = period) +
            individu('primes', period = period) -
            individu('cotisations_employeur', period = period)  # Cotisations employeur sont négatives
            )


class ugtt(Variable):
    column = FloatCol
    entity = Individu
    label = u"Cotisation syndicale UGTT"
    definition_period = MONTH

    def formula(individu, period):
        return -3 * (individu('categorie_salarie', period) == 8)

# class cotisations_employeur(Variable):
#     column = FloatCol
#     entity = Individu
#     label = u"Cotisations sociales employeur"

#     def formula(individu, period, legislation):

#         salaire_brut = individu('salaire_brut', period = period)
#         categorie_salarie = individu('categorie_salarie', period = period)
#         _P = legislation(period.start)

#         # TODO traiter les différents régimes séparément ?

#         smig = _P.cotisations_sociales.gen.smig_40h_mensuel
#         cotisations_sociales = MarginalRateTaxScale('cotisations_sociales', _P.cotisations_sociales)

#         plafond_securite_sociale = 12 * smig
#         # TODO: clean all this
#         n = len(salaire_brut)
#         cotisations_employeur = zeros(n)
#         for categ in CAT:
#             iscat = (categorie_salarie == categ[1])
#             if categ[0] == 're':
#                 return salaire_brut  # on retounre le salaire_brut pour les étudiants
#             else:
#                 continue
#             if 'cotisations_employeur' in cotisations_sociales[categ[0]]:
#                 bareme_employeur = cotisations_sociales[categ[0]]['cotisations_employeur']
#                 baremes = scale_tax_scales(bareme_employeur, plafond_securite_sociale)
#                 bareme_agrege = combine_tax_scales(baremes)
#                 temp = - iscat * bareme_agrege.calc(salaire_brut)
#                 cotisations_employeur += temp
#         return cotisations_employeur


# class cotisations_salarie(Variable):
#     column = FloatCol
#     entity = Individu
#     label = u"Cotisations sociales salariés"

#     def formula(individu, period, legislation):

#         salaire_brut = individu('salaire_brut', period = period)
#         categorie_salarie = individu('categorie_salarie', period = period)
#         _P = legislation(period.start)
#         # TODO traiter les différents régimes
#         smig = _P.cotisations_sociales.gen.smig
#         cotisations_sociales = MarginalRateTaxScale('cotisations_sociales', _P.cotisations_sociales)
#         plafond_securite_sociale = 12 * smig

#         n = len(salaire_brut)
#         cotisations_salarie = zeros(n)

#         for categ in CAT:
#             iscat = (categorie_salarie == categ[1])

#             if categ[0] == 're':
#                 return 0 * salaire_brut  # TODO: doit retounrer la bonne valeur les étudiants
#             else:
#                 continue

#             if 'sal' in cotisations_sociales[categ[0]]:
#                 pat = cotisations_sociales[categ[0]]['sal']
#                 baremes = scale_tax_scales(pat, plafond_securite_sociale)
#                 bar = combine_tax_scales(baremes)
#                 temp = - iscat * bar.calc(salaire_brut)
#                 cotisations_salarie += temp

#         return cotisations_salarie
