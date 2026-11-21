"""Six free-text diamond listings, and what a perfect extraction would return."""

LISTINGS = [
    "Lovely 1.2 carat ideal cut stone, colour G, clarity VS1, asking $6,500",
    "Selling my 0.5ct diamond. Cut: very good. Color E, VVS2. Price 2100 USD.",
    "PREMIUM cut, 2.01 carats, J colour, SI2 clarity - yours for $14,999!",
    "Engagement ring stone: 0.9 carat, good cut, H, SI1. Asking 3.4k dollars.",
    "Fair-cut 1.5 carat diamond, I1 clarity and colour F, only $4,900 or best offer",
    "Flawless (IF) 0.31 carat D colour ideal cut gem, $1,850",
]

EXPECTED = [
    {"carat": 1.2, "cut": "Ideal", "color": "G", "clarity": "VS1",
     "asking_price": 6500},
    {"carat": 0.5, "cut": "Very Good", "color": "E", "clarity": "VVS2",
     "asking_price": 2100},
    {"carat": 2.01, "cut": "Premium", "color": "J", "clarity": "SI2",
     "asking_price": 14999},
    {"carat": 0.9, "cut": "Good", "color": "H", "clarity": "SI1",
     "asking_price": 3400},
    {"carat": 1.5, "cut": "Fair", "color": "F", "clarity": "I1",
     "asking_price": 4900},
    {"carat": 0.31, "cut": "Ideal", "color": "D", "clarity": "IF",
     "asking_price": 1850},
]
