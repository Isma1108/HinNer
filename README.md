# HinNer type analyzer

Aquest petit projecte es tracta de la pràctica de GEI-LP (edició 2023-2024 Q2). Amb l'ajuda de 
Python i antlr4, l'objectiu és crear un analitzador de tipus que sigui capaç de fer inferència de 
tipus d'un subconjunt d'expressions utilitzant l'algorisme de Hindley-Milner. El codi python segueix
les regles d'estil PEP8.

## Instalació de dependències

La dependència principal es python3, i per certes característiques concretes que s'utilitzen, com per
exemple l'operador | pels tipus algebraics o la sentència match, fa falta una versió igual o superior
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
- Future
  ```sh
  pip install future
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
on ja es pot probar el HinNer. La interfície és senzilla, tenim un títol, un àrea de text per escriure els tipus,
un text input per escriure l'expressió, i un botó de Fer. 

### Com escriure els tipus
Per escriure els tipus, cal seguir la següent sintaxi: clau :: tipus. clau pot ser per exemple (+), i tipus
podria ser per exemple N o N -> N. A més, el programa accepta tipus genèrics, com per exemple x -> x -> x

Llavors, exemples de tipus serien (un per línia):

    2 :: N
    (+) :: N -> N -> N
    1 :: P
    (*) :: x -> x -> x

Els errors relacionats amb posar coses que no són tipus al text area dels tipus no estan gestionats, la pràctica
dona a entendre que la detecció d'errors de sintaxi és només per les expressions.

### Com escriure l'expressió
A l'expressió hi podem posar combinacions de variables, constants, aplicacions i abstraccions. Per exemple

    \x -> \y -> (+) 2 ((+) x y)


### Què fa el botó Fer
Un cop tenim els tipus i l'expressió escrits, si donem clic al botó Fer, principalment el que es fa és:

    - Actualitzar la taula de tipus
    - Obtenir l'AST corresponent a l'expressió
    - Intentar realitzar inferència de tipus si és possible

### Jocs de proves
El HinNer passa tots els jocs de proves públics i obligatoris disponibles a l'enunciat: [Enunciat](https://github.com/gebakx/lp-hinner-24)
Per altra banda, també passa un joc de proves opcional, concretament l'exemple 7a1, que es tracta d'un exemple on es defineix
el (+) com un tipus genèric x -> x -> x. Els tipus definits són:

    2 :: N
    (+) :: x -> x -> x

I l'expressió és:

    \x -> \y -> (+) 2 ((+) x y)

Si es dona al botó de Fer es podrà veure que el HinNer és capaç d'inferir bé. Com a detalls, quan hi ha un error de sintaxi
o hi ha un conflicte de tipus, el HinNer ho mostra amb un text de color vermell. Quan el HinNer és capaç de realitzar la inferència
mostra el nombre de recorreguts que han sigut necessaris.

Un altre exemple molt interessant on el HinNer és capaç de realitzar l'inferència de tipus correctament és el següent:

Tipus:
    
    2 :: N

Expressió:

    (*) 2 ((*) x x)

Aparentment pot semblar que no és possible inferir-ho tot, però sí que ho és. Es pot probar aplicant l'algorisme de Milner a mà.

Finalment, cal destacar que si no s'especifica cap tipus, el HinNer és capaç d'inferir deixant les variables sense definir.


## Com està implementat
La gramàtica antlr està implementada amb l'objectiu que els visitors del codi python siguin curts, és a dir, que el pes recaigui en
la gramàtica. Per altra banda, el codi python utilitza streamlit i visitors que hereden dels visitors base per poder crear un AST
corresponent a l'expressió. Al codi hi ha dos visitors, un pels tipus i l'altre per l'expressió. Hi ha una funció que mostra
l'AST un cop generat amb l'ajuda de graphviz, i després hi ha una funció que modifica l'AST per realitzar inferència de tipus. La implementació
de l'inferència de tipus és amb una funció recursiva que es basa en les ecuacions de l'algorisme de Hindley-Milner. Degut a com està 
implementada, en certes expressions fa falta més d'un recorregut de l'arbre, es fan tants recorreguts fins que no es modifiqui
l'arbre o fins que s'arribi a un limit de recorreguts establert.

En quant a les estructures de dades utilitzades al codi cal destacar el següent:

- La symTable del session state és per tipus definits per l'usuari
  que s'han de mantenir entre execucions de diferents arbres

- La localSymTable és el mateix que la symTable però per un AST concret, pel que la informació
  no s'ha de mantenir entre reexecucions. En el primer recorregut nomes tenim parelles
  (text, Variable), de forma que dos nodes amb el mateix text comparteixin variable. Quan
  es fa la inferència de tipus aquesta taula es va actualitzant, fins el punt on no tenim variables
  a inferir, o fins que ens trobem amb un problema d'inferència.

- varTypes és un diccionari que te parelles (variable, tipus), es tracta dels elements que es mostraran
  a la taula de tipus de les variables que se'ns demana mostrar un cop acabada la inferència.

Com a detall, tant l'arbre com els tipus s'han implementat amb tipus algebraics. L'arbre és o bé Buit o bé un Node
que té certs atributs i dos fills arbre. I els tipus són o bé una Constant, o bé una Variable, o bé una Aplicació, la qual
té dos fills tipus.


## Possibles millores

Caldria perfeccionar el fet de mantenir tipus definits per l'usurai entre reexecucions. Degut a les particularitats
del session_state de streamlit, a vegades hi ha certs problemes. Si en algún moment apareix algun error relacionat amb que algun atribut
és NoneType, és per problemes amb el session_state. En aquell cas, reiniciem la pàgina i redefinim tipus i expressió. He preferit dedicar
temps a l'algorisme que no pas amb barallar-me amb streamlit, que no crec que sigui l'objectiu de la pràctica.

Una altra cosa a fer seria afegir algún botó per buidar la taula de tipus. Actualment si s'ha de buidar cal reiniciar la pàgina,
en Gerard Escudero em va dir que amb això era suficient.













