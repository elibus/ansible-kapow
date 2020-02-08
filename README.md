Role Name
=========

Install and configure kapow (https://github.com/BBVA/kapow/).

Requirements
------------

None.

Role Variables
--------------

```
# kapow version to install
kapow_version: 0.3.0
# Distrubution url
kapow_dist_base_url: "https://github.com/BBVA/kapow/releases/download"
# Destination folder where to install the binary
kapow_bin_dir: /usr/local/bin
# File checksum
kapow_checksum: sha512:d5da23bb7480a3e39eb6942cc09397f6fcad525f77381abbf501ae87908840878c83f1a2c623285e1de58619c83ffae8517b3440053edde0c889ccbd0371fcbb
```

Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```
    - hosts: servers
      roles:
         - elibus.kapow
  vars:
    kapow_routes:
      - {
        command: "kapow get /request/matches/message | kapow set /response/body",
        url_pattern: "/hello"
      }
      - {
        command: "kapow get /request/matches/message | kapow set /response/body",
        url_pattern: "/hello2"
      }
      - {
        command: "kapow get /request/matches/message | kapow set /response/body",
        url_pattern: "/hello3",
        state: absent
      }
```

License
-------

GPL3

Author Information
------------------

Github: https://github.com/elibus/ansible-kapow