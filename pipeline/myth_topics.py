"""Hindi mythology Shorts — theme-of-day rotation + no-repeat within each theme.

- **Theme cycle** (IST calendar day): Ganesha → Shiva → Vishnu & avatars → …
  Same theme all day in India; next calendar day advances to the next deity block.
- **Topic pick**: random among topics in today's theme that are not yet marked used.
  When a theme's pool is exhausted, its used-list resets and topics can appear again.

State file: `output/history/myth_topic_rotation.json` (cache this path in CI like story history).
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = REPO_ROOT / "output" / "history" / "myth_topic_rotation.json"

IST = ZoneInfo("Asia/Kolkata")

# Order of themes by calendar day (cycles forever).
THEME_ORDER: list[str] = [
    "hypercars",
    "jdm_legends",
    "supercar_secrets",
    "car_history",
    "banned_and_illegal",
    "easter_eggs",
    "f1_and_racing",
    "car_mysteries",
    "automotive_lessons",
    "muscle_cars",         # New Category!
    "sleeper_cars",        # New Category!
    "future_and_concepts"  # New Category!
]

MYTH_POOLS: dict[str, list[str]] = {
    "hypercars": [
        "Why the Bugatti Chiron's key costs more than a brand new BMW",
        "The story of how Koenigsegg built a 300mph hypercar in a small hangar",
        "Why the McLaren F1 still has a gold-plated engine bay",
        "The crazy active aerodynamics of the Pagani Huayra explained",
        "How the Rimac Nevera became the fastest accelerating car in the world",
        "Why the Ferrari LaFerrari has such a ridiculous name",
        "The story of the Hennessy Venom GT and its fight with Bugatti",
        "Why the Aston Martin Valkyrie sounds exactly like an old F1 car",
        "The secret high-speed test track where Bugatti hits 300mph",
        "Why hypercar tires cost $42,000 and can only be changed in France",
        "The story of the Zenvo TSR-S and its crazy tilting rear wing",
        "Why the Apollo IE looks like a fighter jet and costs $2.7 million",
        "How the Mercedes-AMG One crammed an actual, legal F1 engine into a road car",
        "The Koenigsegg Gemera — a 3-cylinder family car with 1,700 horsepower",
        "Why the SSC Tuatara's 331mph top speed run caused a massive internet scandal",
    ],
    "jdm_legends": [
        "Why the Nissan Skyline R34 GT-R is called 'Godzilla'",
        "The real reason Japan had a '276 HP' gentleman's agreement",
        "How the Toyota Supra 2JZ engine became an unbreakable tuning legend",
        "The legendary story of the Midnight Club — Japan's secret street racers",
        "Why the Mazda RX-7's rotary engine is both a masterpiece and a nightmare",
        "How the Honda NSX was fine-tuned by F1 champion Ayrton Senna",
        "The story behind Initial D and the real AE86 drift king",
        "Why the Nissan Silvia S15 is the ultimate drift machine ever made",
        "How the Subaru WRX vs Mitsubishi Evo rivalry changed rally forever",
        "Why certain JDM cars are legally banned in the US under the 25-year law",
        "The story of the Nissan Stagea — the GT-R station wagon nobody knows about",
        "Why the Honda S2000 has a redline that shames modern supercars",
        "How the tiny Suzuki Cappuccino became a giant-killing JDM track toy",
        "The mythical Toyota Century — Japan's ultra-luxury V12 built for royalty",
        "How Mitsubishi built a street-legal rally car called the Pajero Evolution",
    ],
    "supercar_secrets": [
        "How the Pagani Zonda used fighter jet technology for its exhaust",
        "The secret umbrella hidden inside the door of a Rolls-Royce",
        "Why Lamborghinis are always named after famous fighting bulls",
        "The crazy reason the Porsche Carrera GT is notoriously hard to drive",
        "Why the Lexus LFA needs a digital tachometer because its engine is too fast",
        "How Ferrari chooses who is allowed to buy their limited edition cars",
        "Why the McLaren F1 has its driver seat dead in the middle of the car",
        "The secret 'Valet Mode' in modern supercars and what it hides",
        "Why the Bugatti Veyron needs a second key just to unlock top speed",
        "How the Mercedes SLR Stirling Moss has no windshield but still goes 220mph",
        "The weird story of why the Lamborghini Countach has zero rear visibility",
        "Why the Porsche 911 GT3 RS wing is taller than the roof of the car",
        "How the Maserati MC12 was just a disguised Ferrari Enzo built for racing",
        "Why Lamborghini built the Veneno to look like a spaceship and only made 3",
        "The active cabin noise cancelation secret inside the McLaren Artura",
    ],
    "car_history": [
        "The legendary insult that made Ferruccio Lamborghini build supercars",
        "How a tractor company ended up creating the wildest supercars on Earth",
        "The story of how Ford built the GT40 just to humiliate Ferrari at Le Mans",
        "Why Porsche's logo is actually a combination of two historic crests",
        "The origin of the BMW 'M' colors and what they actually represent",
        "How Mercedes-Benz accidentally invented the world's first modern car",
        "The dark history of how Volkswagen was originally funded and created",
        "How Shelby took a tiny British roadster and made the lethal AC Cobra",
        "The story of how Honda went from making clip-on bicycle motors to F1 engines",
        "Why the DeLorean became an icon despite being a complete engineering failure",
        "The story of how Volvo gave away their 3-point seatbelt patent to save lives",
        "How Peugeot went from making pepper grinders to classic rally cars",
        "The real reason Aston Martin uses the prefix 'DB' on all their cars",
        "How the iconic Jeep grille design was born out of a wartime emergency",
        "The story of why the Red Bull F1 team is actually a marketing miracle",
    ],
    "banned_and_illegal": [
        "Why the Dodge Challenger Demon was banned by the NHRA for being too fast",
        "The illegal active suspension system that F1 had to ban overnight",
        "Why the TVR Sagaris was banned in America for having no safety features",
        "The story of the Chaparral 2J 'vacuum cleaner' car that was outlawed",
        "Why Pagani's wildest track cars are completely illegal on public streets",
        "The active aero wing on the Brabham BT46 'Fan Car' that got banned",
        "Why certain modified car exhausts can land you in jail in Japan",
        "The story of the Group B rally cars that were banned for being too dangerous",
        "Why you can't import a Nissan Skyline R34 to America without risking it being crushed",
        "The crazy emissions defeat device that cost Volkswagen billions of dollars",
        "The radical Tyrrell P34 six-wheeled F1 car that was banned from racing",
        "Why the Radical SR8 is street legal in Europe but completely banned in America",
        "The legal loophole that let the Porsche 959 get imported to the US",
        "Why Dodge's wing car, the Charger Daytona, was banned from NASCAR",
        "The illegal nitrous-oxide cheating scandal that rocked Toyota's rally team",
    ],
    "easter_eggs": [
        "The hidden animal silhouette hidden on every single Jeep Wrangler",
        "Why the Tesla Model X has a secret holiday light show mode",
        "The hidden design easter egg inside the Lexus LFA's moving gauge cluster",
        "Why Volvo's rear seats have a hidden booster seat built right in",
        "The secret 'camp mode' and arcade games hidden inside every Tesla",
        "Why the Dodge Viper has a secret racetrack map molded into its plastic",
        "The hidden umbrella compartment in the Škoda Superb door",
        "How the Koenigsegg Jesko key fob has a hidden shield crest button",
        "The secret ghost logo on Koenigsegg engines and its heroic origin",
        "Why the Jaguar E-Type has a secret signature hidden under the bonnet",
        "The hidden shark silhouettes molded into Vauxhall interior plastics",
        "Why the Ford GT headlights have the number '100' hidden inside them",
        "The hidden video game controller layout on the Tesla Cybertruck pedals",
        "How the Rolls Royce wheel center caps stay upright while spinning",
        "The secret whiskey decanter hidden in the armrest of a Rolls-Royce Phantom",
    ],
    "f1_and_racing": [
        "How Formula 1 drivers lose up to 9 pounds of water weight in one race",
        "The secret button on an F1 steering wheel that controls the drink system",
        "How F1 pit stops went from 20 seconds to a mind-blowing 1.8 seconds",
        "Why F1 cars use titanium skid plates to intentionally create sparks",
        "The physics of how an F1 car generates enough downforce to drive upside down",
        "Why NASCAR tires don't have tread patterns like normal road tires",
        "The secret tactics F1 teams use during 'winter testing' to hide their speed",
        "How the 'halo' device saved multiple F1 drivers' lives in massive crashes",
        "Why rally co-drivers speak in a secret code during a race",
        "How Le Mans drivers manage to race at 200mph in pitch-black darkness",
        "The extreme $200,000 steering wheel of a modern Formula 1 car",
        "How F1 engines achieve over 50% thermal efficiency (better than any road car)",
        "The legendary story of the driver who raced with a broken collarbone",
        "Why racing fuel is chilled before it gets put into an F1 car",
        "How F1 teams use giant supercomputers to run millions of race simulations",
    ],
    "car_mysteries": [
        "The mystery of James Dean's cursed Porsche 550 Spyder 'Little Bastard'",
        "The abandoned warehouse in Japan filled with millions of dollars of classic cars",
        "Why nobody knows where the original, record-breaking Bugatti Aerolithe is",
        "The mystery of the stolen $100 million Ferrari that vanished without a trace",
        "The strange case of the multi-million dollar supercar graveyard in Dubai",
        "Why car manufacturers wrap prototype cars in crazy black-and-white camo tape",
        "The mystery of the underground car tunnels built beneath major cities",
        "Why some supercars spontaneously catch fire while idling at traffic lights",
        "The strange story of the classic cars hidden in a French barn for 50 years",
        "The legendary 'Silver Arrows' paint mystery — did they really scrape the paint off?",
        "The mystery of the luxury cars lost forever at the bottom of the ocean on the Felicity Ace",
        "The secret billionaire car collections in Brunei that are slowly rotting away",
        "The ghost racetrack of Brooklands and why it was abandoned",
        "The mystery of the missing muscle cars that vanished from factory shipping logs",
        "Why classic supercars are secretly being hidden in secure Swiss mountain vaults",
    ],
    "automotive_lessons": [
        "Why buying a cheap used German luxury car is actually a financial trap",
        "What the 'chicken tax' is and how it changed pickup trucks forever",
        "Why car engines sound different in cold weather — the science explained",
        "The truth about premium fuel — does it actually make your normal car faster?",
        "Why the manual transmission is slowly dying and why enthusiasts fight to keep it",
        "The engineering genius behind why modern cars crush themselves in an accident",
        "Why you should never modify your daily driver car's suspension without a plan",
        "How car manufacturers trick your ears by pumping fake engine noise into the speakers",
        "Why low-profile tires look amazing but ruin your car's ride quality",
        "What the Koenigsegg 'Freevalve' engine means for the future of gasoline cars",
        "Why carbon ceramic brakes are terrible for normal city driving",
        "The physics of hydroplaning and how to survive it",
        "Why heavier cars aren't always safer in a modern head-on crash",
        "How bad wheel alignment can secretly destroy your tires in under a week",
        "Why car air conditioning systems drop your fuel mileage and by how much",
    ],
    "muscle_cars": [
        "Why the 1970 Plymouth Superbird had a wing so ridiculously tall",
        "How Dodge squeezed 840 horsepower out of a factory stock Challenger Demon",
        "The story of the Shelby GT500 'Eleanor' and its Hollywood fame",
        "The legendary 426 Hemi engine that dominated drag racing",
        "How the original Ford Mustang created the entire 'Pony Car' era overnight",
        "The tragic end of the American Muscle car era in 1973 due to oil laws",
        "Why the Chevrolet Corvette switched to a mid-engine setup after 60 years",
        "The story of the 'Yenko' Camaros and the dealership that built them illegally",
        "How Pontiac birthed the muscle car craze with the legendary GTO",
        "Why the Buick GNX was faster than a Chevrolet Corvette in the 1980s",
        "The story of the Mercury Cougar — the muscle car for luxury lovers",
        "Why the modern Dodge Hellcat sounds like a screaming mechanical monster",
        "How the Plymouth Hemi Cuda became a multi-million dollar collector goldmine",
        "The story of the Baldwin-Motion phase III muscle cars that guaranteed speed",
        "Why Ford built the Mustang Boss 429 just to qualify an engine for NASCAR",
    ],
    "sleeper_cars": [
        "The family station wagon that can outrun a Porsche 911: Audi RS6",
        "How Ford built a grandma sedan with a Taurus SHO Yamaha engine",
        "The Volvo wagon that dominated the British Touring Car Championship",
        "Why the Buick Roadmaster is a secretly terrifying V8 muscle car",
        "The Mercedes-Benz E500 that was secretly built by hand in a Porsche factory",
        "The GMC Syclone: The 90s pickup truck that beat a Ferrari in a drag race",
        "Why the BMW M5 is the ultimate executive sedan with supercar speed",
        "The Volkswagen Golf R: A hatchback disguised as a golf cart with 300+ HP",
        "How the Lotus Carlton became the most dangerous sedan in Great Britain",
        "The Jeep Grand Cherokee Trackhawk: A family SUV with a Hellcat engine",
        "The sleeper legend of the Mercury Marauder — an undercover cop car on steroids",
        "Why the Toyota Caldina GT-Four is a stealth JDM rocket ship wagon",
        "The story of the Renault Espace F1 — a minivan with an actual F1 V10",
        "How Saab used fighter jet engineering to build stealth highway weapons",
        "The Mazdaspeed 6: The boring-looking family sedan with an all-wheel-drive turbo system",
    ],
    "future_and_concepts": [
        "The radical Mercedes AVTR concept car controlled entirely by your thoughts",
        "How solid-state EV batteries will let cars charge to 80 percent in 5 minutes",
        "Why BMW's color-changing paint technology on the iX Flow is revolutionary",
        "The futuristic hydrogen supercar that emits absolutely nothing but pure drinking water",
        "How active road-scanning suspension in luxury cars will make bumps vanish",
        "Why software-defined cars will let you purchase extra horsepower over the air",
        "The wild concept of car windshields becoming giant heads-up augmented reality displays",
        "How the Peugeot Inception concept uses a video game controller instead of a steering wheel",
        "Why car manufacturers are shifting to eco-friendly mushroom leather interior",
        "The flying car concepts that are actually getting certified for real flights",
        "The Hyundai N Vision 74: The retro-futuristic hydrogen drift machine",
        "How bio-engineered car panels could heal themselves from minor scratches",
        "The Mercedes-Benz C111: The rotary-powered laboratory on wheels that broke every record",
        "Why luxury car brands are building custom apartments and real estate towers",
        "The future of vehicle safety: Cars that talk to traffic lights to prevent accidents",
    ]
}

def _load_state() -> dict[str, dict]:
    if not STATE_PATH.is_file():
        return {}
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(data: dict[str, dict]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def theme_for_today_ist() -> str:
    """Which myth block today (India calendar). Cycles through THEME_ORDER."""
    d = datetime.now(IST).date()
    idx = d.toordinal() % len(THEME_ORDER)
    return THEME_ORDER[idx]


def pick_myth_topic(channel_id: str) -> tuple[str, str]:
    """Return (topic_hint, theme_key) for Groq. Does not persist yet."""
    theme = theme_for_today_ist()
    pool = MYTH_POOLS.get(theme, [])
    if not pool:
        raise RuntimeError(f"No myth topics for theme {theme!r}")

    state = _load_state()
    ch = state.setdefault(channel_id, {"used": {}})

    used_list = ch["used"].setdefault(theme, [])
    used_set = set(used_list)
    available = [t for t in pool if t not in used_set]

    if not available:
        ch["used"][theme] = []
        available = list(pool)

    topic = random.choice(available)
    return topic, theme


def commit_myth_topic(channel_id: str, theme: str, topic: str) -> None:
    """Call after a full successful run so this topic is not chosen again until pool resets."""
    state = _load_state()
    ch = state.setdefault(channel_id, {"used": {}})
    used = ch["used"].setdefault(theme, [])
    if topic not in used:
        used.append(topic)
    _save_state(state)
