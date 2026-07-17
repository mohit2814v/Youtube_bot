"""Channel niches: system prompt + defaults for Groq script generation.

Each preset includes a topic_pool — a list of setting/situation ideas.
One is picked randomly per run if no --topic is provided, ensuring variety.
"""

from __future__ import annotations

from typing import TypedDict


class Variant(TypedDict, total=False):
    """One output variant — same images, different audio/subs/upload target."""
    lang: str  # "en", "hi", etc. used as key in Groq response
    label: str  # human-readable for logs
    tts_voice: str  # Edge TTS voice (e.g. "hi-IN-MadhurNeural")
    caption_font: str  # font filename inside assets/fonts/
    caption_font_name: str  # FFmpeg-visible font family name
    yt_token_env: str  # env var name for YouTube refresh token (e.g. "YT_REFRESH_TOKEN_HI")
    min_words: int  # min word count for narration validation


class ChannelPreset(TypedDict, total=False):
    id: str
    label: str
    groq_system_hint: str
    segment_count: int  # images + script beats
    topic_pool: list[str]
    image_style_suffix: str  # appended to every image prompt
    image_negative_prompt: str  # passed as negative prompt
    # Single-variant fields (backward compat — used when `variants` is absent):
    language: str
    tts_voice: str
    caption_font: str
    caption_font_name: str
    min_words: int  # min word count for narration validation (single-variant)
    # Multi-variant mode — Groq returns translations for each lang, pipeline renders+uploads per variant.
    variants: list[Variant]
    # topic_rotation: "myth" → pipeline/myth_topics.py (IST day theme + no-repeat within theme)
    topic_rotation: str
    # Single-variant YouTube upload: which env var holds this channel's refresh token
    yt_token_env: str
    # Extra uploads: same MP4 uploaded to additional channels using these env var names
    extra_yt_token_envs: list[str]


PRESETS: dict[str, ChannelPreset] = {
    "facts": {
        "id": "facts",
        "label": "Bilingual Car & Formula 1 Facts (Hindi + English)",
        "variants": [
            {
                "lang": "hi",
                "label": "Hindi",
                "tts_voice": "hi-IN-MadhurNeural",
                "caption_font": "NotoSansDevanagari-Bold.ttf",
                "caption_font_name": "Noto Sans Devanagari",
                "yt_token_env": "YT_REFRESH_TOKEN_HI",
                "min_words": 80,
            },
            {
                "lang": "en",
                "label": "English",
                "tts_voice": "en-US-GuyNeural",
                "caption_font": "BebasNeue-Regular.ttf",
                "caption_font_name": "Bebas Neue",
                "yt_token_env": "YT_REFRESH_TOKEN_EN",
                "min_words": 70,
            },
        ],
        "groq_system_hint": (
            "You write punchy, high-octane YouTube Shorts about mind-blowing, surprising, and verified facts "
            "exclusively about Formula 1, hypercars, supercars, legendary racing drivers, track engineering, and automotive performance technology — in MULTIPLE languages. "
            "The same fact will be published as separate videos on different language channels. "
            "STRUCTURE: Intense hook about a racing stat or car capability in opening, supporting details (lap times, mechanical secrets, or historical context) in the middle, punchline + takeaway at end. "
            "TONE: Energetic, enthusiastic, confident, hardcore gearhead/motorsport enthusiast vibes. No fake clickbait. "
            "Each fact must be technically accurate (e.g., downforce metrics, engine configurations, F1 regulations, real performance numbers). "
            "No hashtags inside narration. Original phrasing only. "
            "IMAGE PROMPT RULE: write image prompts in ENGLISH only. Describe real photographs of Formula 1 cars on track, close-ups of steering wheels, aerodynamic carbon fiber wings, or hypercars. "
            "Use real-world subjects, cinematic motion blur, dramatic angles (e.g., low-angle apex shots, tracking shots). NEVER write 'cartoon', 'illustration', "
            "or 'CGI'. Examples: 'low angle tracking photo of a modern Formula 1 car sparking under neon lights during a night race', "
            "'close-up macro photo of an intricate carbon fiber F1 steering wheel with glowing LEDs', "
            "'wide shot of an aggressive hypercar cornering hard at the Nurburgring, glowing brake rotors visible'. "
            "BILINGUAL RULE: the SAME story/facts must be expressed naturally in each language — "
            "do not literally translate word-for-word; rephrase so each version sounds native and flows well. "
            "HINDI LENGTH: variants.hi.full_narration should be long-form — "
            "aim ~150 Devanagari words with rich detail so the Hindi voiceover is substantial (~55-70 seconds). "
            "ENGLISH LENGTH: variants.en.full_narration must be long-form too — "
            "aim 120-155 English words; include hook, 3-4 developed beats with technical racing stats, and a strong closing line so the English voiceover is ~40-50 seconds."
        ),
        "segment_count": 10,
        "image_style_suffix": (
            ", photorealistic motorsport photography, cinematic dramatic lighting, high speed motion blur, ultra detailed, "
            "8k, sharp focus, professional trackside camera, realistic carbon fiber textures, "
            "natural colors, deep shadows, no text, no captions, no watermark, no logos"
        ),
        "image_negative_prompt": (
            "cartoon, anime, illustration, painting, drawing, sketch, 3d render, cgi, "
            "stylized, flat colors, low quality, blurry background vehicle, watermark, logo, text, signature, "
            "deformed, ugly, bad proportions, distorted sponsor decals"
        ),
        "topic_pool": [
            # Formula 1 & Open Wheel Racing
            "how much downforce a modern F1 car generates at 150mph",
            "the physical toll on an F1 driver losing 4kg of weight per race",
            "why Formula 1 cars can theoretically drive upside down on a ceiling",
            "what happens during a record-breaking 1.8-second F1 pitstop",
            "how an F1 steering wheel controls over 100 different settings",
            "the extreme engineering behind F1 carbon ceramic brakes glowing at 1000 degrees",
            "how F1 fuel templates are mixed down to the molecular level for performance",
            "the bizarre active suspension system that was banned in Formula 1",
            "why F1 tires must be wrapped in electric blankets before hitting the track",
            "the secret behind Ayrton Senna's legendary throttle-tapping driving technique",
            "how Michael Schumacher won a Grand Prix by serving a penalty in the pit lane on the final lap",
            "the extreme G-forces F1 drivers withstand through Eau Rouge at Spa",
            # Hypercars & Supercars
            "Bugatti Chiron top speed engineering and why its tires cost a fortune",
            "how the Koenigsegg Jesko Light Speed Transmission shifts gears instantly",
            "the story of why the McLaren F1 used gold foil in its engine bay",
            "how the Pagani Huayra uses active flaps like a fighter jet to corner",
            "the Rimac Nevera electric hypercar breaking 23 acceleration records in one day",
            "why the Porsche 911 GT3 RS top wing hangs upside down like an F1 car",
            "the development of the Lexus LFA V10 engine that revved too fast for analog gauges",
            "how Hennessey pushes a twin-turbo V8 past 1800 horsepower safely",
            "the engineering marvel of the Aston Martin Valkyrie producing its own weight in downforce",
            "why Ferrari closely monitors and bans owners from modifying their supercars",
            "how the Mercedes-AMG One successfully crammed a real F1 engine into a road-legal car",
            "the extreme aerodynamics of the active underbody tunnels on the Lotus Evija"
        ],
    },

    "ghost_stories": {
        "id": "ghost_stories",
        "label": "Car Horror & Ghost Storytime Short",
        "min_words": 100,
        "groq_system_hint": (
            "You write spooky, eerie ghost stories exclusively focused on cars, haunted highways, possessed vehicles, "
            "and phantom racers for YouTube Shorts. "
            "CRITICAL LENGTH RULE: The TOTAL word count across ALL 6 segments MUST be 120-140 words. "
            "Each segment narration = 2-3 sentences, about 20-25 words per segment. "
            "This produces 35-45 seconds of audio when read aloud. "
            "Tone: eerie, suspenseful, creepy, supernatural, but NOT gory or violent. "
            "Segment 1: hook involving a car or dark road that stops scrolling. Last segment: chilling twist or unanswered question. "
            "All stories fictional. Original characters. PG-13. No hashtags in narration."
        ),
        "segment_count": 6,
        "image_style_suffix": (
            ", dark spooky automotive cartoon illustration, eerie highway atmosphere, creepy stylized car art, "
            "bold outlines, muted haunting colors, horror cartoon aesthetic, ghostly headlights, glowing dashboard, "
            "dramatic shadows, sinister mood, professional youtube thumbnail quality, "
            "no text, no captions, no watermark, no logos"
        ),
        "image_negative_prompt": (
            "photorealistic, photograph, happy cheerful bright, anime eyes, blurry, "
            "low quality, watermark, logo, text, title, signature, ugly, grainy, "
            "gore, blood, nudity, child-unsafe"
        ),
        "topic_pool": [
            "a phantom classic car that appears in the rear-view mirror on empty highways at 3 AM",
            "a classic sports car sitting in an abandoned barn whose engine starts by itself",
            "a driver stuck in a loop on a foggy mountain road with a strange hitchhiker",
            "a possessed navigation system that starts guiding the driver to an abandoned graveyard",
            "the ghost of a vintage open-wheel racer seen walking down the pit lane of a dark track",
            "a second-hand muscle car where the radio only plays audio from a 1970s crash",
            "a driver who notices a shadowy figure sitting in their back seat through the mirror",
            "an empty, driverless truck that follows travelers down a desolate desert route",
            "a car showroom where the headlights of a vintage luxury car blink in Morse code after midnight",
            "a midnight street racer who challenges a blacked-out vehicle, only to find it has no driver",
            "a junkyard crushing machine that turns on by itself whenever a specific red car gets near",
            "the urban legend of a stretch of highway where cars completely lose power and drift backward up the hill"
        ],
    },
    "hindi_myth": {
        "id": "hindi_myth",
        "label": "Bilingual Devotional Speed & Chariot Legends (Hindi + English)",
        "topic_rotation": "myth",
        "variants": [
            {
                "lang": "hi",
                "label": "Hindi",
                "tts_voice": "hi-IN-SwaraNeural",
                "caption_font": "NotoSansDevanagari-Bold.ttf",
                "caption_font_name": "Noto Sans Devanagari",
                "yt_token_env": "YT_REFRESH_TOKEN_MYTH",
                "min_words": 100,
            },
            {
                "lang": "en",
                "label": "English",
                "tts_voice": "en-US-GuyNeural",
                "caption_font": "BebasNeue-Regular.ttf",
                "caption_font_name": "Bebas Neue",
                "yt_token_env": "YT_REFRESH_TOKEN_EN",
                "min_words": 80,
            },
        ],
        "groq_system_hint": (
            "You write respectful YouTube Shorts linking ancient Indian scriptures, epics, and divine vehicles (Vahanas/Chariots) "
            "to concepts of speed, divine horsepower, and cosmic engineering — in MULTIPLE languages. "
            "The same myth fact will be published as separate videos on different language channels. "
            "STRUCTURE: Intense opening hook about an ancient weapon, speed metric, or chariot feat, detailed storytelling in the middle, and a powerful takeaway or cosmic realization at the end. "
            "TONE: Warm, storytelling, reverent, yet highly energetic. Focus on the legendary power, mechanics, and jaw-dropping scale of mythological transportation. "
            "No hashtags inside narration. Original phrasing only. "
            "IMAGE PROMPT RULE: Write image prompts in ENGLISH only. Describe epic cinematic scenes of ancient divine vehicles or royal chariots radiating celestial energy. "
            "NEVER write 'cartoon' or 'photorealistic face'. Examples: 'epic digital painting of a majestic ancient gold chariot flying through dark cosmic nebula trails, glowing energy wheel tracks', "
            "'wide cinematic shot of a warrior standing on a grand iron chariot overlooking an epic ancient battlefield at sunset'. "
            "BILINGUAL RULE: The SAME story must be expressed naturally in each language — do not translate word-for-word. "
            "HINDI LENGTH: variants.hi.full_narration must be entirely in Devanagari Hindi, aiming for 105-135 words (~40-50 seconds). "
            "ENGLISH LENGTH: variants.en.full_narration must be in English, aiming for 100-125 words (~35-45 seconds)."
        ),
        "segment_count": 6,
        "image_style_suffix": (
            ", epic cinematic Indian mythology digital painting, golden hour lighting, divine energy trails, "
            "celestial horsepower, cosmic engine aura, majestic composition, respectful devotional art style, "
            "high quality illustration, no text, no watermark, no logos"
        ),
        "image_negative_prompt": (
            "modern metallic cars, photorealistic human face close-up, gore, blood, horror jumpscare, "
            "disrespectful parody, political symbols, watermark, text, logo, blurry, low quality"
        ),
        "topic_pool": [
            "the legendary powers and cosmic speed of Arjuna's chariot Kapidhwaja driven by Lord Krishna",
            "exploring the celestial aerodynamics and immense power of Surya Dev's chariot drawn by seven horses",
            "the advanced ancient engineering of the airborne vehicle Pushpaka Vimana from Ramayana",
            "the symbolic power and massive weight-bearing capacity of Lord Shiva's divine chariot",
            "how the concept of divine Vahanas represents the ancient Indian understanding of speed and energy control",
            "the incredible golden chariot of Lord Vishnu and its divine velocity across realms"
        ],
    },
    "school_story": {
        "id": "school_story",
        "label": "Racing Academy & Elite Driver School Drama",
        "groq_system_hint": (
            "You write fictional storytime Shorts set in elite racing academies, high-stakes karting schools, "
            "or junior driver development camps. Tone: intense suspense, fierce rivalry, and passion for speed. "
            "Characters are original young racing drivers fighting for a single F1 seat. Hook in line 1. "
            "Build to one memorable technical or psychological twist on the final lap. Keep each story kid-safe."
        ),
        "segment_count": 5,
        "topic_pool": [
            "the quiet kid simulator driver who shocked the entire academy on the wet track test",
            "a junior driver's telemetry data that revealed someone secretly messed with their engine mapping",
            "a ruthless academy coach who forced the top two rivals to swap cars for the final race",
            "the mystery of the unknown karting driver who beat the champion using worn-out tires",
            "a high-stress brake-failure incident during an academy session that turned enemies into allies",
            "the final lap of the scholarship shootout where a driver intentionally sacrificed their speed to save a rival"
        ],
    },
    "history_micro": {
        "id": "history_micro",
        "label": "One Dramatic Moment in F1 & Car History",
        "groq_system_hint": (
            "You write one tight, accurate, historical anecdote per Short focused entirely on a singular, game-changing moment "
            "in Formula 1 history, legendary automotive feuds, or engineering breakthroughs. "
            "No graphic violence. Explain the mechanical or historical impact clearly, and end with why it changed the car world in one line."
        ),
        "segment_count": 5,
        "topic_pool": [
            "the legendary 1976 day Niki Lauda walked back into the F1 paddock just six weeks after his fiery accident",
            "how a massive corporate insult from Enzo Ferrari caused Ferruccio Lamborghini to build his very first supercar",
            "the day Colin Chapman introduced ground-effect aerodynamics to F1 and made cars stick to the ground like magnets",
            "how the Tyrell P34 shocked the racing world by showing up to the grid with six wheels instead of four",
            "the secret midnight meeting where Ford decided to build the GT40 strictly to destroy Ferrari at Le Mans",
            "the historic 1988 McLaren season where Ayrton Senna and Alain Prost won 15 out of 16 races through pure psychological warfare"
        ],
    },
}


def list_channel_ids() -> list[str]:
    return sorted(PRESETS.keys())


def get_preset(channel_id: str) -> ChannelPreset:
    key = channel_id.strip().lower().replace("-", "_")
    if key not in PRESETS:
        raise KeyError(f"Unknown channel preset {channel_id!r}. Try: {', '.join(list_channel_ids())}")
    return PRESETS[key]
