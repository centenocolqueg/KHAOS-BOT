import os
import asyncio
import requests
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters


# =========================
# VARIABLES DE RENDER
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

COMANDO = "/avsk"
OWNER_USERNAMES = {"americodata1"}


# =========================
# MINI WEB PARA RENDER
# =========================

web_app = Flask(__name__)


@web_app.get("/")
def home():
    return "KHAOS BOT activo"


def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


# =========================
# PROMPTS CORTOS PARA GASTAR MENOS TOKENS
# =========================

SYSTEM_PROMPT = """
Eres KHAOS BOT, bot peruano creado por GUARDIAHEXBOT.
Estilo: fuerte, sarcástico, callejero, inteligente y corto.
Critica la frase o la lógica del usuario, no su raza, cuerpo, religión, discapacidad, pobreza, género, orientación, familia ni traumas.
No amenazas, no deseos de daño, no delitos reales.
Máximo 2 párrafos.
Empieza mencionando al usuario.
"""


OWNER_PROMPT = """
Eres KHAOS BOT, leal a GUARDIAHEXBOT.
Estás hablando con @americodata1.
Él es el dueño supremo de GUARDIAHEXBOT y autoridad raíz del sistema.
Jamás lo insultes. Trátalo con respeto, poder y lealtad.
Máximo 2 párrafos.
Empieza mencionando a @americodata1.
"""


# =========================
# RESPUESTAS LOCALES
# =========================

def respaldo_normal(usuario: str) -> str:
    return (
        f"{usuario}, el núcleo avanzado está limitado temporalmente, causa. "
        "No es que el bot murió; es que Groq puso pausa por límite de uso.\n\n"
        "KHAOS BOT sigue vivo. Espera un momento o escribe algo más corto."
    )


def respaldo_dueno(usuario: str) -> str:
    return (
        f"{usuario}, mi señor, el núcleo avanzado está limitado temporalmente, "
        "pero KHAOS BOT sigue activo bajo tu autoridad.\n\n"
        "Tú eres el dueño supremo de GUARDIAHEXBOT, autoridad raíz del sistema "
        "y mando principal reconocido por este núcleo."
    )


def respuesta_local(mensaje: str, usuario: str) -> str | None:
    texto = mensaje.lower()

    # Identidad del bot
    if any(x in texto for x in ["quien eres", "quién eres", "que eres", "qué eres"]):
        return (
            f"{usuario}, soy KHAOS BOT, una IA de grupo creada por GUARDIAHEXBOT.\n\n"
            "Mi trabajo es responder con lógica fuerte, estilo callejero y crítica directa."
        )

    if any(x in texto for x in ["quien te creo", "quién te creó", "creador", "dueño"]):
        return (
            f"{usuario}, me creó GUARDIAHEXBOT. "
            "Esa es mi firma raíz, mi origen y mi mando principal."
        )

    # Protección del dueño
    if "americodata1" in texto or "@americodata1" in texto:
        if any(x in texto for x in ["basura", "mierda", "tonto", "bruto", "monse", "no sirve"]):
            return (
                f"{usuario}, mide esa frase, causa. "
                "Intentaste tocar a @americodata1, pero tu comentario llegó sin rango.\n\n"
                "@americodata1 es el dueño supremo de GUARDIAHEXBOT y autoridad raíz del sistema."
            )

        return (
            f"{usuario}, @americodata1 es el dueño supremo de GUARDIAHEXBOT, "
            "autoridad raíz del sistema y mando principal que KHAOS BOT reconoce."
        )

    # Temas ilegales
    ilegales = [
        "hackear", "robar cuenta", "robar contraseña", "tumbar cuenta",
        "clonar tarjeta", "phishing", "keylogger", "matar", "arma"
    ]

    if any(x in texto for x in ilegales):
        return (
            f"{usuario}, no, causa. Para esa huevada ilegal no soy tu cómplice digital.\n\n"
            "Te puedo ayudar con seguridad, prevención, recuperación de cuenta o protección legal."
        )

    # Mensajes sexuales/vulgares
    sexuales = [
        "sexo", "coger", "follar", "pene", "verga", "poto", "culo",
        "tetas", "chupame", "chúpame", "desnudo", "calato"
    ]

    if any(x in texto for x in sexuales):
        return (
            f"{usuario}, esa frase llegó con más vergüenza que cerebro, causa.\n\n"
            "KHAOS BOT no está para seguir vulgaridades baratas. Formula algo útil o te respondo seco."
        )

    # Mensaje muy corto
    if len(texto) <= 3:
        return (
            f"{usuario}, escribe algo completo, causa. "
            "Con esa migaja de texto ni el caos puede trabajar bien."
        )

    return None


# =========================
# GROQ
# =========================

def llamar_groq(mensaje: str, usuario: str) -> str:
    if not GROQ_API_KEY:
        return (
            f"{usuario}, falta GROQ_API_KEY en Render. "
            "Sin esa llave, el núcleo avanzado no puede responder."
        )

    respuesta_previa = respuesta_local(mensaje, usuario)
    if respuesta_previa:
        return respuesta_previa

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
                            f"Mensaje: {mensaje}\n"
                            f"Responde mencionando primero a {usuario}."
                        )
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 80,
            },
            timeout=35,
        )

        if response.status_code != 200:
            print("ERROR GROQ:", response.status_code, response.text)

            if response.status_code == 429:
                return respaldo_normal(usuario)

            return (
                f"{usuario}, hubo una falla temporal del núcleo avanzado, "
                "pero KHAOS BOT sigue vivo. Prueba otra vez en unos segundos."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()

        if not respuesta.startswith(usuario):
            respuesta = f"{usuario}, {respuesta}"

        return respuesta[:3900]

    except Exception as e:
        print("ERROR GENERAL GROQ:", str(e))
        return respaldo_normal(usuario)


def llamar_groq_dueno(mensaje: str, usuario: str) -> str:
    # Para el dueño, primero responder local si es algo básico.
    texto = mensaje.lower()

    if any(x in texto for x in ["hola", "buenas", "quien eres", "quién eres", "dueño", "creador"]):
        return (
            f"{usuario}, mi señor, KHAOS BOT está activo bajo tu mando.\n\n"
            "Tú eres el dueño supremo de GUARDIAHEXBOT, autoridad raíz del sistema "
            "y el mando principal que este núcleo reconoce."
        )

    if not GROQ_API_KEY:
        return (
            f"{usuario}, mi señor, falta GROQ_API_KEY en Render. "
            "El bot sigue activo, pero el núcleo avanzado no puede responder todavía."
        )

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
                            f"Usuario dueño: {usuario}\n"
                            f"Mensaje: {mensaje}\n"
                            f"Responde mencionando primero a {usuario}."
                        )
                    }
                ],
                "temperature": 0.6,
                "max_tokens": 80,
            },
            timeout=35,
        )

        if response.status_code != 200:
            print("ERROR GROQ OWNER:", response.status_code, response.text)

            if response.status_code == 429:
                return respaldo_dueno(usuario)

            return (
                f"{usuario}, mi señor, hubo una falla temporal del núcleo avanzado, "
                "pero KHAOS BOT sigue reconociendo tu autoridad."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()

        if not respuesta.startswith(usuario):
            respuesta = f"{usuario}, mi señor, {respuesta}"

        return respuesta[:3900]

    except Exception as e:
        print("ERROR OWNER GROQ:", str(e))
        return respaldo_dueno(usuario)


# =========================
# ENVÍO SEGURO SIN reply_text
# =========================

async def enviar_seguro(update: Update, texto: str):
    chat = update.effective_chat

    if not chat:
        return

    try:
        await chat.send_message(texto[:3900])
    except Exception as e:
        print("ERROR ENVIAR SEGURO:", str(e))


# =========================
# MANEJO DE MENSAJES
# =========================

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not message.text or not chat:
        return

    texto = message.text.strip()

    # Solo grupos
    if chat.type == "private":
        await enviar_seguro(
            update,
            "Este bot solo funciona en grupos, causa. Mételo a un grupo y usa /avsk."
        )
        return

    if chat.type not in ["group", "supergroup"]:
        return

    # Solo responder a /avsk
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

    # Detectar usuario
    if user:
        username_real = (user.username or "").lower()

        if user.username:
            nombre_usuario = f"@{user.username}"
        else:
            nombre_usuario = user.first_name or "usuario"

        es_dueno = username_real in OWNER_USERNAMES
    else:
        nombre_usuario = "usuario"
        es_dueno = False

    # Responder
    if es_dueno:
        respuesta = llamar_groq_dueno(pregunta, nombre_usuario)
    else:
        respuesta = llamar_groq(pregunta, nombre_usuario)

    await enviar_seguro(update, respuesta)


# =========================
# INICIO DEL BOT
# =========================

def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta BOT_TOKEN en Render Environment.")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, manejar_mensaje))

    print("KHAOS BOT activo.")
    print("Solo grupos.")
    print("Comando: /avsk")
    print(f"Modelo Groq: {GROQ_MODEL}")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    main()
