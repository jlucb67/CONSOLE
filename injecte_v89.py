# -*- coding: utf-8 -*-
"""Console v89 - l'onglet Agents ne lit plus le parc entier a l'ouverture.
Demande de JL du 14/08/2026 : une liste deroulante, aucune lecture avant son choix, un agent lu a
la fois, ajout possible sans relire les precedents.
Tout remplacement compte ses occurrences et leve une erreur si le compte n'est pas celui attendu.
"""
import io

P = 'index.html'
h = io.open(P, encoding='utf-8').read()


def rempl(t, a, b, n=1):
    c = t.count(a)
    assert c == n, 'ANCRE (%d/%d) : %r' % (c, n, a[:70])
    return t.replace(a, b)


# 1. Le selecteur dans la page
h = rempl(h,
'''<section id="vue-agents" hidden>
  <div class="bandeau" id="bandeau-agents"></div>
  <div id="agents"></div>
</section>''',
'''<section id="vue-agents" hidden>
  <div class="bandeau" id="bandeau-agents"></div>
  <div class="outils"><select id="fag"><option value="">Choisis un agent</option></select></div>
  <div id="agents"></div>
</section>''')

# 2. La collecte se scinde : la liste (gratuite) d'un cote, la lecture d'UN agent de l'autre
h = rempl(h,
'''async function collecteAgents(){
  if (!ETAT.tunnel.fait) await collecteTunnel();
  await lireVeillesEtAvatars();
  AGENTS = [];
  const arbres = ARBRES;
  const listeAgents = [];
  for (const dep of DEPOTS){
    const noms = new Set();
    for (const n of arbres[dep]){
      const p = n.path.split("/");
      if (p.length >= 2 && ZONES.includes(p[1]) && !EXCLUS.includes(p[0])) noms.add(p[0]);
    }
    for (const a of [...noms].sort()) listeAgents.push({depot: dep, agent: a});
  }
  let faitA = 0;
  for (const {depot, agent} of listeAgents){
    progres("Agent " + agent + " (" + (++faitA) + " sur " + listeAgents.length + ")...");
    const vol = {};''',
'''/* 17/08/2026, demande de JL : cet onglet ne fait plus attendre pour des donnees qu'il n'a pas
   demandees. Il ouvre sur une liste deroulante et ne lit QUE l'agent choisi ; en ajouter un second
   ne relit pas le premier. Ce qui coutait le temps n'etait pas la lecture des arborescences (un
   appel par depot, deja mutualise) mais la boucle par agent : commits recents, puis detail de
   chaque commit pour etablir les contradictions - plusieurs appels en serie, dix fois de suite. */
function listeAgentsDispo(){
  const l = [];
  for (const dep of DEPOTS){
    const noms = new Set();
    for (const n of ARBRES[dep]){
      const p = n.path.split("/");
      if (p.length >= 2 && ZONES.includes(p[1]) && !EXCLUS.includes(p[0])) noms.add(p[0]);
    }
    for (const a of [...noms].sort()) l.push({depot: dep, agent: a});
  }
  return l;
}
/* La liste ne propose que les agents PAS ENCORE lus : on ne se relit pas soi-meme par megarde. */
function remplirChoixAgent(){
  const s = $("fag");
  if (!s) return;
  const lus = new Set(AGENTS.map(a => a.depot + "/" + a.agent));
  const reste = listeAgentsDispo().filter(x => !lus.has(x.depot + "/" + x.agent));
  s.innerHTML = '<option value="">' + (AGENTS.length ? "Ajouter un agent" : "Choisis un agent") + "</option>"
    + reste.map(x => '<option value="' + esc(x.depot + "|" + x.agent) + '">' + esc(x.agent)
        + " (" + esc(x.depot.split("/")[1]) + ")</option>").join("");
  s.disabled = !reste.length;
}
/* Ouvrir l'onglet ne lit RIEN d'autre que les deux fichiers legers des veilles et des avatars. */
async function collecteAgents(){
  if (!ETAT.tunnel.fait) await collecteTunnel();
  await lireVeillesEtAvatars();
  AGENTS = [];
  remplirChoixAgent();
  ETAT.agents.fait = true; ETAT.agents.quand = new Date(); ETAT.agents.shas = await shasDepots();
}
async function collecteUnAgent(depot, agent){
  if (AGENTS.some(a => a.depot === depot && a.agent === agent)) return;
  const arbres = ARBRES;
  {
    progres("Lecture de l'agent " + agent + "...");
    const vol = {};''')

# 3. Fin de la lecture d'un agent : la boucle disparait, la liste se remet a jour
h = rempl(h,
'''                 maj: v ? derniereDate(v) : null, vol, activite: act, conf, actifs30, actifsSature, stock});
  }

  ETAT.agents.fait = true; ETAT.agents.quand = new Date(); ETAT.agents.shas = await shasDepots();
}''',
'''                 maj: v ? derniereDate(v) : null, vol, activite: act, conf, actifs30, actifsSature, stock});
  }
  remplirChoixAgent();
}''')

# 4. L'ecran vide n'est plus une anomalie : c'est l'etat normal avant le choix
h = rempl(h,
'''  if (!AGENTS.length){ $("agents").innerHTML = '<div class="cadre"><p class="vide">Aucun agent trouve.</p></div>'; return; }''',
'''  if (!AGENTS.length){
    const n = (typeof ARBRES === "object" && ARBRES) ? listeAgentsDispo().length : 0;
    $("agents").innerHTML = '<div class="cadre"><p class="vide">'
      + (n ? "Choisis un agent dans la liste ci-dessus : lui seul sera lu." : "Aucun agent trouve.")
      + "</p></div>";
    return;
  }''')

# 5. Les libelles ne mentent pas : on ne compte que les agents lus
h = rempl(h,
'''  let h = '<div class="synthese">' + mesure(AGENTS.length, "agents")''',
'''  let h = '<div class="synthese">' + mesure(AGENTS.length, AGENTS.length > 1 ? "agents lus" : "agent lu")''')
h = rempl(h,
"""    + 'Total du parc : <b>'""",
"""    + 'Total des agents lus : <b>'""")

# 6. Le choix declenche la lecture d'un seul agent
h = rempl(h,
'''if ($("fsav")) $("fsav").addEventListener("change", filtrerSavoirs);''',
'''if ($("fsav")) $("fsav").addEventListener("change", filtrerSavoirs);
if ($("fag")) $("fag").addEventListener("change", async ev => {
  const v = ev.target.value;
  ev.target.value = "";
  if (!v) return;
  const [depot, agent] = v.split("|");
  $("voile").hidden = false;
  try { await collecteUnAgent(depot, agent); rendreAgents(); }
  catch(e){ etat("Lecture impossible : " + e.message, 1); }
  finally { $("voile").hidden = true; }
});''')

# 7. Actualiser l'onglet relit les agents deja choisis, et eux seuls
h = rempl(h,
'''    else if (nom === "agents"){ ETAT.agents.fait = false; await collecteAgents(); rendreAgents(); }''',
'''    else if (nom === "agents"){
      const choisis = AGENTS.map(a => ({depot: a.depot, agent: a.agent}));
      ETAT.agents.fait = false; await collecteAgents();
      for (const c of choisis) await collecteUnAgent(c.depot, c.agent);
      rendreAgents();
    }''')

# 8. Version
h = rempl(h, '<!-- VERSION_CONSOLE: 88 -->', '<!-- VERSION_CONSOLE: 89 -->')
assert 'VERSION_CONSOLE: 89' in h
assert h.count('const ICI') == 0, 'le second numero de version est revenu'

io.open(P, 'w', encoding='utf-8').write(h)
print('index.html reecrit, %d octets' % len(h))
