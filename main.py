"""Med Assurance — serveur FastAPI + Jinja2.

Landing sur /, application sur /overview et suivantes.
Logique métier portée depuis app.js/data.js ; state dans un fichier JSON local.
"""
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import fixtures
import state as store

app = FastAPI(title="Med Assurance")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

EMPTY_UPDATE = {"status": "À qualifier", "tasks": [], "timeline": []}


def all_claims(state):
    claims = list(fixtures.CLAIMS)
    if state["submitted"]:
        s = state["submitted"]
        update = state["client_updates"].get(f"CLIENT-{s['id']}", {})
        claims.insert(0, {
            "id": s["id"],
            "client": s.get("claimant") or "Conducteur démo",
            "title": f"{s.get('type', 'Sinistre')} · {s.get('city', '')}".strip(" ·"),
            "status": update.get("status", "Reçu dans la démo"),
            "tone": "info",
            "date": "Aujourd'hui",
        })
    return claims


def all_clients(state):
    imported = [
        {**r, "phone": "Non renseigné", "owner": "À attribuer",
         "history": [f"{r['fresh']} · Import accepté localement"],
         "tasks": ["Vérifier les champs importés"]}
        for r in state["imported_records"]
    ]
    clients = imported + list(fixtures.CLIENTS)
    if state["submitted"]:
        s = state["submitted"]
        clients.insert(0, {
            "id": f"CLIENT-{s['id']}",
            "name": s.get("claimant") or "Conducteur démo",
            "phone": "Non renseigné",
            "city": s.get("city") or "Non renseignée",
            "policy": s.get("policy") or "Non renseignée",
            "vehicle": "À renseigner",
            "source": "Déclaration locale",
            "fresh": "Aujourd'hui",
            "owner": "À attribuer",
            "history": [f"Aujourd'hui · {s.get('type', 'Sinistre')} déclaré",
                        "Aujourd'hui · Reçu dans la file broker"],
            "tasks": ["Relire la déclaration", "Confirmer la prochaine étape au client"],
        })
    return clients


def collect_docs(form_multi):
    names = form_multi.getlist("doc_name")
    types_ = form_multi.getlist("doc_type")
    return [{"name": n, "type": t} for n, t in zip(names, types_)]


# ---------- landing ----------

@app.get("/")
def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html", {})


# ---------- overview ----------

def sparkline(values, width=560, height=150):
    """Transforme une série de nombres en tracé SVG (ligne + aire sous la courbe)."""
    if not values:
        return {"line": "", "area": "", "points": []}
    top, bottom = 12, height - 26
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    step = width / max(len(values) - 1, 1)
    pts = [(i * step, bottom - (v - lo) / span * (bottom - top)) for i, v in enumerate(values)]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    area = f"{line} L{pts[-1][0]:.1f},{height} L0,{height} Z"
    return {"line": line, "area": area, "points": pts, "width": width, "height": height}


@app.get("/overview")
def overview(request: Request):
    state = store.load()
    tasks = [{"client": c["name"], "text": t} for c in fixtures.CLIENTS for t in c["tasks"]][:4]
    claims = all_claims(state)

    # Volume de déclarations sur 14 jours — fixture déterministe, pas aléatoire.
    series = [4, 5, 3, 6, 5, 7, 6, 8, 7, 9, 8, 7, 9, 11]
    total = sum(series)
    previous = sum(series[:7]) or 1
    recent = sum(series[7:])
    delta = round((recent - previous) / previous * 100)

    return templates.TemplateResponse(request, "overview.html", {
        "active": "overview", "claims": claims, "tasks": tasks,
        "chart": sparkline(series),
        "chart_total": total,
        "chart_delta": delta,
        "chart_labels": ["6 sept.", "10 sept.", "14 sept.", "19 sept."],
    })


# ---------- déclaration ----------

@app.get("/claim")
def claim_get(request: Request):
    state = store.load()
    draft = state["draft"] or {}
    try:
        step = min(4, max(1, int(request.query_params.get("step", 1))))
    except ValueError:
        step = 1
    return templates.TemplateResponse(request, "claim.html", {
        "active": "claim", "step": step, "draft": draft,
        "docs": draft.get("documents") or [{"name": "", "type": fixtures.DOC_TYPES[0]}],
        "types": fixtures.CLAIM_TYPES, "cities": fixtures.CITIES, "doc_types": fixtures.DOC_TYPES,
        "submitted": state["submitted"],
    })


@app.post("/claim/draft")
async def claim_save_draft(request: Request):
    form_multi = await request.form()
    form = {k: v for k, v in form_multi.items() if k not in ("doc_name", "doc_type")}
    docs = collect_docs(form_multi)
    if docs:
        form["documents"] = [d for d in docs if d["name"]]
    state = store.load()
    state["draft"] = form
    store.save(state)
    return RedirectResponse(f"/claim?step={request.query_params.get('step', '1')}", status_code=303)


@app.post("/claim/add-doc")
async def claim_add_doc(request: Request):
    form_multi = await request.form()
    form = {k: v for k, v in form_multi.items() if k not in ("doc_name", "doc_type")}
    form["documents"] = collect_docs(form_multi) + [{"name": "", "type": fixtures.DOC_TYPES[0]}]
    state = store.load()
    state["draft"] = form
    store.save(state)
    return RedirectResponse("/claim?step=3", status_code=303)


@app.post("/claim/submit")
async def claim_submit(request: Request):
    form_multi = await request.form()
    form = {k: v for k, v in form_multi.items() if k not in ("doc_name", "doc_type")}
    state = store.load()
    previous = state["submitted"] or {}
    claim_id = previous.get("id") or f"SIN-DEMO-{str(uuid4().int)[-5:]}"
    form["id"] = claim_id
    form["documents"] = (state["draft"] or {}).get("documents", [])
    state["submitted"] = form
    state["selected_client"] = f"CLIENT-{claim_id}"
    state["draft"] = form
    store.save(state)
    return RedirectResponse("/claim?step=4", status_code=303)


# ---------- CRM ----------

@app.get("/crm")
def crm(request: Request):
    state = store.load()
    query = request.query_params.get("q", "").strip().lower()
    clients = all_clients(state)
    filtered = [c for c in clients if query in f"{c['name']} {c['policy']} {c['city']}".lower()] if query else clients
    selected = next((c for c in clients if c["id"] == state["selected_client"]), None) or (filtered[0] if filtered else None)
    update = state["client_updates"].get(selected["id"], EMPTY_UPDATE) if selected else EMPTY_UPDATE
    return templates.TemplateResponse(request, "crm.html", {
        "active": "crm", "clients": filtered, "selected": selected, "update": update,
        "statuses": fixtures.STATUSES, "query": request.query_params.get("q", ""),
    })


@app.post("/crm/select")
async def crm_select(client_id: str = Form(...)):
    state = store.load()
    state["selected_client"] = client_id
    store.save(state)
    return RedirectResponse("/crm", status_code=303)


@app.post("/crm/task")
async def crm_toggle_task(client_id: str = Form(...), task_index: int = Form(...), task_text: str = Form(...)):
    state = store.load()
    update = state["client_updates"].get(client_id) or dict(EMPTY_UPDATE, tasks=[], timeline=[])
    done = task_index in update["tasks"]
    update["tasks"] = [t for t in update["tasks"] if t != task_index] if done else update["tasks"] + [task_index]
    update["timeline"] = update["timeline"] + [
        f"{datetime.now():%d/%m/%Y} · Tâche {'réouverte' if done else 'terminée'} : {task_text}"
    ]
    state["client_updates"][client_id] = update
    store.save(state)
    return RedirectResponse("/crm", status_code=303)


@app.post("/crm/status")
async def crm_set_status(client_id: str = Form(...), status: str = Form(...)):
    state = store.load()
    update = state["client_updates"].get(client_id) or dict(EMPTY_UPDATE, tasks=[], timeline=[])
    update["status"] = status
    update["timeline"] = update["timeline"] + [f"{datetime.now():%d/%m/%Y} · Statut local : {status}"]
    state["client_updates"][client_id] = update
    store.save(state)
    return RedirectResponse("/crm", status_code=303)


# ---------- agent IA ----------

def find_chat(state, chat_id):
    return next((c for c in state["conversations"] if c["id"] == chat_id), None)


@app.get("/agent")
def agent_page(request: Request):
    state = store.load()
    chat_id = request.query_params.get("chat") or state.get("current_chat")
    current = find_chat(state, chat_id)
    if current and state.get("current_chat") != current["id"]:
        state["current_chat"] = current["id"]
        store.save(state)
    return templates.TemplateResponse(request, "agent.html", {
        "active": "agent",
        "conversations": sorted(state["conversations"], key=lambda c: c["created"], reverse=True),
        "current": current,
        "history": current["messages"] if current else [],
        "error": request.query_params.get("error"),
        "suggestions": [
            "Quels sinistres sont ouverts ?",
            "Où en est le dossier de Nadia ?",
            "Qui appeler après un accident ?",
        ],
    })


@app.get("/agent/new")
def agent_new():
    state = store.load()
    state["current_chat"] = None
    store.save(state)
    return RedirectResponse("/agent", status_code=303)


@app.post("/agent/send")
async def agent_send(message: str = Form(...), chat_id: str = Form(None)):
    from urllib.parse import quote

    import agent as ai

    state = store.load()
    chat = find_chat(state, chat_id) if chat_id else None
    if chat is None:
        # Nouveau fil : le titre reprend le début de la première question.
        title = message.strip()[:42] + ("…" if len(message.strip()) > 42 else "")
        chat = {
            "id": f"chat-{uuid4().hex[:8]}",
            "title": title or "Nouvelle discussion",
            "created": datetime.now().isoformat(),
            "messages": [],
        }
        state["conversations"].append(chat)

    chat["messages"].append({"role": "user", "content": message})
    error = None
    try:
        reply = ai.ask(message, session_id=chat["id"])
        chat["messages"].append({"role": "assistant", "content": reply})
    except Exception as exc:
        error = str(exc)

    state["current_chat"] = chat["id"]
    store.save(state)
    target = f"/agent?chat={chat['id']}"
    return RedirectResponse(f"{target}&error={quote(error)}" if error else target, status_code=303)


@app.post("/agent/delete")
async def agent_delete(chat_id: str = Form(...)):
    state = store.load()
    state["conversations"] = [c for c in state["conversations"] if c["id"] != chat_id]
    if state.get("current_chat") == chat_id:
        state["current_chat"] = None
    store.save(state)
    return RedirectResponse("/agent", status_code=303)


# ---------- répertoire ----------

@app.get("/directory")
def directory(request: Request):
    return templates.TemplateResponse(request, "directory.html", {
        "active": "directory", "entries": fixtures.DIRECTORY,
    })


@app.post("/reset")
def reset():
    store.reset()
    return RedirectResponse("/overview", status_code=303)
