from flask import Flask, render_template, request, redirect
import requests
import json


app = Flask(__name__)

games_list = []
biz_list = [
    {"biz": "hk4e_global", "game": "Genshin Impact"},
    {"biz": "hkrpg_global", "game": "Honkai: Star Rail"},
    {"biz": "nap_global", "game": "Zenless Zone Zero"}
]
hi3 = {"biz": "bh3_global", "game": "Honkai Impact 3rd"}
lang_key = [
    {"abv": "en-us", "language": "English"},
    {"abv": "ja-jp", "language": "Japanese"},
    {"abv": "ko-kr", "language": "Korean"},
    {"abv": "zh-cn", "language": "Chinese"},
    {"abv": "zh-tw", "language": "Taiwanese"}
]

@app.route("/", methods=["GET", "POST"])
def index():
    global games_list
    if request.method == "POST":
        url = request.form.get("url")
        try:
            json = requests.get(url).json()
        except:
            return render_template("index.html", message="Enter a valid API URL.")
        if json["retcode"] != 0 or json["message"] != "OK" or json.get("data") == None:
            return render_template("index.html", message="Enter the correct API URL.")
        
        games_list = []
        for biz in biz_list:
            for package in json["data"]["game_packages"]:
                if biz["biz"] == package["game"]["biz"]:
                    temp_data = {}
                    temp_data["biz"] = biz["biz"]
                    temp_data["game"] = biz["game"]
                    if package["pre_download"]["major"]:
                        temp_data["pre"] = True
                    else:
                        temp_data["pre"] = False
                    temp_data["link"] = package
                    games_list.append(temp_data)
        temp_data = {}
        for package in json["data"]["game_packages"]:
            if package["game"]["biz"] == hi3["biz"]:
                temp_data["biz"] = hi3["biz"]
                temp_data["game"] = hi3["game"]
                if package["pre_download"]["major"]:
                    temp_data["pre"] = True
                temp_data["link"] = []
                temp_data["link"].append(package)
        if temp_data:
            if "pre" not in temp_data:
                temp_data["pre"] = False
            games_list.append(temp_data)
        if len(games_list) == 0:
            return render_template("index.html", message="API Error, try again.")
        return redirect("/select")
    return render_template("index.html")

@app.route("/select")
def select():
    if request.args.get('code') == "001":
        return render_template("select.html", games=games_list, message = "Pre-Download not available. Choose Main Download.")
    if request.args.get('code') == "002":
        return render_template("select.html", games=games_list, message = "Select a Game.")
    if request.args.get('code') == "003":
        return render_template("select.html", games=games_list, message = "Select a Download Method.")
        
    return render_template("select.html", games=games_list)

@app.route("/links", methods=["GET", "POST"])
def links():
    if request.method == "POST":
        select_game = {}
        select_game["biz"] = request.form.get("game")
        select_game["pre_download"] = request.form.get("pre")
        game_biz = biz_list.copy()
        is_game = False
        for game in game_biz:
            if game["biz"] == select_game["biz"]:
                is_game = True
        if not(is_game) and select_game["biz"] != hi3["biz"]:
            return redirect("/select?code=002")
        if select_game["pre_download"] != "yes" and select_game["pre_download"] != "no":
            return redirect("/select?code=003")
        if select_game["biz"] == hi3["biz"]:
            select_game["name"] = hi3["game"]
            select_game["links"] = []
            for game in games_link:
                if game["game"]["biz"] == select_game["biz"]:
                    if select_game["pre_download"] == "yes":
                        if game["pre_download"]["major"]:
                            select_game["links"].append(game["pre_download"])
                        else:
                            return redirect("/select?code=001")
                    if select_game["pre_download"] == "no":
                        select_game["links"].append(game["main"])
            return render_template("links.html", game=select_game)
        else:
            for game in game_biz:
                if game["biz"] == select_game["biz"]:
                    select_game["name"] = game["game"]
            for game in games_link:
                if game["game"]["biz"] == select_game["biz"]:
                    if select_game["pre_download"] == "yes":
                        if game["pre_download"]["major"]:
                            select_game["links"] = game["pre_download"]
                        else:
                            return redirect("/select?code=001")
                    if select_game["pre_download"] == "no":
                        select_game["links"] = game["main"]
            for lang_select in select_game["links"]["major"]["audio_pkgs"]:
                for lang in lang_key:
                    if lang_select["language"] == lang["abv"]:
                        lang_select["language"] = lang["language"]
            for patch in select_game["links"]["patches"]:
                for lang_select in patch["audio_pkgs"]:
                    for lang in lang_key:
                        if lang_select["language"] == lang["abv"]:
                            lang_select["language"] = lang["language"]
            return render_template("links.html", game=select_game)
    return render_template("index.html")