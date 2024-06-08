# HinNer type analyzer

Aquest petit projecte es tracta de la pràctica de GEI-LP (edició 2023-2024 Q2). Amb l'ajuda de 
Python i antlr4, l'objectiu és crear un analitzador de tipus que sigui capaç de fer inferència de 
tipus.

## Instalació de dependències

La dependència principal es python3, i per certes característiques concretes que s'utilitzen, com per
exemple l'operador | pels tipus algebraitcs o la sentència match, fa falta una versió igual o superior
a python3.10. Es pot executar també en un entorn virtual com pot ser venv o també utilitzant pyenv per
cambiar la versió de python.

Després hi ha algunes dependències específiques:

- Streamlit
  ```sh
  pip install streamlit
  ```
- Graphviz
  ```sh
  pip install graphviz
  ```
- Pandas
  ```sh
  pip install pandas
  ```
- Dataclasses
  ```sh
  pip install dataclasses
  ```
- Antlr4: possiblement cal instalar una versió específica del runtime que sigui compatible amb la versió
          concreta de antlr4 que s'instal·la.
  ```sh
  pip install antlr4-tools
  pip install antlr4-python3-runtime
  ```

## Ús

Primerament, per poder tenir el codi dels visitors base, cal executar a la terminal:
  ```sh
  antlr4 -Dlanguage=Python3 -no-listener -visitor hm.g4
  ```
Això crearà els visitors, i després únicament caldrà executar:
  ```sh
  streamlit run hm.py
  ```
sempre que es vulgui executar el programa. Streamlit obrirà en un navegador una finestra en local,
on ja es pot probar el HinNer. La interfície és senzilla, tenim un títol, un area de text per escriure els tipus,
un text input per escriure l'expressió, i un botó de Fer. 

### Com escriure els tipus
Per escriure els tipus, cal seguir la següent sintaxi: clau :: tipus. clau pot ser per exemple (+), i tipus
podria ser N o N -> N. A més, el programa accepta tipus genèrics, com per exemple x -> x -> x

Llavors, exemples de tipus serien (un per línia):

    2 :: N
    (+) :: N -> N -> N
    1 :: P
    (*) :: x -> x -> x


### Com escriure l'expressió










### Jocs de proves


## Com està implementat


## Possibles millores


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
