
Set up docker for, e.g., Ubuntu, using the stable channel
=========================================================

Instructions cribbed from: https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository

    $ sudo apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common
    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    $ sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable"

Install docker
==============
$ sudo apt-get update
$ sudo apt-get install docker-ce docker-compose

You may need to add yourself to the docker group thus:

$ sudo adduser $LOGNAME docker
$ exec newgrp docker    # or log out, log back in

Edit db.env file
================

$ cp db.env.example db.env
$ $EDITOR db.env

Set up environment
==================

$ docker-compose up

Test
====

    $ env-vars ()
    {
        awk -F= '{printf "'%s=%s' ", $1, $2}' config/test_api.env
    }
    $ docker exec -it metrics_api env $(env-vars) nosetests -v
