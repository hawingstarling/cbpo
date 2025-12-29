#!/bin/bash
npm install --registry http://npm-registry.channelprecision.com
npm run build:lib
npm version $VERSION --force
echo $?
echo '//npm-registry.channelprecision.com/:_authToken=${NPM_TOKEN}'>.npmrc
npm publish --registry http://npm-registry.channelprecision.com --access public
