import utils as u
import re
from tools import *
import asyncio
# Push from terminal from a second user
# git config --local credential.helper ""




def main():
    asyncio.run(export_messages())
    

async def export_messages(export_file = "base.txt"):
    
        channel_dict = dict()  # {channel_id: channel_name}
        
        try:
            contenido = scraper()
            cleansed_content = cleanse_message(contenido)
            channel_dict = update_channel_dict(cleansed_content, channel_dict)
        except Exception as e:
            print("exportMessages : ERROR :", e)
            sys.exit(0)
            
        export_channels(channel_dict, export_file)
    
  
def cleanse_message(message_content):
    
    cleansed_content = ""
    rows = [row for row in message_content.split("\n") if len(row.strip()) > 0]
    channel_id_regex = r'[a-zA-Z0-9]{40}'
    
    if re.search(channel_id_regex, message_content):
        for i, row in enumerate(rows):
            if re.search(channel_id_regex, row):
                if i > 0:
                  cleansed_content += rows[i-1] + "\n" + row + "\n"
                else:
                  cleansed_content += "UNTITLED CHANNEL" + "\n" + row + "\n"
                
    return cleansed_content


def update_channel_dict(message_content, channel_dict):
    
    rows = message_content.split("\n")
    
    for i, row in enumerate(rows):
        if i % 2 == 1:
            channel_id = row
            channel_name = rows[i-1]
            if "DAZN F1 1080" in channel_name:
                channel_name = "DAZN F1 1080"
            elif "DAZN F1 720" in channel_name:
                channel_name = "DAZN F1 720"
            elif "SmartBanck" in channel_name:
                channel_name = channel_name.replace("SmartBanck", "Smartbank")
            elif "La1" in channel_name:
                channel_name = channel_name.replace("La1", "La 1")
            elif "LA 1" in channel_name:
                channel_name = channel_name.replace("LA 1", "La 1")
            elif "Tv" in channel_name:
                channel_name = channel_name.replace("Tv", "TV")
            elif "#0 de Movistar" in channel_name:
                channel_name = channel_name.replace("#0 de Movistar", "#0 M+ HD")
            elif "BarÃ§a" in channel_name:
                channel_name = channel_name.replace("BarÃ§a", "Barça")
            elif "beIN SPORTS Ã±" in channel_name:
                channel_name = channel_name.replace("beIN SPORTS Ã±", "beIN SPORTS ñ")
                
            channel_dict[channel_id] = channel_name
            
    return channel_dict


def export_channels(channel_dict, export_file):
    
    channel_list = []
    
    for channel_id, channel_name in channel_dict.items():
        group_title = u.extract_group_title(channel_name)
        tvg_id = u.extract_tvg_id(channel_name)
        logo = u.get_logo(tvg_id)
        identif = (channel_id[0:4])
        channel_info = {"group_title": group_title,
                        "tvg_id": tvg_id,
                        "logo": logo,
                        "channel_id": channel_id,
                        "channel_name": channel_name + "  " + identif}
        channel_list.append(channel_info)
        
    all_channels = ""
    all_channels += '#EXTM3U url-tvg="https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guia.xml, https://raw.githubusercontent.com/acidjesuz/EPG/master/guide.xml"\n'
    channel_pattern = '#EXTINF:-1 group-title="GROUPTITLE" tvg-id="TVGID" tvg-logo="LOGO" ,CHANNELTITLE\nacestream://CHANNELID\n'
    #channel_pattern = '#EXTINF:-1 group-title="GROUPTITLE" tvg-id="TVGID" tvg-logo="LOGO" ,CHANNELTITLE\nhttp://127.0.0.1:6878/ace/getstream?id=CHANNELID\n'

    for group_title in u.group_title_order:
        for channel_info in channel_list:
            if channel_info["group_title"] == group_title:
                all_channels += channel_pattern.replace("GROUPTITLE", channel_info["group_title"]) \
                                               .replace("TVGID", channel_info["tvg_id"]) \
                                               .replace("LOGO", channel_info["logo"]) \
                                               .replace("CHANNELID", channel_info["channel_id"]) \
                                               .replace("CHANNELTITLE", channel_info["channel_name"])

    if all_channels != "":
        
        all_channels_kodi = all_channels.replace("acestream://", "plugin://script.module.horus?action=play&id=")
        all_channels_get = all_channels.replace("acestream://", "http://127.0.0.1:6878/ace/getstream?id=")
        blacklist = ["Francia", "Polonia", "Alemania", "UK", "Adultos", "Rusia", "Rumania", "Barça TV", "Ziggo", "Kings", "BT", "ESPN", "Fox", "Sport Tv", "720", "Telecinco", "Sky", "Spain", "Twitch", "Peliculas", "Deportes sin Acestream", "TDT", "Colombia", "DirectSports Plus", "RALLY", "tdt", "rally", "RUSIA-РОССИЯ", "UNITED STATES", "LAT", "MUSIC", "CANADA", "CHILE", "PARAGUAY", "MEXICO", "ECUADOR", "PERU", "CUBA", "BOLIVIA", "COLOMBIA", "URUGUAY", "ARGENTINA", "ESPAÑA", "DESPORTOS MUNDO", "VENEZUELA", "Luca", "Setanta", "Mundotoro", "SETANTA SPORTS", "Petanca", "INSTAT",  "instat", "#EXTINF:0", "VOD ESPAÑOL"]  # lista negra    
        i = 0  # inicializamos el índice

        while i < len(all_channels):
            if i < len(all_channels) - 1 and "#EXTINF" in all_channels[i] and any(b in all_channels[i] for b in blacklist):
                i += 2  # saltar las dos líneas
            else:
                filtered_playlist.append(all_channels[i])
                i += 1
        filtered_playlist = "\n".join(filtered_playlist)  # unimos las líneas filtradas
        with open(export_file, "w") as f:
            f.write(all_channels)
            print("exportChannels : OK : list exported to Github")
            f.close()

        with open("kodi.txt", "w") as k:
            k.write(all_channels_kodi)
            print("exportChannels : OK : kodi list exported to Github")
            k.close()

        with open("get.txt", "w") as g:
            g.write(all_channels_get)
            print("exportChannels : OK : get list exported to Github")
            g.close()
            
    else:
        print("exportChannels : ERROR : list is empty")
        

if __name__ == "__main__":
    main()
