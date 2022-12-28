#!/usr/bin/env bash

# Dumps Git log output to JSON.
# https://gist.github.com/april/ee2e104b1435f3113e67663d8875bbef

git-log-json() {
  IFS='' read -r -d '' FORMAT << 'EOF'
  {
  ^^^^author^^^^: { ^^^^name^^^^: ^^^^%aN^^^^,
    ^^^^email^^^^: ^^^^%aE^^^^,
    ^^^^date^^^^: ^^^^%aD^^^^,
    ^^^^dateISO8601^^^^: ^^^^%aI^^^^},
  ^^^^body^^^^: ^^^^%b^^^^,
  ^^^^commitHash^^^^: ^^^^%H^^^^,
  ^^^^commitHashAbbreviated^^^^: ^^^^%h^^^^,
  ^^^^committer^^^^: {
    ^^^^name^^^^: ^^^^%cN^^^^,
    ^^^^email^^^^: ^^^^%cE^^^^,
    ^^^^date^^^^: ^^^^%cD^^^^,
    ^^^^dateISO8601^^^^: ^^^^%cI^^^^},
  ^^^^encoding^^^^: ^^^^%e^^^^,
  ^^^^notes^^^^: ^^^^%N^^^^,
  ^^^^parent^^^^: ^^^^%P^^^^,
  ^^^^parentAbbreviated^^^^: ^^^^%p^^^^,
  ^^^^refs^^^^: ^^^^%D^^^^,
  ^^^^signature^^^^: {
    ^^^^key^^^^: ^^^^%GK^^^^,
  ^^^^signer^^^^: ^^^^%GS^^^^,
  ^^^^verificationFlag^^^^: ^^^^%G?^^^^},
  ^^^^subject^^^^: ^^^^%s^^^^,
  ^^^^subjectSanitized^^^^: ^^^^%f^^^^,
  ^^^^tree^^^^: ^^^^%T^^^^,
  ^^^^treeAbbreviated^^^^: ^^^^%t^^^^
  },
EOF
  FORMAT=$(echo $FORMAT|tr -d '\r\n ')

  git -C $1 log --pretty=format:$FORMAT | \
  sed -e ':a' -e 'N' -e '$!ba' -e s'/\^^^^},\n{\^^^^/^^^^},{^^^^/g' \
      -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\^^^^/"/g' -e '$ s/,$//' | \
  sed -e ':a' -e 'N' -e '$!ba' -e 's/\r//g' -e 's/\n/\\n/g' -e 's/\t/\\t/g' | \
  awk 'BEGIN { ORS=""; printf("[") } { print($0) } END { printf("]\n") }'
}

git-log-json "$1"
