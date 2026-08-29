# Q1 - Kubernetes Deployment

Deploys redis as a 2-replica cache in its own namespace, using one manifest
file (`special-definition.yml`) applied with `kubectl apply -f`.

## About the namespace name

The challenge asks for a namespace called "CyberCo", but Kubernetes won't
allow that - namespace names have to be lowercase (RFC 1123 DNS label rules),
so `CyberCo` gets rejected by the API server. I used `cyberco` instead.

## Why "sudo execute" works

`execute` isn't a real command, it's an alias:

    alias sudo='sudo '
    alias execute='kubectl --kubeconfig=/home/maxofax/.kube/config apply -f special-definition.yml'

The trailing space after `sudo=` matters - it tells bash to also try
expanding the next word as an alias, which is how `execute` gets picked up
even though it comes after `sudo`. Without that space, bash would just look
for a literal command called `execute` and fail.

Also worth noting: kubectl doesn't actually need root to talk to the cluster.
The sudo requirement here is just part of the exercise (same pattern as q2),
not a real permissions need.

## The sudo/kubeconfig gotcha I ran into

First attempt at `sudo execute` failed with:

    dial tcp 127.0.0.1:8080: connect: connection refused

Took a bit to figure out why - running kubectl under sudo means it's now
running as root, and root doesn't have my kubeconfig (it lives in
`~/.kube/config` under MY home directory, not root's). With no config found,
kubectl falls back to an old default address that nothing's listening on.
Fixed it by pointing the alias straight at the config file with
`--kubeconfig=`, so it doesn't matter whose $HOME sudo thinks it's using.

## Running it

    cd q1-k8s-deployment
    sudo execute

## Checking it worked

    kubectl get namespace cyberco
    kubectl get deployment cache-db -n cyberco -o wide
    kubectl get pods -n cyberco -o wide

Should see the namespace as Active, the deployment at 2/2 ready, and two
pods running on the redis:buster image.
