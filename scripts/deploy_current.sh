#!/bin/bash

git add *
git commit -m "Ops: Temporal commit for Heroku deployment"
./scripts/deploy.sh "$(git branch --show-current)"
git reset --soft HEAD~1
git reset
