"""
campus_data.py
Landmark coordinates (lat, lon) for UEW South Campus, collected via
OpenStreetMap using ALPHA's in-app coordinate calibration tool.

NOTE: Routes between any two locations are calculated as a direct
straight-line path (see navigation.py). This is an honest simplification
for a one-week project -- it does not account for buildings, walls, or
roads that a real walker would go around. Upgrading this to real
turn-by-turn walkways (by tracing actual paths with the calibration
tool) is listed as future work.
"""

CAMPUS_LOCATIONS = {
    "entrance":                  (5.33872, -0.62475),
    "advance park":               (5.34026, -0.63020),
    "kwame nkrumah avenue":       (5.33838, -0.62378),
    "health insurance office":    (5.33824, -0.62450),
    "south market":               (5.33873, -0.62455),
    "ghartey hall a":             (5.33907, -0.62557),
    "ghartey hall b":             (5.33925, -0.62510),
    "ghartey hall c":             (5.34004, -0.62633),
    "annex lab":                  (5.33988, -0.62610),
    "library":                    (5.33962, -0.62577),
    "ict department":             (5.33966, -0.62551),
    "university street":          (5.33922, -0.62551),
    "mosque":                     (5.33998, -0.62592),
    "science department":         (5.33891, -0.62640),
    "university hearing center":  (5.33889, -0.62732),
    "volleyball court":           (5.33855, -0.62684),
    "src natoc":                  (5.33834, -0.62706),
    "aggrey hall a":              (5.33763, -0.62603),
    "aggrey hall b":              (5.33803, -0.62525),
    "assembly hall":              (5.33781, -0.62551),
    "transport unit":             (5.33963, -0.62714),
    "clinic":                     (5.33850, -0.62403),
    "winneba guesthouse":         (5.33758, -0.62987),

    # Newly added locations
    "slt 7":                      (5.33910, -0.62682),
    "slt 8":                      (5.33910, -0.62682),   # NOTE: identical to SLT 7 -- verify with calibration tool
    "french department":          (5.33931, -0.62696),
    "school of business":         (5.33865, -0.62499),
}


# Alternate names (French, and a starter set of Fante terms) that map
# back to the canonical English key in CAMPUS_LOCATIONS. French entries
# are reasonably reliable; Fante entries are a best-effort starting
# point and should be reviewed/corrected by a native speaker -- they
# are clearly marked as such so nobody mistakes them for verified.
LANDMARK_ALIASES = {
    # ---------- French (fr) ----------
    "bibliotheque": "library",
    "la bibliotheque": "library",
    "entree": "entrance",
    "entree principale": "entrance",
    "marche": "south market",
    "clinique": "clinic",
    "mosquee": "mosque",
    "salle d'assemblee": "assembly hall",
    "bureau d'assurance sante": "health insurance office",
    "unite de transport": "transport unit",
    "auberge winneba": "winneba guesthouse",
    "departement des sciences": "science department",
    "ecole de commerce": "school of business",
    "departement de francais": "french department",
    "terrain de volleyball": "volleyball court",
    "avenue kwame nkrumah": "kwame nkrumah avenue",
    "rue de l'universite": "university street",
    "parc advance": "advance park",

    # ---------- Fante (fat) -- STARTER SET, NEEDS NATIVE SPEAKER REVIEW ----------
    "nwomakorabea": "library",     # "book house" -- approximate
    "kwanano": "entrance",         # "road entrance" -- approximate
    "gua": "south market",         # "market" -- approximate
    "ayaresabea": "clinic",        # "place of healing" -- approximate
}


# For destinations that OSRM incorrectly routes to via the long outer
# public road loop (due to missing internal footpath data), these
# waypoints force the route back through University Street -- the real,
# already-mapped internal road -- instead of detouring outside.
# NOTE: these are approximate anchor points along University Street;
# fine-tune with the in-app coordinate calibration tool if a specific
# route still looks off.
ROUTE_VIA_WAYPOINTS = {
    "ict department":  [(5.33922, -0.62551)],
    "ghartey hall c":  [(5.33922, -0.62551), (5.33988, -0.62610)],
    "mosque":          [(5.33922, -0.62551), (5.33988, -0.62610)],
    "src natoc":       [(5.33922, -0.62551)],
}