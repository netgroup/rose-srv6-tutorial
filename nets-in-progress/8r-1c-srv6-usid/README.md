# 8r-1c-srv6-usid Topology

A Mininet topology with 8 routers running IS-IS routing protocol, 12 hosts, 3 datacenters and a controller connected out-of-band to all the routers of the network.

This topology has been used to perform fuctional assessment and interoperability demonstration of the Micro SIDs solution described [here](https://arxiv.org/pdf/2007.12286.pdf).


The topology is not contained in this repository, but it is available as *git submodule* on this repository. The original repository is [here](https://github.com/netgroup/usid-interop-testbed). To load the submodule, you need to execute the command:

```
git submodule update --init
```

And then you can find the topology under the folder `rose-srv6-tutorial/nets-in-progress/8r-1c-srv6-usid/usid-interop-testbed/`.