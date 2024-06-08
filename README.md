# HinNer type analyzer

Aquest petit projecte es tracta de la pràctica de GEI-LP (edició 2023-2024 Q2). Amb l'ajuda de 
Python i antlr4, l'objectiu és crear un analitzador de tipus que sigui capaç de fer inferència de 
tipus.


### Fet amb:

* [![Python][Python.org]][Python-utl]



Important:
- La symTable del session state es per constants definides per l'usuari
  que s'han de mantenir entre execucions de diferents arbres

- La localSymTable es el mateix que la symTable però per un AST concret, pel que la informació
  no s'ha de mantenir entre reexecucions. En el primer recorregut nomes tenim parelles
  (text, Variable), de forma que dos nodes amb el mateix text comparteixin variable. Quan
  es fa la inferència de tipus aquesta taula es va actualitzant, fins el punt on no tenim variables
  a inferir, o fins que ens trobem amb un problema d'inferència.

- varTypes es un diccionari que te parelles (variable, tipus), es tracta dels elements que es mostraran
  a la taula de tipus de les variables que se'ns demana mostrar un cop acabada la inferència.
