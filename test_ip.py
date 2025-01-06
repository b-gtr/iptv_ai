#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import vlc
import time

M3U_URL = "https://iptv-org.github.io/iptv/countries/tr.m3u"

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
        'name': 'TRT 1',
        'url': 'http://.../some_stream.m3u8'
      },
      ...
    ]
    """
    channels = []
    
    # Wir suchen Zeilen, die mit #EXTINF beginnen (enthält Kanalname etc.)
    # und danach direkt eine Zeile mit der URL
    # Beispiel:
    # #EXTINF:-1 tvg-id="..." tvg-name="TRT 1" ... ,TRT 1
    # http://some_stream_url.m3u8
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

def select_channels(channels, filter_list=None):
    """
    Filtert die Kanal-Liste optional nach bestimmten Sendernamen,
    wenn `filter_list` angegeben ist.
    Beispiel: filter_list = ["ATV", "TRT 1", "Kanal 7"]
    Gibt die gefilterte Liste zurück oder alles, wenn `filter_list` = None.
    """
    if not filter_list:
        return channels
    
    filtered = []
    for ch in channels:
        # Wir suchen exakte Matches oder einfache 'in'-Matches,
        # je nachdem, wie du filtern möchtest.
        for f in filter_list:
            if f.lower() in ch['name'].lower():
                filtered.append(ch)
                break
    return filtered

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
            state = player.get_state()
            # Optional: Statusausgabe oder Fehlermanagement
            time.sleep(1)
    except KeyboardInterrupt:
        print("Wiedergabe wird beendet...")
    finally:
        player.stop()

def main():
    print("IPTV-Player mit Daten von iptv-org (Land: Türkei)")
    print("Lade M3U-Liste...")

    try:
        m3u_data = fetch_m3u(M3U_URL)
    except Exception as e:
        print(f"Fehler beim Laden der M3U-Datei: {e}")
        return

    print("Parsing der M3U-Liste...")
    all_channels = parse_m3u(m3u_data)
    print(f"Anzahl gefundener Sender: {len(all_channels)}")

    # Optionale Filter-Liste (nur bestimmte Sender anzeigen)
    desired_channels = ["atv", "TRT 1", "Kanal 7"]  # Beispiel
    filtered_channels = select_channels(all_channels, desired_channels)

    if not filtered_channels:
        print("Keine passenden Sender gefunden.")
        return

    # Sender-Auswahl anzeigen
    print("\nGefundene Sender:")
    for idx, ch in enumerate(filtered_channels, 1):
        print(f"{idx}. {ch['name']}")

    choice = input("\nBitte wähle einen Sender (Zahl eingeben): ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(filtered_channels):
            chosen_channel = filtered_channels[choice - 1]
            print(f"Du hast gewählt: {chosen_channel['name']}")
            play_stream(chosen_channel['url'])
        else:
            print("Ungültige Auswahl.")
    except ValueError:
        print("Bitte eine gültige Zahl eingeben.")

if __name__ == "__main__":
    main()
