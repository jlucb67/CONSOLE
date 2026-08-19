/* Compare le tunnel AVANT et APRES la correction, sur les trois depots reels. */
const fs = require("fs"), path = require("path");
const QUEL = process.argv[2];               /* chemin du fichier console.js a executer */
const src = fs.readFileSync(QUEL, "utf8");
function bloc(nom){
  const i = src.indexOf(nom);
  if (i < 0) throw new Error("introuvable : " + nom);
  let j = src.indexOf("{", i), p = 0;
  for (let k = j; k < src.length; k++){
    if (src[k] === "{") p++; else if (src[k] === "}"){ p--; if (!p) return src.slice(i, k + 1); }
  }
}
const RAC = {"jlucb67/SOCLE": "/home/claude/socle", "jlucb67/GENERAL": "/home/claude/general", "jlucb67/LFI": "/home/claude/lfi"};
function arbreReel(base){
  const out = [];
  (function marche(d){
    for (const e of fs.readdirSync(d, {withFileTypes: true})){
      if (e.name === ".git" || e.name === ".github") continue;
      const p = path.join(d, e.name);
      if (e.isDirectory()) marche(p); else out.push({path: path.relative(base, p), type: "blob", size: fs.statSync(p).size});
    }
  })(base);
  return out;
}
const DEPOTS = Object.keys(RAC);
const ZONES = ["informations-publiques", "connaissances-stockees", "savoir"];
const EXCLUS = ["pack-modele", "socle-commun"];
const DATED = /^\d{4}-\d{2}-\d{2}[_-]?/;
let LIGNES = [], ARBRES = {};
const ETAT = {tunnel: {}};
const CACHE = {}; for (const d of DEPOTS) CACHE[d] = arbreReel(RAC[d]);
function progres(){}
async function arbre(d){ return CACHE[d]; }
async function shasDepots(){ return {}; }
async function texteOuNull(depot, chemin){
  const p = path.join(RAC[depot], chemin);
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : null;
}
function normStable(x){ return x; }
if (src.includes("function metaListe")){ eval(bloc("function metaListe(txt)")); eval(bloc("function metaUneLigne(c)")); }
eval(bloc("function metaParse(txt)"));
eval(bloc("function dateDe(nom)"));
eval(bloc("async function collecteTunnel()"));
(async () => {
  await collecteTunnel();
  const par = {};
  for (const r of LIGNES){
    const o = par[r.agent] || (par[r.agent] = {lignes: 0, dus: 0, z1: 0});
    o.lignes++;
    if ((r.declare === undefined || r.declare) && r.resume === "non lu") o.dus++;
    if (r.z["informations-publiques"]) o.z1++;
  }
  for (const a of Object.keys(par).sort())
    console.log(a.padEnd(30) + "lignes " + String(par[a].lignes).padStart(4)
      + " | resumes dus " + String(par[a].dus).padStart(4) + " | zone 1 " + String(par[a].z1).padStart(4));
})();
