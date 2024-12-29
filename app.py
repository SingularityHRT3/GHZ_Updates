from flask import Flask, render_template, request, redirect
import requests
import json


app = Flask(__name__)

games_link = []
game_list = []
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
    global games_link, game_list
    if request.method == "POST":
        url = request.form.get("url")
        try:
            json = requests.get(url).json()
        except:
            return render_template("index.html", message="Enter the correct API URL.")
        if json["retcode"] != 0 or json["message"] != "OK" or json.get("data") == None:
            return render_template("index.html", message="Enter the correct API URL.")
        games_link = []
        for game in json["data"]["game_packages"]:
            games_link.append(game)
        game_list = []
        game_biz = biz_list.copy()
        for biz in game_biz:
            for game in games_link:
                if game["game"]["biz"] == biz["biz"]:
                    game_list.append(biz)
        for game in games_link:
            if game["game"]["biz"] == hi3["biz"]:
                game_list.append(hi3)
                break
        if len(game_list) == 0:
            return render_template("index.html", message="API Error, try again.")
        return redirect("/select")
    return render_template("index.html")

@app.route("/select")
def select():
    if request.args.get('code') == "001":
        return render_template("select.html", games=game_list, message = "Pre-Download not available. Choose Main Download.")
    if request.args.get('code') == "002":
        return render_template("select.html", games=game_list, message = "Select a Game.")
    if request.args.get('code') == "003":
        return render_template("select.html", games=game_list, message = "Select a Download Method.")
        
    return render_template("select.html", games=game_list)

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