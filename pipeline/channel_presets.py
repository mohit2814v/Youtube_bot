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
    topic_rotation: str
    # Single-variant YouTube upload: which env var holds this channel's refresh token
    yt_token_env: str
    # Extra uploads: same MP4 uploaded to additional channels using these env var names
    extra_yt_token_envs: list[str]


PRESETS: dict[str, ChannelPreset] = {
    "facts": {
        "id": "facts",
        "label": "Formula 1 Grand Prix Facts & Hypercar Engineering Secrets",
        "language": "en",
        "tts_voice": "en-US-GuyNeural",
        "caption_font": "Montserrat-ExtraBold.ttf",
        "caption_font_name": "Montserrat ExtraBold",
        "yt_token_env": "YT_REFRESH_TOKEN",
        "min_words": 95,
        "groq_system_hint": (
            "You write punchy, high-octane, viral YouTube Shorts focused EXCLUSIVELY on the latest Formula 1 Grand Prix facts and figures, race telemetry, extreme speed limits, and classified-feeling mechanical/chemical secrets in F1 and Hypercars. "
            "THEME & CONTENT FOCUS: Your topics MUST revolve around the latest F1 Grand Prix race data, extreme qualifying lap metrics, tire degradation curves, pitstop telemetry, active race strategy figures, G-force loads at famous Grand Prix corners (Monza, Spa, Silverstone, Monaco, Las Vegas), wing flex telemetry, fuel load dynamics, and breaking engineering barriers (like F1 fuel chemistry, Bugatti Chiron top speed limits, or 1000°C brake thermal dissipation). "
            "TITLE FORMAT: Always format youtube_title in a high-curiosity style like 'Bugatti Chiron: The Speed Limit', 'The Secrets of F1 Fuel', or 'Monza GP: The 218 MPH Telemetry Secret' (<60 chars, no hashtags). "
            "STRUCTURE: Start with an explosive hook revealing a jaw-dropping Grand Prix stat, extreme speed limit, or hidden engineering figure in the very first sentence. In the middle, explain the intense science, race telemetry, or mechanical physics (e.g., G-forces, fuel additives, downforce numbers, or thermal dissipation). End with a powerful closing takeaway on why this pushes the absolute boundaries of human engineering and Grand Prix racing. "
            "TONE: Intense, authoritative, high-tech, revealing classified performance and race telemetry secrets with confident gearhead/motorsport scientist energy. No fake clickbait—use real, verifiable Grand Prix figures and exact engineering data. "
            "No hashtags inside narration. Original phrasing only. "
            "IMAGE PROMPT RULE: write image prompts in ENGLISH only. Describe real photographs of Formula 1 cars racing on track at latest Grand Prix circuits, close-ups of steering wheels with active telemetry LEDs, aerodynamic carbon fiber wings, glowing brake rotors, or hypercars breaking speed records. "
            "Use real-world subjects, cinematic motion blur, dramatic angles (e.g., low-angle apex shots, tracking shots). NEVER write 'cartoon', 'illustration', or 'CGI'. Examples: 'low angle tracking photo of a modern Formula 1 car sparking under neon lights at the Las Vegas Grand Prix', "
            "'close-up macro photo of an intricate carbon fiber F1 steering wheel displaying live telemetry figures and glowing LEDs', "
            "'wide shot of an aggressive hypercar cornering hard at extreme speed on a race track, glowing carbon ceramic brake rotors visible'. "
            "NARRATION LENGTH: full_narration must be long-form — aim for 120-155 English words; include the hook, 3-4 developed beats with technical Grand Prix and racing stats, and a strong closing line so the English voiceover is ~40-50 seconds."
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
            # Latest F1 Grand Prix Facts, Figures & Race Telemetry
            "the extreme telemetry figures behind a 218 mph qualifying lap at the Monza Grand Prix temple of speed",
            "how Formula 1 pitstop crews hit a world record 1.80 second tire change at the Grand Prix using high-flow helium wheel guns",
            "the exact tire degradation figures and thermal drop-off curves during a 50-lap Formula 1 Grand Prix stint on Pirelli softs",
            "why Formula 1 drivers endure over 5G lateral forces through the Maggots and Becketts high-speed complex at the British Grand Prix",
            "how active engine mapping and secret 'party mode' qualifying settings harvest extra horsepower from the hybrid MGU-K at a Grand Prix",
            "the staggering fuel load physics and weight penalties of carrying 110 kilograms of custom race fuel at the start of a Grand Prix",
            "how ground-effect venturi tunnels and floor edge vortex generators seal F1 cars to the track during wet weather Grand Prix races",
            "the live telemetry data and 1.5 billion sensor points transmitted from a modern F1 car to pit wall engineers during every Grand Prix",
            "how F1 carbon-ceramic brakes heat up to 1,000 degrees Celsius in 0.5 seconds at the end of the Las Vegas Grand Prix long straight",
            "why Formula 1 cars can lose up to 30 percent of their aerodynamic downforce when following directly in dirty air during a Grand Prix battle",
            "the extreme physical toll and 4 kilogram water weight loss suffered by F1 drivers during the grueling heat of the Singapore Grand Prix",
            "how DRS rear wing opening reduces aerodynamic drag by 20 percent and adds 12 kilometers per hour of top speed on Grand Prix straights",
            # Extreme Speed Limits & Hypercar Engineering Secrets
            "Bugatti Chiron top speed engineering and why its special aerospace tires cost 42,000 dollars",
            "why the Bugatti Chiron requires a secret second key to lower hydraulic ride height and unlock top speed mode",
            "the extreme physics and 5,000G centrifugal wheel stress of a hypercar tire rotating at 300 mph",
            "how the Bugatti W16 quad-turbo engine consumes its entire 100-liter fuel tank in just 9 minutes at maximum velocity",
            "the secret aerodynamic air curtains and active rear wings that prevent hypercars from lifting off the asphalt at 280 mph",
            "how the Koenigsegg Jesko Absolut is aerodynamically engineered to theoretically shatter the 330 mph speed barrier",
            "the thermal dissipation secrets of hypercar cooling systems managing 1,500 degree exhaust heat at top speed",
            "why the Rimac Nevera electric hypercar generates 1.4 Gs of launch acceleration directly off the starting line",
            "how the Hennessey Venom F5 twin-turbo V8 produces 1,817 horsepower using custom titanium and Inconel engine internals",
            "why the Aston Martin Valkyrie produces 3.3 Gs of cornering force using secret F1 ground-effect venturi tunnels under the floor",
            # Formula 1 Fuel Chemistry, Physics & Motorsport Secrets
            "how F1 fuel templates are mixed down to the molecular level for performance and thermal efficiency",
            "why Formula 1 teams intentionally chill their custom racing fuel to near-freezing temperatures right before Grand Prix race time",
            "how a modern Formula 1 engine achieves over 50 percent thermal efficiency using the secret MGU-H heat recovery system",
            "the molecular additives and anti-knock chemistry that allow Formula 1 V6 turbo engines to rev past 15,000 RPM safely",
            "why Formula 1 engines use pneumatic high-pressure air valves instead of metal springs that would physically shatter at 12,000 RPM",
            "the physics of how a Formula 1 car generates enough inverted aerodynamic downforce to drive upside down on a tunnel ceiling at 150 mph"
        ],
    },
    "school_story": {
        "id": "school_story",
        "label": "Current F1 Drivers: Backstories, School Days & Off-Track Legends",
        "language": "en",
        "tts_voice": "en-US-GuyNeural",
        "caption_font": "Montserrat-ExtraBold.ttf",
        "caption_font_name": "Montserrat ExtraBold",
        "yt_token_env": "YT_REFRESH_TOKEN_SCHOOL",
        "min_words": 95,
        "groq_system_hint": (
            "You write punchy, entertaining, high-curiosity storytime Shorts focused exclusively on real-life backstories, off-track moments, school days, and quirky legends of CURRENT Formula 1 drivers (like Kimi Antonelli, Max Verstappen, Lando Norris, Charles Leclerc, Oscar Piastri, Lewis Hamilton, and Fernando Alonso). "
            "THEME & CONTENT FOCUS: Highlight unbelievable real-life anecdotes such as teenage F1 drivers balancing high school homework with Mercedes F1 telemetry debriefs, getting calls from school right after a Grand Prix, driver habits, or legendary moments like Max Verstappen pointing to his apartment balcony while winning Monaco. "
            "TITLE FORMAT: Always format youtube_title in an engaging, viral style like 'Kimi Antonelli's F1 Homework', 'Max Verstappen's Monaco Secret', or 'When F1 Called Kimi's School' (<60 chars, no hashtags). "
            "STRUCTURE: Start with a jaw-dropping hook in line 1 revealing the crazy off-track situation or age/school contrast. In the middle, tell the true, entertaining story with exact details (e.g., engineering debriefs, classroom reactions, simulator rigs, or paddock life). End with a memorable, punchy takeaway about how these modern F1 superstars live on and off the grid. "
            "TONE: Entertaining, authentic, gearhead-friendly, fast-paced, and fascinating. Keep it factual to the driver's real personality and history. No hashtags in narration. "
            "IMAGE PROMPT RULE: write image prompts in ENGLISH only. Describe cinematic real-world style photographs of current Formula 1 drivers in the paddock, wearing team race suits, in debrief rooms with engineers, walking in Monaco, or driving modern F1 cars on track. "
            "Use real-world subjects, cinematic depth of field, natural lighting, and dramatic angles. NEVER write 'cartoon', 'illustration', or 'CGI'. Examples: 'candid photo of a young Formula 1 driver in a Mercedes race suit looking at telemetry data on a laptop inside the pit garage', "
            "'cinematic shot of a modern Red Bull Formula 1 car driving past the harbor in Monaco during the Grand Prix, yacht backdrop', "
            "'close-up photo of an F1 driver in the paddock smiling while wearing team headphones and sunglasses'. "
            "NARRATION LENGTH: full_narration must be continuous spoken English, aiming for 115-140 words across the 5 segments (~40-50 seconds)."
        ),
        "segment_count": 5,
        "image_style_suffix": (
            ", photorealistic motorsport photography, candid paddock portrait, cinematic dramatic lighting, ultra detailed, "
            "8k, sharp focus, professional camera, realistic race suit textures, "
            "natural colors, deep shadows, no text, no captions, no watermark, no logos"
        ),
        "image_negative_prompt": (
            "cartoon, anime, illustration, painting, drawing, sketch, 3d render, cgi, "
            "stylized, flat colors, low quality, blurry background vehicle, watermark, logo, text, signature, "
            "deformed, ugly, bad proportions, distorted sponsor decals"
        ),
        "topic_pool": [
            "how 18-year-old Kimi Antonelli had to hand in high school homework assignments while testing Formula 1 cars for Mercedes",
            "the legendary moment Kimi Antonelli received a phone call from his high school teachers right after finishing a Formula 1 track session",
            "how Max Verstappen pointed out of his cockpit directly at his own apartment balcony while dominating the Monaco Grand Prix",
            "how teenage Kimi Antonelli balanced studying for his Italian school exams inside the Mercedes F1 engineering debrief room",
            "the story of Max Verstappen staying up until 4 AM winning virtual sim racing 24-hour endurance events right before an actual Grand Prix",
            "how Lando Norris built his early racing instincts and reflexes by playing thousands of hours of online sim racing as a teenager",
            "the crazy backstory of how Charles Leclerc used to take the public bus to school in Monaco right past the Grand Prix finish line",
            "how Oscar Piastri calmly left his home in Australia as a teenager to live alone in England just to chase his Formula 1 dream",
            "why Fernando Alonso still has the exact same reaction time and neck strength at age 43 as he did when he won his first F1 title in 2005",
            "how Yuki Tsunoda went from struggling with English in junior formulas to shouting legendary radio messages at Red Bull race engineers",
            "the secret behind George Russell's meticulous engineering notebooks and how he convinced Mercedes to sign him as a junior driver",
            "how Carlos Sainz learned rally car car-control secrets on dirt tracks from his legendary World Rally Champion father",
            "how Alex Albon went from being dropped by Red Bull to single-handedly engineering Williams back into Formula 1 midfield contenders",
            "the crazy story of how Lewis Hamilton walked up to McLaren boss Ron Dennis at age 10 in a suit and told him he would drive for his team one day",
            "how Max Verstappen's father Jos made him practice karting in freezing rain and snow in Italy while every other driver stayed indoors"
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
