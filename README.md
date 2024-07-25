# Introduction

This python tool makes it easy to generate boilerplate code for creating Terraform resource.

# Build

*Prerequsite:* Install Poetry first.

Install tool dependencies:

```shell
poetry install
```

# Usage

```
poetry run crd2go <crd.yaml> <output-file>
```

Example:

```
poetry run crd2go example.txt example.yaml
```

Look at the [example.txt](./example.txt) and [example.go](./example.go) in the root folder to see how the CRD spec is translated.