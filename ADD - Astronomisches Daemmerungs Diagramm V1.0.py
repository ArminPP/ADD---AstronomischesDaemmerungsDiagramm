""" 

(c) Armin P Pressler (2025)
Dieses Projekt erstellt ein Diagramm für Astrophotographen, das die verschiedenen Phasen der astronomischen Dämmerung visualisiert.
Dabei wird die jeweilige Helligkeit des Mondes berücksichtigt. 
Es basiert auf Python und verwendet Bibliotheken wie skyfield, matplotlib, usw.zur Berechnung und Darstellung.



Das Programm wurde mit Hilfe von KI erstellt, und ist mein erster Versuch, etwas nützliches zu erstellen.
Der Grund ist, dass ich leider nur ein sehr begrenztes Python-Wissen habe, 
und ohne Hilfe nicht in der Lage gewesen wäre, eine so komplexe Aufgabe zu verwirklichen.
Ich habe Ende 2024 begonnen ein Script zu schreiben, und habe dann versucht, 
es mit Hilfe von Copilot fertig zustellen.
Leider scheiterte ich damals daran. Mitte April 2025 startete ich einen neuen Versuch, 
diesmal liess ich das bereits vorhandene, nicht funktionierende, Script von Gemini analysieren und korrigieren.
Der Unterschied war enorm! In diesem halben Jahr machten die KIs einen enormen Entwicklungssprung, 
das Script funktionierte in groben Zügen.
Das Finetuning erfolgte dann wieder inline in VScode mit Copilot.
 
"""

# Importiere die benötigten Bibliotheken
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from skyfield.api import load, wgs84, N, E
from skyfield import almanac
import datetime
import pytz
import time
from tkinter import filedialog, StringVar
import os
import platform

import sys
from PIL import Image, ImageTk
import io

"""
Tabelle für den April 2025:
Apr.25	Moonrise Moonset	Moonrise
1		07:37	-			-
2		-		00:08		08:11
3		-		01:30		08:57
4		-		02:38		09:57
5		-		03:30		11:08
6		-		04:07		12:24
7		-		04:33		13:40
8		-		04:53		14:53
9		-		05:09		16:03
10		-		05:23		17:10
11		-		05:35		18:17
12		-		05:48		19:24
13		-		06:02		20:32
14		-		06:17		21:41
15		-		06:36		22:51
16		-		07:01		-
17		00:00	07:34		-
18		01:03	08:18		-
19		01:58	09:15		-
20		02:41	10:22		-
21		03:15	11:38		-
22		03:41	12:58		-
23		04:02	14:19		-
24		04:19	15:41		-
25		04:36	17:05		-
26		04:53	18:32		-
27		05:12	20:02		-
28		05:35	21:34		-
29		06:05	23:03		-
30		06:47	-			-
"""

# Webseiten zur Berechnung von Mondaufgang und Monduntergang 
# https://www.timeanddate.com/moon/austria/vienna
# https://www.fullmoonphase.com/europe/austria/vienna-moonrise-set
# https://aa.usno.navy.mil/calculated/rstt/year?ID=AA&year=2025&task=1&lat=48.21&lon=16.36&label=Vienna&tz=1&tz_sign=1&submit=Get+Data
# https://www.heute-am-himmel.de/dunkle-naechte
# https://dersphere.github.io/moon-and-darkness-calendar/?lat=48.2083537&lon=16.3725042
# https://www.hcgreier.at/ephempedia/apps/lunafree/
# https://www.hcgreier.at/ephempedia/apps/aufgang_untergang/
# https://www.hcgreier.at/ephempedia/apps/monatskalender/
            
            

# Globale Variablen
DEFAULT_LATITUDE = 48.210033  # Wien
DEFAULT_LONGITUDE = 16.363449  # Wien
DEFAULT_LOCATION_NAME = "Wien"
DEFAULT_TIMEZONE = 'Europe/Vienna' # Zeitzone für Wien
EPHEMERIDEN_FILE = 'de421.bsp' # wird automatisch heruntergeladen, wenn nicht vorhanden
LOADED_LOCATION_NAME = None # Globale Variable für den geladenen Ort
SELECTED_TIMEZONE = DEFAULT_TIMEZONE # Aktuell gewählte Zeitzone

# Initialisiere das globale pytz-Objekt
try:
    LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    print(f"FEHLER: Default-Zeitzone '{SELECTED_TIMEZONE}' ungültig! Fallback auf UTC.")
    SELECTED_TIMEZONE = 'UTC'
    LOCAL_TZ = pytz.utc


# Klasse zum Umleiten der Konsolenausgabe in ein Textfeld
class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

# Funktion zur Konvertierung von UTC-Zeit in lokale Zeit
def convert_to_local_time(skyfield_time):
    global LOCAL_TZ # Wichtig: Nutzt das dynamische globale Objekt
    if skyfield_time is None: return None
    try: return skyfield_time.astimezone(LOCAL_TZ)
    except TypeError:
        try:
             utc_dt = skyfield_time.utc_datetime()
             if utc_dt.tzinfo is None: utc_dt = pytz.utc.localize(utc_dt)
             return utc_dt.astimezone(LOCAL_TZ)
        except Exception: return None
    except Exception: return None

# Funktion zur Berechnung der Tageslichtzeiten für mehrere Monate
def calculate_daylight(latitude, longitude, year, start_month, num_months):
    global LOCAL_TZ # Wichtig: Nutzt das dynamische globale Objekt
    ts = load.timescale()
    eph = load(EPHEMERIDEN_FILE)
    moon = eph['Moon']
    sun = eph['Sun']
    vie = wgs84.latlon(latitude * N, longitude * E)
    observer = eph['Earth'] + vie

    daylight_times = []

    total_days_to_calculate = 0
    month_days_list = []
    for m_offset in range(num_months):
        month = start_month + m_offset
        current_month = month if month <= 12 else month - 12
        current_year = year if month <= 12 else year + (month - 1) // 12 # Korrekte Jahresberechnung für Überlauf
        days_in_month = (datetime.date(current_year + (current_month // 12), (current_month % 12) + 1, 1) - datetime.timedelta(days=1)).day if current_month != 12 else 31
        month_days_list.append(days_in_month)
        total_days_to_calculate += days_in_month

    progress_counter = 0

    for m_offset in range(num_months):
        month = start_month + m_offset
        current_month = month if month <= 12 else month - 12
        current_year = year if month <= 12 else year + (month - 1) // 12 # Korrekte Jahresberechnung
        num_days = month_days_list[m_offset]
        root.update_idletasks() # Wichtig für GUI-Update

        for day in range(1, num_days + 1):
            progress_counter += 1
            # Fortschrittsbalken aktualisieren
            progress = int((progress_counter / total_days_to_calculate) * 100)
            progress_var.set(progress)
            root.update_idletasks() # Wichtig für GUI-Update

            date_obj = datetime.date(current_year, current_month, day)

            # Lokale Zeit für 00:00 und 23:59:59 des Kalendertages
            t_day_start_local = LOCAL_TZ.localize(datetime.datetime(current_year, current_month, day, 0, 0, 0))
            t_day_end_local = LOCAL_TZ.localize(datetime.datetime(current_year, current_month, day, 23, 59, 59))
            t_day_start_utc = ts.from_datetime(t_day_start_local)
            t_day_end_utc = ts.from_datetime(t_day_end_local)

            # Berechnung Sonnenaufgang/-untergang & Dämmerung für den Kalendertag
            s_rise, _ = almanac.find_risings(observer, sun, t_day_start_utc, t_day_end_utc)
            s_set, _ = almanac.find_settings(observer, sun, t_day_start_utc, t_day_end_utc)
            sunrise_time = convert_to_local_time(s_rise[0].utc_datetime()) if len(s_rise) > 0 else None
            sunset_time = convert_to_local_time(s_set[0].utc_datetime()) if len(s_set) > 0 else None

            horizon = 18.0
            astro_rise, _ = almanac.find_risings(observer, sun, t_day_start_utc, t_day_end_utc, -horizon)
            astro_set, _ = almanac.find_settings(observer, sun, t_day_start_utc, t_day_end_utc, -horizon)
            astro_rise_time = convert_to_local_time(astro_rise[0].utc_datetime()) if len(astro_rise) > 0 else None # Verwende None statt min
            astro_set_time = convert_to_local_time(astro_set[0].utc_datetime()) if len(astro_set) > 0 else None # Verwende None statt min

            # Definiere das exakte Zeitfenster für den Diagramm-Balken in Lokalzeit
            chart_bar_start_local = LOCAL_TZ.localize(datetime.datetime.combine(date_obj, datetime.time(12, 0, 0)))
            chart_bar_end_local = chart_bar_start_local + datetime.timedelta(days=1) - datetime.timedelta(seconds=1) # Endet um 11:59:59

            # Definiere ein erweitertes Suchfenster (Sicherheit für Randfälle)
            # Von 00:00 an Tag D bis 23:59 an Tag D+1
            search_start_local = LOCAL_TZ.localize(datetime.datetime.combine(date_obj, datetime.time(0, 0, 0)))
            search_end_local   = LOCAL_TZ.localize(datetime.datetime.combine(date_obj + datetime.timedelta(days=1), datetime.time(23, 59, 59)))
            t_search_start_utc = ts.from_datetime(search_start_local)
            t_search_end_utc   = ts.from_datetime(search_end_local)

            # Finde alle Auf- und Untergänge im erweiterten Fenster
            t_rise_ts, _ = almanac.find_risings(observer, moon, t_search_start_utc, t_search_end_utc)
            t_set_ts, _  = almanac.find_settings(observer, moon, t_search_start_utc, t_search_end_utc)

            # Kombiniere und sortiere alle Ereignisse
            events = []
            for t in t_rise_ts: events.append({'time': t, 'type': 'rise'})
            for t in t_set_ts: events.append({'time': t, 'type': 'set'})
            events.sort(key=lambda x: x['time'].utc_datetime())

            # Bestimme initialen Zustand am Anfang des Chart-Balkens (12:00 lokal)
            t_chart_start_utc = ts.from_datetime(chart_bar_start_local)
            t_chart_end_utc = ts.from_datetime(chart_bar_end_local)

            last_event_before_start = None
            for e in reversed(events):
                if e['time'].utc_datetime() <= chart_bar_start_local:
                    last_event_before_start = e
                    break

            is_up_at_start = False
            if last_event_before_start:
                is_up_at_start = (last_event_before_start['type'] == 'rise')
            else:
                # Wenn kein Ereignis davor, prüfe die Höhe zur Startzeit
                alt, _, _ = observer.at(t_chart_start_utc).observe(moon).apparent().altaz()
                is_up_at_start = alt.degrees > 0

            # Erzeuge Intervalle der Mondsichtbarkeit innerhalb des Chart-Fensters
            moon_visible_intervals = []
            current_time_utc = t_chart_start_utc
            current_state_is_up = is_up_at_start

            for event in events:
                event_time_utc = event['time']
                # Nur Ereignisse *nach* dem Start des aktuellen Intervalls und *innerhalb* des Chart-Fensters betrachten
                if event_time_utc.utc_datetime() > current_time_utc.utc_datetime() and event_time_utc.utc_datetime() <= chart_bar_end_local :
                    if current_state_is_up:
                        # Wenn der Mond oben war, endet das Sichtbarkeitsintervall hier (oder am Ende des Chart-Fensters)
                        # Konvertiere zu Lokalzeit nur zum Speichern
                        start_interval_local = convert_to_local_time(current_time_utc.utc_datetime())
                        end_interval_local = convert_to_local_time(min(event_time_utc, t_chart_end_utc).utc_datetime())
                        if end_interval_local > start_interval_local: # Stelle sicher, dass das Intervall eine Dauer hat
                             moon_visible_intervals.append((start_interval_local, end_interval_local))

                    # Aktualisiere den Zustand basierend auf dem Ereignis
                    current_state_is_up = (event['type'] == 'rise')
                    current_time_utc = event_time_utc

            # Handle das letzte Intervall bis zum Ende des Chart-Fensters
            if current_state_is_up:
                 if current_time_utc.utc_datetime() < chart_bar_end_local:
                    start_interval_local = convert_to_local_time(current_time_utc.utc_datetime())
                    end_interval_local = convert_to_local_time(t_chart_end_utc.utc_datetime())
                    if end_interval_local > start_interval_local:
                        moon_visible_intervals.append((start_interval_local, end_interval_local))

            # Mond Meridian-Durchgang und max. Höhe
            max_altitude_time_local = None 
            max_altitude_deg = -999 # Initialisiere mit unwahrscheinlichem Wert

            # Erzeuge Zeitpunkte für das Sampling (z.B. alle 5 Minuten)
            # linspace erzeugt ein Time-Array
            sampling_times = ts.linspace(t_chart_start_utc, t_chart_end_utc, num=int(24 * 12) + 1) # 289 Punkte

            # Berechne Höhen für alle Zeitpunkte (vectorisiert)
            alts, azs, ds = observer.at(sampling_times).observe(moon).apparent().altaz()
            altitudes_deg = alts.degrees

            # Finde den Index der maximalen Höhe
            if len(altitudes_deg) > 0:
                 max_index = np.argmax(altitudes_deg)
                 max_altitude_deg_found = altitudes_deg[max_index]

                 # Speichere nur, wenn die maximale Höhe sinnvoll ist (z.B. über dem Horizont)
                 if max_altitude_deg_found > -90: # Praktisch immer der Fall
                      max_altitude_deg = max_altitude_deg_found
                      # Hole das Time-Objekt am Maximum-Index
                      max_altitude_time_ts = sampling_times[max_index] # Dies ist ein einzelnes Time-Objekt
                      max_altitude_time_local = convert_to_local_time(max_altitude_time_ts)

            # Mondphase (Berechnung für 12:00 Uhr mittags des Kalendertages ist ok)
            t_noon_local = LOCAL_TZ.localize(datetime.datetime.combine(date_obj, datetime.time(12, 0, 0)))
            t_noon_utc = ts.from_datetime(t_noon_local)
            moon_phase_degrees = almanac.moon_phase(eph, t_noon_utc).degrees
            if moon_phase_degrees <= 180:
                moon_phase_percent = (moon_phase_degrees / 180.0) * 100
            else:
                moon_phase_percent = ((360 - moon_phase_degrees) / 180.0) * 100

            # Zeiten und Mondphase in Tupel speichern (ersetze moonrise/set mit Intervallen)
            daylight_times.append((
                astro_rise_time, sunrise_time, sunset_time, astro_set_time,
                date_obj,
                moon_phase_percent, # Für Helligkeit
                moon_visible_intervals, # Die Liste der Sichtbarkeitsintervalle
                max_altitude_time_local,  # Mond Meridian-Durchgang Zeit
                max_altitude_deg     # Mond max. Höhe in Grad
            ))

            # Debug Ausgabe der berechneten Werte
            # for start, end in moon_visible_intervals:
            #     moonrise_str = start.strftime('%Y-%m-%d %H:%M:%S') if start else 'None            '
            #     moonset_str = end.strftime('%Y-%m-%d %H:%M:%S') if end else 'None            '
            # sunset_str = sunset_time.strftime(
            #     '%Y-%m-%d %H:%M') if sunset_time else 'None            '
            # sunrise_str = sunrise_time.strftime(
            #     '%Y-%m-%d %H:%M') if sunrise_time else 'None            '
            # astro_rise_time_str = astro_rise_time.strftime(
            #     '%Y-%m-%d %H:%M') if astro_rise_time else 'None            '
            # astro_set_time_str = astro_set_time.strftime(
            #     '%Y-%m-%d %H:%M') if astro_set_time else 'None            '
            # print(f"START: {t_day_start_local.strftime('%Y-%m-%d %H:%M')}, END: {t_day_end_local.strftime('%Y-%m-%d %H:%M')} | Sr: {sunrise_str}, Ss: {sunset_str}, Ar: {astro_rise_time_str}, As: {astro_set_time_str}, Mr: {moonrise_str}, Ms: {moonset_str}, Mp: {moon_phase_percent:.1f}%")
            # sys.stdout.flush()

    return daylight_times

# In create_diagram Funktion
def create_diagram(latitude, longitude, year, start_month, num_months, eph):
    global LOCAL_TZ # Wichtig: Nutzt das dynamische globale Objekt
    start_time_calc = time.time()
    daylight_times = calculate_daylight(latitude, longitude, year, start_month, num_months)
    elapsed_time_calc = (time.time() - start_time_calc) * 1000
    print(f"Zeit für die Berechnung: {elapsed_time_calc:.2f} ms")

    num_days = len(daylight_times)
    if num_days == 0:
        print("Keine Daten zum Zeichnen.")
        return None # Frühzeitiger Ausstieg, wenn keine Daten vorhanden sind

    fig, ax = plt.subplots(figsize=(18, 12))

    # Anpassung der X-Achse
    custom_hours = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00',
                    '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00']
    ax.set_xticks(np.arange(0, 24, 1))
    ax.set_xticklabels(custom_hours)
    ax.tick_params(axis='x', which='major', top=True, labeltop=True, bottom=False, labelbottom=False) # Beschriftung nur oben
    ax2 = ax.twinx() # Zweite Y-Achse

    bar_height = 1 # Etwas kleiner für bessere Trennung
    weekend_bar_width = 0.2 # Breite in Stunden (kleiner Wert, anpassen nach Geschmack)

    # Farben
    night_color = (0.1, 0.1, 0.44)
    twilight_color = (0.4, 0.4, 0.7)
    day_color = (0.75, 0.75, 0.75)
    weekend_color = 'gray' # Farbe für die Wochenendbalken
 
    start_time_plot = time.time()

    # Platzhalter für Legende (Vollmond)
    full_moon_plotted = False
    full_moon_handle = None

    # Funktion zur Konvertierung von datetime nach Diagrammstunden (0-24)
    def time_to_chart_hours(dt_local):
        if dt_local is None:
            return None
        # Zeit seit letztem Mittag (12:00 Uhr) in Sekunden
        seconds_since_noon = (dt_local.hour * 3600 + dt_local.minute * 60 + dt_local.second) - (12 * 3600)
        # Wenn negativ, ist es am nächsten Tag (relativ zum 12:00 Start) -> 24h addieren
        if seconds_since_noon < 0:
            seconds_since_noon += 24 * 3600
        return seconds_since_noon / 3600.0

    for i, (astro_rise_time, sunrise_time, sunset_time, astro_set_time, # Namen getauscht, da Start/Ende Dämmerung
            date_obj, moon_phase_percent, moon_visible_intervals,
            transit_time_local, max_altitude_deg) in enumerate(daylight_times):
       
        # Wochenenden mit Balken markieren
        if date_obj.weekday() in [3, 4, 5, 6]: # 5 = Samstag, 6 = Sonntag
            # Linker Balken
            ax.barh(i, weekend_bar_width, height=bar_height, left=0,
                    color=weekend_color, edgecolor='none', align='edge', zorder=7) # zorder=0.5 -> hinter den Daten
            # Rechter Balken
            ax.barh(i, weekend_bar_width, height=bar_height, left=24 - weekend_bar_width,
                    color=weekend_color, edgecolor='none', align='edge', zorder=7) # zorder=0.5 -> hinter den Daten

        # Hintergrund plotten (Tag/Dämmerung/Nacht basierend auf Kalendertag Sonnenzeiten)
        # Konvertiere Sonnen-/Dämmerungszeiten in Diagrammstunden
        astro_rise_adj = time_to_chart_hours(astro_rise_time) if astro_rise_time else None # Beginn Nacht
        sunrise_adj    = time_to_chart_hours(sunrise_time)    if sunrise_time else None    # Beginn Tag
        sunset_adj     = time_to_chart_hours(sunset_time)     if sunset_time else None     # Ende Tag
        astro_set_adj  = time_to_chart_hours(astro_set_time)  if astro_set_time else None  # Ende Dämmerung (Beginn Nacht)
        # Debug Ausgabe für astro_rise_adj und astro_set_adj
        # print(f"astro_rise_adj: {astro_rise_adj:.2f}" if astro_rise_adj is not None else "astro_rise_adj: None")
        # print(f"sunrise_adj: {sunrise_adj:.2f}" if sunrise_adj is not None else "sunrise_adj: None")
        # print(f"astro_set_adj: {astro_set_adj:.2f}" if astro_set_adj is not None else "astro_set_adj: None")
        # print(f"sunset_adj: {sunset_adj:.2f}" if sunset_adj is not None else "sunset_adj: None")

        # Nacht (ganzer Balken, wird überschrieben)
        ax.barh(i, 24, height=bar_height, color=night_color, edgecolor='none', align='edge', left=0) # Starte mit Nacht

        # Tag zeichnen
        if sunrise_adj is not None and sunset_adj is not None:
             # Fall 1: Tag geht NICHT über Mitternacht (00:00 im Diagramm = 12:00 Lokalzeit)
             if sunset_adj >= sunrise_adj:
                 # Tag zeichnen
                 ax.barh(i, sunset_adj - sunrise_adj, left=sunrise_adj, height=bar_height, color=day_color, edgecolor='none', align='edge', zorder=2)

             else: # Fall 2: Tag geht über Mitternacht (Polartag) - Zeichne zwei Teile
                 # Tag Teil 1 (von sunrise_adj bis 24:00)
                 ax.barh(i, 24 - sunrise_adj, left=sunrise_adj, height=bar_height, color=day_color, edgecolor='none', align='edge', zorder=2)
                 # Tag Teil 2 (von 0:00 bis sunset_adj)
                 ax.barh(i, sunset_adj, left=0, height=bar_height, color=day_color, edgecolor='none', align='edge', zorder=2)
        # Else: Wenn sunrise oder sunset None sind, bleibt es Nacht (schon gezeichnet)

        # Dämmerung zeichnen (überlagert Nacht/Tagränder)
        # Morgendämmerung (astronomisch)
        if astro_rise_adj is not None and sunrise_adj is not None:
            if astro_rise_adj < sunrise_adj: # Normalfall: Dämmerung endet vor oder bei Sonnenaufgang am selben "Diagramm-Tag"
                ax.barh(i, sunrise_adj - astro_rise_adj, left=astro_rise_adj, height=bar_height, color=twilight_color, edgecolor='none', align='edge', zorder=3)
            else: # Dämmerung kreuzt Mitternacht (z.B. Beginn 23:00, Sonnenaufgang 01:00)
                # Teil 1: von astro_rise_adj bis 24h
                ax.barh(i, 24 - astro_rise_adj, left=astro_rise_adj, height=bar_height, color=twilight_color, edgecolor='none', align='edge', zorder=3)
                # Teil 2: von 0h bis sunrise_adj
                ax.barh(i, sunrise_adj, left=0, height=bar_height, color=twilight_color, edgecolor='none', align='edge', zorder=3)

        # Abenddämmerung (astronomisch)
        if sunset_adj is not None and astro_set_adj is not None:
            if astro_set_adj > sunset_adj: # Normalfall: Dämmerung beginnt nach oder bei Sonnenuntergang am selben "Diagramm-Tag"
                ax.barh(i, astro_set_adj - sunset_adj, left=sunset_adj, height=bar_height, color=twilight_color, edgecolor='none', align='edge', zorder=3)
            else: # Dämmerung kreuzt Mitternacht (z.B. Sonnenuntergang 23:00, Ende Dämmerung 01:00)
                # Teil 1: von sunset_adj bis 24h
                ax.barh(i, 24 - sunset_adj, left=sunset_adj, height=bar_height, color=twilight_color, edgecolor='none', align='edge', zorder=3)
                # Teil 2: von 0h bis astro_set_adj
                ax.barh(i, astro_set_adj, left=0, height=bar_height, color=twilight_color, edgecolor='none', align='edge', zorder=3)


        # Mond plotten (basierend auf den Intervallen)
        brightness = 0.1 + (moon_phase_percent / 100) * 0.9 # Helligkeit anpassen (0.1-1.0 -> 10% bis 100%)
        moon_color = (brightness, brightness, 0) # Gelblich

        for start_vis, end_vis in moon_visible_intervals:
            adj_start_hour = time_to_chart_hours(start_vis)
            adj_end_hour = time_to_chart_hours(end_vis)

            # Korrektur für Endzeit genau um 12:00 des nächsten Tages -> sollte 24.0 sein
            if adj_end_hour == 0.0 and end_vis > start_vis:
                 adj_end_hour = 24.0

            if adj_start_hour is None or adj_end_hour is None: continue # Sollte nicht passieren, aber sicher ist sicher
            
            # Mondbalken zeichnen
            if adj_end_hour > adj_start_hour: # Normalfall, kein Überlauf über 12:00 (Diagramm-Mitternacht)
                ax.barh(i, adj_end_hour - adj_start_hour, left=adj_start_hour, height=bar_height,
                        alpha=brightness, color=moon_color, edgecolor='none', align='edge', zorder=5) # zorder=5 damit es über dem Hintergrund liegt
            elif adj_end_hour <= adj_start_hour and not (adj_start_hour == 0 and adj_end_hour == 0) : # Intervall geht über 12:00 (Diagramm-Mitternacht)
                # Teil 1: von Start bis 24:00
                ax.barh(i, 24 - adj_start_hour, left=adj_start_hour, height=bar_height,
                        alpha=brightness, color=moon_color, edgecolor='none', align='edge', zorder=5)
                # Teil 2: von 0:00 bis Ende
                ax.barh(i, adj_end_hour, left=0, height=bar_height,
                        alpha=brightness, color=moon_color, edgecolor='none', align='edge', zorder=5)
            
            # Prüfen, ob Transit in diesem sichtbaren Intervall liegt
            if transit_time_local is not None and max_altitude_deg is not None:
                 # Vergleiche lokale Zeiten direkt
                 if start_vis <= transit_time_local <= end_vis:
                     transit_is_visible = True
                     # Wir brauchen die Schleife nicht weiterzuführen, wenn Transit sichtbar ist
                     # break (nicht nötig, da Flag nur einmal gesetzt wird)

        # Text für maximale Höhe hinzufügen, WENN Transit sichtbar war
        if transit_is_visible:
             transit_hour_adj = time_to_chart_hours(transit_time_local)
             if transit_hour_adj is not None: # Zusätzliche Sicherheitsprüfung
                 alt_text = f'{max_altitude_deg:.0f}°' # Höhe als ganze Zahl mit Grad-Symbol
                 ax.text(transit_hour_adj, i + bar_height / 2, alt_text,
                         color='black', # Farbe für Text (anpassen bei Bedarf)
                         fontsize=7,    # Schriftgröße (anpassen bei Bedarf)
                         ha='center', va='center', # Zentrierte Ausrichtung
                         zorder=11)     # Über allem anderen (auch Vollmond-Marker)


        # Vollmond-Symbol
        ts_local = load.timescale() # Lokale Zeitskala für Vollmondprüfung

        # Suchfenster: Von 12:00 Mittag bis 12:00 Mittag nächster Tag
        chart_day_start_local = LOCAL_TZ.localize(
            datetime.datetime.combine(date_obj, datetime.time(12, 0, 0))
        )
        # Ende exklusiv, oder eine Sekunde davor nehmen. find_discrete ist inklusiv.
        # Sicherer ist, bis zum Start des nächsten Tages zu suchen.
        chart_day_end_local = chart_day_start_local + datetime.timedelta(days=1)

        # Konvertiere zu Skyfield Time Objekten (UTC basiert intern)
        t0_fm = ts_local.from_datetime(chart_day_start_local)
        t1_fm = ts_local.from_datetime(chart_day_end_local)

        # Finde Vollmondphasen (yi == 2) in diesem 12-bis-12 Fenster
        f, y = almanac.find_discrete(t0_fm, t1_fm, almanac.moon_phases(eph))

        for ti, yi in zip(f, y):
            # Prüfe nur auf Vollmond
            if yi == 2:
                # Konvertiere die gefundene Zeit ti (ist ein Skyfield Time Objekt)
                full_moon_time_local = convert_to_local_time(ti) # Nutze deine Konvertierungsfunktion

                if full_moon_time_local: # Prüfen ob Konvertierung erfolgreich
                    # Konvertiere die lokale Zeit in Diagrammstunden (0-24 relativ zu 12:00)
                    # Diese Funktion sollte korrekt mit Zeiten nach Mitternacht umgehen
                    full_moon_hour_adj = time_to_chart_hours(full_moon_time_local)

                    if full_moon_hour_adj is not None:
                        fm_label = f'Vollmond {full_moon_time_local.strftime("%d.%m %H:%M")}' if not full_moon_plotted else ""
                        # Plotte auf dem *aktuellen* Balken (i), aber an der korrekten X-Position
                        handle = ax.plot(full_moon_hour_adj, i + bar_height / 2,
                                         marker='o', markersize=8, # Größe leicht reduziert für Ästhetik
                                         color='red', markeredgecolor='black',
                                         zorder=10, label=fm_label)
                        if not full_moon_plotted:
                            full_moon_handle = handle[0] # Speichere Handle für Legende
                            full_moon_plotted = True
                        # print(f"Vollmond gefunden für Balken {i} ({date_obj}) am: {full_moon_time_local}") # Debugging
                        break # Normalerweise nur ein Vollmond pro 24h-Fenster


    # Achsen und Legende
    # Y-Achsenbeschriftung (links - Tage)
    german_weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    # Dynamische Tick-Dichte basierend auf Anzahl der Tage
    if num_days <= 35: # Jeden Tag
        tick_step = 1
    elif num_days <= 70: # Jeden zweiten Tag
        tick_step = 2
    elif num_days <= 150: # Jeden fünften Tag
        tick_step = 5
    else: # Jeden zehnten Tag
        tick_step = 10

    final_y_ticks = []
    final_y_labels = []
    for i, (astro_rise_time, _, _, astro_set_time, date_obj, _, _, _, _) in enumerate(daylight_times):
         if i % tick_step == 0:
              final_y_ticks.append(i + bar_height / 2) # Tick in der Mitte des Balkens
              label = f'{date_obj.day}. {month_names[date_obj.month-1]} ({german_weekdays[date_obj.weekday()]})'
              # Optional: Dämmerungszeiten hinzufügen, wenn Platz ist
            #   if num_days <= 35 and astro_rise_time and astro_set_time:
            #        label += f'\n{astro_set_time.strftime("%H:%M")}-{astro_rise_time.strftime("%H:%M")}'
              final_y_labels.append(label)

    ax.set_yticks(final_y_ticks)
    ax.set_yticklabels(final_y_labels)
    ax.set_ylabel('Datum')

    # Zweite Y-Achse (rechts) - zeigt den nächsten Tag (nach 0 uhr) an
    final_y2_labels = []
    for i, (astro_rise_time, _, _, astro_set_time, date_obj, _, _, _, _) in enumerate(daylight_times):
         if i % tick_step == 0:
              next_day = date_obj + datetime.timedelta(days=1)
              label = f'{next_day.day}. {month_names[next_day.month-1]} ({german_weekdays[next_day.weekday()]})'
              # Optional: Dämmerungszeiten hinzufügen, wenn Platz ist
            #   if num_days <= 35 and astro_rise_time and astro_set_time:
            #        label += f'\n{astro_set_time.strftime("%H:%M")}-{astro_rise_time.strftime("%H:%M")}'
              final_y2_labels.append(label)

    # Zweite Y-Achse (rechts)
    ax2.set_yticks(ax.get_yticks())
    ax2.set_yticklabels(final_y2_labels) # Leere Labels
    ax2.set_ylabel('')

    
    # Linien
    for hour in range(1, 24):
        ax.axvline(x=hour, color='black', linestyle=':', linewidth=0.5, zorder=6)
    for day_idx in range(1, num_days):
        ax.axhline(y=day_idx, color='gray', linestyle='--', linewidth=0.5, zorder=6)
    if num_months <= 2:
        for i, (_, _, _, _, date_obj, _, _, _, _) in enumerate(daylight_times):
            if date_obj.weekday() in [3]:  # Do
                ax.axhline(y=i, color='gray', linestyle='-', linewidth=1.8, zorder=7) # Unter dem Balken
            elif date_obj.weekday() in [6]:  # So
                ax.axhline(y=i + bar_height, color='gray', linestyle='-', linewidth=1.8, zorder=7) # Über dem Balken


    # Achslimits und Titel
    ax.set_xlim(0, 24)
    ax.set_ylim(num_days, 0) # Invertiert, Tag 1 oben, endet unter dem letzten Balken
    ax2.set_ylim(num_days, 0)

    ax.set_xlabel('Uhrzeit (12:00 - 00:00 - 11:59)') # X-Achse oben durch tick_params gesetzt

    # Titel
    end_month_index = (start_month + num_months - 1 -1) % 12
    end_year = year + (start_month + num_months - 1 -1) // 12
    if num_months == 1:
         title = f'Astronomische Dämmerung & Mondsichtbarkeit für {month_names[start_month-1]} {year}'
    else:
         title = f'Dämmerung & Mondsichtbarkeit: {month_names[start_month-1]} {year} bis {month_names[end_month_index]} {end_year}'
    ax.set_title(title, fontsize=18, fontweight='bold', y=1.11)  # , pad=20 Erhöhtes Padding für mehr Abstand
    location_name_to_display = LOADED_LOCATION_NAME if LOADED_LOCATION_NAME else DEFAULT_LOCATION_NAME
    ax.text(0.5, 1.07, f'{location_name_to_display} (Lat: {latitude:.2f}, Lon: {longitude:.2f})', 
            fontsize=12, fontweight='bold', transform=ax.transAxes, ha='center', va='center')  # Erhöhtes Y-Offset für mehr Abstand

    # Legende erstellen
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color=day_color, label='Tag'),
        plt.Rectangle((0, 0), 1, 1, color=twilight_color, label='Dämmerung (astron.)'),
        plt.Rectangle((0, 0), 1, 1, color=night_color, label='Nacht'),
        plt.Rectangle((0, 0), 1, 1, color=moon_color, alpha=0.8, label='Mondsichtbarkeit'),
        plt.Rectangle((0, 0), 1, 1, color=weekend_color, label='Wochenende') # Wochenend-Markierung
    ]
    if full_moon_handle: # Füge Vollmond hinzu, wenn geplottet
        legend_elements.append(full_moon_handle)

    ax.legend(handles=legend_elements, loc='upper right', fontsize=10, bbox_to_anchor=(1.0, -0.02), ncol=len(legend_elements)) # Legende unterhalb

    plt.tight_layout(rect=[0, 0.03, 1, 1.0]) # Mehr Platz für Titel lassen

    elapsed_time_plot = (time.time() - start_time_plot) * 1000
    print(f"Zeit für das Diagramm: {elapsed_time_plot:.2f} ms")

    return fig

# Funktion save_diagram anpassen
def save_diagram(fig, start_month, year, num_months, location_name, latitude, longitude):
    # Speichert das Diagramm mit dynamischem Dateinamen.
    # Monatsnamen für Dateinamen
    start_month_name = month_names[start_month-1] # [:3] Nimm nur die ersten 3 Buchstaben
    end_month_index = (start_month + num_months - 1 - 1) % 12
    end_year = year + (start_month + num_months - 1 - 1) // 12
    end_month_name = month_names[end_month_index] # [:3] Nimm nur die ersten 3 Buchstaben

    # Baue den Dateinamen zusammen
    # Stelle sicher, dass location_name nicht leer ist
    if not location_name:
        location_name = DEFAULT_LOCATION_NAME # Fallback
    if num_months == 1:    
        filename = (f'Dämmerungsdiagramm {start_month_name} {year}')
    else:
        filename = (f'Dämmerungsdiagramm {start_month_name} {year} bis {end_month_name} {end_year}')
    filename +=  f' ({location_name} Lat {latitude:.2f} Lon {longitude:.2f}).png'   

    # Ersetze ungültige Zeichen für Dateinamen (optional, aber empfohlen)
    # filename = filename.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
    filename = filename.replace(",", "")

    # System-Dialog zum Speichern der Datei öffnen
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile=filename, # Setze den konstruierten Namen als Vorschlag
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )

    if save_path:
        try:
            fig.savefig(save_path)
            plt.close(fig) # Schließe die Figur nach dem Speichern
            short_path = '.../' + '/'.join(save_path.split('/')[-2:])
            print(f"Gespeichert unter: {short_path}")

            # Öffne das gespeicherte Bild mit dem systemeigenen Bildbetrachter
            if os.path.exists(save_path): # Prüfen ob Speichern erfolgreich war
                if platform.system() == 'Darwin':       # macOS
                    os.system(f'open "{save_path}"')
                elif platform.system() == 'Windows':    # Windows
                    # os.startfile(save_path) ist oft besser als os.system
                    try:
                        os.startfile(save_path)
                    except AttributeError: # Fallback für ältere Python-Versionen
                        os.system(f'start "" "{save_path}"')
                else:                                   # Linux
                    os.system(f'xdg-open "{save_path}"')
            else:
                 print("Fehler: Datei wurde nicht gefunden nach dem Speichern.")

        except Exception as e:
            print(f"Fehler beim Speichern oder Öffnen der Datei: {e}")
            plt.close(fig) # Schließe Figur auch bei Fehler

    else:
        print("Speichern abgebrochen.")
        plt.close(fig) # Schließe Figur, wenn Speichern abgebrochen wird

# Funktion für den "Erstellen"-Button
def on_create_button():
    global LOADED_LOCATION_NAME # Zugriff um den Namen zu lesen
    # Koordinaten holen
    try:
        latitude = float(latitude_entry.get() or DEFAULT_LATITUDE)
        longitude = float(longitude_entry.get() or DEFAULT_LONGITUDE)
    except ValueError:
        print("FEHLER: Ungültige Eingabe für Breitengrad oder Längengrad. (Format: nn.nnnn)")
        return # Berechnung abbrechen

    # Datum holen
    start_month = month_dropdown.current() + 1
    year = int(year_dropdown.get())
    # Berechne Anzahl Monate korrekt basierend auf Auswahl
    start_idx = month_dropdown.current()
    end_idx = end_month_dropdown.current()
    end_month_value_index = (start_idx + end_idx +1 ) % 12 # Index des Endmonats in month_names
    # if end_month_value_index <= start_idx: # Geht über Jahrwechsel
    #      num_months = 12 - start_idx + end_month_value_index +1
    # else: # Innerhalb desselben Jahres
    #      num_months = end_month_value_index - start_idx +1

    # Alternative, einfachere Zählung der Monate im Dropdown
    num_months = end_month_dropdown.current() + 1


    print("Starte Berechnung...")
    # sys.stdout.flush() # Nicht mehr nötig mit RedirectText

    # Ephemeriden prüfen
    if not os.path.exists(EPHEMERIDEN_FILE):
        print(f"{EPHEMERIDEN_FILE} nicht im Verzeichnis gefunden.")
        print("Ephemeriden werden einmalig heruntergeladen.")
        print("Bitte um Geduld, das kann etwas dauern...")
    try:
        eph = load(EPHEMERIDEN_FILE)
    except Exception as e:
        print(f"Fehler beim Laden der Ephemeriden-Datei {EPHEMERIDEN_FILE}: {e}")
        print("Stelle sicher, dass die Datei existiert oder heruntergeladen werden kann.")
        return # Berechnung abbrechen

    # Diagramm erstellen
    fig = create_diagram(latitude, longitude, year, start_month, num_months, eph)

    # Speichern vorbereiten
    if fig is not None: # Nur speichern, wenn Diagramm erstellt wurde
        # Bestimme den Namen für den Speicherort
        current_location_name = LOADED_LOCATION_NAME if LOADED_LOCATION_NAME else DEFAULT_LOCATION_NAME

        # Übergib die aktuellen Werte an save_diagram 
        save_diagram(fig, start_month, year, num_months, current_location_name, latitude, longitude)
    else:
        print("Diagrammerstellung fehlgeschlagen. Nichts zu speichern.")

    progress_var.set(0)

# Funktion zum Speichern der Werte in eine INI-Datei (wird von save_button verwendet)
def save_to_ini():
    global LOADED_LOCATION_NAME, location_display_var, SELECTED_TIMEZONE
    initial_name = f"{LOADED_LOCATION_NAME}.ini" if LOADED_LOCATION_NAME else "Koordinaten.ini"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".ini", initialfile=initial_name,
        filetypes=[("INI files", "*.ini"), ("All files", "*.*")])
    if file_path:
        try:
            current_tz = timezone_combo.get() # Hole aktuelle Auswahl aus Combobox
            with open(file_path, 'w') as file:
                file.write(f"latitude={latitude_entry.get()}\n")
                file.write(f"longitude={longitude_entry.get()}\n")
                file.write(f"timezone={current_tz}\n") # Schreibe Zeitzone 
            print(f"Koordinaten und Zeitzone gespeichert unter: {file_path}")
            base = os.path.basename(file_path); new_name = os.path.splitext(base)[0]
            LOADED_LOCATION_NAME = new_name
            location_display_var.set(f"Ort: {LOADED_LOCATION_NAME}")
            # Update globale TZ nur wenn nötig (wird eigentlich durch Auswahl-Event gemacht)
            if current_tz != SELECTED_TIMEZONE:
                 SELECTED_TIMEZONE = current_tz
                 try:
                      LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
                 except pytz.exceptions.UnknownTimeZoneError:
                      print(f"FEHLER: Gespeicherte Zeitzone '{SELECTED_TIMEZONE}' ist ungültig?")
                      # Fallback? Eigentlich sollte Combobox nur gültige enthalten.
                      SELECTED_TIMEZONE = DEFAULT_TIMEZONE
                      LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
                      timezone_combo.set(SELECTED_TIMEZONE)

            root.title(f"Dämmerungsdiagramm | {LOADED_LOCATION_NAME}")
        except Exception as e:
            print(f"Fehler beim Speichern der INI-Datei: {e}")

# Funktion zum Laden der Werte aus einer INI-Datei
def load_from_ini():
    global LOADED_LOCATION_NAME, location_display_var
    global SELECTED_TIMEZONE, LOCAL_TZ # Zugriff auf TZ-Variablen
    file_path = filedialog.askopenfilename(
        filetypes=[("INI files", "*.ini"), ("All files", "*.*")])
    if file_path:
        lat_str, lon_str, tz_str = None, None, None
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("latitude="): lat_str = line.split("=")[1].strip()
                    elif line.startswith("longitude="): lon_str = line.split("=")[1].strip()
                    elif line.startswith("timezone="): tz_str = line.split("=")[1].strip() # Lese Zeitzone 

            # Setze Koordinaten
            if lat_str is not None: latitude_entry.delete(0, tk.END); latitude_entry.insert(0, lat_str)
            if lon_str is not None: longitude_entry.delete(0, tk.END); longitude_entry.insert(0, lon_str)

            # Setze Ortsnamen und Titel
            base_name = os.path.basename(file_path)
            location_name_from_file = os.path.splitext(base_name)[0]
            LOADED_LOCATION_NAME = location_name_from_file
            location_display_var.set(f"Ort: {LOADED_LOCATION_NAME}")
            root.title(f"Dämmerungsdiagramm | {LOADED_LOCATION_NAME}")

            # Setze Zeitzone 
            tz_set = False
            if tz_str and tz_str in timezone_combo['values']: # Prüfe ob gefunden UND gültig
                try:
                    SELECTED_TIMEZONE = tz_str
                    LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE) # Aktualisiere TZ-Objekt
                    timezone_combo.set(SELECTED_TIMEZONE)       # Setze Combobox-Anzeige
                    print(f"Zeitzone '{SELECTED_TIMEZONE}' aus INI geladen.")
                    tz_set = True
                except pytz.exceptions.UnknownTimeZoneError:
                     print(f"Warnung: Ungültige Zeitzone '{tz_str}' in INI gefunden.")
            else:
                 if tz_str: # Gefunden aber nicht in Liste
                      print(f"Warnung: Unbekannte Zeitzone '{tz_str}' in INI ignoriert.")

            if not tz_set: # Wenn nicht gesetzt (nicht gefunden oder ungültig) -> Default
                SELECTED_TIMEZONE = DEFAULT_TIMEZONE
                LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
                timezone_combo.set(SELECTED_TIMEZONE)
                print(f"Keine gültige Zeitzone in INI gefunden, verwende Default: {SELECTED_TIMEZONE}")

            print(f"Einstellungen für '{LOADED_LOCATION_NAME}' geladen von: {file_path}")

        except Exception as e:
            print(f"Fehler beim Lesen der INI-Datei: {e}")
            LOADED_LOCATION_NAME = None
            # Reset auf Defaults bei Fehler
            location_display_var.set(f"Ort: {DEFAULT_LOCATION_NAME}")
            SELECTED_TIMEZONE = DEFAULT_TIMEZONE
            LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
            timezone_combo.set(SELECTED_TIMEZONE)
            root.title(f"Dämmerungsdiagramm")


# GUI erstellen
root = tk.Tk()
root.geometry("500x480")
root.resizable(False, False)
root.title("ADD V1.0 | Armin Pressler 2025")

# StringVar für die Ortsanzeige erstellen
location_display_var = StringVar()
location_display_var.set(f"Ort: {DEFAULT_LOCATION_NAME}") # Initialwert setzen

# Standort-Eingaben mit Rahmen
frame = tk.Frame(root, bd=2, relief="groove")
frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

# Breitengrad
tk.Label(frame, text="Breitengrad:").grid(row=0, column=0, padx=5, pady=5)
latitude_entry = tk.Entry(frame, width=int(20 * 0.8))  # Verkleinern um 80%
latitude_entry.grid(row=0, column=1, padx=5, pady=5)
latitude_entry.insert(0, str(DEFAULT_LATITUDE))  # Standardwert setzen

# Längengrad
tk.Label(frame, text="Längengrad:").grid(row=0, column=2, padx=5, pady=5)
longitude_entry = tk.Entry(frame, width=int(20 * 0.8))  # Verkleinern um 80%
longitude_entry.grid(row=0, column=3, padx=5, pady=5)
longitude_entry.insert(0, str(DEFAULT_LONGITUDE))  # Standardwert setzen

# Zeile 1: Zeitzone
tk.Label(frame, text="Zeitzone:").grid(row=1, column=0, padx=(5,0), pady=5, sticky='w')

# Liste aller Zeitzonen holen
all_tzs = sorted(pytz.all_timezones)
timezone_combo = ttk.Combobox(frame, values=all_tzs, state="readonly", width=28) # Breite angepasst
timezone_combo.grid(row=1, column=1, columnspan=3, padx=(0,5), pady=5, sticky='ew')

# Default setzen
try:
    default_tz_index = all_tzs.index(DEFAULT_TIMEZONE)
    timezone_combo.current(default_tz_index)
except ValueError:
    print(f"Warnung: Default Zeitzone '{DEFAULT_TIMEZONE}' nicht in pytz Liste gefunden. Setze erste.")
    timezone_combo.current(0) # Fallback: erste Zone in der Liste
    SELECTED_TIMEZONE = timezone_combo.get() # Update globalen String
    LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE) # Update TZ Objekt

# Funktion und Binding für Zeitzonen-Änderung
def on_timezone_selected(event):
    global SELECTED_TIMEZONE, LOCAL_TZ
    new_tz_str = timezone_combo.get()
    if new_tz_str != SELECTED_TIMEZONE:
        print(f"Zeitzone manuell geändert zu: {new_tz_str}")
        SELECTED_TIMEZONE = new_tz_str
        try:
            LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
        except pytz.exceptions.UnknownTimeZoneError:
             print(f"FEHLER: Ausgewählte Zeitzone '{SELECTED_TIMEZONE}' ungültig?!")
             # Fallback auf Default oder UTC? Hier Default.
             SELECTED_TIMEZONE = DEFAULT_TIMEZONE
             LOCAL_TZ = pytz.timezone(SELECTED_TIMEZONE)
             timezone_combo.set(SELECTED_TIMEZONE)

timezone_combo.bind("<<ComboboxSelected>>", on_timezone_selected)


# Icons als binäre Arrays
load_icon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x19\x08\x06\x00\x00\x00\xc4\xe9\x85c\x00\x00\x01\x82IDATx\x9c\xdd\xd5\xb1jTQ\x10\x06\xe0\xef\xae\x1b\x836B*\xb10\xcf\x90\x80\x01\x8b4B\xf2\x04\x924Bl\x02\xf1\x01\x04[\xbb\xbc\x82\x96\x16\xe9l$\xe9\xc4R_CB\xb0KcT\xccjr\xc3\x81\xb9\xe6ds\xef\xeeYv\xb5\xf0\x87\xcb=;3g\xfe\x99\x7f\x87\xb9\xfc\x03T#|\xbd1\xfe\x843S\xa0\x9ae\\\xd5a\xab\xb1\x8a\xa5\xa86\x8f\xab\xd1\xc7\x11\xdef\xf1\xc5$I\xa2s<\xc3c|\x8c\x04\xf5PL\xfa\xbd\x82Ox\x19\xa4\xbf\'\xe9j\x0e\xefq\xaf\xe0\xce;<\x8fs"jE\x9b\xe3&\xbe\xe1G\xf8s9\xaa8/F\xa7\x1b\xd8\xc7W\xbc\xea\xea(\xb5>\x8c:\xec7\xe2B\xdbs\x0b\x0f\xf1\x13\x9b\xd8\xc2\x93\xf0\xf5JHr\xb2.\x9ce\xe3{\x8c5<\xc5z\xfc\xa7W\xf2v\xea8\x82\xb8\xc2a\xbc_c\x10\xd2\xfe\xc2\x1b,\xe3K.\xf3\xa4$\r\xbe\x87D\x0fB\xd6T\xf9\x01Nq2J\x89f\xban\xc7\xd4,\x0c\xd9K\xb0\x13\x03!\xc8M\xd3IC\xde\x14\xd0LU\x9a\xbak\x98\x86\xa4\xce$9\x8fgP:\xc2f\xd4\xdd_#i\xc5\xffC\xd2\xef\xb07\xab\xa5W\xb2\xca]\xae\xa1\xba\x94$M\xc9|,\xbdt.\xc1 \xdeU\x9b:\xfd\x96\xea\xd3\xd2\xfb\x8c\xddX\x13sc:\xa9b\xa5\xdc\xc7#lg\xc5\xfe\t\x18\xbe\x90\x12\xde\xc1\x0b\xdc\xcd\xf6\xd5(\xd4\x91t\x0f\x1f\n%\x9e\n\xd5XCfo>\xc5\x93&\x9f\xe4\xce\xecp\x01i\xcdV\xf0\xd7A\x14\x9a\x00\x00\x00\x00IEND\xaeB`\x82'
save_icon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x19\x08\x06\x00\x00\x00\xc4\xe9\x85c\x00\x00\x02EIDATx\x9c\xad\x96\xbf\x8fLQ\x14\xc7?w\xd6\xceX\xbfg\xac\x15"Q\xa0Q\x88Rh%J\x89R)4\x12\x7f\x80\xce\xafF%\n\x1aT*\n\x95\x06\x8dh%\xf4\x92m\x10,A\xfc\nf\xc6<\xb9\x9b\xefYg\xcf\xde7\xcf\x86orsf\xee\xfb\xde\xf3\xfb\x9e\xf7\xe0\x0f\x12\xff\x8eVi3*^\xef\x88\xbf\x80\x891\n\x93d\xa5\xf5\r\x18\xe8\xfc(\x12\x93H\xe7\x80\xe3R\x9e\x89k\x80\xafzf\x1cC\x12\xaf\x12\xb7\r\xf4\x81#\xc0c`\x050$`\x1d\xf0\x0e\xd8\x0bt\x81\x9d\xc0\x1c\xb0\x03\xe8\x01\x1b%me\xce6`\x97\x9e]\x06f\x81g\xc0\x01\xe9\xcc\x86\x16!\x1f|\x0e\xacuF_\xb8\xff\x11\x93\xc0S\xe0\rpXY\xb8\x08\x1c\x02\xbe\x03\xfb\xc4\x9bO\xbd\xe5\xdf\xc2\xee(\x15\xed [A\xf6\xe4\xe9\x13`\xb7R5\r\xdc\x03N\x01\x0f\x80\xfd\xaaM+\x86dE\xb4\xfc\xc7\xdf^~\x04^\xbb\x06\x19J^\x97#\xb7\x95\xf6\x1f\xc5\x96s\xca&\x94\x9a\xb82\xf6\xa8\xd0\xbey\xacinJ\xae*\x16GHz\x96\x9b\xa1\x849\xe0\x04\xb0U\x9e\x9fv\xed>RgZ\xf7-1b\xa9\xf8\xa2T\xdc\x02\xde\xca\xab*p?H\xe1yE\x94\xa5a\xe4\xef`]\xba~\x02G\x81W\x8e\x93\xc2\xda\x0cl\x01\xa6\x80\x0b\xc0\r\x1a\x90\xfb\xfe\xa5\xba\xc6\x14.\x17\xc9\x9d\xebI_w\\M\x0c\xd3\xcau\xd5\xa0<w\xd6\xfb:\xe7\xea\x8cd\xa5g\xdd\x98\xf1^zX\x8bgG\xae\x01gX\x86\x91<(O\x02\x075\tJ\x85G\x86s\x91\xb7\x03\xf7\x81K\xc0\'\x1a\x8c\x98\xb7\x93\x1a\x0f\xb3\x1a\x92M\xe8\xe7K\xe7\xee\xd0\xa2\xa8\xeb\xba+\x8e\x19\x1b\'),\xdb_9&\xdab\xba\xbc\x17\xa5\xb1\x12\xe19\x94jW\x8ad\\\'\xfd\r\xaa\xa6H\xb2\xd1\r5\x17\xb0\x84\x14d<\xbf\xb0i\xa4\x81jpG\xb7\xb8\xaf\xbdJ\x1dT\x15\x96\xed\x0f\xc4\x9f\xd2\xf9\x8e\xf6\x92\x8fd\xa8\xa16\x03\x1c\x13i5\xb0I\x9c\xf8\xfa5\xd8~W\xfc\x8e\xce\xcfH\xdf\xfc+\xd8\x14|\x06\xae\x02w5\xb7\xda\xea\x98G5\xefx\x82\x11\xeb\xb0\x87\x8a(\x9f\xbf"\xbd\xa9\xf4\xb5bc\xa4\xe9k%\xc2\xf8\xf6\x91\xb1\xe4R\x9aW\xff\x13\x0b\xfa~\x03x\x14\x8d\x17\x1c\xc7e\xd1\x00\x00\x00\x00IEND\xaeB`\x82'

save_icon_image = Image.open(io.BytesIO(save_icon_data))
load_icon_image = Image.open(io.BytesIO(load_icon_data))
save_icon = ImageTk.PhotoImage(save_icon_image)
load_icon = ImageTk.PhotoImage(load_icon_image)

# Buttons etwas anders platzieren neben dem Label
save_button = tk.Button(frame, image=save_icon, command=save_to_ini)
save_button.grid(row=2, column=5, padx=(10,5), pady=(5, 5), sticky='e') # Spalte 5
load_button = tk.Button(frame, image=load_icon, command=load_from_ini)
load_button.grid(row=2, column=6, padx=5, pady=(5, 5), sticky='e') # Spalte 6
save_button.image = save_icon
load_button.image = load_icon

# Label für Ortsanzeige in Zeile 2
location_label = tk.Label(frame, textvariable=location_display_var, font=('TkDefaultFont', 12, 'bold'))
location_label.grid(row=2, column=0, columnspan=5, padx=5, pady=(0, 5), sticky='ew') # In neuer Zeile, über alle Spalten

# Grid Konfiguration für Standort-Rahmen
frame.grid_columnconfigure(1, weight=1) # Eingabefeld Breite wachsen lassen
frame.grid_columnconfigure(3, weight=1) # Eingabefeld Länge wachsen lassen
# frame.grid_columnconfigure(4, weight=1) # Platz zwischen Eingabe und Buttons
frame.grid_columnconfigure(5, weight=0) # Button feste Breite
frame.grid_columnconfigure(6, weight=0) # Button feste Breite
frame_date = tk.Frame(root, bd=2, relief="groove")
frame_date.grid(row=2, column=0, columnspan=4, padx=5, pady=15, sticky='ew')

# Startmonat
tk.Label(frame_date, text="Start-Monat:").grid(row=0, column=0, padx=5, pady=5)
month_names = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
               'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
month_dropdown = ttk.Combobox(frame_date, values=month_names, state="readonly")
month_dropdown.grid(row=0, column=1, padx=5, pady=5)
# month_dropdown.current(current_month)

current_date = datetime.datetime.now()
current_month_idx = current_date.month - 1 # Monat ist 1-basiert, Index ist 0-basiert
month_dropdown.current(current_month_idx) # Setze den Index für den aktuellen Monat

# Endmonat
tk.Label(frame_date, text="Ende-Monat:").grid(row=0, column=2, padx=5, pady=5)
end_month_dropdown = ttk.Combobox(frame_date, state="readonly")
end_month_dropdown.grid(row=0, column=3, padx=5, pady=5)

# Endmonat basierend auf dem Startmonat aktualisieren
# https://stackoverflow.com/questions/62401123/tkinter-combobox-dependent-on-another-combobox
def update_end_month_dropdown(event):
    start_month_index = month_dropdown.current() - 1
    available_months = month_names[start_month_index +
                                   1:] + month_names[:start_month_index + 1]
    end_month_dropdown['values'] = available_months
    end_month_dropdown.current(0)

# Endmonat aktualisieren, wenn der Startmonat geändert wird
month_dropdown.bind("<<ComboboxSelected>>", update_end_month_dropdown)
update_end_month_dropdown(None)

# Jahr
tk.Label(frame_date, text="Jahr:").grid(row=2, column=0, padx=5, pady=5)
current_year = current_date.year # Kann current_date von oben wiederverwenden
year_values = list(range(current_year - 5, current_year + 21))
year_dropdown = ttk.Combobox(frame_date, values=year_values, state="readonly", width=7)
year_dropdown.grid(row=2, column=1, padx=5, pady=5)
if current_year in year_values:
    year_dropdown.current(year_values.index(current_year))
else:
    year_dropdown.current(len(year_values) // 2)

# Erstellen-Button
create_button = tk.Button(root, text="Diagramm erstellen und speichern", command=on_create_button)
create_button.grid(row=4, column=0, columnspan=4, padx=5, pady=15)

# Progress Bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, length=490, maximum=100)  # , mode='determinate'
progress_bar.grid(row=6, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

# Textfeld für Konsolenausgaben mit Scrollbars
console_frame = tk.Frame(root)
console_frame.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

console_text = tk.Text(console_frame, height=10, wrap='none', width=40, font=("TkDefaultFont", 8))
console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_y = tk.Scrollbar(console_frame, command=console_text.yview)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
console_text['yscrollcommand'] = scrollbar_y.set

scrollbar_x = tk.Scrollbar(root, orient='horizontal', command=console_text.xview)
scrollbar_x.grid(row=8, column=0, columnspan=4, padx=5, pady=0, sticky='ew')
console_text['xscrollcommand'] = scrollbar_x.set

# Umleiten der Standardausgabe auf das Textfeld
sys.stdout = RedirectText(console_text)
sys.stderr = RedirectText(console_text)

print("ADD - Astronomisches Dämmerungs Diagramm ist bereit.")

root.mainloop()