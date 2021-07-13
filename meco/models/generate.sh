rm *.dot*
textx generate grammar.tx --target=dot
textx generate nodes.ent --grammar grammar.tx --target=dot
dot -Tpng -O grammar.dot
dot -Tpng -O nodes.dot
