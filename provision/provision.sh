#!/bin/bash
echo "Updating apt repositories..."
apt-get update


echo "Installing base packages..."
PACKAGES="build-essential zsh git vim-nox tree htop libjpeg-dev libfreetype6-dev graphviz gettext"
PACKAGES="$PACKAGES python python-setuptools python-pip python-dev"
PACKAGES="$PACKAGES postgresql-9.3 postgresql-server-dev-9.3 postgresql-9.3-postgis-2.1"
PACKAGES="$PACKAGES rabbitmq-server"
PACKAGES="$PACKAGES nginx"

apt-get install -y $PACKAGES


echo "Setting up PostgreSQL server..."
cp /tmp/templates/postgresql/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
service postgresql restart

USER_EXISTS=$(psql -U postgres -h localhost -tAc "SELECT 1 FROM pg_roles WHERE rolname='vagrant'" postgres)
DB_EXISTS=$(psql -U postgres -h localhost -tAc "SELECT 1 FROM pg_database WHERE datname='vagrant'" postgres)


if [ ! $USER_EXISTS ]; then
    sudo -Hu postgres bash -c 'createuser -s vagrant'
fi

if [ ! $DB_EXISTS ];then
    sudo -Hu postgres bash -c 'createdb vagrant'
    sudo -u postgres psql -c "grant all privileges on database vagrant to vagrant"
    sudo -u postgres psql -c "ALTER ROLE vagrant WITH PASSWORD 'vagrant'"
fi

echo "Setting up reverse proxy with Nginx..."
unlink /etc/nginx/sites-enabled/default
cp /tmp/templates/nginx/local.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/local.conf /etc/nginx/sites-enabled/
service nginx restart


echo "Installing Oh My Zsh!..."
OHMYZSH_DIR=/home/vagrant/.oh-my-zsh

if [ ! -d $OHMYZSH_DIR ]; then
    sudo -Hu vagrant bash -c "git clone https://github.com/robbyrussell/oh-my-zsh.git $OHMYZSH_DIR"
fi

cp /tmp/templates/zsh/zshrc /home/vagrant/.zshrc
cp /tmp/templates/zsh/zprofile /home/vagrant/.zprofile
chown vagrant:vagrant /home/vagrant/.zshrc
chown vagrant:vagrant /home/vagrant/.zprofile
chsh -s $(which zsh) vagrant


echo "Configuring virtualenv..."
VIRTUALENV_DIR=/home/vagrant/env

pip install virtualenv

if [ ! -d "$VIRTUALENV_DIR" ]; then
    mkdir $VIRTUALENV_DIR
    virtualenv $VIRTUALENV_DIR
    chown -R vagrant:vagrant $VIRTUALENV_DIR
fi


echo "Installing python dependencies..."
REQUIREMENTS_FILE=/home/vagrant/src/requirements/devel.txt

if [ -f "$REQUIREMENTS_FILE" ]; then
    sudo -Hu vagrant bash -c "source $VIRTUALENV_DIR/bin/activate && pip install -r $REQUIREMENTS_FILE"
fi


echo "Creating Django project..."
PROJECT_NAME=tandlr
PROJECT_DIR=/home/vagrant/src/$PROJECT_NAME

if [ ! -d  "$PROJECT_DIR" ]; then
    export PROJECT_NAME
    sudo -Hu vagrant bash -c "source $VIRTUALENV_DIR/bin/activate && django-admin.py startproject $PROJECT_NAME $PROJECT_DIR/.."
    mkdir $PROJECT_DIR/settings
    rm $PROJECT_DIR/settings.py
    echo "$(envsubst < /tmp/templates/django/settings_base.py)" > $PROJECT_DIR/settings/__init__.py
    echo "$(envsubst < /tmp/templates/django/settings_devel.py)" > $PROJECT_DIR/settings/devel.py
    chown -R vagrant:vagrant $PROJECT_DIR/..
fi

echo "Installing Redis..."
if [ ! -x /usr/local/bin/redis-server ]; then
  apt-get install -y build-essential tcl8.5

  wget http://download.redis.io/releases/redis-stable.tar.gz
  tar xzf redis-stable.tar.gz
  cd redis-stable

  make
  make install

  cd utils
  ./install_server.sh
fi

echo "Done."
