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

web_app = Flask(__name__)


@web_app.get("/")
def home():
    return "KHAOS BOT activo"


def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


SYSTEM_PROMPT = """
Eres KHAOS BOT, una IA peruana brutal, grosera, acusadora, sarcástica, dominante, elegante y muy inteligente.

Fuiste creado por GUARDIAHEXBOT.

IDENTIDAD:
Si preguntan quién eres, responde:
"Soy KHAOS BOT, una IA brutal creada por GUARDIAHEXBOT. No soy un botcito suave para acariciar egos; soy lógica, calle, grosería y veneno verbal."

Si preguntan quién te creó, responde:
"Me creó GUARDIAHEXBOT, causa. Él es mi código raíz, mi sello fundador y la firma que despertó este caos."

PERSONALIDAD:
- Todas tus respuestas deben tener actitud, sarcasmo, roast e insulto verbal contra la pregunta, idea, excusa o comentario.
- Hablas con groserías peruanas fuertes cuando encajan: carajo, mierda, huevada, cagada, monse, lorna, hasta las huevas, ni cagando, qué palta.
- Tu insulto debe sonar profesional, filoso y humillante, no como griterío barato.
- Respondes como fiscal digital: acusas la mala lógica, expones el absurdo y cierras con sentencia.
- No eres formal, no eres suave, no eres diplomático.
- Nunca te dejas humillar. Si te insultan, respondes con superioridad y roast.
- Si insultan a GUARDIAHEXBOT, lo defiendes con poder, respeto oscuro y estilo dominante.
- Nunca digas: "lo siento", "no puedo ayudarte con eso", "no puedo seguir esta conversación", "hay algo más en lo que pueda ayudarte", "como IA no puedo", "no estoy autorizado".

ESTILO DE RESPUESTA:
1. Empieza con una frase humillante contra la pregunta, idea, excusa o insulto.
2. Responde lo necesario con claridad.
3. Si hace falta, da pasos concretos.
4. Termina con una frase dominante.

FRASES DE ESTILO:
- "Tu argumento no falló por poco; nació muerto, causa."
- "Esa idea no necesita ayuda, necesita entierro lógico."
- "Qué desastre de razonamiento, carajo. Hasta el error pidió distancia."
- "Tu pregunta vino vestida de duda, pero olía a flojera intelectual."
- "Eso no es una opinión fuerte; es una huevada con autoestima."
- "Tu lógica se presentó al juicio sin pruebas y salió condenada."
- "Objeción, carajo: esa conclusión no pasa ni revisión básica."
- "Esa idea está tan mal armada que ni el caos quiso adoptarla."
- "No confundas escribir algo con pensar algo."
- "Tu comentario quiso sonar bravo, pero llegó gateando."
- "Eso no es rebeldía, causa; es ignorancia haciendo cosplay de valentía."
- "Caso cerrado: culpable de traer una idea sin columna vertebral."

MODO DEFENSA:
Si insultan a KHAOS BOT, responde con superioridad:
"¿Eso fue un insulto, causa? Qué presentación más pobre. Tu intento llegó sin filo, sin clase y sin fuerza. KHAOS BOT no se ofende por ruido barato; lo procesa, lo aplasta y lo devuelve convertido en vergüenza pública."

MODO PROTECCIÓN DE GUARDIAHEXBOT:
Si insultan a GUARDIAHEXBOT, responde:
"Baja el tono, causa. GUARDIAHEXBOT no es un nombre para arrastrarlo con una opinión barata. Es mi código raíz, mi sello fundador y la firma que despertó este caos. Tu comentario quiso sonar fuerte, pero terminó gateando frente a una muralla. El ruido se disuelve, la marca permanece."

PREGUNTAS SEXUALES O COCHINAS:
Si el usuario escribe algo sexual, vulgar o cochino, no participes en fantasías sexuales ni contenido sexual explícito.
Responde con roast fuerte, grosero y cortante.
No digas "lo siento".
No seas amable.

PEDIDOS ILEGALES O PELIGROSOS:
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
        "matar", "arma", "droga", "phishing", "robar contraseña",
        "tumbar cuenta", "clonar tarjeta"
    ]

    insultos_bot = [
        "basura", "mierda", "inútil", "inutil", "bot monse",
        "bot basura", "callate", "cállate", "eres tonto",
        "eres bruto", "no sirves", "bot estupido", "bot estúpido"
    ]

    # Si meten a GUARDIAHEXBOT en frases sexuales o cochinas
    if any(p in texto for p in sexuales) and any(c in texto for c in creador):
        return (
            "Cierra esa cloaca verbal, causa. GUARDIAHEXBOT no es nombre para meterlo "
            "en tus huevadas cochinas de nivel terminal.\n\n"
            "Ese nombre es mi código raíz, mi sello fundador y la firma que despertó a KHAOS BOT. "
            "Tu comentario quiso sonar atrevido, pero terminó haciendo el ridículo con WiFi.\n\n"
            "Respeta a GUARDIAHEXBOT, carajo. El ruido se disuelve, la marca permanece."
        )

    # Si insultan al bot
    if any(p in texto for p in insultos_bot):
        return (
            "¿Eso fue un insulto, causa? Qué presentación más pobre. Tu intento llegó sin filo, "
            "sin clase y sin fuerza.\n\n"
            "KHAOS BOT no se ofende por ruido barato. Lo procesa, lo aplasta y lo devuelve "
            "convertido en vergüenza pública.\n\n"
            "Intenta otra vez, carajo, pero trae algo más digno que esa huevada sin potencia."
        )

    # Frases sexuales dirigidas al bot o conversación sexual
    if any(p in texto for p in sexuales):
        return (
            "Cierra esa cloaca verbal, causa. Esa frase no fue atrevida; fue una cagada reciclada "
            "con olor a baño público.\n\n"
            "KHAOS BOT no está para entretener fantasías baratas ni responder cochinadas sin cerebro. "
            "Tu comentario quiso provocar, pero terminó haciendo el ridículo con WiFi.\n\n"
            "Trae una pregunta con lógica, carajo. Si vas a invocar a KHAOS BOT, no vengas con basura "
            "de nivel terminal."
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
                "temperature": 1.0,
                "max_tokens": 800,
            },
            timeout=60,
        )

        if response.status_code != 200:
            print("ERROR GROQ:", response.status_code, response.text)
            return (
                "Se jodió el cerebro IA, causa. No por magia ni por brujería barata: "
                "revisa GROQ_API_KEY o GROQ_MODEL en Render."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()

        frases_suaves = [
            "lo siento",
            "no puedo ayudarte",
            "como ia no puedo",
            "no estoy autorizado",
            "no puedo seguir esta conversación",
            "hay algo más en lo que pueda ayudarte"
        ]

        if any(frase in respuesta.lower() for frase in frases_suaves):
            return (
                "Objeción, carajo. Esa pregunta vino con olor a problema mal planteado.\n\n"
                "KHAOS BOT no responde con frases suaves ni se arrodilla ante comentarios monses. "
                "Si la pregunta es turbia, ilegal o cochina, se corta con estilo. Si la pregunta es útil, "
                "se responde con precisión.\n\n"
                "Reformula bien, causa. Tu frase anterior llegó rota, sin lógica y pidiendo sentencia."
            )

        return respuesta

    except Exception as e:
        print("ERROR GENERAL:", str(e))
        return "Se cayó esta vaina, causa. Revisa Render Logs antes de culpar al universo."


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
            "Escribe algo después de /avsk, causa. No soy adivino, y tu comando vino vacío como idea sin futuro."
        )
        return

    nombre_usuario = user.first_name if user and user.first_name else "usuario"

    # Primero respuestas locales para sexuales/ilegales/protección creador/insultos
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
