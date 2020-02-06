# 1920-srv6-tutorial

The file ospf_generator.py reads all the hosts, routers and links out of the YAML-file input-onlineyamltools.yaml, generates all configuration files in /nodeconf/ and then creates the python file ospf.py, which can be used to start mininet with the desired topology, running: sudo python ospf.py