# Open-Meteo Weather

Intégration Home Assistant pour récupérer les données météo, qualité de l'air et pollen via l'API gratuite [Open-Meteo](https://open-meteo.com) et la localisation via [Nominatim (OpenStreetMap)](https://nominatim.openstreetmap.org).

---

<p align="center">
  <img src="https://img.shields.io/badge/HACS-Custom-orange?style=for-the-badge" alt="HACS Custom">
  <img src="https://img.shields.io/badge/HA-2026.1+-blue?style=for-the-badge" alt="HA Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <a href="https://buymeacoffee.com/khirale">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="45">
  </a>
</p>

---

## Caractéristiques

- ✅ Entièrement gratuit, sans clé API
- ✅ Données météo actuelles, horaires (24h) et journalières (7 jours)
- ✅ Qualité de l'air avec données horaires sur 24h
- ✅ Pollens (arbres, herbes, graminées) avec prévisions sur 7 jours
- ✅ Localisation automatique via la zone Home de HA ou coordonnées GPS manuelles
- ✅ Rafraîchissement automatique toutes les heures

---

## Installation

### Via HACS (recommandé)

1. Ouvrir **HACS** dans Home Assistant
2. Aller dans **Intégrations** → cliquer sur les **3 points** en haut à droite
3. Sélectionner **Dépôts personnalisés**
4. Ajouter l'URL : `https://github.com/khirale/open_meteo_weather`
5. Catégorie : **Intégration**
6. Cliquer sur **Ajouter**
7. Rechercher **Open-Meteo Weather** dans HACS et cliquer sur **Télécharger**
8. Redémarrer Home Assistant

### Manuelle

1. Télécharger le contenu du dossier `custom_components/open_meteo_weather/`
2. Le copier dans `/config/custom_components/open_meteo_weather/`
3. Redémarrer Home Assistant

---

## Configuration

1. Aller dans **Paramètres** → **Appareils et services** → **Ajouter une intégration**
2. Rechercher **Open-Meteo Weather**
3. Choisir la source de localisation :
   - **Zone Home de HA** : utilise automatiquement les coordonnées GPS définies dans les paramètres de votre Home Assistant
   - **Coordonnées manuelles** : saisir manuellement la latitude et la longitude

> ℹ️ Après l'installation, un appareil **Open-Meteo Weather** apparaît dans vos appareils HA avec le nom de votre ville dans le champ modèle.

---

## Liste des sensors

### 📍 Localisation

| Sensor | Utilité |
|---|---|
| `sensor.open_meteo_weather_localisation` | Nom de la ville résolu automatiquement via les coordonnées GPS |

**Attributs :**

| Attribut | Description |
|---|---|
| `latitude` | Latitude configurée |
| `longitude` | Longitude configurée |
| `country` | Pays |
| `country_code` | Code pays (ex: FR) |
| `postcode` | Code postal |
| `state` | Région / département |

---

### 🌡️ Conditions actuelles

Ces sensors reflètent la valeur en temps réel, mise à jour toutes les heures.

| Sensor | Utilité |
|---|---|
| `sensor.open_meteo_weather_temperature` | Température extérieure actuelle en °C |
| `sensor.open_meteo_weather_ressenti` | Température ressentie en °C, prenant en compte vent et humidité |
| `sensor.open_meteo_weather_humidite` | Taux d'humidité relative de l'air en % |
| `sensor.open_meteo_weather_precipitations` | Quantité de précipitations tombées sur l'heure en mm |
| `sensor.open_meteo_weather_vitesse_du_vent` | Vitesse du vent à 10m d'altitude en km/h |
| `sensor.open_meteo_weather_direction_du_vent` | Direction d'où vient le vent en degrés (0° = Nord) |
| `sensor.open_meteo_weather_rafales` | Vitesse maximale des rafales de vent en km/h |
| `sensor.open_meteo_weather_pression` | Pression atmosphérique en hPa |
| `sensor.open_meteo_weather_indice_uv` | Indice UV actuel (0 = nul, 11+ = extrême) |
| `sensor.open_meteo_weather_rayonnement_solaire` | Rayonnement solaire incident en W/m² |
| `sensor.open_meteo_weather_condition_meteo` | Condition météo actuelle sous forme de texte (ex: `clear_sky`, `light_rain`) |

---

### ⏱️ Prévisions horaires

Ces sensors ont pour **état (state)** la valeur de l'heure actuelle (H0), et exposent les **24 heures suivantes en attributs**.

| Sensor | Utilité |
|---|---|
| `sensor.open_meteo_weather_temperature_horaire` | Évolution de la température sur les 24 prochaines heures |
| `sensor.open_meteo_weather_probabilite_precipitations_horaire` | Probabilité de pluie heure par heure en % |
| `sensor.open_meteo_weather_vitesse_vent_horaire` | Évolution de la vitesse du vent sur 24h en km/h |
| `sensor.open_meteo_weather_direction_vent_horaire` | Évolution de la direction du vent sur 24h en degrés |
| `sensor.open_meteo_weather_indice_uv_horaire` | Évolution de l'indice UV sur 24h |
| `sensor.open_meteo_weather_condition_meteo_horaire` | Condition météo heure par heure |

#### Structure des attributs horaires

Chaque sensor horaire expose 24 attributs nommés `h0` à `h23` :

```
state : valeur à l'heure actuelle
attributs :
  h0  : valeur heure actuelle
  h1  : valeur dans 1 heure
  h2  : valeur dans 2 heures
  ...
  h23 : valeur dans 23 heures
```

**Exemple** pour `sensor.open_meteo_weather_temperature_horaire` à 14h00 :

```
state  : 22
  h0   : 22   → 14h00
  h1   : 23   → 15h00
  h2   : 22   → 16h00
  h3   : 21   → 17h00
  ...
  h23  : 14   → 13h00 le lendemain
```

---

### 📅 Prévisions journalières

Ces sensors ont pour **état (state)** la valeur du jour actuel (J0), et exposent les **7 jours suivants en attributs**.

| Sensor | Utilité |
|---|---|
| `sensor.open_meteo_weather_temperature_max_journaliere` | Température maximale prévue chaque jour en °C |
| `sensor.open_meteo_weather_temperature_min_journaliere` | Température minimale prévue chaque jour en °C |
| `sensor.open_meteo_weather_precipitations_journalieres` | Cumul de précipitations prévu chaque jour en mm |
| `sensor.open_meteo_weather_condition_meteo_journaliere` | Condition météo dominante du jour |
| `sensor.open_meteo_weather_indice_uv_max_journalier` | Pic d'indice UV prévu dans la journée |
| `sensor.open_meteo_weather_vitesse_vent_max_journaliere` | Rafale maximale prévue dans la journée en km/h |

#### Structure des attributs journaliers

Chaque sensor journalier expose 7 attributs nommés `j0` à `j6` :

```
state : valeur du jour actuel
attributs :
  j0 : aujourd'hui
  j1 : demain
  j2 : après-demain
  ...
  j6 : dans 6 jours
```

**Exemple** pour `sensor.open_meteo_weather_temperature_max_journaliere` un lundi :

```
state : 19
  j0  : 19   → lundi (aujourd'hui)
  j1  : 22   → mardi
  j2  : 18   → mercredi
  j3  : 15   → jeudi
  j4  : 17   → vendredi
  j5  : 20   → samedi
  j6  : 21   → dimanche
```

---

### 🌿 Qualité de l'air

Ces sensors ont pour **état (state)** la valeur actuelle et exposent les **24 heures suivantes en attributs** (h0 à h23, même structure que les sensors horaires météo).

| Sensor | Utilité |
|---|---|
| `sensor.open_meteo_weather_indice_qualite_air` | Indice européen AQI (0–500). Attribut `category` : good / fair / moderate / poor / very_poor / extremely_poor |
| `sensor.open_meteo_weather_pm2_5` | Particules fines PM2.5 en µg/m³ — émises par le trafic et les feux |
| `sensor.open_meteo_weather_pm10` | Particules PM10 en µg/m³ — poussières, pollens, moisissures |
| `sensor.open_meteo_weather_ozone` | Concentration d'ozone en µg/m³ — se forme par temps ensoleillé |
| `sensor.open_meteo_weather_dioxyde_d_azote` | NO₂ en µg/m³ — lié au trafic routier |
| `sensor.open_meteo_weather_dioxyde_de_soufre` | SO₂ en µg/m³ — lié aux centrales et à l'industrie |
| `sensor.open_meteo_weather_monoxyde_de_carbone` | CO en µg/m³ — lié à la combustion incomplète |

#### Catégories AQI européen

| Valeur | Catégorie | Signification |
|---|---|---|
| 0 – 20 | `good` | Bonne qualité |
| 21 – 40 | `fair` | Qualité acceptable |
| 41 – 60 | `moderate` | Modérée |
| 61 – 80 | `poor` | Mauvaise |
| 81 – 100 | `very_poor` | Très mauvaise |
| > 100 | `extremely_poor` | Extrêmement mauvaise |

---

### 🌸 Pollens

Ces sensors ont pour **état (state)** la valeur du jour actuel et exposent les **7 jours suivants en attributs** (j0 à j6, même structure que les sensors journaliers météo).

Les valeurs sont en µg/m³ et correspondent au pic journalier.

| Sensor | Utilité |
|---|---|
| `sensor.open_meteo_weather_pollen_arbres` | Indice pollinique des arbres (principalement bouleau en Europe) |
| `sensor.open_meteo_weather_pollen_herbes` | Indice pollinique des graminées |
| `sensor.open_meteo_weather_pollen_graminees` | Indice pollinique des plantes herbacées (ambroisie principalement) |

---

## Condition météo — valeurs possibles

Le sensor `condition_meteo` retourne une des valeurs suivantes :

| Valeur | Signification |
|---|---|
| `clear_sky` | Ciel dégagé |
| `mainly_clear` | Principalement dégagé |
| `partly_cloudy` | Partiellement nuageux |
| `overcast` | Couvert |
| `fog` | Brouillard |
| `icy_fog` | Brouillard givrant |
| `light_drizzle` | Bruine légère |
| `moderate_drizzle` | Bruine modérée |
| `heavy_drizzle` | Bruine forte |
| `light_freezing_drizzle` | Bruine verglaçante légère |
| `heavy_freezing_drizzle` | Bruine verglaçante forte |
| `light_rain` | Pluie légère |
| `moderate_rain` | Pluie modérée |
| `heavy_rain` | Pluie forte |
| `light_freezing_rain` | Pluie verglaçante légère |
| `heavy_freezing_rain` | Pluie verglaçante forte |
| `light_snow` | Neige légère |
| `moderate_snow` | Neige modérée |
| `heavy_snow` | Neige forte |
| `snow_grains` | Grésil |
| `light_showers` | Averses légères |
| `moderate_showers` | Averses modérées |
| `heavy_showers` | Averses fortes |
| `light_snow_showers` | Averses de neige légères |
| `heavy_snow_showers` | Averses de neige fortes |
| `thunderstorm` | Orage |
| `thunderstorm_light_hail` | Orage avec grêle légère |
| `thunderstorm_heavy_hail` | Orage avec grêle forte |

---

## Sources de données

| Donnée | Source |
|---|---|
| Météo, UV, prévisions | [Open-Meteo Forecast API](https://open-meteo.com/en/docs) |
| Qualité de l'air, pollens | [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) |
| Localisation (ville) | [Nominatim — OpenStreetMap](https://nominatim.openstreetmap.org) |

---

## Licence

MIT — Voir [LICENSE](LICENSE)
