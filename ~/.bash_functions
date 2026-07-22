#!/use/bin/env bash
acp() {
  MSG="$@"
  if [ -z "$MSG" ]; then
    MSG="Updates"
  fi
  git status -s && \
    git add -A && \
    git status -s && \
    git commit -m "$MSG" && \
    git push
}