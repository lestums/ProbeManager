#!/usr/bin/env bash



echo '## discover ##'
ls -la
which python
which git
git describe master
echo $PWD

echo '## Install ##'
pip install -r requirements/base.txt
pip install -r requirements/test.txt
DJANGO_SETTINGS_MODULE="probemanager.settings.dev"
export DJANGO_SETTINGS_MODULE
export PYTHONPATH=$PYTHONPATH:$PWD/probemanager

echo '## Set Git ##'
git_bin=$( which git )
echo "[GIT]"  >> conf.ini
echo "GIT_BINARY = $git_bin" >> conf.ini

echo '## Generate version ##'
python probemanager/manage.py runscript version --settings=probemanager.settings.dev --script-args -


echo '## Create DB ##'
for f in probemanager/*; do
    if [[ -d $f ]]; then
        if test -d "$f"/migrations ; then
            rm "$f"/migrations/00*.py
        fi
    fi
done
sudo su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD 'probemanager';\""
sudo su postgres -c 'createdb -T template0 -O probemanager probemanager'

python probemanager/manage.py makemigrations --settings=probemanager.settings.dev
python probemanager/manage.py migrate --settings=probemanager.settings.dev
python probemanager/manage.py loaddata init.json --settings=probemanager.settings.dev
python probemanager/manage.py loaddata crontab.json --settings=probemanager.settings.dev
for f in probemanager/*; do
    if [[ -d $f ]]; then
        if test -f "$f"/init_db.sh ; then
            ./"$f"/init_db.sh dev
        fi
    fi
done

echo '## Generate doc ##'
python probemanager/manage.py runscript generate_doc --settings=probemanager.settings.dev

echo '## END  INSTALL##'
