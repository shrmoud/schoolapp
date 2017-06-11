# Tandlr
Pltaform to teach and learn.


## Prerequisites
+ [Oracle's VirtualBox](https://www.virtualbox.org/)
+ [Vagrant](http://www.vagrantup.com/)
+ [Python](http://www.python.org/)
+ [Fabric](http://www.fabfile.org/)
+ [fabutils](https://github.com/vinco/fabutils)
+ [flake8](https://flake8.readthedocs.org/en/latest/)
+ [flake8-import-order](https://github.com/public/flake8-import-order)


## Testing prerequisites
+ [SpatiaLite](https://docs.djangoproject.com/en/1.7/ref/contrib/gis/install/spatialite/)
+ [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)


## Usage

1. Start up project.

    ```bash
    $ vagrant up
    $ fab environment:vagrant bootstrap
    ```

2. Run server.

    ```bash
    $ fab environment:vagrant runserver
    ```

3. Run worker.
    ```bash
    $ fab environment:vagrant runworker
    ```

4. Run Daphne
    ```bash
    $ fab environment:vagrant rundaphne
    ```

5. Run Celery
    ```bash
    $ fab environment:vagrant celery
    ```


## Testing

1. Install SpatiaLite if it isn't already installed.


2. Create a virtualenvironment for the project (if it does not exists).

    ```bash
    $ mkvirtualenv tandlr
    $ pip install tox
    ```

3. Activate the testing virtual environment.

    ```bash
    $ workon tandlr
    ```

4. Run the proper command with tox.

    ```bash
    # Run the full test suite including the PEP8 linter.
    $ tox

    # Run only the test suite.
    $ tox -e py27-django

    # Run only the PEP8 linter.
    $ tox -e py27-flake8

    # Pass -r flag to recreate the virtual environment when requirements changes.
    $ tox -r
    ```

5. Deactivate the virtual environment.

    ```bash
    $ deactivate
    ```

6.  Redirect the required domains to your localhost

    ```bash
    # /etc/hosts
    192.168.33.40       tandlr.local
    ```

# Socket server usage

## Connect
* You need connect with a client socket to next URL.

    ```json
    ws://domain.or.address:8888/notifications
    ```

## Response
There are two types of answer that are returned by the sockets server.

1.  Mass notification with/without university

    ```json
    {
        "target_action": "mass_notification",
        "message": "Message defined by admin"
    }
    ```

2.  Push notification

    ```json
    /*
        target_id: Id of object modified.

        target_type: Class name of object modified, these can be:
            class
            mass_notification
            chat
            requestclassextensiontime

        target_action: Action done on object. For example, a class can be:
            rejected
            scheduled
            accepted
            on course
            ended
            pending
            canceled
    */
    {
        "target_id": "1",
        "target_type": "class",
        "target_action": "accepted"
    }
    ```