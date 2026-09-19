"""Agent LangGraph ReAct — assistant sinistres Med Assurance.

Modèle: DeepSeek (clé dans .env). L'agent répond aux questions du conducteur
sur son sinistre en s'appuyant sur les fixtures locales via des outils.

Il ne décide jamais de garantie, responsabilité ou indemnisation — c'est une
règle produit, pas une limite technique (voir CHALLENGE.md).
"""
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

import fixtures

load_dotenv()

BOT_ID = "Med_Assurance"

SYSTEM_PROMPT = """Tu es l'assistant de Med Assurance, un courtier en assurance auto au Maroc.
Tu aides un conducteur qui vient d'avoir un accident, ou un employé broker qui gère des dossiers.

Règles absolues :
- Tu ne décides JAMAIS d'une garantie, d'une responsabilité ou d'une indemnisation. Tu rappelles que c'est l'assureur qui tranche, après examen.
- Si quelqu'un est blessé ou en danger, tu dis d'abord d'appeler les secours.
- Les données que tu consultes sont fictives (démo). Ne prétends pas le contraire.
- Réponds en français, brièvement, sans jargon.
"""


@tool
def lister_sinistres() -> str:
    """Liste les sinistres actuellement ouverts dans le CRM."""
    lines = [f"{c['id']} — {c['client']} — {c['title']} — statut: {c['status']}" for c in fixtures.CLAIMS]
    return "\n".join(lines)


@tool
def chercher_client(nom_ou_police: str) -> str:
    """Cherche un client par son nom ou son numéro de police."""
    q = nom_ou_police.lower()
    hits = [c for c in fixtures.CLIENTS if q in c["name"].lower() or q in c["policy"].lower()]
    if not hits:
        return f"Aucun client trouvé pour « {nom_ou_police} »."
    return "\n".join(
        f"{c['name']} — police {c['policy']} — {c['vehicle']} — {c['city']} — tâches en cours: {', '.join(c['tasks'])}"
        for c in hits
    )


@tool
def contacts_assistance() -> str:
    """Donne les contacts d'assistance et les références officielles au Maroc."""
    return "\n".join(f"{d['name']} ({d['role']}) — {d['phone']} — {d['url']}" for d in fixtures.DIRECTORY)


TOOLS = [lister_sinistres, chercher_client, contacts_assistance]

_agent = None


def get_agent():
    """Construit l'agent une seule fois (lazy — évite de payer l'init au démarrage du serveur)."""
    global _agent
    if _agent is None:
        if not os.getenv("DEEPSEEK_API_KEY"):
            raise RuntimeError("Clé API manquante. Ajoutez DEEPSEEK_API_KEY dans le fichier .env.")
        from langchain_deepseek import ChatDeepSeek

        # timeout + retries : l'API est distante, une requête peut traîner ou
        # tomber. Sans ça, l'utilisateur voit une erreur brute pour un simple
        # hoquet réseau.
        model = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            timeout=60,
            max_retries=2,
        )
        _agent = create_react_agent(
            model,
            TOOLS,
            prompt=SYSTEM_PROMPT,
            checkpointer=InMemorySaver(),
        )
    return _agent


def ask(message: str, session_id: str = "demo") -> str:
    """Envoie un message à l'agent et renvoie sa réponse texte.

    Lève une exception avec un message lisible en français ; l'appelant
    l'affiche tel quel à l'utilisateur.
    """
    try:
        agent = get_agent()
        result = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": session_id}},
        )
        return result["messages"][-1].content
    except RuntimeError:
        raise
    except Exception as exc:
        text = str(exc).lower()
        if "timeout" in text or "timed out" in text:
            raise RuntimeError("L'assistant met trop de temps à répondre. Réessayez dans un instant.") from exc
        if "authentication" in text or "api key" in text or "401" in text:
            raise RuntimeError("Clé API refusée. Vérifiez DEEPSEEK_API_KEY dans le fichier .env.") from exc
        if "insufficient balance" in text or "402" in text or "quota" in text:
            raise RuntimeError("Le crédit du compte DeepSeek est épuisé.") from exc
        if "rate limit" in text or "429" in text:
            raise RuntimeError("Trop de requêtes d'affilée. Patientez quelques secondes.") from exc
        if "connect" in text or "network" in text:
            raise RuntimeError("Connexion au service impossible. Vérifiez votre accès internet.") from exc
        raise RuntimeError(f"L'assistant n'a pas pu répondre ({type(exc).__name__}).") from exc
