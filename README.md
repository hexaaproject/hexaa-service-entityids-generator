Docker image to generate the SP list for hexaa backend with metadata source url in the parameters.

You can list several space separated metadata source urls.


Configuration
-------------

Configure the script via environment variables:

**METADATA_SOURCE_URLS**: comma separated list of xml format metadata soucre urls.

**TARGET_FILE_PATH**: the path of the hexaa\_entityids.yml in the container. Be sure to mount the required volume into the container.

**UPDATE_INTERVAL_MINUTES**: By default, the list is generated once after starting the program/container. If this variable is set, then the generation is repeated after the specified interval passes, until it is manually stopped.

Usage
-----
example:

`docker run -t --rm --name hexaa-service-entityids-generator -e METADATA_SOURCE_URLS=https://metadata.eduid.hu/current/href.xml -e TARGET_FILE_PATH=/tmp/hexaa_entityids.yml -v /tmp/aa:/tmp szabogyula/hexaa-service-entityids-generator`
