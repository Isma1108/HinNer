// Grammar based on EBF CFG's

grammar hm;

///////////////////
/// PARSER RULES///
///////////////////

root : expr             
     ;

expr : aplicacio 	
     | abstraccio 
     | variable     
     | natural      
     ;


aplicacio : '(' abstraccio ')' expr # aplAbs
          | aplicacio expr          # aplRec
          | OP expr 		    # aplOp		
          ;

abstraccio: '\\' variable '->' expr;

variable : VAR;

natural  : NAT;


//////////////////
/// LEXER RULES///
//////////////////

VAR : LLETRA+;
NAT : DIGIT+;
OP  : '(' ('+' | '-' | '*' | '/') ')';


// Fragments
fragment LLETRA : 'a'..'z'|'A'..'Z';
fragment DIGIT  : '0'..'9';

WS  : [ \t\n\r]+ -> skip ;
