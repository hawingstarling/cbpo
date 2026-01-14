#!/bin/bash
npm install --registry http://npm-registry.channelprecision.com
npm run build:lib --fix
npm version ${VERSION:1}
npm publish --registry http://npm-registry.channelprecision.com --access public