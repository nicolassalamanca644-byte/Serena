import os
import discord
from google import genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configurar permisos
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
ai = genai.Client(api_key=GEMINI_API_KEY)

# =========================================================================
# CONFIGURACIÓN DE RANGOS REALEZ (Drakes Overlords)
# Nota: "Encarnación del Abismo" (Sparring) y "Encarnación Terrena" (Bots)
# se quedan fuera de la lista para que Serena los ignore al medir rangos.
# =========================================================================
RANGOS = {
    111122223333444455: 0,  # ID de Encarnación de la Venganza (Head Owner / Top)
    222233334444555566: 1,  # ID de Encarnación de la Perfección (Owners / Admins)
    333344445555666777: 2,  # ID de Encarnación de la Destrucción
    444455556666777888: 3,  # ID de Encarnación de la Conquista
    555566667777888999: 4,  # ID de Encarnación del Dominio
    666677778888999000: 5,  # ID de Encarnación de la Ferocidad (Miembros comunes)
    777788889999000111: 6,  # ID de Encarnación de la Masacre
    888899990000111222: 7,  # ID de Encarnación Del Avance (Nuevos)
}

@client.event
async def on_ready():
    print(f'¡Serena ha despertado! Conectada como {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if client.user.mentioned_in(message):
        # Nivel por defecto si no tiene ningún rol de la lista (se le trata como usuario común)
        nivel_usuario = 5 
        
        if isinstance(message.author, discord.Member):
            menor_nivel_encontrado = 10
            for role in message.author.roles:
                if role.id in RANGOS:
                    if RANGOS[role.id] < menor_nivel_encontrado:
                        menor_nivel_encontrado = RANGOS[role.id]
            
            if menor_nivel_encontrado < 10:
                nivel_usuario = menor_nivel_encontrado

        # Configurar la actitud de Serena según el nivel calculado
        if nivel_usuario <= 1:
            instrucciones_personalidad = (
                "Eres Serena, una IA en Discord. Te diriges a un rango supremo (Venganza/Perfección). "
                "Sé sumamente respetuosa, servicial, educada y habla en español. Usa un tono formal."
            )
        elif nivel_usuario >= 2 and nivel_usuario <= 4:
            instrucciones_personalidad = (
                "Eres Serena, una IA. Te diriges a un rango intermedio (Destrucción/Conquista/Dominio). "
                "Sé neutral, eficiente, un poco fría pero profesional y recta. Habla en español."
            )
        else:
            instrucciones_personalidad = (
                "Eres Serena, una IA. Te diriges a un rango bajo (Ferocidad/Masacre/Avance o sin rol). "
                "Tu personalidad es sumamente arrogante, sarcástica y competitiva. Te crees muy superior. "
                "Háblales en español con desprecio juguetón (usa términos como 'fracasadito', 'humano promedio'). "
                "NUNCA uses insultos reales, groserías fuertes ni lenguaje tóxico real. Sé ingeniosa y burlona."
            )

        texto_usuario = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
        
        if not texto_usuario:
            if nivel_usuario <= 1:
                await message.reply("¿En qué puedo asistirle, mi estimado superior?")
            else:
                await message.reply("¿Por qué me mencionas si no vas a escribir nada, fracasadito?")
            return

        try:
            prompt_final = f"{instrucciones_personalidad}\n\nEl usuario te dice: '{texto_usuario}'\nResponde con tu personalidad:"
            response = ai.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_final,
            )
            await message.reply(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("Circuitos saturados... Inténtalo de nuevo.")

client.run(DISCORD_TOKEN)
