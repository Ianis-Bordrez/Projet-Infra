# ***Instructions d'installation***
### *Préparation de l’environnement*
Tout d’abord vous devrez louer un serveur sur le site que vous trouver le plus adapté pour vous. Lorsque vous avez établir une connexion au terminal, vous pouvez suivre les commandes suivantes pour mettre en place le serveur.

##### Mise en place du serveur:
```bash=


-        sudo apt install python3-pip nginx
-        sudo /etc/init.d/nginx start
-        sudo rm /etc/nginx/sites-enabled/default
-        sudo touch /etc/nginx/sites-available/flask_settings
-        sudo ln -s /etc/nginx/sites-available/flask_settings /etc/nginx/sites-enabled/flask_settings
-     nano /etc/nginx/sites-enabled/flask_settings

server {
    	location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
    	}
}
-        sudo /etc/nginx/init.d/nginx restart
-        pip3 install virtualenv flask gunicorn flask_monitoringdashboard
-        cd /home/ianis/
-        mkdir streamify
-        cd streamify
-        python3 -m venv env
-      source env/bin/activate
- 	export FLASK_APP=main.py
-	flask run
- 	gunicorn main :app
```
---
Ouverture des ports :
port 80 (http)
port 5000 (flask)
port 19999 (netdata)

L’arborescence du dossier est notamment important dans flask pour qu’il puisse reconnaître les différents type de fichier et leur utilité. 

Dans static nous avons les musiques que nous voulons afficher et dans templates les pages webs.
De plus, nous pouvons remarquer la présence d’un fichier main.py qui représente le coeur de l’application flask et qui nous permet de servir les différentes pages. Pour le faire marcher, il faut compléter le fichier de cette manière:
##### Setup de l'application Flask:

```python=


from flask import Flask, render_template,request
from pathlib import Path

import os
import flask_monitoringdashboard as dashboard

app = Flask(__name__, static_folder="static")
dashboard.bind(app)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["inputFile"]
        if not file.filename.lower().endswith((".mp3",".wav")):
                return "Mauvais format"
        elif Path(f"static/music/{file.filename}").is_file():
                return "Cette musique existe déjà"

        file.save(f"static/music/{file.filename}")
        return f"Musique envoyée {file.filename}"
    except Exception as e:
        return f"Erreur lors de l'envoi : {e}"

@app.route("/")
def index():
        return render_template("index.html")

@app.route("/music")
def music():
    musicList = []
    files = os.listdir("static/music")
    for f in files:
        musicList.append(f)
    return render_template("music.html", musicList=musicList)
```
---
##### Installation de BorgBackup :
```bash=


~$ borg init --encryption=repokey /home/ianis/borg
~/borg$ borg create ~/borg/::Monday ~/Streamify/static/music/
~$ borg list ~/borg/::Monday
~/borg_test$ borg extract ~/borg/::Monday
~$ cd ~/borg_test/
~/borg_test$ touch backup.sh
~$ sudo nano backup.sh
#!/bin/sh
export BORG_REPO=/home/ianis/borg/
export BORG_PASSPHRASE='borg_streamify'
info() { printf "\n%s %s\n\n" "$( date )" "$*" >&2; }
trap 'echo $( date ) Backup interrupted >&2; exit 2' INT TERM
info "Starting backup"
borg create                         \
    --verbose                       \
    --filter AME                    \
    --list                          \
    --stats                         \
    --show-rc                       \
    --compression lz4               \
    --exclude-caches                \
                                    \
    ::'{hostname}-{now}'            \
     ~/Streamify/static/music/      \
backup_exit=$?
info "Pruning repository"
borg prune                          \
    --list                          \
    --prefix '{hostname}-'          \
    --show-rc                       \
    --keep-daily    7               \
prune_exit=$?
global_exit=$(( backup_exit > prune_exit ? backup_exit : prune_exit ))
if [ ${global_exit} -eq 0 ]; then
    info "Backup and Prune finished successfully"
elif [ ${global_exit} -eq 1 ]; then
    info "Backup and/or Prune finished with warnings"
else
    info "Backup and/or Prune finished with errors"
fi
exit ${global_exit}
~$ ./backup.sh
```
