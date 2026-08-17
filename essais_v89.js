/* Essais de la console v89 - l'onglet Agents a la demande.
   On EXECUTE les fonctions avec des donnees factices et des dependances bouchonnees :
   le controle de syntaxe ne prouve rien d'autre que la syntaxe. */
const fs = require("fs");
const src = fs.readFileSync("/tmp/console.js", "utf8");

function bloc(nom){
  const i = src.indexOf(nom);
  if (i < 0) throw new Error("fonction introuvable : " + nom);
  let j = src.indexOf("{", i), p = 0;
  for (let k = j; k < src.length; k++){
    if (src[k] === "{") p++;
    else if (src[k] === "}"){ p--; if (!p) return src.slice(i, k + 1); }
  }
  throw new Error("accolades non fermees : " + nom);
}

let ok = 0, ko = 0;
function t(nom, cond){ if (cond){ ok++; console.log("  ok   " + nom); } else { ko++; console.log("  ECHEC " + nom); } }

/* --- bouchons --- */
const elems = {};
function $(id){ return elems[id] || null; }
function esc(s){ return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
const DEPOTS = ["jlucb67/SOCLE", "jlucb67/GENERAL", "jlucb67/LFI"];
const ZONES = ["informations-publiques", "connaissances-stockees", "savoir"];
const EXCLUS = ["pack-modele", "socle-commun"];
const ARBRES = {
  "jlucb67/SOCLE":   [{path: "ADMIN/savoir/VEILLE.md", type: "blob", size: 10},
                      {path: "pack-modele/savoir/X.md", type: "blob", size: 10},
                      {path: "MANIFESTE/METAMODELE.md", type: "blob", size: 10}],
  "jlucb67/GENERAL": [{path: "EA/savoir/A.md", type: "blob", size: 10},
                      {path: "Blockchain/informations-publiques/B.md", type: "blob", size: 10}],
  "jlucb67/LFI":     [{path: "MI-Politique/savoir/etat.md", type: "blob", size: 10}]
};
let AGENTS = [];
const VEILLES = [], VEILLES_NOMS = new Set(), AVATARS = new Map(), LIGNES = [];
function mesure(v, l){ return "[" + v + " " + l + "]"; }

eval(bloc("function listeAgentsDispo()"));
eval(bloc("function remplirChoixAgent()"));

console.log("Liste des agents disponibles");
const l = listeAgentsDispo();
t("quatre agents trouves, pack-modele exclu", l.length === 4);
t("MANIFESTE n'est pas un agent (pas de zone)", !l.some(x => x.agent === "MANIFESTE"));
t("ADMIN present", l.some(x => x.agent === "ADMIN" && x.depot === "jlucb67/SOCLE"));
t("MI-Politique present", l.some(x => x.agent === "MI-Politique"));

console.log("Remplissage du selecteur");
elems["fag"] = {innerHTML: "", disabled: false};
remplirChoixAgent();
t("une option vide plus quatre agents", (elems["fag"].innerHTML.match(/<option/g) || []).length === 5);
t("invite a choisir tant que rien n'est lu", elems["fag"].innerHTML.includes("Choisis un agent"));
t("le depot est rappele entre parentheses", elems["fag"].innerHTML.includes("EA (GENERAL)"));
t("selecteur actif", elems["fag"].disabled === false);

AGENTS = [{depot: "jlucb67/GENERAL", agent: "EA"}];
remplirChoixAgent();
t("l'agent deja lu disparait de la liste", !/>EA \(/.test(elems["fag"].innerHTML));
t("il reste trois agents proposes", (elems["fag"].innerHTML.match(/<option/g) || []).length === 4);
t("l'invite devient un ajout", elems["fag"].innerHTML.includes("Ajouter un agent"));

AGENTS = listeAgentsDispo();
remplirChoixAgent();
t("selecteur desactive quand tout est lu", elems["fag"].disabled === true);

console.log("Ecran vide : invitation, pas anomalie");
AGENTS = [];
elems["agents"] = {innerHTML: ""};
eval(bloc("function rendreAgents()"));
rendreAgents();
t("invite au choix", elems["agents"].innerHTML.includes("Choisis un agent dans la liste"));
t("ne dit pas qu'aucun agent n'existe", !elems["agents"].innerHTML.includes("Aucun agent trouve"));

console.log("Garde-fou : un agent deja lu n'est pas relu");
/* aucune dependance de lecture n'est definie ici : si la fonction allait plus loin, elle jetterait. */
eval(bloc("async function collecteUnAgent(depot, agent)"));
AGENTS = [{depot: "jlucb67/GENERAL", agent: "EA"}];
let relu = null;
collecteUnAgent("jlucb67/GENERAL", "EA").then(() => { relu = false; }).catch(() => { relu = true; });
setTimeout(() => {
  t("retour immediat sans aucune lecture", relu === false);
  console.log("\n" + ok + " essais passes, " + ko + " en echec");
  process.exit(ko ? 1 : 0);
}, 50);
