# Contribution Guide

You shouldn't edit the node class files by yourself.

## Set up your environment

* See [DEVELOPMENT][DEVELOPMENT.md] ??

## Resources

### Update nodes

Images should be resized to fit a maximum of 256 pixels wide or high.

[DEVELOPMENT.md]: ./DEVELOPMENT.md

## Run Tests

```shell
python -m unittest tests/*.py -v
```

## Testing changes to the website

The [Docusaurus](https://docusaurus.io/)-based documentation website can be run by installing dependencies, then simply running `npm run start`.

```bash
cd website/
npm i
npm run start
```

The website will be available on [http://localhost:3000](http://localhost:3000).

Edit files in `website/` and `docs/` respectively to edit documentation.
