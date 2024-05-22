// Grammar based on EBF CFG's
grammar hm;

///////////////////
/// PARSER RULES///
///////////////////

root : (typeDef)*
		 | expr             
     ;

typeDef : leftType '::' ty;

leftType : (natural | OP);

ty : tipus '->' ty  # multiType
	 | tipus          # singleType
	 ;

tipus : VAR | CNT;


expr : aplicacio 	
     | abstraccio 
     | variable     
     | operador
     | natural      
     ;



aplicacio : aplicacio '(' expr ')'    # aplRec
					| aplicacio expr           	# aplRec
					|'(' abstraccio ')' expr  	# aplAbs
          | operador expr 	     			# aplOp
          ;

abstraccio: '\\' variable '->' expr;

variable : VAR;

natural  : NAT;

operador : OP;


//////////////////
/// LEXER RULES///
//////////////////

VAR : 'a'..'z';
CNT : 'A'..'Z';
NAT : DIGIT+;
OP  : '(' ('+' | '-' | '*' | '/') ')';


// Fragments
fragment DIGIT  : '0'..'9';

WS  : [ \t\n\r]+ -> skip ;
