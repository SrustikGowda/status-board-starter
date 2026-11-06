# A Yard of Hubs: Kubernetes on your laptop

Hands-on files for the film "Kubernetes: A Yard of Hubs". You build a tiny cluster with kind, ask for
three copies of the Status Board, delete one, and watch the cluster open another.

Film words and Kubernetes words:

| Film | Kubernetes | In these files |
| --- | --- | --- |
| crate | pod | a running copy of `status-board` |
| hub | node | a Docker container named `yard-worker` or `yard-worker2` |
| yard | cluster | the kind cluster `yard` |
| clipboard | Deployment | `deployment.yaml` |
| counter | Service | `service.yaml` |

## What you need

- Docker (Docker Desktop is fine), running
- [kind](https://kind.sigs.k8s.io/) (`brew install kind`)
- kubectl (`brew install kubectl`, or the one that ships with Docker Desktop)
- About 2 GB of free memory and a few minutes the first time (images are downloaded once)

Run every script from anywhere; they find their own files. Port 8092 on your laptop must be free for step 05.

## Run the scripts in order

Each script prints what it is about to do, then does it.

| Script | Film chapter | What you should see |
| --- | --- | --- |
| `./00-create-yard.sh` | the yard | A kind cluster with 3 nodes, all `Ready`. The app is built as `status-board:v1` and loaded into every node. |
| `./01-write-the-clipboard.sh` | the clipboard | `deployment.yaml` applied; `3/3` ready; three pods spread over the two workers. |
| `./02-delete-a-crate.sh` | on your laptop | One pod goes `Terminating`, a new one appears within a second and is `Running` a few seconds later. You touch nothing. |
| `./03-ask-for-five.sh` | ask for five | Change `replicas` to 5: two more pods open. Then the real file (three) is applied again and two close. |
| `./04-one-at-a-time.sh` | one at a time | Build `status-board:v2` (heading reads "Status Board v2"), roll it out one pod at a time with no gap, then `rollout undo` back to v1. |
| `./05-the-counter.sh` | the counter | A Service in front of the pods; `curl localhost:8092/health` answers `OK` every time. |
| `./06-dark-hub.sh` | dark hub | One worker node (a Docker container) is stopped. After about 80 seconds its pods are replaced on the other worker. The node is then started again. |
| `./07-literal.sh` | literal | A wrong image tag and `replicas: 0` are applied. The cluster does exactly that. You fix the file, not the pods. |
| `./99-clean-up.sh` | | Deletes the cluster. |

`SAMPLE_OUTPUT.txt` is a real run of scripts 00 to 07 on an Apple silicon Mac, for comparison.
Pod names, IP addresses and timings will differ on your machine.

## Check yourself

After step 02 you should be able to say, without looking:

> the clipboard still said three, so the tower opened another.

That is the whole mechanism: the Deployment's `replicas: 3` is the desired state, and the controller
keeps creating pods until the number running matches it.

## Notes

- `deployment.yaml` has a 30-second toleration for unreachable nodes (the default is 300 s) so the
  dark-hub demo finishes in about a minute and a half. Leave it out in a real cluster unless you mean it.
- Version two is made by `Dockerfile.v2`, which only changes the page heading, so you can see the new
  version without editing `app.py`.
- Everything is local. `99-clean-up.sh` removes the cluster; to also remove the images:
  `docker rmi status-board:v1 status-board:v2`.
- If a step is interrupted halfway, the scripts are safe to run again, except `00-create-yard.sh`,
  which needs `./99-clean-up.sh` first if the cluster already exists.
