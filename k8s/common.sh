# Shared by the numbered scripts. Source it; do not run it.
set -euo pipefail
K8S_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$K8S_DIR")"          # the starter folder, where the Dockerfile lives
CLUSTER=yard                             # kind cluster name; node containers are yard-control-plane, yard-worker, yard-worker2
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"

say() { printf '\n== %s\n' "$*"; }                 # announce a step
run() { printf '$ %s\n' "$*"; "$@"; }              # show a command, then run it

use_yard() {
  kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || { echo "No '$CLUSTER' cluster. Run ./00-create-yard.sh first."; exit 1; }
  kubectl config use-context "kind-$CLUSTER" >/dev/null
}

# Load a local image into every kind node. Falls back to an archive if the direct load fails.
load_image() {
  if ! kind load docker-image "$1" --name "$CLUSTER"; then
    echo "direct load failed; trying docker save | kind load image-archive"
    local tar; tar="$(mktemp -t kindimg).tar"
    docker save "$1" -o "$tar" && kind load image-archive "$tar" --name "$CLUSTER"; rm -f "$tar"
  fi
}

PODS="kubectl get pods -l app=status-board -o wide"
