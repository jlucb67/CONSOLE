#!/usr/bin/env python3
# v92 - Les documents declares au tableau dont le fichier vit dans un SOUS-DOSSIER de zone
# entraient nulle part : la collecte ne lisait que la racine des trois zones. Les compteurs
# « resumes dus » et « en attente de toi » mentaient donc sur MI-Politique (65 lignes vues
# sur 290). Chaque ancre est comptee avant remplacement.
import io, re

F = "index.html"
h = io.open(F, encoding="utf-8").read()

def rempl(h, a, b, n=1):
    c = h.count(a)
    assert c == n, "ANCRE (%d/%d) : %r" % (c, n, a[:80])
    return h.replace(a, b)

# 1. metaListe : les lignes du tableau DANS L'ORDRE, doublons de nom compris.
A1 = """function metaParse(txt){
  const m = {};
  if (!txt) return m;
  const lignes = txt.split("\\n").filter(l => l.trim() && !l.startsWith("#"));
  for (const l of lignes){
    const c = l.split("\\t");
    if (c.length < 2) continue;
    if (/^document\\b/i.test(c[0])) continue;
    m[c[1].trim()] = {"""
B1 = """/* metaListe rend les lignes du tableau DANS L'ORDRE, doublons de nom compris
   (deux documents differents peuvent porter le meme nom de fichier dans deux
   sous-dossiers : plans/outre-mer.md et livrets/outre-mer.md). metaParse, lui,
   indexe par nom de fichier et ne peut donc en garder qu'une : les deux usages
   coexistent, chacun a sa place. */
function metaListe(txt){
  const out = [];
  if (!txt) return out;
  const lignes = txt.split("\\n").filter(l => l.trim() && !l.startsWith("#"));
  for (const l of lignes){
    const c = l.split("\\t");
    if (c.length < 2) continue;
    if (/^document\\b/i.test(c[0])) continue;
    out.push([c[1].trim(), metaUneLigne(c)]);
  }
  return out;
}
function metaParse(txt){
  const m = {};
  for (const [fic, o] of metaListe(txt)) m[fic] = o;
  return m;
}
function metaUneLigne(c){
    return {"""
h = rempl(h, A1, B1)

# fin de l'ancienne boucle de metaParse -> fin de metaUneLigne
A2 = """      majeurs: (c[12]||"").trim().split(/\\s+/).filter(Boolean)
    };
  }
  return m;
}
function dateDe(nom){"""
B2 = """      majeurs: (c[12]||"").trim().split(/\\s+/).filter(Boolean)
    };
}
function dateDe(nom){"""
h = rempl(h, A2, B2)

# 2. garder le texte du tableau (metaListe en a besoin)
A3 = """    const meta = metaParse(await texteOuNull(depot, agent + "/META_DOCUMENTS.tsv"));"""
B3 = """    const txtMeta = await texteOuNull(depot, agent + "/META_DOCUMENTS.tsv");
    const meta = metaParse(txtMeta);"""
h = rempl(h, A3, B3)

# 3. noter les fichiers reellement vus a la racine des zones
A4 = """    const docs = {};
    for (const n of arbres[depot]){"""
B4 = """    const docs = {};
    const plats = new Set();   /* fichiers vus a la RACINE d'une zone : deja portes par la boucle */
    for (const n of arbres[depot]){"""
h = rempl(h, A4, B4)

A5 = """      d.z[zone] = [fic, ex ? ex[1].toLowerCase() : "texte", n.size || 0];"""
B5 = """      d.z[zone] = [fic, ex ? ex[1].toLowerCase() : "texte", n.size || 0];
      plats.add(fic);"""
h = rempl(h, A5, B5)

# 4. deuxieme passe : les lignes du tableau dont le fichier est dans un sous-dossier
A6 = """        date: dateDe(Object.values(d.z)[0][0]) || ""
      });
    }
  }
  ETAT.tunnel.fait = true;"""
B6 = """        date: dateDe(Object.values(d.z)[0][0]) || ""
      });
    }

    /* DEUXIEME PASSE - les lignes du tableau dont le fichier vit dans un SOUS-DOSSIER de zone.
       La boucle ci-dessus ne lit que la racine des trois zones : ces documents n'entraient donc
       ni dans le tunnel ni dans les compteurs (« resumes dus », « en attente de toi »), alors
       qu'ils sont declares au tableau. Une ligne du tableau = une ligne ici.
       Quand deux sous-dossiers portent le meme nom de fichier, on attribue les emplacements
       dans l'ordre d'apparition (rang), sans quoi les deux lignes montreraient le meme chemin.
       Ces documents ne portent AUCUN bouton d'action : le robot de promotion ne deplace que des
       fichiers poses a la racine d'une zone - pas de bouton mort. */
    const parNom = new Map();
    for (const n of arbres[depot]){
      if (n.type !== "blob") continue;
      const p = n.path.split("/");
      if (p.length <= 3 || p[0] !== agent || !ZONES.includes(p[1])) continue;
      const f = p[p.length - 1];
      if (!parNom.has(f)) parNom.set(f, []);
      parNom.get(f).push([p[1], n.path, n.size || 0]);
    }
    const rangs = new Map();
    for (const [fic, m] of metaListe(txtMeta)){
      if (!fic || plats.has(fic)) continue;
      const lieux = parNom.get(fic);
      if (!lieux) continue;
      const rg = rangs.get(fic) || 0; rangs.set(fic, rg + 1);
      const [zone, chemin, taille] = lieux[Math.min(rg, lieux.length - 1)];
      const ex = fic.match(/\\.([A-Za-z0-9]{1,6})$/);
      LIGNES.push({
        agent, depot, doc: m.doc || fic, sousDossier: chemin,
        z: {[zone]: [fic, ex ? ex[1].toLowerCase() : "texte", taille]},
        tags: m.tags && m.tags.length ? m.tags : [],
        statut: m.statut || "-", origine: m.origine || "-",
        resume: m.resume || "non lu",
        couvert: (m.savoir || "").split(/[;,]/).map(x => x.trim()).filter(Boolean)
                   .filter(f => savoirsPresents.has(f)),
        cat: (m.cat === "actualite" || /veille/i.test(m.origine || "")) ? "actu" : "fond",
        date: dateDe(fic) || ""
      });
    }
  }
  ETAT.tunnel.fait = true;"""
h = rempl(h, A6, B6)

# 5. aucun bouton pour ces documents : le robot ne sait pas les deplacer
A7 = """function actions(r){
  const zo = zonesOccupees(r);"""
B7 = """function actions(r){
  if (r.sousDossier)
    return '<span class="zoneac"><span></span><span class="lesboutons">'
      + '<span class="mut" title="Ce document vit dans un sous-dossier de zone : le robot de promotion ne deplace que les fichiers poses a la racine d\\'une zone.">-</span></span></span>';
  const zo = zonesOccupees(r);"""
h = rempl(h, A7, B7)

# 6. version
m = re.search(r"<!-- VERSION_CONSOLE: (\d+) -->", h)
assert m, "marqueur de version introuvable"
v = int(m.group(1))
h = rempl(h, "<!-- VERSION_CONSOLE: %d -->" % v, "<!-- VERSION_CONSOLE: %d -->" % (v + 1))
io.open(F, "w", encoding="utf-8").write(h)
print("ecrit, version %d -> %d" % (v, v + 1))
