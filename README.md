Docker image to generate the SP list (YAML) for HEXAA backend from
metadata source (XML) URL in the parameters.

You can set several metadata source URLs as a comma separated list.

You can find the built image on [Docker Hub](https://hub.docker.com/r/hexaaproject/hexaa-service-entityids-generator).

Building
--------

```
docker build -t hexaaproject/hexaa-service-entityids-generator .
```

Configuration
-------------

Configure the script via environment variables:

**METADATA_SOURCE_URLS**: comma separated list of xml format metadata soucre urls.

**TARGET_FILE_PATH**: the path of the hexaa\_entityids.yml in the container. Be sure to mount the required volume into the container.

**UPDATE_INTERVAL_MINUTES**: By default, the list is generated once after starting the program/container. If this variable is set, then the generation is repeated after the specified interval passes, until it is manually stopped.

Usage
-----

Example:

```
mkdir -p -m o+w /tmp/sp
docker run -t --rm --name hexaa-service-entityids-generator \
    -e METADATA_SOURCE_URLS=https://metadata.eduid.hu/current/href.xml \
    -e TARGET_FILE_PATH=/tmp/hexaa_entityids.yml \
    -v /tmp/sp:/tmp \
    hexaaproject/hexaa-service-entityids-generator
```

This will put the generated list in `/tmp/sp/hexaa_entityids.yml`.
