window.MED_FIXTURES = {
  clients: [
    { id:"C-1042", name:"Nadia El Mansouri", phone:"06•••••142", city:"Casablanca", policy:"MA-AUTO-24018", vehicle:"Dacia Sandero · 2022", source:"CRM broker", fresh:"19 sept. 2026 · 08:40", owner:"Salma", history:["18 sept. · Collision légère au rond-point","18 sept. · Constat manquant signalé","19 sept. · Rappel demandé"], tasks:["Obtenir le constat signé","Vérifier les coordonnées de l'autre conducteur"] },
    { id:"C-1088", name:"Omar Benali", phone:"06•••••604", city:"Rabat", policy:"MA-AUTO-23872", vehicle:"Renault Clio · 2021", source:"Import navigateur simulé", fresh:"19 sept. 2026 · 08:12", owner:"Youssef", history:["19 sept. · Véhicule immobilisé","19 sept. · Assistance à vérifier"], tasks:["Vérifier la garantie assistance","Proposer un rappel humain"] },
    { id:"C-1103", name:"Sara Amrani", phone:"06•••••881", city:"Marrakech", policy:"MA-AUTO-24191", vehicle:"Peugeot 208 · 2023", source:"Formulaire local", fresh:"19 sept. 2026 · 07:55", owner:"Imane", history:["19 sept. · Blessure signalée","19 sept. · Escalade humaine ouverte"], tasks:["Confirmer la prise en charge humaine immédiate"] }
  ],
  claims: [
    { id:"SIN-26091", client:"Nadia El Mansouri", title:"Collision légère · Casablanca", status:"Pièce manquante", tone:"warning", date:"18 sept. 2026", source:"Formulaire local" },
    { id:"SIN-26094", client:"Omar Benali", title:"Véhicule immobilisé · Rabat", status:"Assistance à vérifier", tone:"violet", date:"19 sept. 2026", source:"Import simulé" },
    { id:"SIN-26095", client:"Sara Amrani", title:"Accident avec blessure · Marrakech", status:"Escalade humaine", tone:"danger", date:"19 sept. 2026", source:"Formulaire local" }
  ],
  directory: [
    {name:"Sanlam Maroc", role:"Assistance automobile 24 h/24 et 7 j/7", phone:"3434 · fixe/étranger: +212 5 22 95 75 75", url:"https://sanlam.ma/fr/sinistres/accident-de-voiture/", note:"Page officielle accident automobile."},
    {name:"RMA", role:"Centre de relation client général", phone:"2526", url:"https://www.rmaassurance.com/fr/nous-contacter", note:"Service général, pas présenté comme secours d'urgence."},
    {name:"Wafa Assurance", role:"Contact général", phone:"+212 5 22 54 55 55", url:"https://www.wafaassurance.ma/fr/compagnie-assurance-maroc/contact", note:"Numéro vérifié via l'index officiel; la page directe était indisponible lors du contrôle."},
    {name:"AXA Assurance Maroc", role:"Référence officielle; assistance à vérifier sur le contrat", phone:"Numéro non affiché: variantes officielles incohérentes", url:"https://www.axa.ma/", note:"Ne pas déduire un numéro sans vérification directe actuelle."},
    {name:"TRT Broker", role:"Courtier · compte, contrats et documents", phone:"+212 5 22 27 03 43", url:"https://trtbroker.com/mentions-legales", note:"Candidat possible pour le bonus avec compte autorisé/test."},
    {name:"OuiAssur / ALINQAD", role:"Courtier · inscription, connexion et devis", phone:"Non vérifié pendant ce contrôle", url:"https://www.ouiassur.ma/", note:"Candidat possible pour le bonus avec compte autorisé/test."}
  ]
};
