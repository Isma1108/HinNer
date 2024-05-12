// Grammar based on EBF CFG's

grammar hm;

root : expr             
     ;

expr : NUM
     ;

NUM : [0-9]+ ;

WS  : [ \t\n\r]+ -> skip ;
