/* Essais de la console v92 - les lignes du tableau en sous-dossier entrent dans le tunnel.
   On EXECUTE collecteTunnel sur l'arbre REEL de MI-Politique (clone local) et sur son vrai
   META_DOCUMENTS.tsv. Le controle de syntaxe ne prouve rien d'autre que la syntaxe. */
const fs = require("fs"), path = require("path");
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
function t(nom, cond){ if (cond){ ok++; console.log("  ok    " + nom); } else { ko++; console.log("  ECHEC " + nom); } }

/* --- arbre reel du clone LFI, au format de l'API --- */
const RACINE = "/home/claude/lfi";
function arbreReel(dir, base){
  const out = [];
  (function marche(d){
    for (const e of fs.readdirSync(d, {withFileTypes: true})){
      if (e.name === ".git") continue;
      const p = path.join(d, e.name);
      if (e.isDirectory()) marche(p);
      else out.push({path: path.relative(base, p), type: "blob", size: fs.statSync(p).size});
    }
  })(dir);
  return out;
}
const ARBRE_LFI = arbreReel(path.join(RACINE, "MI-Politique"), RACINE);

/* --- bouchons --- */
const DEPOTS = ["jlucb67/LFI"];
const ZONES = ["informations-publiques", "connaissances-stockees", "savoir"];
const EXCLUS = ["pack-modele", "socle-commun"];
const DATED = /^\d{4}-\d{2}-\d{2}[_-]?/;
let LIGNES = [], ARBRES = {};
const ETAT = {tunnel: {}};
function progres(){}
async function arbre(){ return ARBRE_LFI; }
async function shasDepots(){ return {}; }
async function texteOuNull(depot, chemin){
  const p = path.join(RACINE, chemin);
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : null;
}
function normStable(x){ return x; }

eval(bloc("function metaListe(txt)"));
eval(bloc("function metaUneLigne(c)"));
eval(bloc("function metaParse(txt)"));
eval(bloc("function dateDe(nom)"));
eval(bloc("async function collecteTunnel()"));
eval(bloc("function zonesOccupees(r)"));
eval(bloc("function zoneVive(r)"));
function esc(s){ return String(s == null ? "" : s); }
eval(bloc("function actions(r)"));

/* --- le tableau, lu independamment de la console --- */
const tsv = fs.readFileSync(path.join(RACINE, "MI-Politique/META_DOCUMENTS.tsv"), "utf8")
  .split("\n").filter(l => l.trim());
const entete = tsv[0].split("\t");
const rangs = tsv.slice(1).map(l => l.split("\t"));
const nonLuTableau = rangs.filter(r => (r[entete.indexOf("resume")] || "").trim() === "non lu").length;

(async () => {
  console.log("Le tableau (source independante)");
  t("290 lignes au tableau", rangs.length === 290);
  t("170 lignes portent « non lu »", nonLuTableau === 170);

  console.log("metaListe garde les doublons de nom, metaParse les fond");
  const liste = metaListe(fs.readFileSync(path.join(RACINE, "MI-Politique/META_DOCUMENTS.tsv"), "utf8"));
  t("metaListe rend 290 lignes", liste.length === 290);
  t("metaParse rend 288 entrees (deux noms en double)", Object.keys(metaParse(
      fs.readFileSync(path.join(RACINE, "MI-Politique/META_DOCUMENTS.tsv"), "utf8"))).length === 288);
  t("outre-mer.md apparait deux fois dans la liste",
     liste.filter(([f]) => f === "outre-mer.md").length === 2);

  await collecteTunnel();
  const siens = LIGNES.filter(r => r.agent === "MI-Politique");
  const dette = siens.filter(r => r.resume === "non lu").length;
  const attente = siens.filter(r => r.z["informations-publiques"]).length;
  const enSous = siens.filter(r => r.sousDossier).length;

  console.log("Le tunnel apres correction");
  console.log("  lignes MI-Politique : " + siens.length + " - dont sous-dossier : " + enSous);
  console.log("  resumes dus : " + dette + " - en attente (Zone 1) : " + attente);
  t("au moins 290 lignes (les 290 du tableau)", siens.length >= 290);
  t("les 225 documents en sous-dossier sont entres", enSous === 225);
  t("le compteur ne compte que les lignes du tableau", siens.filter(r => r.declare && r.resume === "non lu").length === 170);
  t("le compteur « resumes dus » atteint les 170 du tableau", dette >= 170);
  t("aucune ligne sans zone", siens.every(r => Object.keys(r.z).length > 0));
  t("aucun doublon de chemin sur outre-mer.md",
     new Set(siens.filter(r => r.sousDossier && /outre-mer\.md$/.test(r.sousDossier))
       .map(r => r.sousDossier)).size === siens.filter(r => r.sousDossier && /outre-mer\.md$/.test(r.sousDossier)).length);

  console.log("Aucun bouton mort sur les documents en sous-dossier");
  const unSous = siens.find(r => r.sousDossier);
  const a = actions(unSous);
  t("ni case a cocher ni bouton", !/input|<button/.test(a));
  const unPlat = siens.find(r => !r.sousDossier && r.z["informations-publiques"]);
  t("les documents a la racine gardent leurs boutons", unPlat ? /<button/.test(actions(unPlat)) : true);

  console.log("\n" + ok + " essais passes, " + ko + " en echec.");
  process.exit(ko ? 1 : 0);
})();
