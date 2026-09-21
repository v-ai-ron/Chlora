"""Costanti del reattore da 10 L."""

# I2C del Raspberry Pi 5. L'ADS1115 con ADDR a GND risponde a 0x48.
I2C_BUS = 1
ADS1115_ADDRESS = 0x48

# La sonda analogica è alimentata a 5 V. Un partitore 10k/20k
# porta l'uscita sotto i 3,3 V dell'ADC. V_sonda = V_adc * DIVIDER_GAIN.
DIVIDER_GAIN = 1.5

# Relè attivo basso, tipico dei moduli a optoisolatore.
PUMP_GPIO = 17
PUMP_ACTIVE_HIGH = False

VOLUME_L = 10.0

# Isteresi sulla torbidità. La pompa parte al picco e si ferma
# solo quando la coltura si è schiarita, così il relè non batte.
HARVEST_ON_NTU = 280.0
HARVEST_OFF_NTU = 90.0
MIN_PUMP_ON_S = 45.0
MIN_PUMP_OFF_S = 90.0

# Bande del ciclo, lette sulla stessa scala NTU della sonda.
LAG_NTU = 45.0
PEAK_NTU = 240.0
RECOVER_RISE_NTU = 35.0

PHASES = ("latenza", "crescita", "picco", "raccolta", "recupero")

SAMPLE_PERIOD_S = 1.0
HISTORY = 90

# Peso secco per NTU, percorso ottico della SEN0189 in questa vasca.
# 250 NTU corrispondono a 0,95 g/L.
DW_G_PER_L_PER_NTU = 0.0038

# Produttività netta di C. vulgaris con il pannello luminoso del reattore.
O2_G_PER_G_DW_PER_H = 0.12

HOST = "127.0.0.1"
PORT = 8080
