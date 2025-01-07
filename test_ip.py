#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import vlc
import time

# Dictionary für die verfügbaren Sprachen und die zugehörige M3U-URL
# (Basierend auf iptv-org/languages)
LANGUAGE_PLAYLISTS = {
    "de": "https://iptv-org.github.io/iptv/languages/deu.m3u",  # Deutsch
    "en": "https://iptv-org.github.io/iptv/languages/eng.m3u",  # Englisch
    "tr": "https://iptv-org.github.io/iptv/languages/tur.m3u",  # Türkisch
}

def fetch_m3u(url):
    """
    Lädt die M3U-Datei von der angegebenen URL herunter
    und gibt den Inhalt als String zurück.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

def parse_m3u(m3u_content):
    """
    Parst den Inhalt einer M3U-Datei (als String).
    Gibt eine Liste von Sendern zurück,
    wobei jeder Sender ein Dictionary mit Name und URL ist:
    
    [
      {
        'name': 'Kanalname',
        'url': 'http://.../some_stream.m3u8'
      },
      ...
    ]
    """
    channels = []
    
    # Wir suchen Zeilen, die mit #EXTINF beginnen (enthält Kanalname etc.)
    # und danach direkt eine Zeile mit der URL:
    #  #EXTINF:-1 tvg-id="..." tvg-name="..." ... ,Kanalname
    #  http://some_stream_url.m3u8
    pattern = r'#EXTINF.*?,(.*?)\n(http.*?)(?:\n|$)'
    matches = re.findall(pattern, m3u_content, flags=re.MULTILINE)
    
    for match in matches:
        channel_name = match[0].strip()
        channel_url = match[1].strip()
        channels.append({
            'name': channel_name,
            'url': channel_url
        })
    
    return channels

def play_stream(stream_url):
    """
    Spielt einen IPTV-Stream per VLC ab.
    """
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(stream_url)
    player.set_media(media)

    player.play()
    print(f"Starte Wiedergabe: {stream_url}")

    try:
        while True:
            # Optional: Status ermitteln, Fehlerbehandlung etc.
            time.sleep(1)
    except KeyboardInterrupt:
        print("Wiedergabe wird beendet...")
    finally:
        player.stop()

def main():
    # 1) Sprache auswählen
    print("Verfügbare Sprachen:")
    print("1. Deutsch (de)")
    print("2. Englisch (en)")
    print("3. Türkisch (tr)")
    choice_lang = input("\nBitte wähle eine Sprache (Zahl eingeben): ")
    
    if choice_lang == "1":
        selected_lang = "de"
    elif choice_lang == "2":
        selected_lang = "en"
    elif choice_lang == "3":
        selected_lang = "tr"
    else:
        print("Ungültige Auswahl. Programm wird beendet.")
        return
    
    # 2) M3U für die gewählte Sprache laden
    m3u_url = LANGUAGE_PLAYLISTS.get(selected_lang)
    if not m3u_url:
        print("Keine passende M3U-URL für diese Sprache gefunden.")
        return
    
    print(f"\nLade M3U-Liste für Sprache '{selected_lang}'...")
    try:
        m3u_data = fetch_m3u(m3u_url)
    except Exception as e:
        print(f"Fehler beim Laden der M3U-Datei: {e}")
        return

    # 3) Kanalliste parsen
    print("Parsing der M3U-Liste...")
    channels = parse_m3u(m3u_data)
    print(f"Anzahl gefundener Sender: {len(channels)}")

    if not channels:
        print("Keine Sender gefunden. Programm wird beendet.")
        return

    # 4) Kanäle auflisten
    print("\nVerfügbare Sender:")
    for idx, ch in enumerate(channels, start=1):
        print(f"{idx}. {ch['name']}")

    # 5) Sender auswählen
    choice_channel = input("\nBitte wähle einen Sender (Zahl eingeben): ")
    try:
        choice_channel = int(choice_channel)
        if 1 <= choice_channel <= len(channels):
            chosen_channel = channels[choice_channel - 1]
            print(f"\nDu hast gewählt: {chosen_channel['name']}")
            print("Starte Wiedergabe...\n")
            play_stream(chosen_channel['url'])
        else:
            print("Ungültige Auswahl. Programm wird beendet.")
    except ValueError:
        print("Bitte eine gültige Zahl eingeben. Programm wird beendet.")

if __name__ == "__main__":
    main()
