
TroubleShooting
===============

Port Already in use
___________________

Don't panic when this error occurs.
This error is because two Melodie Visualizers cannot run on the same port.
Please verify that there aren't any other visualizer process running on your computer.

Windows
^^^^^^^
On Windows, use this command:

.. code-block:: shell

    netstat -aon|findstr "8765"

The output is:

.. code-block:: shell

    C:\Users\UserName>netstat -aon|findstr "8765"
    TCP    127.0.0.1:8765         0.0.0.0:0              LISTENING       19064
    TCP    127.0.0.1:8765         127.0.0.1:64450        ESTABLISHED     19064
    TCP    127.0.0.1:64450        127.0.0.1:8765         ESTABLISHED     24236
    TCP    [::1]:8765             [::]:0                 LISTENING       19064

The output above indicates that process 19064 is LISTENING port 8765, let's kill this process by:

.. code-block:: shell

    taskkill /T /F /PID 19064

MacOS, Linux or other *nix systems
^^^^^^^
On MacOS or Linux, use this command:

.. code-block:: shell

    # lsof -i:8765
    COMMAND   PID USER   FD   TYPE   DEVICE SIZE/OFF NODE NAME
    python  26993 root   10u  IPv4 37999514      0t0  TCP *:8765 (LISTEN)

The output shows that process 26993 is holding this port, so kill this process by:

.. code-block:: shell

    kill -9 26993

In the future, different visualizer will start in different ports automatically.
