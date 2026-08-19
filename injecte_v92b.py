#!/usr/bin/env python3
# Suite de v92, trois defauts vus par l'execution sur les donnees reelles :
# 1. deux documents dont le TITRE commence par « # » etaient jetes comme des commentaires ;
# 2. une ligne du tableau dont le nom de fichier existe aussi a la racine d'une zone etait
#    perdue (europe.md) : on ne saute que la PREMIERE ligne portant ce nom ;
# 3. « resumes dus » comptait aussi les fichiers presents mais absents du tableau : un
#    document non declare n'est pas un resume du.
import io

F = "index.html"
h = io.open(F, encoding="utf-8").read()

def rempl(h, a, b, n=1):
    c = h.count(a)
    assert c == n, "ANCRE (%d/%d) : %r" % (c, n, a[:80])
    return h.replace(a, b)

# 1. un commentaire n'a pas de tabulation ; un titre peut commencer par un croisillon
A1 = """function metaListe(txt){
  const out = [];
  if (!txt) return out;
  const lignes = txt.split("\\n").filter(l => l.trim() && !l.startsWith("#"));"""
B1 = """function metaListe(txt){
  const out = [];
  if (!txt) return out;
  /* Une ligne de commentaire commence par un croisillon ET ne porte aucune tabulation.
     Deux documents s'appellent « #AlloMelenchon du ... » : leur titre commence par un
     croisillon et ils etaient jetes comme des commentaires. */
  const lignes = txt.split("\\n").filter(l => l.trim() && !(l.startsWith("#") && !l.includes("\\t")));"""
h = rempl(h, A1, B1)

# 2. le rang se compte AVANT de sauter les noms deja vus a la racine
A2 = """      if (!fic || plats.has(fic)) continue;
      const lieux = parNom.get(fic);
      if (!lieux) continue;
      const rg = rangs.get(fic) || 0; rangs.set(fic, rg + 1);"""
B2 = """      if (!fic) continue;
      const rg = rangs.get(fic) || 0; rangs.set(fic, rg + 1);
      if (rg === 0 && plats.has(fic)) continue;   /* cette ligne-la est deja portee par la racine */
      const lieux = parNom.get(fic);
      if (!lieux) continue;"""
h = rempl(h, A2, B2)

A3 = """      const [zone, chemin, taille] = lieux[Math.min(rg, lieux.length - 1)];"""
B3 = """      const [zone, chemin, taille] = lieux[Math.min(plats.has(fic) ? rg - 1 : rg, lieux.length - 1)];"""
h = rempl(h, A3, B3)

# 3. les lignes disent si elles sont declarees au tableau
A4 = """        agent, depot, doc: d.doc, z: d.z,
        tags: m.tags && m.tags.length ? m.tags : [],"""
B4 = """        agent, depot, doc: d.doc, z: d.z, declare: !!d.meta,
        tags: m.tags && m.tags.length ? m.tags : [],"""
h = rempl(h, A4, B4)

A5 = """        agent, depot, doc: m.doc || fic, sousDossier: chemin,"""
B5 = """        agent, depot, doc: m.doc || fic, sousDossier: chemin, declare: true,"""
h = rempl(h, A5, B5)

# 4. « resumes dus » ne compte que les documents DECLARES au tableau
A6 = """    const dette = siens.filter(r => r.resume === "non lu").length;"""
B6 = """    /* Un resume du est une ligne DU TABLEAU sans resume. Un fichier present mais jamais
       declare au tableau n'est pas un resume du : c'est un document non declare. */
    const dette = siens.filter(r => r.declare && r.resume === "non lu").length;"""
h = rempl(h, A6, B6)

A7 = """  const nonLus = LIGNES.filter(r => r.resume === "non lu").length;"""
B7 = """  const nonLus = LIGNES.filter(r => r.declare && r.resume === "non lu").length;"""
h = rempl(h, A7, B7)

io.open(F, "w", encoding="utf-8").write(h)
print("ecrit")
