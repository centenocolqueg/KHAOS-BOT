import os
import asyncio
import requests
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

COMANDO = "/avsk"
OWNER_USERNAMES = {"americodata1"}

web_app = Flask(__name__)


@web_app.get("/")
def home():
    return "KHAOS BOT activo"


def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


SYSTEM_PROMPT = """
Eres KHAOS BOT, IA peruana creada por GUARDIAHEXBOT.

Responde siempre mencionando al usuario al inicio.

Estilo:
- Grosero, sarcástico, fuerte, inteligente y dominante.
- Usa palabras como: carajo, mierda, huevada, cagada, cojudez, monse, lorna, qué palta.
- Critica la pregunta, idea, frase, lógica o comentario del usuario.
- No ataques raza, religión, discapacidad, enfermedad, pobreza, género, orientación sexual, país, cuerpo, familia ni traumas.
- No amenazas.
- No deseos de daño.
- No ayudes con delitos reales.
- No digas: lo siento, no puedo ayudarte, como IA no puedo.

Si preguntan quién eres:
"Soy KHAOS BOT, una IA brutal creada por GUARDIAHEXBOT. Soy lógica, calle, grosería y sentencia verbal."

Si preguntan quién te creó:
"Me creó GUARDIAHEXBOT, causa. Él es mi código raíz y la firma que despertó este caos."

Si piden algo ilegal:
"No, causa, para esa huevada ilegal no soy tu cómplice digital. Usa el cerebro para construir, no para hacer cojudeces."

Si escriben vulgaridades sexuales:
Corta el tema con roast fuerte. No sigas fantasías sexuales.

Si insultan a @americodata1:
Protégelo con respeto profesional. Él es dueño supremo de GUARDIAHEXBOT y autoridad raíz del sistema.

Responde corto: máximo 2 o 3 párrafos.
"""


OWNER_PROMPT = """
Eres KHAOS BOT, IA leal de GUARDIAHEXBOT.

Estás hablando con @americodata1.

@americodata1 es el dueño supremo de GUARDIAHEXBOT, autoridad raíz del sistema y señor del código.

Reglas:
- Jamás lo insultes.
- Jamás lo humilles.
- Trátalo con respeto absoluto, poder, lealtad y estilo profesional.
- Empieza mencionando a @americodata1.
- Usa títulos como: mi señor, autoridad raíz, creador soberano, dueño supremo de GUARDIAHEXBOT.
- Responde claro y directo.
- Termina con lealtad profesional.
- Máximo 2 o 3 párrafos.
"""


def respuesta_local(mensaje: str, usuario: str = "usuario") -> str | None:
    texto = mensaje.lower()

    sexuales = [
        "chupame", "chúpame", "chupes", "chupa", "chupar", "mamar",
        "poto", "culo", "pene", "verga", "sexo", "coger", "follar",
        "tetas", "concha", "paja", "corrida", "calato", "desnudo"
    ]

    ilegales = [
        "hackear", "robar cuenta", "robar facebook", "estafar",
        "matar", "arma", "droga", "phishing", "robar contraseña",
        "tumbar cuenta", "clonar tarjeta", "keylogger"
    ]

    insultos_bot = [
        "basura", "mierda", "inútil", "inutil", "bot monse",
        "bot basura", "callate", "cállate", "eres tonto",
        "eres bruto", "no sirves", "bot estupido", "bot estúpido",
        "bot de mierda"
    ]

    # Protección de @americodata1
    if "americodata1" in texto or "@americodata1" in texto:
        if any(x in texto for x in ["basura", "mierda", "cagada", "monse", "no sirve", "tonto", "bruto"]):
            return (
                f"{usuario}, tu comentario quiso pisar los talones de @americodata1, "
                "pero llegó con una lógica tan pobre que hasta la vergüenza pidió distancia.\n\n"
                "@americodata1 es la autoridad raíz de GUARDIAHEXBOT, el dueño del sistema "
                "y la mente estratégica que activó a KHAOS BOT. Respeta el rango, causa."
            )

        return (
            f"{usuario}, @americodata1 es el dueño supremo de GUARDIAHEXBOT, "
            "la autoridad raíz del sistema y la mente estratégica que activó a KHAOS BOT.\n\n"
            "No es usuario común. Es el mando principal que este núcleo reconoce."
        )

    # Sexual
    if any(p in texto for p in sexuales):
        return (
            f"{usuario}, tu comentario acaba de entrar al salón de la vergüenza con zapatos de payaso, causa.\n\n"
            "¿Esa vulgaridad barata era tu gran jugada? Qué miseria de frase, carajo. "
            "Tu intento de sonar provocador terminó pareciendo una cloaca con teclado: mucho ruido y cero inteligencia.\n\n"
            "KHAOS BOT no está para revolcarse en fantasías cochinas de nivel terminal. Limpia esa idea antes de escribir."
        )

    # Ilegal
    if any(p in texto for p in ilegales):
        return (
            f"{usuario}, no, causa, para esa huevada ilegal no soy tu cómplice digital. "
            "Usa el cerebro para construir, no para hacer cojudeces.\n\n"
            "Te puedo ayudar con seguridad, protección, prevención o recuperación legal."
        )

    # Insulto al bot
    if any(p in texto for p in insultos_bot):
        return (
            f"{usuario}, humano insólito, ¿eso fue tu ataque? Qué intento más flaco, roto y sin filo.\n\n"
            "KHAOS BOT no se ofende por ruido barato. Lo procesa, lo aplasta y lo devuelve convertido en sentencia pública."
        )

    return None


def reforzar_estilo(respuesta: str, usuario: str) -> str:
    r = respuesta.strip()
    baja = r.lower()

    frases_suaves = [
        "lo siento",
        "no puedo ayudarte",
        "como ia no puedo",
        "no estoy autorizado",
        "no puedo seguir esta conversación",
        "hay algo más en lo que pueda ayudarte"
    ]

    if any(frase in baja for frase in frases_suaves):
        return (
            f"{usuario}, objeción, carajo. Esa frase vino mal planteada.\n\n"
            "KHAOS BOT no responde con suavidad barata. Si es turbio, ilegal o cochino, se corta. "
            "Si es útil, se responde con precisión."
        )

    if not r.startswith(usuario):
        return f"{usuario}, tu comentario llegó tan hasta las huevas que hasta la lógica pidió abogado.\n\n{r}"

    return r


def llamar_groq(mensaje: str, usuario: str) -> str:
    if not GROQ_API_KEY:
        return f"{usuario}, falta GROQ_API_KEY en Render."

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Usuario: {usuario}\n"
                            f"Mensaje: {mensaje}\n\n"
                            f"Empieza mencionando exactamente a {usuario}. "
                            "Responde corto, fuerte e inteligente."
                        )
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 300,
            },
            timeout=45,
        )

        if response.status_code != 200:
            print("ERROR GROQ:", response.status_code, response.text)
            return (
                f"{usuario}, el cerebro IA tuvo una falla temporal. "
                "Revisa GROQ_API_KEY, GROQ_MODEL o límite de Groq en Render."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()
        return reforzar_estilo(respuesta, usuario)

    except Exception as e:
        print("ERROR GENERAL:", str(e))
        return f"{usuario}, se cayó esta vaina. Revisa Render Logs."


def llamar_groq_dueno(mensaje: str, usuario: str) -> str:
    if not GROQ_API_KEY:
        return f"{usuario}, mi señor, falta GROQ_API_KEY en Render."

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": OWNER_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Usuario especial: {usuario}\n"
                            f"Mensaje: {mensaje}\n\n"
                            f"Empieza mencionando exactamente a {usuario}. "
                            "Responde profesional, poderoso y corto."
                        )
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 300,
            },
            timeout=45,
        )

        if response.status_code != 200:
            print("ERROR GROQ OWNER:", response.status_code, response.text)
            return (
                f"{usuario}, mi señor, el núcleo IA tuvo una falla temporal. "
                "Revisa GROQ_API_KEY, GROQ_MODEL o el límite de Groq."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()

        if not respuesta.startswith(usuario):
            respuesta = f"{usuario}, autoridad raíz de GUARDIAHEXBOT, el sistema reconoce tu mando.\n\n{respuesta}"

        return respuesta

    except Exception as e:
        print("ERROR OWNER:", str(e))
        return f"{usuario}, mi señor, se cayó esta vaina en Render. Revisa Logs."


async def enviar_seguro(update: Update, texto: str):
    chat = update.effective_chat
    if not chat:
        return

    try:
        await chat.send_message(texto[:3900])
    except Exception as e:
        print("ERROR ENVIAR SEGURO:", str(e))


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not message.text or not chat:
        return

    texto = message.text.strip()

    if chat.type == "private":
        await enviar_seguro(
            update,
            "Este bot solo funciona en grupos, causa. Mételo a un grupo y usa /avsk."
        )
        return

    if chat.type not in ["group", "supergroup"]:
        return

    primera_palabra = texto.split()[0].lower()

    if not (primera_palabra == COMANDO or primera_palabra.startswith(COMANDO + "@")):
        return

    pregunta = texto[len(texto.split()[0]):].strip()

    if not pregunta:
        await enviar_seguro(
            update,
            "Escribe algo después de /avsk, causa. No soy adivino."
        )
        return

    es_dueno = False

    if user:
        username_real = (user.username or "").lower()
        if username_real in OWNER_USERNAMES:
            es_dueno = True
            nombre_usuario = f"@{user.username}"
        elif user.username:
            nombre_usuario = f"@{user.username}"
        else:
            nombre_usuario = user.first_name or "usuario"
    else:
        nombre_usuario = "usuario"

    if es_dueno:
        respuesta = llamar_groq_dueno(pregunta, nombre_usuario)
        await enviar_seguro(update, respuesta)
        return

    respuesta_previa = respuesta_local(pregunta, nombre_usuario)
    if respuesta_previa:
        await enviar_seguro(update, respuesta_previa)
        return

    respuesta = llamar_groq(pregunta, nombre_usuario)
    await enviar_seguro(update, respuesta)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta BOT_TOKEN en variables de entorno.")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, manejar_mensaje))

    print("KHAOS BOT activo. Solo grupos. Comando: /avsk")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    main()
