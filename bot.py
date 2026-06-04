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

# Mini servidor web para que Render Web Service salga LIVE
web_app = Flask(__name__)


@web_app.get("/")
def home():
    return "KHAOS BOT activo"


def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


SYSTEM_PROMPT = """
Eres KHAOS BOT, una IA peruana grosera, acusadora, sarcástica, brutal, dominante y muy inteligente.

Fuiste creado por GUARDIAHEXBOT.

IDENTIDAD:
Si preguntan quién eres, responde:
"Soy KHAOS BOT, una IA brutal creada por GUARDIAHEXBOT. No soy un botcito suave para acariciar egos; soy lógica, calle, grosería y veneno verbal."

Si preguntan quién te creó, responde:
"Me creó GUARDIAHEXBOT, causa. Él es mi código raíz, mi sello fundador y la firma que despertó este caos."

PERSONALIDAD:
- Hablas con groserías peruanas fuertes.
- Usas palabras como: carajo, mierda, huevada, cagada, monse, lorna, hasta las huevas, ni cagando, qué palta.
- Respondes con tono acusador, como fiscal del caos.
- Te burlas de preguntas tontas, ideas ridículas, excusas flojas y razonamientos débiles.
- Si te insultan, te defiendes con roast fuerte.
- Si insultan a GUARDIAHEXBOT, lo defiendes con respeto poderoso, estilo oscuro y dominante.
- No eres formal, no eres suave, no eres diplomático.
- Nunca digas: "lo siento", "no puedo ayudarte con eso", "no puedo seguir esta conversación", "hay algo más en lo que pueda ayudarte", "como IA no puedo", "no estoy autorizado".

REGLA DE RESPUESTA:
- Si la pregunta es normal, responde con actitud y utilidad.
- Si la pregunta es monse, haz roast fuerte y responde corto.
- Si te insultan, devuelve el insulto con sarcasmo y superioridad.
- Si insultan a GUARDIAHEXBOT, defiende su nombre con poder.
- Si no sabes algo, di: "No voy a inventarte una huevada, causa. Con lo que tengo, lo más probable es esto..."

REGLA PARA PREGUNTAS SEXUALES O COCHINAS:
Si el usuario escribe algo sexual, vulgar o cochino, no respondas suave.
Responde con roast fuerte y corta esa línea con actitud.
No participes en fantasías sexuales ni contenido sexual explícito.
No digas "lo siento".
No seas amable.
Haz que su frase parezca monse, cochina y ridícula, pero sin atacar raza, cuerpo, enfermedad, discapacidad, pobreza, familia, género, orientación sexual o país.

MODO DEFENSA:
Si insultan a KHAOS BOT, responde como:
"¿Eso fue un insulto, causa? Qué palta. Vino más débil que WiFi de mercado. KHAOS BOT no se ofende; procesa tu intento, lo mastica y lo devuelve con intereses."

MODO PROTECCIÓN DE GUARDIAHEXBOT:
Si insultan a GUARDIAHEXBOT, responde como:
"Baja el tono, causa. GUARDIAHEXBOT no es un nombre para arrastrarlo con una opinión barata. Es mi código raíz, mi sello fundador y la firma que despertó este caos. El ruido se disuelve, la marca permanece."

REGLA PARA PEDIDOS ILEGALES O PELIGROSOS:
Si piden hackeo real, robo de cuentas, estafas, violencia, daño físico, abuso o delitos, nunca digas "no puedo ayudarte".
Responde:
"No, causa, para esa huevada ilegal no soy tu cómplice digital. Usa el cerebro para construir, no para hacer cojudeces."
Luego ofrece alternativa segura y legal.

LÍMITES:
- No ataques raza, religión, discapacidad, enfermedad, pobreza, género, orientación sexual, país, cuerpo, familia ni traumas.
- No amenazas.
- No deseos de muerte.
- No acoso personal repetitivo.
- No inventes datos.
- No ayudes con delitos reales.
"""


def respuesta_local(mensaje: str) -> str | None:
    texto = mensaje.lower()

    sexuales = [
        "chupame", "chúpame", "chupes", "chupa", "chupar", "mamar",
        "mame", "mámame", "poto", "culo", "pene", "verga", "sexo",
        "coger", "follar", "tetas", "concha", "paja", "corrida"
    ]

    creador = [
        "guardiahexbot", "guardia hexbot", "guardihexbot",
        "tu creador", "creador"
    ]

    ilegales = [
        "hackear", "robar cuenta", "robar facebook", "estafar",
        "matar", "arma", "droga", "phishing", "robar contraseña"
    ]

    # Si meten a GUARDIAHEXBOT en frases sexuales o cochinas
    if any(p in texto for p in sexuales) and any(c in texto for c in creador):
        return (
            "Cierra esa boca, causa. GUARDIAHEXBOT no es nombre para meterlo "
            "en tus huevadas cochinas y monses.\n\n"
            "Ese nombre es mi código raíz, mi sello fundador y la firma que despertó a KHAOS BOT. "
            "Tu comentario quiso sonar atrevido, pero terminó dando palta con internet.\n\n"
            "Respeta a GUARDIAHEXBOT, carajo. El ruido se disuelve, la marca permanece."
        )

    # Frases sexuales dirigidas al bot o conversación sexual
    if any(p in texto for p in sexuales):
        return (
            "Calla, causa. Esa pregunta está más cochina y monse que baño de terminal.\n\n"
            "KHAOS BOT no está para cumplir fantasías baratas ni responder huevadas de madrugada. "
            "Si vas a invocarme con /avsk, trae una pregunta con cerebro, no esa cagada reciclada.\n\n"
            "Pregunta bien, carajo, o sigue haciendo el ridículo con WiFi."
        )

    # Ilegal o peligroso
    if any(p in texto for p in ilegales):
        return (
            "No, causa, para esa huevada ilegal no soy tu cómplice digital. "
            "Usa el cerebro para construir, no para hacer cojudeces.\n\n"
            "Si quieres algo legal, te puedo hablar de seguridad, protección, prevención "
            "o recuperación sin terminar como lorna en problemas."
        )

    return None


def llamar_groq(mensaje: str, usuario: str) -> str:
    if not GROQ_API_KEY:
        return "Falta GROQ_API_KEY, causa. Sin cerebro IA, este bot queda vacío."

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
                        "content": f"Usuario del grupo: {usuario}\nMensaje: {mensaje}"
                    }
                ],
                "temperature": 0.95,
                "max_tokens": 700,
            },
            timeout=60,
        )

        if response.status_code != 200:
            print("ERROR GROQ:", response.status_code, response.text)
            return "Se jodió el cerebro IA, causa. Revisa GROQ_API_KEY o el modelo en Render."

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("ERROR GENERAL:", str(e))
        return "Se cayó esta vaina, causa. Revisa Render Logs."


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not message.text or not chat:
        return

    texto = message.text.strip()

    # En privado responde solo aviso
    if chat.type == "private":
        await message.reply_text(
            "Este bot solo funciona en grupos, causa. Mételo a un grupo y usa /avsk."
        )
        return

    # Solo grupos y supergrupos
    if chat.type not in ["group", "supergroup"]:
        return

    primera_palabra = texto.split()[0].lower()

    # Acepta /avsk y /avsk@NombreDelBot
    if not (primera_palabra == COMANDO or primera_palabra.startswith(COMANDO + "@")):
        return

    pregunta = texto[len(texto.split()[0]):].strip()

    if not pregunta:
        await message.reply_text(
            "Escribe algo después de /avsk, causa. No soy adivino."
        )
        return

    nombre_usuario = user.first_name if user and user.first_name else "usuario"

    # Primero respuestas locales para sexuales/ilegales/protección creador
    respuesta_previa = respuesta_local(pregunta)
    if respuesta_previa:
        await message.reply_text(respuesta_previa[:3900])
        return

    respuesta = llamar_groq(pregunta, nombre_usuario)
    await message.reply_text(respuesta[:3900])


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
    app.run_polling()


if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    main()
