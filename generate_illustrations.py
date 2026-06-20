#!/usr/bin/env python3
"""Generates 100 vintage-industrial graphic novel SVG illustrations -> illustrations.zip"""
import math, random, zipfile, io

C = {
    'ink': '#1A0A00', 'sepia_dark': '#2C1A0A', 'sepia_mid': '#6B3E1A',
    'golden': '#D4920A', 'amber': '#C07820', 'cream': '#F5DEB3',
    'rust': '#8B3A1A', 'smoke': '#9E8060', 'skin': '#C49060',
    'hat': '#D4A017', 'denim': '#3A2810', 'metal': '#4A3020',
    'pipe_hi': '#8B6914', 'glow_green': '#2A5A1A', 'blueprint': '#1A2A4A',
}

CAPTIONS = [
    ["The gauges never lie — but they rarely tell the whole truth.",
     "Night shift, cup three. The refinery breathes in the dark.",
     "Every flicker of the CRT holds a story.",
     "The hum of machinery is the only lullaby we need.",
     "Coffee, calculations, and the quiet weight of responsibility.",
     "When the alarms sleep, so does he — barely.",
     "The console knows all. I just need to ask the right questions.",
     "Between readings, he thinks of the sea.",
     "Bolt holds the flashlight. I hold the answers.",
     "Seventeen years on this shift. The screens have changed. I haven't.",
     "The old monitors glow amber in the dark like dying stars.",
     "He named the robot. The robot does not mind.",
     "Output nominal. Pressure steady. The world outside can wait.",
     "Every digit on that readout represents someone's hard work.",
     "The chair is worn in exactly my shape. That means something.",
     "Some engineers read manuals. We read the plant.",
     "A mug of coffee, a reliable companion, a reliable machine.",
     "The midnight hum is a language we've learned to speak.",
     "Routine is not boring when everything depends on it.",
     "He checks, double-checks, and checks again. That's the job."],
    ["The sparks fall like stars that forgot how to stay.",
     "Where metal meets metal, something new is born.",
     "Forty feet up, and the world makes more sense.",
     "One good weld holds longer than a thousand promises.",
     "Bolt and I have fixed worse. Much worse.",
     "The joint will hold. We made sure of it.",
     "Heat and pressure — same forces that shape everything worth keeping.",
     "The catwalks remember every footstep ever taken.",
     "We don't make things pretty up here. We make them last.",
     "The arc says everything that words cannot.",
     "High above the noise, the work is pure.",
     "He welds. I watch. Together, we make it whole.",
     "The sparks will fade. The joint will not.",
     "There is art in a perfect bead of weld.",
     "This pipe carries the work of a thousand people. Treat it so.",
     "Up here, the city below seems like a distant rumor.",
     "Forty meters of steel and the certainty of craft.",
     "The torch knows only forward.",
     "We fix things, Bolt and I. It's a kind of faith.",
     "Every spark is a small controlled sun."],
    ["We built something worth looking at.",
     "The refinery at dusk — ugly and magnificent at once.",
     "The sky turns our colors. We accept the compliment.",
     "Somewhere in those pipes is tomorrow's possibility.",
     "End of shift. The plant runs itself for a moment.",
     "Bolt sees it differently. But Bolt agrees it's something.",
     "From here, you can see everything we've kept running.",
     "The flares burn like promises we actually kept.",
     "He stood here on his first day. He stands here still.",
     "The horizon belongs to the work.",
     "Sunset on the refinery — it's the only painting I need.",
     "After everything, you need a moment to just look.",
     "They say beauty is in the eye of the beholder. I behold this.",
     "The tanks, the towers, the pipes — all ours to tend.",
     "In thirty years I have not tired of this view.",
     "The light hits the steel and reminds us what we're for.",
     "Tomorrow it starts again. Tonight, we watch.",
     "Even machines deserve a moment of quiet.",
     "This is what an honest day's work looks like from above.",
     "The plant hums below. We breathe above it all."],
    ["The needle tells the truth. My job is to listen.",
     "An analog gauge in a digital world — still the most honest thing here.",
     "If the pressure drops, we notice. That's the whole job.",
     "Bolt lights the way. I write down what we find.",
     "Every reading recorded. Every anomaly investigated.",
     "The old instruments know things the new ones forgot.",
     "He reads the gauge like a doctor reads a patient.",
     "Notes, numbers, and the quiet certainty of knowledge.",
     "Pressure: nominal. Trust: earned.",
     "In the dark corner, the answer is always hiding.",
     "The flashlight cuts through what the numbers leave out.",
     "We check every dial. We trust nothing we haven't verified.",
     "This gauge has been here longer than I have. I respect it.",
     "The pen is mightier when the plant is on the line.",
     "Bolt's beam finds what my eyes miss.",
     "The difference between an incident and a shift is in the details.",
     "Every notation in this clipboard is someone's safety.",
     "He inspects carefully. Bolt assists without complaint.",
     "The gauge has seen everything. So has he.",
     "Numbers on paper. Lives in the balance. Same clipboard."],
    ["Rain doesn't stop the work. It just makes it colder.",
     "The blueprints are getting wet. We are committed.",
     "He knows where every valve is, even in the dark.",
     "The broken joint doesn't care about the weather.",
     "In the rain, problems become very clear very fast.",
     "Bolt doesn't mind the rain. Bolt minds the rust.",
     "We've fixed worse in worse weather.",
     "The water makes everything heavier. We lift it anyway.",
     "A wrench, a flashlight, and determination.",
     "The plant doesn't pause for weather. Neither do we.",
     "The valve won't fix itself. So here we are.",
     "The blueprint is a map to somewhere better.",
     "Even the pipes look cold in this rain.",
     "Small robot, large ambition, one broken valve.",
     "Mud, rain, oil — the textures of honest work.",
     "He reads the plan. I hold the light. We both get wet.",
     "The storm is temporary. The fix is permanent.",
     "Water on steel on blueprints on hands.",
     "Every broken valve is an opportunity to learn something.",
     "After the rain, the plant runs better. It's worth it."],
]

SKY_VARIANTS = [
    ('#3D1C02', '#D4A017', '#C0632B'),
    ('#1A0805', '#4A2010', '#8B4020'),
    ('#2A1208', '#C07820', '#D4920A'),
    ('#0D0500', '#2A1208', '#6B3E1A'),
    ('#4A2810', '#D4920A', '#F5DEB3'),
]


def v(base, vi, amp):
    return base + amp * math.sin(vi * 1.618)


def make_params(idx):
    scene_idx = idx // 20
    var_idx = idx % 20
    rng = random.Random(idx * 37 + 13)
    return {
        'idx': idx, 'scene_idx': scene_idx, 'var_idx': var_idx, 'rng': rng,
        'sky': SKY_VARIANTS[var_idx % 5],
        'eng_pose': var_idx % 3,
        'bot_pose': (var_idx + 1) % 3,
        'grain_freq': 0.55 + 0.025 * (var_idx % 10),
        'gauge_angle': 30 + var_idx * 12,
        'caption': CAPTIONS[scene_idx][var_idx],
        'panel_num': idx + 1,
        'rain_count': 80 + var_idx * 3,
        'spark_count': 22 + var_idx * 2,
        'sub_variant': var_idx < 10,
    }


def build_defs(params):
    gf = params['grain_freq']
    s1, s2, s3 = params['sky']
    return f'''<defs>
  <filter id="f-grain" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency="{gf:.3f}" numOctaves="3" stitchTiles="stitch" result="noise"/>
    <feColorMatrix type="saturate" values="0" in="noise" result="gn"/>
    <feBlend in="SourceGraphic" in2="gn" mode="multiply" result="blend"/>
    <feComposite in="blend" in2="SourceGraphic" operator="in"/>
  </filter>
  <filter id="f-glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="8" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="f-sglow" x="-25%" y="-25%" width="150%" height="150%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="f-shadow">
    <feDropShadow dx="3" dy="4" stdDeviation="5" flood-color="{C['ink']}" flood-opacity="0.7"/>
  </filter>
  <linearGradient id="g-sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{s1}"/>
    <stop offset="60%" stop-color="{s2}"/>
    <stop offset="100%" stop-color="{s3}"/>
  </linearGradient>
  <linearGradient id="g-pipe" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{C['smoke']}"/>
    <stop offset="35%" stop-color="{C['sepia_mid']}"/>
    <stop offset="100%" stop-color="{C['sepia_dark']}"/>
  </linearGradient>
  <linearGradient id="g-panel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{C['sepia_mid']}"/>
    <stop offset="100%" stop-color="{C['ink']}"/>
  </linearGradient>
  <radialGradient id="g-sun" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{C['cream']}" stop-opacity="0.95"/>
    <stop offset="40%" stop-color="{C['golden']}" stop-opacity="0.7"/>
    <stop offset="100%" stop-color="{C['rust']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="g-weld" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#FFFFFF"/>
    <stop offset="35%" stop-color="{C['golden']}" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="{C['rust']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="g-crt" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{C['glow_green']}" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="{C['glow_green']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="g-vignette" cx="50%" cy="50%" r="70%">
    <stop offset="55%" stop-color="{C['ink']}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{C['ink']}" stop-opacity="0.8"/>
  </radialGradient>
  <linearGradient id="g-flash" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{C['cream']}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{C['golden']}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="p-hatch" width="8" height="8" patternUnits="userSpaceOnUse">
    <line x1="0" y1="8" x2="8" y2="0" stroke="{C['sepia_dark']}" stroke-width="0.6" opacity="0.35"/>
  </pattern>
  <pattern id="p-grate" width="20" height="20" patternUnits="userSpaceOnUse">
    <rect width="20" height="20" fill="{C['sepia_dark']}"/>
    <line x1="0" y1="0" x2="20" y2="0" stroke="{C['sepia_mid']}" stroke-width="1"/>
    <line x1="0" y1="0" x2="0" y2="20" stroke="{C['sepia_mid']}" stroke-width="1"/>
  </pattern>
</defs>'''


def draw_engineer(cx, cy, pose=0, direction='right'):
    cx, cy = int(cx), int(cy)
    arm_r = [-20, 55, -40][pose % 3]
    arm_l = [15, -15, 35][pose % 3]
    e = []

    # Boots
    e.append(f'<rect x="{cx-20}" y="{cy-26}" width="16" height="26" rx="3" fill="{C["ink"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx+4}" y="{cy-26}" width="16" height="26" rx="3" fill="{C["ink"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # Pants
    e.append(f'<rect x="{cx-18}" y="{cy-88}" width="14" height="64" fill="{C["denim"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx+4}" y="{cy-88}" width="14" height="64" fill="{C["denim"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # Belt
    e.append(f'<rect x="{cx-22}" y="{cy-96}" width="44" height="11" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx-5}" y="{cy-95}" width="10" height="9" fill="{C["golden"]}" rx="1"/>')
    # Torso
    e.append(f'<rect x="{cx-24}" y="{cy-172}" width="48" height="78" rx="4" fill="{C["denim"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<rect x="{cx+4}" y="{cy-162}" width="14" height="17" rx="2" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1"/>')
    # Right arm
    ra = math.radians(arm_r)
    ax1, ay1 = cx+24, cy-152
    ax2, ay2 = ax1 + 55*math.sin(ra), ay1 + 55*math.cos(ra)
    e.append(f'<line x1="{ax1:.0f}" y1="{ay1:.0f}" x2="{ax2:.0f}" y2="{ay2:.0f}" stroke="{C["denim"]}" stroke-width="14" stroke-linecap="round"/>')
    e.append(f'<line x1="{ax1:.0f}" y1="{ay1:.0f}" x2="{ax2:.0f}" y2="{ay2:.0f}" stroke="{C["ink"]}" stroke-width="1.5" fill="none" stroke-linecap="round"/>')
    e.append(f'<circle cx="{ax2:.0f}" cy="{ay2:.0f}" r="7" fill="{C["skin"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # Left arm
    la = math.radians(arm_l)
    lx1, ly1 = cx-24, cy-152
    lx2, ly2 = lx1 - 55*math.sin(la), ly1 + 55*math.cos(la)
    e.append(f'<line x1="{lx1:.0f}" y1="{ly1:.0f}" x2="{lx2:.0f}" y2="{ly2:.0f}" stroke="{C["denim"]}" stroke-width="14" stroke-linecap="round"/>')
    e.append(f'<line x1="{lx1:.0f}" y1="{ly1:.0f}" x2="{lx2:.0f}" y2="{ly2:.0f}" stroke="{C["ink"]}" stroke-width="1.5" fill="none" stroke-linecap="round"/>')
    e.append(f'<circle cx="{lx2:.0f}" cy="{ly2:.0f}" r="7" fill="{C["skin"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # Neck
    e.append(f'<rect x="{cx-8}" y="{cy-190}" width="16" height="20" fill="{C["skin"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # Head
    e.append(f'<ellipse cx="{cx}" cy="{cy-212}" rx="22" ry="24" fill="{C["skin"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    # Eyes
    e.append(f'<circle cx="{cx-7}" cy="{cy-215}" r="3" fill="{C["ink"]}"/>')
    e.append(f'<circle cx="{cx+7}" cy="{cy-215}" r="3" fill="{C["ink"]}"/>')
    # Wrinkles
    e.append(f'<line x1="{cx-3}" y1="{cy-222}" x2="{cx+3}" y2="{cy-220}" stroke="{C["sepia_dark"]}" stroke-width="0.8" opacity="0.6"/>')
    # Beard polygon
    bx, by = cx, cy-204
    beard = f'{bx-18},{by-4} {bx-20},{by+8} {bx-12},{by+20} {bx},{by+22} {bx+12},{by+20} {bx+20},{by+8} {bx+18},{by-4} {bx+9},{by} {bx},{by+2} {bx-9},{by}'
    e.append(f'<polygon points="{beard}" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # Mustache
    mpts = f'{bx-11},{by-2} {bx-7},{by+4} {bx},{by+2} {bx+7},{by+4} {bx+11},{by-2} {bx+7},{by-3} {bx},{by-1} {bx-7},{by-3}'
    e.append(f'<polygon points="{mpts}" fill="{C["ink"]}" opacity="0.85"/>')
    # Hard hat dome + brim
    e.append(f'<ellipse cx="{cx}" cy="{cy-233}" rx="26" ry="16" fill="{C["hat"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<ellipse cx="{cx}" cy="{cy-222}" rx="30" ry="7" fill="{C["hat"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<ellipse cx="{cx-7}" cy="{cy-238}" rx="8" ry="4" fill="{C["cream"]}" opacity="0.35"/>')

    if direction == 'left':
        return f'<g transform="scale(-1,1) translate({-2*cx},0)">\n' + '\n'.join(e) + '\n</g>'
    return '\n'.join(e)


def draw_robot(cx, cy, pose=0, direction='right'):
    cx, cy = int(cx), int(cy)
    e = []
    # Treads
    e.append(f'<rect x="{cx-28}" y="{cy-14}" width="22" height="14" rx="4" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<rect x="{cx+6}" y="{cy-14}" width="22" height="14" rx="4" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    for i in range(4):
        e.append(f'<line x1="{cx-25+i*6}" y1="{cy-13}" x2="{cx-25+i*6}" y2="{cy-2}" stroke="{C["ink"]}" stroke-width="0.8" opacity="0.5"/>')
        e.append(f'<line x1="{cx+9+i*6}" y1="{cy-13}" x2="{cx+9+i*6}" y2="{cy-2}" stroke="{C["ink"]}" stroke-width="0.8" opacity="0.5"/>')
    # Lower chassis
    e.append(f'<rect x="{cx-25}" y="{cy-70}" width="50" height="58" rx="5" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    e.append(f'<rect x="{cx-12}" y="{cy-58}" width="24" height="30" rx="3" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<circle cx="{cx}" cy="{cy-72}" r="4" fill="{C["rust"]}" stroke="{C["ink"]}" stroke-width="1"/>')
    # Upper body
    e.append(f'<rect x="{cx-20}" y="{cy-106}" width="40" height="38" rx="4" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    # Head
    e.append(f'<rect x="{cx-19}" y="{cy-138}" width="38" height="34" rx="6" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    # Binocular eyes
    e.append(f'<circle cx="{cx-7}" cy="{cy-123}" r="10" fill="{C["ink"]}" stroke="{C["pipe_hi"]}" stroke-width="2"/>')
    e.append(f'<circle cx="{cx+7}" cy="{cy-123}" r="10" fill="{C["ink"]}" stroke="{C["pipe_hi"]}" stroke-width="2"/>')
    e.append(f'<circle cx="{cx-7}" cy="{cy-123}" r="6" fill="{C["glow_green"]}" opacity="0.85"/>')
    e.append(f'<circle cx="{cx+7}" cy="{cy-123}" r="6" fill="{C["glow_green"]}" opacity="0.85"/>')
    e.append(f'<circle cx="{cx-10}" cy="{cy-126}" r="2" fill="{C["cream"]}" opacity="0.9"/>')
    e.append(f'<circle cx="{cx+4}" cy="{cy-126}" r="2" fill="{C["cream"]}" opacity="0.9"/>')
    # Antenna
    e.append(f'<line x1="{cx}" y1="{cy-138}" x2="{cx}" y2="{cy-158}" stroke="{C["sepia_mid"]}" stroke-width="2"/>')
    e.append(f'<circle cx="{cx}" cy="{cy-161}" r="4" fill="{C["golden"]}" stroke="{C["ink"]}" stroke-width="1"/>')
    # Arms (pose: 0=down, 1=right up, 2=left forward)
    arm_angles = [(80, 80), (25, 80), (80, 30)]
    ra, la = arm_angles[pose % 3]
    rx_a = math.radians(ra)
    ax1, ay1 = cx+20, cy-95
    ax2, ay2 = ax1 + 38*math.sin(rx_a), ay1 + 38*math.cos(rx_a)
    e.append(f'<line x1="{ax1:.0f}" y1="{ay1:.0f}" x2="{ax2:.0f}" y2="{ay2:.0f}" stroke="{C["sepia_mid"]}" stroke-width="10" stroke-linecap="round"/>')
    e.append(f'<line x1="{ax1:.0f}" y1="{ay1:.0f}" x2="{ax2:.0f}" y2="{ay2:.0f}" stroke="{C["ink"]}" stroke-width="1.5" fill="none" stroke-linecap="round"/>')
    lx_a = math.radians(la)
    lax1, lay1 = cx-20, cy-95
    lax2, lay2 = lax1 - 38*math.sin(lx_a), lay1 + 38*math.cos(lx_a)
    e.append(f'<line x1="{lax1:.0f}" y1="{lay1:.0f}" x2="{lax2:.0f}" y2="{lay2:.0f}" stroke="{C["sepia_mid"]}" stroke-width="10" stroke-linecap="round"/>')
    e.append(f'<line x1="{lax1:.0f}" y1="{lay1:.0f}" x2="{lax2:.0f}" y2="{lay2:.0f}" stroke="{C["ink"]}" stroke-width="1.5" fill="none" stroke-linecap="round"/>')

    if direction == 'left':
        return f'<g transform="scale(-1,1) translate({-2*cx},0)">\n' + '\n'.join(e) + '\n</g>'
    return '\n'.join(e)


def draw_wrench(cx, cy, angle=0):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    def r(x, y): return cx+x*c-y*s, cy+x*s+y*c
    x1,y1 = r(0,-28); x2,y2 = r(0,28)
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{C["sepia_mid"]}" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="9" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="2"/>'
            f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="5" fill="{C["ink"]}"/>'
            f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="7" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="2"/>'
            f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{C["ink"]}" stroke-width="2" stroke-linecap="round" fill="none"/>')


def draw_coffee_mug(cx, cy):
    return (f'<rect x="{cx-10}" y="{cy-20}" width="20" height="22" rx="2" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="2"/>'
            f'<rect x="{cx-8}" y="{cy-18}" width="16" height="5" fill="{C["sepia_dark"]}" rx="1"/>'
            f'<path d="M{cx+10},{cy-12} Q{cx+18},{cy-10} {cx+18},{cy-5} Q{cx+18},{cy+1} {cx+10},{cy+1}" fill="none" stroke="{C["ink"]}" stroke-width="2"/>')


def draw_steam(cx, cy, count=3):
    e = []
    for i in range(count):
        ox = cx + (i - count//2) * 8
        pts = f'M{ox},{cy}'
        y = cy
        for j in range(4):
            xo = 6 * math.sin(j*1.3 + i*0.8)
            pts += f' Q{ox+xo:.0f},{y-12} {ox:.0f},{y-24}'
            y -= 24
        e.append(f'<path d="{pts}" fill="none" stroke="{C["cream"]}" stroke-width="1.8" opacity="{0.08+i*0.04:.2f}" stroke-linecap="round"/>')
    return '\n'.join(e)


def draw_pipes(ys, width=1200):
    e = []
    for i, y in enumerate(ys):
        h = 18 + (i % 3)*6
        e.append(f'<rect x="0" y="{y}" width="{width}" height="{h}" fill="url(#g-pipe)" stroke="{C["ink"]}" stroke-width="1.5"/>')
        e.append(f'<line x1="0" y1="{y+2}" x2="{width}" y2="{y+2}" stroke="{C["pipe_hi"]}" stroke-width="1.5" opacity="0.55"/>')
        for fx in range(0, width, 185 + i*22):
            fw = 12
            e.append(f'<rect x="{fx-fw//2}" y="{y-4}" width="{fw}" height="{h+8}" rx="2" fill="{C["amber"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    return '\n'.join(e)


def draw_towers(x0, y_base, count, rng):
    e = []
    x = x0
    for i in range(count):
        tw = rng.randint(12, 24)
        th = rng.randint(90, 260)
        tx = x + rng.randint(-15, 15)
        ty = y_base - th
        e.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1"/>')
        for py in range(ty+40, y_base, rng.randint(45,75)):
            pw = tw*2
            e.append(f'<rect x="{tx-pw//4}" y="{py}" width="{pw}" height="4" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="0.8"/>')
        if rng.random() > 0.4:
            e.append(f'<ellipse cx="{tx+tw//2}" cy="{ty-8}" rx="5" ry="11" fill="{C["golden"]}" opacity="0.75" filter="url(#f-sglow)"/>')
        x += rng.randint(55, 110)
    return '\n'.join(e)


def draw_control_console(x, y, width, crt_count, rng):
    e = []
    h = 200
    e.append(f'<rect x="{x}" y="{y}" width="{width}" height="{h}" fill="url(#g-panel)" stroke="{C["ink"]}" stroke-width="3"/>')
    e.append(f'<rect x="{x}" y="{y}" width="{width}" height="18" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1"/>')
    crt_w = min(110, (width - 40) // crt_count - 8)
    for i in range(crt_count):
        cx = x + 20 + i * (crt_w + 10)
        cy = y + 28
        ch = int(crt_w * 0.72)
        e.append(f'<rect x="{cx}" y="{cy}" width="{crt_w}" height="{ch}" rx="5" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="2"/>')
        sx, sy, sw, sh = cx+5, cy+5, crt_w-10, ch-10
        e.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="3" fill="{C["glow_green"]}" opacity="0.65"/>')
        e.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="3" fill="url(#g-crt)" filter="url(#f-sglow)"/>')
        for sl in range(sy+4, sy+sh, 4):
            e.append(f'<line x1="{sx+2}" y1="{sl}" x2="{sx+sw-2}" y2="{sl}" stroke="{C["ink"]}" stroke-width="0.5" opacity="0.25"/>')
        for dl in range(3):
            dly = sy + 8 + dl*(sh//4)
            dlw = rng.randint(sw//4, sw-6)
            e.append(f'<line x1="{sx+3}" y1="{dly}" x2="{sx+3+dlw}" y2="{dly}" stroke="{C["cream"]}" stroke-width="1.5" opacity="0.7"/>')
    gy = y + 148
    for gi in range(min(7, width//55)):
        gx = x + 28 + gi * (width//7)
        r = 17
        e.append(f'<circle cx="{gx}" cy="{gy}" r="{r}" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="2"/>')
        for t in range(8):
            ta = math.radians(-135 + t*38.5)
            e.append(f'<line x1="{gx+(r-5)*math.cos(ta):.0f}" y1="{gy+(r-5)*math.sin(ta):.0f}" x2="{gx+r*math.cos(ta):.0f}" y2="{gy+r*math.sin(ta):.0f}" stroke="{C["ink"]}" stroke-width="1.5"/>')
        na = math.radians(-135 + rng.randint(20,240))
        e.append(f'<line x1="{gx}" y1="{gy}" x2="{gx+(r-5)*math.cos(na):.0f}" y2="{gy+(r-5)*math.sin(na):.0f}" stroke="{C["rust"]}" stroke-width="2"/>')
        e.append(f'<circle cx="{gx}" cy="{gy}" r="3" fill="{C["ink"]}"/>')
    return '\n'.join(e)


def draw_armchair(cx, cy):
    cx, cy = int(cx), int(cy)
    e = []
    e.append(f'<rect x="{cx-50}" y="{cy-38}" width="100" height="58" rx="10" fill="{C["rust"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    e.append(f'<rect x="{cx-44}" y="{cy-32}" width="88" height="52" rx="8" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx-48}" y="{cy-138}" width="96" height="103" rx="12" fill="{C["rust"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    e.append(f'<rect x="{cx-42}" y="{cy-132}" width="84" height="93" rx="10" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx-65}" y="{cy-98}" width="22" height="62" rx="8" fill="{C["rust"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    e.append(f'<rect x="{cx+43}" y="{cy-98}" width="22" height="62" rx="8" fill="{C["rust"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    for lx in [cx-40, cx-10, cx+10, cx+40]:
        e.append(f'<rect x="{lx-4}" y="{cy+18}" width="8" height="22" rx="2" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx-40}" y="{cy-32}" width="80" height="50" rx="8" fill="url(#p-hatch)" opacity="0.4"/>')
    return '\n'.join(e)


def draw_pressure_gauge(cx, cy, r, reading_angle):
    cx, cy, r = int(cx), int(cy), int(r)
    e = []
    e.append(f'<circle cx="{cx}" cy="{cy}" r="{r+14}" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="3"/>')
    e.append(f'<circle cx="{cx}" cy="{cy}" r="{r+9}" fill="{C["metal"]}" stroke="{C["pipe_hi"]}" stroke-width="2"/>')
    e.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    for t in range(25):
        ta = math.radians(-135 + t*(270/24))
        major = t % 4 == 0
        tl = 16 if major else 9
        e.append(f'<line x1="{cx+(r-tl)*math.cos(ta):.0f}" y1="{cy+(r-tl)*math.sin(ta):.0f}" x2="{cx+(r-3)*math.cos(ta):.0f}" y2="{cy+(r-3)*math.sin(ta):.0f}" stroke="{C["ink"]}" stroke-width="{2 if major else 1}"/>')
        if major:
            val = t*(300//24)
            lx = cx+(r-26)*math.cos(ta)
            ly = cy+(r-26)*math.sin(ta)
            e.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" dominant-baseline="middle" font-family="serif" font-size="11" fill="{C["sepia_dark"]}">{val}</text>')
    e.append(f'<text x="{cx}" y="{cy+r//3}" text-anchor="middle" font-family="serif" font-size="13" font-style="italic" fill="{C["sepia_dark"]}">PSI</text>')
    # Danger arc
    arc_pts = []
    for ti in range(20):
        ta = math.radians(-135 + 246 + ti*(24/19))
        arc_pts.append(f'{cx+(r-5)*math.cos(ta):.0f},{cy+(r-5)*math.sin(ta):.0f}')
    e.append(f'<polyline points="{" ".join(arc_pts)}" fill="none" stroke="{C["rust"]}" stroke-width="9" stroke-linecap="round" opacity="0.65"/>')
    na = math.radians(-135 + min(reading_angle, 268))
    e.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+(r-18)*math.cos(na):.0f}" y2="{cy+(r-18)*math.sin(na):.0f}" stroke="{C["rust"]}" stroke-width="4" stroke-linecap="round"/>')
    e.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{C["ink"]}"/>')
    ga1, ga2 = math.radians(-80), math.radians(-25)
    e.append(f'<line x1="{cx+(r-18)*math.cos(ga1):.0f}" y1="{cy+(r-18)*math.sin(ga1):.0f}" x2="{cx+(r-10)*math.cos(ga2):.0f}" y2="{cy+(r-10)*math.sin(ga2):.0f}" stroke="white" stroke-width="3" opacity="0.3" stroke-linecap="round"/>')
    for ba in [45, 135, 225, 315]:
        bra = math.radians(ba)
        e.append(f'<circle cx="{cx+(r+7)*math.cos(bra):.0f}" cy="{cy+(r+7)*math.sin(bra):.0f}" r="5" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    return '\n'.join(e)


def draw_clipboard(cx, cy, angle=0):
    cx, cy = int(cx), int(cy)
    return (f'<g transform="rotate({angle},{cx},{cy})">'
            f'<rect x="{cx-22}" y="{cy-35}" width="44" height="55" rx="3" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="2"/>'
            f'<rect x="{cx-8}" y="{cy-40}" width="16" height="10" rx="3" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="1.5"/>'
            f'<line x1="{cx-16}" y1="{cy-20}" x2="{cx+16}" y2="{cy-20}" stroke="{C["sepia_mid"]}" stroke-width="1"/>'
            f'<line x1="{cx-16}" y1="{cy-10}" x2="{cx+16}" y2="{cy-10}" stroke="{C["sepia_mid"]}" stroke-width="1"/>'
            f'<line x1="{cx-16}" y1="{cy}" x2="{cx+10}" y2="{cy}" stroke="{C["sepia_mid"]}" stroke-width="1"/>'
            f'<line x1="{cx-16}" y1="{cy+10}" x2="{cx+14}" y2="{cy+10}" stroke="{C["sepia_mid"]}" stroke-width="1"/>'
            f'</g>')


def draw_flashlight_beam(fx, fy, tx, ty, width=120):
    dx, dy = tx-fx, ty-fy
    length = math.sqrt(dx*dx+dy*dy)
    if length < 1: return ''
    px, py = -dy/length*width/2, dx/length*width/2
    p1x,p1y = fx+px*0.1, fy+py*0.1
    p2x,p2y = fx-px*0.1, fy-py*0.1
    return f'<polygon points="{p1x:.0f},{p1y:.0f} {p2x:.0f},{p2y:.0f} {tx-px:.0f},{ty-py:.0f} {tx+px:.0f},{ty+py:.0f}" fill="url(#g-flash)" opacity="0.45"/>'


def draw_catwalk(y_l, y_r, x1=0, x2=1200):
    e = []
    e.append(f'<line x1="{x1}" y1="{y_l-38}" x2="{x2}" y2="{y_r-38}" stroke="{C["sepia_mid"]}" stroke-width="5"/>')
    e.append(f'<line x1="{x1}" y1="{y_l}" x2="{x2}" y2="{y_r}" stroke="{C["sepia_mid"]}" stroke-width="8"/>')
    e.append(f'<line x1="{x1}" y1="{y_l+80}" x2="{x2}" y2="{y_r+80}" stroke="{C["sepia_mid"]}" stroke-width="8"/>')
    for t in range(11):
        frac = t/10
        fx = int(x1 + (x2-x1)*frac)
        fy_top = int(y_l - 38 + (y_r-y_l)*frac)
        fy_bot = int(y_l + 80 + (y_r-y_l)*frac)
        e.append(f'<line x1="{fx}" y1="{fy_top}" x2="{fx}" y2="{fy_bot}" stroke="{C["sepia_dark"]}" stroke-width="2"/>')
        if t < 10:
            fx2 = int(x1 + (x2-x1)*(t+1)/10)
            fy_top2 = int(y_l - 38 + (y_r-y_l)*(t+1)/10)
            e.append(f'<line x1="{fx}" y1="{fy_bot}" x2="{fx2}" y2="{fy_top2}" stroke="{C["sepia_dark"]}" stroke-width="1.5" opacity="0.6"/>')
    for t in range(0, 11, 2):
        frac = t/10
        fx = int(x1 + (x2-x1)*frac)
        fy_top = int(y_l-38+(y_r-y_l)*frac)
        fy_bot = int(y_l+80+(y_r-y_l)*frac)
        e.append(f'<line x1="{fx}" y1="{fy_top-55}" x2="{fx}" y2="{fy_bot}" stroke="{C["sepia_mid"]}" stroke-width="4" stroke-linecap="round"/>')
    return '\n'.join(e)


def draw_pipe_joint(cx, cy, pr=45):
    cx, cy, pr = int(cx), int(cy), int(pr)
    e = []
    e.append(f'<rect x="0" y="{cy-pr}" width="{cx-18}" height="{pr*2}" fill="url(#g-pipe)" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<line x1="0" y1="{cy-pr+3}" x2="{cx-18}" y2="{cy-pr+3}" stroke="{C["pipe_hi"]}" stroke-width="2" opacity="0.55"/>')
    e.append(f'<rect x="{cx+18}" y="{cy-pr}" width="{1200-cx-18}" height="{pr*2}" fill="url(#g-pipe)" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<line x1="{cx+18}" y1="{cy-pr+3}" x2="1200" y2="{cy-pr+3}" stroke="{C["pipe_hi"]}" stroke-width="2" opacity="0.55"/>')
    fr = pr + 18
    e.append(f'<ellipse cx="{cx-13}" cy="{cy}" rx="11" ry="{fr}" fill="{C["amber"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    e.append(f'<ellipse cx="{cx+13}" cy="{cy}" rx="11" ry="{fr}" fill="{C["amber"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    for by_ in [cy-fr+10, cy-fr//2, cy, cy+fr//2, cy+fr-10]:
        e.append(f'<circle cx="{cx-13}" cy="{by_}" r="5" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
        e.append(f'<circle cx="{cx+13}" cy="{by_}" r="5" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    return '\n'.join(e)


def draw_welding_arc(cx, cy, spark_count, rng):
    cx, cy = int(cx), int(cy)
    e = []
    e.append(f'<circle cx="{cx}" cy="{cy}" r="32" fill="url(#g-weld)" filter="url(#f-glow)"/>')
    e.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="white" opacity="0.95"/>')
    cols = [C['golden'], C['cream'], C['amber'], C['rust'], '#FFFFFF']
    for i in range(spark_count):
        sa = rng.uniform(0, 2*math.pi)
        sl = rng.uniform(14, 85)
        ex, ey = cx+sl*math.cos(sa), cy+sl*math.sin(sa)
        col = rng.choice(cols)
        op = rng.uniform(0.35, 1.0)
        sw = rng.uniform(0.5, 2.2)
        e.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.0f}" y2="{ey:.0f}" stroke="{col}" stroke-width="{sw:.1f}" opacity="{op:.2f}"/>')
    for i in range(spark_count//2):
        sa = rng.uniform(0, 2*math.pi)
        sl = rng.uniform(28, 110)
        px, py = cx+sl*math.cos(sa), cy+sl*math.sin(sa)
        e.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{rng.uniform(1,3.5):.1f}" fill="{rng.choice(cols)}" opacity="{rng.uniform(0.25,0.85):.2f}"/>')
    return '\n'.join(e)


def draw_railing(x1, y1, x2, y2, posts=9):
    e = []
    e.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["sepia_mid"]}" stroke-width="6"/>')
    e.append(f'<line x1="{x1}" y1="{y1+24}" x2="{x2}" y2="{y2+24}" stroke="{C["sepia_mid"]}" stroke-width="3"/>')
    for i in range(posts+1):
        px = int(x1 + (x2-x1)*i/posts)
        py = int(y1 + (y2-y1)*i/posts)
        e.append(f'<line x1="{px}" y1="{py}" x2="{px}" y2="{py+58}" stroke="{C["sepia_mid"]}" stroke-width="4"/>')
    return '\n'.join(e)


def draw_rain(count, rng):
    e = []
    for _ in range(count):
        rx = rng.uniform(0,1200); ry = rng.uniform(0,900)
        length = rng.uniform(14,38)
        ang = math.radians(rng.uniform(73,88))
        ex, ey = rx+length*math.sin(ang), ry+length*math.cos(ang)
        e.append(f'<line x1="{rx:.0f}" y1="{ry:.0f}" x2="{ex:.0f}" y2="{ey:.0f}" stroke="{C["smoke"]}" stroke-width="0.75" opacity="{rng.uniform(0.12,0.45):.2f}"/>')
    return '\n'.join(e)


def draw_puddles(count, rng):
    e = []
    for _ in range(count):
        px = rng.uniform(80,1120); py = rng.uniform(690,820)
        rx = rng.uniform(18,55); ry = rng.uniform(4,16)
        e.append(f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1" opacity="0.55"/>')
        e.append(f'<ellipse cx="{px-rx*0.2:.0f}" cy="{py:.0f}" rx="{rx*0.28:.0f}" ry="{ry*0.38:.0f}" fill="{C["golden"]}" opacity="0.28"/>')
    return '\n'.join(e)


def draw_blueprints(cx, cy):
    cx, cy = int(cx), int(cy)
    e = []
    e.append(f'<rect x="{cx-60}" y="{cy-38}" width="120" height="78" rx="3" fill="{C["blueprint"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    for i in range(6):
        ly = cy-26+i*11
        e.append(f'<line x1="{cx-50}" y1="{ly}" x2="{cx+50}" y2="{ly}" stroke="white" stroke-width="0.8" opacity="0.45"/>')
    e.append(f'<rect x="{cx-40}" y="{cy-8}" width="80" height="12" fill="none" stroke="white" stroke-width="1.4" opacity="0.65"/>')
    e.append(f'<circle cx="{cx-28}" cy="{cy-2}" r="6" fill="none" stroke="white" stroke-width="1.4" opacity="0.65"/>')
    e.append(f'<ellipse cx="{cx-60}" cy="{cy}" rx="6" ry="38" fill="{C["blueprint"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<ellipse cx="{cx+60}" cy="{cy}" rx="6" ry="38" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    return '\n'.join(e)


def draw_valve_assembly(cx, cy, broken=False):
    cx, cy = int(cx), int(cy)
    e = []
    e.append(f'<rect x="{cx-80}" y="{cy-14}" width="160" height="28" fill="url(#g-pipe)" stroke="{C["ink"]}" stroke-width="2"/>')
    e.append(f'<rect x="{cx-25}" y="{cy-33}" width="50" height="47" rx="5" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="2.5"/>')
    e.append(f'<circle cx="{cx}" cy="{cy-48}" r="21" fill="none" stroke="{C["sepia_mid"]}" stroke-width="4"/>')
    for sa in [0,60,120,180,240,300]:
        a = math.radians(sa)
        e.append(f'<line x1="{cx}" y1="{cy-48}" x2="{cx+19*math.cos(a):.0f}" y2="{cy-48+19*math.sin(a):.0f}" stroke="{C["sepia_mid"]}" stroke-width="3"/>')
    e.append(f'<circle cx="{cx}" cy="{cy-48}" r="6" fill="{C["amber"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="{cx-4}" y="{cy-48}" width="8" height="18" fill="{C["sepia_mid"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    if broken:
        for i in range(5):
            e.append(f'<circle cx="{cx+(i-2)*5}" cy="{cy+14+i*11}" r="{3.5-i*0.5:.1f}" fill="{C["sepia_dark"]}" opacity="0.65"/>')
        e.append(f'<line x1="{cx-10}" y1="{cy}" x2="{cx+10}" y2="{cy}" stroke="{C["golden"]}" stroke-width="2" stroke-dasharray="3,2" opacity="0.75"/>')
    return '\n'.join(e)


def draw_panel_chrome(params):
    caption = params['caption'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
    num = params['panel_num']
    return f'''<g id="chrome">
  <rect x="8" y="8" width="1184" height="884" fill="none" stroke="{C["ink"]}" stroke-width="8"/>
  <rect x="16" y="16" width="1168" height="868" fill="none" stroke="{C["golden"]}" stroke-width="1.5" opacity="0.65"/>
  <rect x="8" y="826" width="1184" height="66" fill="{C["ink"]}" opacity="0.9"/>
  <line x1="8" y1="826" x2="1192" y2="826" stroke="{C["golden"]}" stroke-width="1.5" opacity="0.75"/>
  <text x="600" y="862" text-anchor="middle" dominant-baseline="middle"
    font-family="Georgia,serif" font-style="italic" font-size="16"
    fill="{C["cream"]}" opacity="0.93">{caption}</text>
  <rect x="14" y="14" width="50" height="28" rx="3" fill="{C["ink"]}" opacity="0.85"/>
  <text x="39" y="31" text-anchor="middle" dominant-baseline="middle"
    font-family="Georgia,serif" font-size="13" font-weight="bold"
    fill="{C["golden"]}">{num:03d}</text>
  <rect x="0" y="0" width="1200" height="900" fill="url(#g-vignette)"/>
</g>'''


# ─── SCENES ──────────────────────────────────────────────────────────────────

def scene_control_room(p):
    rng = p['rng']; vi = p['var_idx']
    crt_count = 3 + vi % 4
    e = []
    e.append(f'<rect x="0" y="0" width="1200" height="900" fill="{C["ink"]}"/>')
    e.append(f'<rect x="0" y="0" width="1200" height="820" fill="{C["sepia_dark"]}"/>')
    for wx in range(0, 1200, 120):
        e.append(f'<line x1="{wx}" y1="0" x2="{wx}" y2="820" stroke="{C["ink"]}" stroke-width="1.5" opacity="0.35"/>')
    glow_x = int(400 + v(0, vi, 200))
    e.append(f'<ellipse cx="{glow_x}" cy="300" rx="380" ry="280" fill="{C["glow_green"]}" opacity="0.055" filter="url(#f-glow)"/>')
    e.append(draw_pipes([int(y + v(0, vi, 14)) for y in [80, 128, 162]]))
    e.append(draw_control_console(80, 350, 900, crt_count, rng))
    e.append(f'<rect x="0" y="758" width="1200" height="142" fill="{C["sepia_dark"]}"/>')
    for fx in range(0, 1200, 80):
        e.append(f'<line x1="{fx}" y1="758" x2="{fx}" y2="900" stroke="{C["ink"]}" stroke-width="0.8" opacity="0.25"/>')
    e.append(f'<rect x="0" y="756" width="1200" height="5" fill="{C["sepia_mid"]}" opacity="0.45"/>')
    chair_x = int(500 + v(0, vi, 80))
    e.append(draw_armchair(chair_x, 760))
    e.append(draw_engineer(chair_x+5, 742, pose=p['eng_pose']))
    e.append(draw_coffee_mug(chair_x+40, 742-155))
    e.append(draw_steam(chair_x+40, 742-175, count=3))
    bot_x = int(chair_x - 95 + v(0, vi, 28))
    e.append(draw_robot(bot_x, 750, pose=p['bot_pose']))
    e.append(draw_wrench(bot_x+32, 750-78, angle=32))
    tc_x = int(1000 + v(0, vi, 38))
    e.append(f'<rect x="{tc_x}" y="558" width="118" height="200" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    for dr in range(4):
        e.append(f'<rect x="{tc_x+10}" y="{568+dr*45}" width="98" height="33" rx="2" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
        e.append(f'<circle cx="{tc_x+59}" cy="{584+dr*45}" r="4" fill="{C["golden"]}" stroke="{C["ink"]}" stroke-width="1"/>')
    return '\n'.join(e)


def scene_welding_walkway(p):
    rng = p['rng']; vi = p['var_idx']
    e = []
    e.append(f'<rect x="0" y="0" width="1200" height="900" fill="url(#g-sky)"/>')
    e.append(draw_towers(50, int(500+v(0,vi,40)), 3+vi%4, rng))
    e.append(draw_towers(620, int(515+v(0,vi+1,30)), 2+vi%3, rng))
    for si in range(3):
        sx = int(100 + si*360 + v(0, vi+si, 75))
        e.append(draw_steam(sx, int(345+v(0,vi+si,55)), count=2))
    cw_yl = int(608 + v(0, vi, 38))
    cw_yr = int(568 + v(0, vi+2, 28))
    e.append(draw_catwalk(cw_yl, cw_yr))
    jcx = int(582 + v(0, vi, 58))
    jcy = int(542 + v(0, vi+1, 28))
    pr = 40 + vi%3*8
    e.append(draw_pipe_joint(jcx, jcy, pr=pr))
    wx = jcx + 14; wy = jcy - pr + 8
    e.append(draw_welding_arc(wx, wy, p['spark_count'], rng))
    eng_x = jcx - 105; eng_y = cw_yl - 8
    e.append(draw_engineer(eng_x, eng_y, pose=1, direction='right'))
    torch_x = eng_x + 48; torch_y = eng_y - 138
    e.append(f'<line x1="{torch_x}" y1="{torch_y}" x2="{wx-4}" y2="{wy+4}" stroke="{C["sepia_mid"]}" stroke-width="5" stroke-linecap="round"/>')
    e.append(f'<rect x="{torch_x-8}" y="{torch_y-6}" width="16" height="11" rx="3" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    bot_x = jcx + 135; bot_y = cw_yr - 8
    e.append(draw_robot(bot_x, bot_y, pose=2))
    e.append(f'<rect x="195" y="{cw_yl-58}" width="28" height="48" rx="4" fill="{C["rust"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    return '\n'.join(e)


def scene_observation_deck(p):
    rng = p['rng']; vi = p['var_idx']
    e = []
    e.append(f'<rect x="0" y="0" width="1200" height="900" fill="url(#g-sky)"/>')
    sun_x = int(600 + v(0, vi, 200))
    e.append(f'<ellipse cx="{sun_x}" cy="558" rx="195" ry="118" fill="url(#g-sun)" filter="url(#f-glow)"/>')
    for hi, hy in enumerate([552, 562, 572]):
        e.append(f'<rect x="0" y="{hy}" width="1200" height="18" fill="{C["golden"]}" opacity="{0.11-hi*0.03:.2f}"/>')
    hy = 558
    e.append(draw_towers(0, hy, 5+vi%4, rng))
    e.append(draw_towers(400, int(hy+v(0,vi,18)), 4+vi%3, rng))
    e.append(draw_towers(720, int(hy+v(0,vi+1,22)), 3+vi%4, rng))
    tank_defs = [(int(148+v(0,vi,58)), hy-38, 44), (int(898+v(0,vi+1,48)), hy-28, 34), (int(1048+v(0,vi+2,38)), hy-58, 52)]
    for tcx, tcy, tr in tank_defs:
        e.append(f'<circle cx="{tcx}" cy="{tcy}" r="{tr}" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    e.append(f'<rect x="0" y="682" width="1200" height="218" fill="{C["sepia_dark"]}"/>')
    e.append(f'<rect x="0" y="682" width="1200" height="218" fill="url(#p-grate)" opacity="0.45"/>')
    e.append(f'<line x1="0" y1="684" x2="1200" y2="684" stroke="{C["sepia_mid"]}" stroke-width="4"/>')
    e.append(draw_railing(48, 692, 1152, 692, posts=10))
    eng_x = int(478 + v(0, vi, 58))
    e.append(draw_engineer(eng_x, 786, pose=p['eng_pose'], direction='right'))
    e.append(draw_robot(eng_x+132, 786, pose=1, direction='right'))
    for si in range(2+vi%3):
        sx = int(195 + si*308 + v(0, vi+si, 98))
        e.append(draw_steam(sx, int(hy-78), count=4))
    return '\n'.join(e)


def scene_gauge_inspection(p):
    rng = p['rng']; vi = p['var_idx']
    e = []
    e.append(f'<rect x="0" y="0" width="1200" height="900" fill="{C["sepia_dark"]}"/>')
    for wx in range(0, 1200, 14):
        tone = C['sepia_dark'] if wx%28==0 else C['ink']
        e.append(f'<line x1="{wx}" y1="0" x2="{wx}" y2="900" stroke="{tone}" stroke-width="1" opacity="0.35"/>')
    e.append(draw_pipes([int(y+v(0,vi,11)) for y in [60,100]]))
    e.append(draw_pipes([int(y+v(0,vi+1,13)) for y in [778, 818]]))
    gcx = int(748 + v(0, vi, 58))
    gcy = int(418 + v(0, vi+1, 48))
    gr = 130 + vi%3*14
    e.append(f'<rect x="{gcx-gr-38}" y="{gcy-gr-38}" width="{(gr+38)*2}" height="{(gr+38)*2}" fill="{C["metal"]}" stroke="{C["ink"]}" stroke-width="3"/>')
    for gi in range(2+vi%3):
        sgx = gcx - gr - 78 + gi*58
        sgy = gcy + gr - 18
        e.append(f'<circle cx="{sgx}" cy="{sgy}" r="24" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="2"/>')
        na = math.radians(rng.randint(-100,80))
        e.append(f'<line x1="{sgx}" y1="{sgy}" x2="{sgx+17*math.cos(na):.0f}" y2="{sgy+17*math.sin(na):.0f}" stroke="{C["rust"]}" stroke-width="2"/>')
    e.append(draw_pressure_gauge(gcx, gcy, gr, p['gauge_angle']))
    bot_x = int(948 + v(0, vi, 38))
    bot_y = 702
    ftx = gcx + gr + 95
    fty = gcy + 98
    e.append(draw_flashlight_beam(bot_x-18, bot_y-78, ftx, fty, width=145))
    eng_x = int(358 + v(0, vi, 58))
    e.append(draw_engineer(eng_x, 762, pose=p['eng_pose'], direction='right'))
    e.append(draw_clipboard(eng_x+32, 762-118, angle=-8+vi*2))
    e.append(draw_robot(bot_x, bot_y, pose=1, direction='left'))
    e.append(f'<rect x="{ftx-48}" y="{fty-78}" width="245" height="195" fill="{C["ink"]}" opacity="0.58"/>')
    e.append(f'<rect x="{ftx+18}" y="{fty-38}" width="58" height="78" rx="4" fill="{C["sepia_dark"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    return '\n'.join(e)


def scene_rain_field_work(p):
    rng = p['rng']; vi = p['var_idx']
    is_rain = p['sub_variant']
    e = []
    e.append(f'<rect x="0" y="0" width="1200" height="900" fill="{C["ink"]}"/>')
    e.append(f'<rect x="0" y="0" width="1200" height="600" fill="{C["sepia_dark"]}"/>')
    for ci in range(5+vi%3):
        ccx = rng.randint(50,1150); ccy = rng.randint(40,195)
        e.append(f'<ellipse cx="{ccx}" cy="{ccy}" rx="{rng.randint(75,195)}" ry="{rng.randint(38,75)}" fill="{C["ink"]}" opacity="0.45"/>')
    e.append(draw_towers(0, 548, 4+vi%3, rng))
    e.append(draw_towers(508, 558, 3+vi%3, rng))
    e.append(f'<rect x="0" y="702" width="1200" height="198" fill="{C["ink"]}"/>')
    e.append(f'<rect x="0" y="700" width="1200" height="5" fill="{C["sepia_dark"]}"/>')
    e.append(draw_puddles(3+vi%4, rng))
    e.append(draw_rain(p['rain_count'] if is_rain else 42, rng))
    if is_rain:
        eng_x = int(418 + v(0, vi, 78))
        e.append(draw_engineer(eng_x, 792, pose=1, direction='right'))
        bot_x = eng_x + 128
        e.append(draw_robot(bot_x, 792, pose=p['bot_pose'], direction='right'))
        bpx = (eng_x + bot_x)//2 + 12
        e.append(draw_blueprints(bpx, 792-138))
    else:
        valve_x = int(582 + v(0, vi, 78))
        valve_y = 742
        e.append(draw_valve_assembly(valve_x, valve_y, broken=True))
        eng_x = valve_x - 92
        e.append(draw_engineer(eng_x, 792, pose=2, direction='right'))
        e.append(draw_wrench(eng_x+52, 792-78, angle=45))
        bot_x = valve_x + 102
        e.append(draw_robot(bot_x, 792, pose=1, direction='left'))
        e.append(draw_flashlight_beam(bot_x-18, 792-88, valve_x+18, valve_y-18, width=78))
    return '\n'.join(e)


SCENE_FUNCS = [
    scene_control_room,
    scene_welding_walkway,
    scene_observation_deck,
    scene_gauge_inspection,
    scene_rain_field_work,
]


def generate_svg(params):
    scene_fn = SCENE_FUNCS[params['scene_idx']]
    body = scene_fn(params)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 1200 900" width="1200" height="900">
  {build_defs(params)}
  <g id="scene" filter="url(#f-grain)">
    {body}
  </g>
  {draw_panel_chrome(params)}
</svg>'''


def main():
    print("Generating 100 vintage-industrial illustrations...")
    scene_names = ['Control Room','Welding Walkway','Observation Deck','Gauge Inspection','Rain/Field Work']
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for i in range(100):
            params = make_params(i)
            svg = generate_svg(params)
            filename = f"illustration_{i+1:03d}.svg"
            zf.writestr(filename, svg.encode('utf-8'))
            print(f"  [{i+1:03d}/100] {scene_names[params['scene_idx']]} variant {params['var_idx']+1}")
    output_path = "illustrations.zip"
    with open(output_path, "wb") as f:
        f.write(buf.getvalue())
    size_mb = len(buf.getvalue()) / 1024 / 1024
    print(f"\nDone! {output_path} created.")
    print(f"  Size: {size_mb:.2f} MB | 100 SVG files at 1200x900px")


if __name__ == '__main__':
    main()
