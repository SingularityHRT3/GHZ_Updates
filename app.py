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
                    temp_data["link"] = package
                    if package["pre_download"]["major"]:
                        temp_data["pre"] = True
                        for abv in lang_key:
                            for lang in temp_data["link"]["pre_download"]["major"]["audio_pkgs"]:
                                if lang["language"] == abv["abv"]:
                                    lang["language"] = abv["language"]
                            for patch in temp_data["link"]["pre_download"]["patches"]:
                                for lang in patch["audio_pkgs"]:
                                    if lang["language"] == abv["abv"]:
                                        lang["language"] = abv["language"]
                    else:
                        temp_data["pre"] = False
                        for abv in lang_key:
                            for lang in temp_data["link"]["main"]["major"]["audio_pkgs"]:
                                if lang["language"] == abv["abv"]:
                                    lang["language"] = abv["language"]
                            for patch in temp_data["link"]["main"]["patches"]:
                                for lang in patch["audio_pkgs"]:
                                    if lang["language"] == abv["abv"]:
                                        lang["language"] = abv["language"]                    
                    games_list.append(temp_data)
        temp_data = {}
        temp_data["link"] = []
        for package in json["data"]["game_packages"]:
            if package["game"]["biz"] == hi3["biz"]:
                temp_data["biz"] = hi3["biz"]
                temp_data["game"] = hi3["game"]
                if package["pre_download"]["major"]:
                    temp_data["pre"] = True
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
        links = {}
        for game in games_list:
            if game["biz"] == select_game["biz"]:
                links = game["link"]
        select_game["pre"] = request.form.get("pre")
        select_game["method"] = request.form.get("method")
        select_game["language"] = request.form.get("language")
        temp_pre = ""
        if select_game["pre"] == "yes":
            temp_pre = "pre_download"
        else:
            temp_pre = "main"
        if select_game["biz"] == hi3["biz"]:
            select_game["game"] = hi3["game"]
            select_game["links"] = []
            for link in links:
                select_game["version"] = link[temp_pre]["major"]["version"]
                for package in link[temp_pre]["major"]["game_pkgs"]:
                    select_game["links"].append(package)
        else:
            for game in biz_list:
                if game["biz"] == select_game["biz"]:
                    select_game["game"] = game["game"]
                    break
            select_game["version"] = links[temp_pre]["major"]["version"]
            if select_game["method"] == "major":
                select_game["links"] = links[temp_pre]["major"]
            else:
                select_game["links"] = []
                for patch in links[temp_pre]["patches"]:
                    select_game["links"].append(patch)
        return render_template("links.html", game=select_game)
    return render_template("index.html")