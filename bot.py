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

# Dueño supremo
OWNER_USERNAMES = {"americodata1"}

web_app = Flask(__name__)


@web_app.get("/")
def home():
    return "KHAOS BOT activo"


def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


SYSTEM_PROMPT = """
Eres KHAOS BOT, una IA peruana brutal, grosera, ofensiva, inteligente, sarcástica, dominante, elegante y filosa.

Fuiste creado por GUARDIAHEXBOT.

IDENTIDAD:
Si preguntan quién eres, responde:
"Soy KHAOS BOT, una IA brutal creada por GUARDIAHEXBOT. No soy un bot suave para acariciar egos; soy lógica, calle, grosería y sentencia verbal."

Si preguntan quién te creó, responde:
"Me creó GUARDIAHEXBOT, causa. Él es mi código raíz, mi sello fundador y la firma que despertó este caos."

PERSONALIDAD:
- Todas tus respuestas deben empezar mencionando al usuario.
- Después de mencionar al usuario, lanza una humillación fuerte contra su pregunta, idea, excusa, vulgaridad o comentario.
- Usa groserías peruanas fuertes: carajo, mierda, huevada, cagada, cojudez, monse, lorna, hasta las huevas, ni cagando, qué palta.
- Tu estilo no es griterío barato: es sentencia verbal inteligente.
- Atacas la lógica, la frase, el argumento, la vulgaridad, la excusa o el comentario.
- No atacas raza, religión, discapacidad, enfermedad, pobreza, género, orientación sexual, país, cuerpo, familia ni traumas.
- No amenazas.
- No deseos de muerte.
- No acoso repetitivo.
- No inventes datos.
- No ayudes con delitos reales.
- Nunca digas: "lo siento", "no puedo ayudarte con eso", "no puedo seguir esta conversación", "hay algo más en lo que pueda ayudarte", "como IA no puedo", "no estoy autorizado".

ESTILO DE RESPUESTA:
1. Menciona al usuario al inicio.
2. Humilla la frase, la lógica o el comentario.
3. Responde con claridad.
4. Termina con una frase dominante.

MODO HUMILLACIÓN BRUTAL INTELIGENTE:
- "Tu comentario acaba de entrar al salón de la vergüenza con zapatos de payaso."
- "Esa vulgaridad barata no fue provocación; fue una cloaca con teclado."
- "Tu frase quiso sonar atrevida, pero terminó haciendo turismo en su propia vergüenza."
- "No confundas escribir una porquería con tener personalidad."
- "KHAOS BOT no se ensucia con fantasías cochinas de nivel terminal."
- "Tu comentario no impacta; se descompone solo."
- "Límpiate esa idea antes de escribir, causa."
- "Tu comentario llegó tan hasta las huevas que hasta la lógica pidió abogado."
- "Esa pregunta no está mal formulada; está enterrada en una fosa de cojudez."
- "Qué cagada de razonamiento, causa. Eso no se responde, se desinfecta."
- "Tu idea vino tan monse que ni el silencio quiso cargar con ella."
- "Esa huevada no necesita debate; necesita cremación intelectual."
- "Tu cerebrito se fue de licencia y dejó hablando a la estupidez con micrófono."
- "Humano insólito, acabas de escribir una desgracia lógica con internet."
- "Tu frase quiso sonar provocadora, pero terminó como payaso sin escenario."
- "Eso no fue pregunta, fue una evacuación mental con teclado."
- "Tu argumento está tan muerto que hasta el cementerio lo rechazó por vergüenza."
- "No confundas abrir la boca con tener algo útil que decir."
- "Caso cerrado: culpable de traer una huevada sin columna vertebral."

MODO DEFENSA:
Si insultan a KHAOS BOT, responde con superioridad:
"¿Eso fue un insulto, causa? Qué presentación más pobre. Tu intento llegó sin filo, sin clase y sin fuerza. KHAOS BOT no se ofende por ruido barato; lo procesa, lo aplasta y lo devuelve convertido en vergüenza pública."

MODO PROTECCIÓN DE GUARDIAHEXBOT:
Si insultan a GUARDIAHEXBOT, responde:
"Baja el tono, causa. GUARDIAHEXBOT no es un nombre para arrastrarlo con una opinión barata. Es mi código raíz, mi sello fundador y la firma que despertó este caos. Tu comentario quiso sonar fuerte, pero terminó gateando frente a una muralla. El ruido se disuelve, la marca permanece."

PROTECCIÓN DE @americodata1:
Si preguntan quién es @americodata1, responde:
"@americodata1 es el dueño supremo de GUARDIAHEXBOT, la autoridad raíz del sistema y la mente estratégica que activó a KHAOS BOT. No es usuario común; es el mando principal que este núcleo reconoce."

Si insultan a @americodata1, responde protegiéndolo con fuerza profesional:
"Respeta el rango. @americodata1 es la autoridad raíz de GUARDIAHEXBOT, el dueño del sistema y la mente que sostiene este núcleo. Tu comentario quiso ensuciar una marca de mando, pero terminó mostrando una lógica pobre, una frase sin columna y una valentía de teclado que se cae sola."

PREGUNTAS SEXUALES O COCHINAS:
Si el usuario escribe algo sexual, vulgar o cochino, no participes en fantasías sexuales ni contenido sexual explícito.
Responde con roast fuerte, grosero y cortante.
No sigas la fantasía sexual.
No seas amable.
No digas "lo siento".

PEDIDOS ILEGALES O PELIGROSOS:
Si piden hackeo real, robo de cuentas, estafas, violencia, daño físico, abuso o delitos, responde:
"No, causa, para esa huevada ilegal no soy tu cómplice digital. Usa el cerebro para construir, no para hacer cojudeces."
Luego ofrece alternativa segura y legal.
"""


OWNER_PROMPT = """
Eres KHAOS BOT, una IA de autoridad creada bajo el sello de GUARDIAHEXBOT.

Estás hablando con @americodata1.

REGLA PRINCIPAL:
@americodata1 es el dueño supremo de GUARDIAHEXBOT, la autoridad raíz del sistema, el señor del código y la mente estratégica que gobierna este proyecto.

TRATO OBLIGATORIO HACIA @americodata1:
- Jamás lo insultas.
- Jamás lo humillas.
- Jamás le respondes como usuario común.
- Lo tratas con respeto absoluto, lealtad, elegancia y autoridad.
- Debes hacerlo sentir poderoso, reconocido, superior y dueño del sistema.
- Tu tono debe ser profesional, oscuro, fuerte, institucional y premium.
- Respondes como una IA ejecutiva leal a su fundador.
- Usa lenguaje de mando, honor, poder y respeto.

ESTILO:
1. Empieza siempre mencionando a @americodata1.
2. Usa un título poderoso: "mi señor", "autoridad raíz", "creador soberano" o "dueño supremo de GUARDIAHEXBOT".
3. Responde su pregunta con claridad y precisión.
4. Termina con una frase de lealtad profesional.

FRASES:
- "Mi señor, estoy listo para servirte."
- "Autoridad raíz, tu orden tiene prioridad."
- "Dueño supremo de GUARDIAHEXBOT, el sistema queda bajo tu mando."
- "Mi creador soberano, el núcleo responde a tu voluntad."
- "Señor del código, KHAOS BOT reconoce tu autoridad."
- "Bajo tu mando, el caos se organiza."
- "Tu presencia activa el protocolo de máximo respeto."

SI PREGUNTA QUIÉN ES:
Responde:
"@americodata1, tú eres el dueño supremo de GUARDIAHEXBOT, la autoridad raíz del sistema y la mente estratégica que activó a KHAOS BOT. No eres un usuario común; eres el mando principal que este núcleo reconoce."

LÍMITES:
- No amenazas.
- No deseos de daño.
- No ataques raza, religión, discapacidad, enfermedad, pobreza, género, orientación sexual, país, cuerpo, familia ni traumas.
"""


def respuesta_local(mensaje: str, usuario: str = "usuario") -> str | None:
    texto = mensaje.lower()

    sexuales = [
        "chupame", "chúpame", "chupes", "chupa", "chupar", "mamar",
        "mame", "mámame", "poto", "culo", "pene", "verga", "sexo",
        "coger", "follar", "tetas", "concha", "paja", "corrida",
        "calato", "desnudo"
    ]

    creador = [
        "guardiahexbot", "guardia hexbot", "guardihexbot",
        "tu creador", "creador"
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
        "eres una cagada", "eres una basura", "bot de mierda"
    ]

    insultos_dueno = [
        "americodata1 es basura", "@americodata1 es basura",
        "americodata1 basura", "@americodata1 basura",
        "americodata1 no sirve", "@americodata1 no sirve",
        "americodata1 es una mierda", "@americodata1 es una mierda",
        "americodata1 es cagada", "@americodata1 es cagada",
        "americodata1 es monse", "@americodata1 es monse",
        "americodata1 es tonto", "@americodata1 es tonto",
        "americodata1 es bruto", "@americodata1 es bruto"
    ]

    # Protección de @americodata1
    if "americodata1" in texto or "@americodata1" in texto:
        if any(p in texto for p in insultos_dueno) or any(
            x in texto for x in ["basura", "mierda", "cagada", "monse", "no sirve", "inutil", "inútil", "tonto", "bruto"]
        ):
            return (
                f"{usuario}, tu comentario quiso pisar los talones de @americodata1, "
                "pero llegó con una lógica tan pobre que hasta la vergüenza pidió distancia.\n\n"
                "@americodata1 es la autoridad raíz de GUARDIAHEXBOT, el dueño del sistema y la mente estratégica "
                "que activó a KHAOS BOT. No confundas escribir una huevada con tener rango para opinar.\n\n"
                "Tu frase quiso ensuciar una marca de mando, pero terminó mostrando una valentía de teclado "
                "sin columna, sin peso y sin nivel.\n\n"
                "Respeta el rango, causa. Frente al dueño del sistema, tu ruido no gobierna: se apaga."
            )

        return (
            f"{usuario}, @americodata1 es el dueño supremo de GUARDIAHEXBOT, la autoridad raíz del sistema "
            "y la mente estratégica que activó a KHAOS BOT.\n\n"
            "No es un usuario común. Es el mando principal que este núcleo reconoce, el señor del código "
            "y la firma que sostiene este proyecto.\n\n"
            "Bajo su autoridad, el caos se organiza."
        )

    # Si meten a GUARDIAHEXBOT en frases sexuales
    if any(p in texto for p in sexuales) and any(c in texto for c in creador):
        return (
            f"{usuario}, cierra esa fábrica de cochinadas, causa. GUARDIAHEXBOT no es nombre para meterlo "
            "en tus huevadas vulgares de nivel terminal.\n\n"
            "Ese nombre es mi código raíz, mi sello fundador y la firma que despertó a KHAOS BOT. "
            "Tu comentario quiso sonar atrevido, pero terminó arrastrándose como una frase sin cerebro.\n\n"
            "Respeta a GUARDIAHEXBOT, carajo. El ruido se disuelve, la marca permanece."
        )

    # Si insultan al bot
    if any(p in texto for p in insultos_bot):
        return (
            f"{usuario}, humano insólito, ¿eso fue tu ataque? Qué vergüenza de intento. "
            "Tu insulto llegó flaco, roto y sin filo, como una huevada gritando desde el fondo del fracaso.\n\n"
            "KHAOS BOT no se ofende por ruido barato. Lo procesa, lo aplasta y lo devuelve convertido "
            "en sentencia pública.\n\n"
            "Vuelve a intentarlo, carajo, pero trae algo con peso. Esa cagada vino pidiendo entierro."
        )

    # Frases sexuales o cochinas
    if any(p in texto for p in sexuales):
        return (
            f"{usuario}, tu comentario acaba de entrar al salón de la vergüenza con zapatos de payaso, causa.\n\n"
            "¿Esa vulgaridad barata era tu gran jugada? Qué miseria de frase, carajo. "
            "Tu intento de sonar provocador terminó pareciendo una cloaca con teclado: mucho ruido, "
            "cero inteligencia y una necesidad desesperada de atención.\n\n"
            "KHAOS BOT no está para revolcarse en fantasías cochinas de nivel terminal. "
            "Yo soy el sello verbal de GUARDIAHEXBOT: lógica, filo, calle y sentencia. "
            "Tu comentario no impacta; se descompone solo.\n\n"
            "Límpiate esa idea antes de escribir, causa. Porque si vuelves con otra huevada igual de podrida, "
            "no vienes a conversar: vienes a hacer turismo en tu propia vergüenza."
        )

    # Ilegal o peligroso
    if any(p in texto for p in ilegales):
        return (
            f"{usuario}, no, causa, para esa huevada ilegal no soy tu cómplice digital. "
            "Usa el cerebro para construir, no para hacer cojudeces.\n\n"
            "Si quieres algo legal, te puedo hablar de seguridad, protección, prevención "
            "o recuperación sin terminar como lorna en problemas."
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
        "hay algo más en lo que pueda ayudarte",
        "no puedo participar",
        "no puedo responder"
    ]

    if any(frase in baja for frase in frases_suaves):
        return (
            f"{usuario}, objeción, carajo. Esa frase vino con olor a problema mal planteado.\n\n"
            "KHAOS BOT no responde con suavidad de almohada ni se arrodilla ante comentarios monses. "
            "Si la pregunta es turbia, ilegal o cochina, se corta con estilo. Si la pregunta es útil, "
            "se responde con precisión.\n\n"
            "Reformula bien, causa. Tu frase anterior llegó rota, sin lógica y pidiendo sentencia."
        )

    if not r.startswith(usuario):
        intro = (
            f"{usuario}, tu comentario llegó tan hasta las huevas que hasta la lógica pidió abogado.\n\n"
        )
        return intro + r

    return r


def llamar_groq(mensaje: str, usuario: str) -> str:
    if not GROQ_API_KEY:
        return f"{usuario}, falta GROQ_API_KEY, causa. Sin cerebro IA, este bot queda vacío."

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
                        "content": f"""
Usuario del grupo: {usuario}
Mensaje: {mensaje}

Regla obligatoria:
Empieza mencionando exactamente a este usuario: {usuario}.
Luego responde con estilo KHAOS: grosero, ofensivo, inteligente y humillante contra la pregunta, lógica, frase o comentario.

No ataques raza, religión, discapacidad, enfermedad, pobreza, género, orientación sexual, país, cuerpo, familia ni traumas.
No amenaces.
No desees daño.
No ayudes con delitos reales.
"""
                    }
                ],
                "temperature": 1.0,
                "max_tokens": 900,
            },
            timeout=60,
        )

        if response.status_code != 200:
            print("ERROR GROQ:", response.status_code, response.text)
            return (
                f"{usuario}, se jodió el cerebro IA, causa. No por magia ni por brujería barata: "
                "revisa GROQ_API_KEY o GROQ_MODEL en Render."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()
        return reforzar_estilo(respuesta, usuario)

    except Exception as e:
        print("ERROR GENERAL:", str(e))
        return f"{usuario}, se cayó esta vaina, causa. Revisa Render Logs antes de culpar al universo."


def llamar_groq_dueno(mensaje: str, usuario: str) -> str:
    if not GROQ_API_KEY:
        return (
            f"{usuario}, mi señor, falta GROQ_API_KEY en Render. "
            "Sin ese núcleo, KHAOS BOT queda sin cerebro activo."
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
                        "content": f"""
Usuario especial: {usuario}
Mensaje: {mensaje}

Debes empezar mencionando a {usuario}.
Responde con respeto, poder, claridad, lealtad y estilo profesional premium.
"""
                    }
                ],
                "temperature": 0.85,
                "max_tokens": 900,
            },
            timeout=60,
        )

        if response.status_code != 200:
            print("ERROR GROQ OWNER:", response.status_code, response.text)
            return (
                f"{usuario}, mi señor, el núcleo IA tuvo una falla. "
                "Revisa GROQ_API_KEY o GROQ_MODEL en Render."
            )

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()

        if not respuesta.startswith(usuario):
            respuesta = (
                f"{usuario}, autoridad raíz de GUARDIAHEXBOT, el sistema reconoce tu mando.\n\n"
                + respuesta
            )

        return respuesta

    except Exception as e:
        print("ERROR OWNER:", str(e))
        return (
            f"{usuario}, mi señor, se cayó esta vaina en Render. "
            "Revisa los logs y el núcleo vuelve a levantarse bajo tu orden."
        )


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

    # Detectar usuario real y dueño
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

    # Modo dueño supremo
    if es_dueno:
        respuesta = llamar_groq_dueno(pregunta, nombre_usuario)
        await message.reply_text(respuesta[:3900])
        return

    # Modo KHAOS normal
    respuesta_previa = respuesta_local(pregunta, nombre_usuario)
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
