# Bandeira + nome PT-BR por seleção (extraído de build_dashboard.py; vira fonte única na Fase 2.1).
# A bandeira agora é SVG inline (flags.py): emoji de bandeira NÃO renderiza no Windows. PT[t][0] é
# sobrescrito ao fim do arquivo (o emoji no literal abaixo fica só como referência legível do país).
from flags import ref as _flagref
PT={
"Spain":["\U0001F1EA\U0001F1F8","Espanha"],"France":["\U0001F1EB\U0001F1F7","França"],
"Argentina":["\U0001F1E6\U0001F1F7","Argentina"],"England":["\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F","Inglaterra"],
"Portugal":["\U0001F1F5\U0001F1F9","Portugal"],"Brazil":["\U0001F1E7\U0001F1F7","Brasil"],
"Germany":["\U0001F1E9\U0001F1EA","Alemanha"],"Netherlands":["\U0001F1F3\U0001F1F1","Holanda"],
"Belgium":["\U0001F1E7\U0001F1EA","Bélgica"],"Norway":["\U0001F1F3\U0001F1F4","Noruega"],
"Colombia":["\U0001F1E8\U0001F1F4","Colômbia"],"Japan":["\U0001F1EF\U0001F1F5","Japão"],
"Morocco":["\U0001F1F2\U0001F1E6","Marrocos"],"United States":["\U0001F1FA\U0001F1F8","Estados Unidos"],
"Uruguay":["\U0001F1FA\U0001F1FE","Uruguai"],"Mexico":["\U0001F1F2\U0001F1FD","México"],
"Switzerland":["\U0001F1E8\U0001F1ED","Suíça"],"Croatia":["\U0001F1ED\U0001F1F7","Croácia"],
"Turkey":["\U0001F1F9\U0001F1F7","Turquia"],"Ecuador":["\U0001F1EA\U0001F1E8","Equador"],
"Senegal":["\U0001F1F8\U0001F1F3","Senegal"],"Sweden":["\U0001F1F8\U0001F1EA","Suécia"],
"Austria":["\U0001F1E6\U0001F1F9","Áustria"],"Canada":["\U0001F1E8\U0001F1E6","Canadá"],
"Paraguay":["\U0001F1F5\U0001F1FE","Paraguai"],"Ivory Coast":["\U0001F1E8\U0001F1EE","Costa do Marfim"],
"Egypt":["\U0001F1EA\U0001F1EC","Egito"],"Algeria":["\U0001F1E9\U0001F1FF","Argélia"],
"Scotland":["\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F","Escócia"],"Czechia":["\U0001F1E8\U0001F1FF","Chéquia"],
"Bosnia and Herzegovina":["\U0001F1E7\U0001F1E6","Bósnia"],"Ghana":["\U0001F1EC\U0001F1ED","Gana"],
"South Korea":["\U0001F1F0\U0001F1F7","Coreia do Sul"],"Iran":["\U0001F1EE\U0001F1F7","Irã"],
"Tunisia":["\U0001F1F9\U0001F1F3","Tunísia"],"Australia":["\U0001F1E6\U0001F1FA","Austrália"],
"DR Congo":["\U0001F1E8\U0001F1E9","RD Congo"],"Cape Verde":["\U0001F1E8\U0001F1FB","Cabo Verde"],
"Iraq":["\U0001F1EE\U0001F1F6","Iraque"],"Jordan":["\U0001F1EF\U0001F1F4","Jordânia"],
"New Zealand":["\U0001F1F3\U0001F1FF","Nova Zelândia"],"Panama":["\U0001F1F5\U0001F1E6","Panamá"],
"Qatar":["\U0001F1F6\U0001F1E6","Catar"],"Saudi Arabia":["\U0001F1F8\U0001F1E6","Arábia Saudita"],
"South Africa":["\U0001F1FF\U0001F1E6","África do Sul"],"Uzbekistan":["\U0001F1FA\U0001F1FF","Uzbequistão"],
"Curacao":["\U0001F1E8\U0001F1FC","Curaçao"],"Haiti":["\U0001F1ED\U0001F1F9","Haiti"],
}
for _t in PT:  # troca o emoji pela bandeira SVG (mantém o nome PT-BR); fonte única = flags.py
    PT[_t][0] = _flagref(_t)
